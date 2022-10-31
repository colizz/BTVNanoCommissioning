import os
import sys
import json

import numpy as np
import pandas as pd
import rhalphalib as rl
import uproot
import ROOT

AK8taggers = ['btagDDBvLV2', 'btagDDCvLV2', 'particleNetMD_Xbb_QCD', 'particleNetMD_Xcc_QCD']
regions = ['pass', 'fail']

epsilon = 1e-3

def rebin(h_vals, h_sumw2, bins, lo, hi):
    binwidth = bins[1] - bins[0]
    bin_centers = (bins + 0.5*binwidth)[:-1]
    mask = (bin_centers >= lo) & (bin_centers <= hi)
    idx = np.argwhere(mask)[0][0]
    mask_bins = np.concatenate((mask[:idx],[True],mask[idx:]))      # Add an extra True value for `bins` array
    h_vals = h_vals[mask]
    h_sumw2 = h_sumw2[mask]
    bins = bins[mask_bins]

    return h_vals, h_sumw2, bins

class Fit():
    def __init__(self, cfg, categories, var, xlim):
        self.cfg = cfg
        self.year = cfg["dataset"]["filter"]["year"]
        if len(self.year) > 1:
            raise NotImplementedError
        else: self.year = self.year[0]
        self.var = var
        self.lo = xlim[0]
        self.hi = xlim[1]
        self.define_flavors()
        if self.cfg["sf_options"]["label"]:
            self.templates = np.load(os.path.abspath(os.path.join(self.cfg["output"], 'output_{}.pkl'.format(self.cfg["sf_options"]["label"]))), allow_pickle=True)
            if self.merge_x_xx & (not self.cfg["sf_options"]["label"].startswith('bbcc')):
                raise NotImplementedError
        else:
            self.templates = np.load(os.path.abspath(os.path.join(self.cfg["output"], 'output.pkl')), allow_pickle=True)
        #self.categories = json.load( open(os.path.join(self.cfg["output"], 'categories.json')) )
        self.categories = categories
        self.fitResults = {
            'bb' : os.path.join(os.getcwd(), self.cfg["output"], 'fitResults_bb.csv'),
            'cc' : os.path.join(os.getcwd(), self.cfg["output"], 'fitResults_cc.csv'),
        }
        self.signal_name = {}
        self.define_bins()
        self.define_observable()
        self.initialize_models_dict()
        self.load_parameters()
        self.define_independent_parameters()
        self.define_frozen_parameters()
        self.build_fit_models()
        self.build_combine_script()
        #self.run_fits()
        #self.save_results()

    def define_flavors(self):
        self.merge_x_xx = self.cfg["sf_options"]["merge_x_xx"]
        if self.merge_x_xx:
            self.flavors = ['bb', 'cc', 'l']
        else:
            self.flavors = ['bb', 'cc', 'b', 'c', 'l']

    def define_bins(self):
        name_map = {'n_or_arr' : 'num', 'lo' : 'start', 'hi' : 'stop'}
        arguments = dict((name_map[name], val) for name, val in self.cfg['sf_options']['rebin'][self.var]['binning'].items())
        arguments['num'] += 1
        self.bins = np.linspace(**arguments)

    def define_observable(self):
        self.observable = rl.Observable(self.var, self.bins)

    def initialize_models_dict(self):
        self.categories_region = {}
        self.categories_region['pass'] = list( filter( lambda c : 'pass' in c, self.categories ) )
        if len(self.categories_region['pass']) == 0:
            sys.exit("No 'pass' region found in categories' list")
        self.categories_region['fail'] = [c.replace('pass', 'fail') for c in self.categories_region['pass']]
        self.models = {}
        for region in ['pass']:
            categories = self.categories_region[region]

            for cat in categories:
                model_name = cat.replace(region, '')
                self.models[model_name] = rl.Model("sfModel")

    def load_parameters(self):
        self.parameters = self.cfg["sf_options"]["parameters"]
        for model_name in self.models.keys():
            if not model_name in self.parameters.keys():
                self.parameters[model_name] = {}
                for flavor in self.flavors:
                    self.parameters[model_name][flavor] = {'value' : 1., 'lo' : 0., 'hi' : 2.}

    def define_independent_parameters(self):
        self.indep_pars = {}
        for model_name in self.models.keys():
            self.indep_pars[model_name] = {}
            for flavor in self.flavors:
                self.indep_pars[model_name][flavor] = rl.IndependentParameter(flavor, **self.parameters[model_name][flavor])

    def define_frozen_parameters(self):
        self.freeze = {}
        for model_name in self.models.keys():
            self.freeze[model_name] = []
            for name, par in self.parameters[model_name].items():
                if par['lo'] == par['hi']:
                    self.freeze[model_name].append(name)
            #print(model_name, ": Freeze parameters :", self.freeze)

    def define_signal_name(self, model_name):
        self.tagger = [tagger for tagger in AK8taggers if tagger in model_name][0]
        if self.tagger in ['btagDDBvLV2', 'particleNetMD_Xbb_QCD']:
            self.signal_name[model_name] = 'bb'
        elif self.tagger in ['btagDDCvLV2', 'particleNetMD_Xcc_QCD']:
            self.signal_name[model_name] = 'cc'
        else:
            sys.exit("There is no known tagger to calibrate in the given category")

    def get_templ(self, histname, lo, hi, sumw2=True):
        h_vals = self.templates[histname][0]
        h_sumw2 = self.templates[histname][1]
        bins = self.observable.binning
        
        h_vals, h_sumw2, bins = rebin(h_vals, h_sumw2, bins, lo, hi)

        if not sumw2:
            return (h_vals, bins, self.observable.name)
        else:
            return (h_vals, bins, self.observable.name, h_sumw2)

    def build_fit_models(self):
        self.fitdirs = {}

        for region in regions:
            for cat in self.categories_region[region]:
                model_name = cat.replace(region, '')
                self.define_signal_name(model_name)
                channel = rl.Channel("sf{}".format(region))
                for flavor in self.flavors:
                    template = self.get_templ("hist_{}_{}_QCD_{}_{}".format(self.var, cat, flavor, self.year), self.lo, self.hi)

                    is_signal = True if flavor == self.signal_name[model_name] else False
                    sType = rl.Sample.SIGNAL if is_signal else rl.Sample.BACKGROUND
                    sample = rl.TemplateSample("{}_{}".format(channel.name, flavor), sType, template)
                    sample.autoMCStats(epsilon=epsilon)
                    channel.addSample(sample)

                template_obs = self.get_templ("hist_{}_{}_Data_{}".format(self.var, cat, self.year), self.lo, self.hi, sumw2=False)
                channel.setObservation(template_obs)

                self.models[model_name].addChannel(channel)

        for model_name, model in self.models.items():
            for flavor, SF in self.indep_pars[model_name].items():
                sample_pass = self.models[model_name]['sfpass'][flavor]
                sample_fail = self.models[model_name]['sffail'][flavor]
                pass_fail   = sample_pass.getExpectation(nominal=True).sum() / sample_fail.getExpectation(nominal=True).sum()
                sample_pass.setParamEffect(SF, 1.0 * SF)
                sample_fail.setParamEffect(SF, (1 - SF) * pass_fail + 1)

            fitdir = os.path.abspath(os.path.join(self.cfg["output"], 'fitdir', model_name))
            if not os.path.exists(fitdir):
                os.makedirs(fitdir)
            self.models[model_name].renderCombine(fitdir)
            self.fitdirs[model_name] = fitdir

    def build_combine_script(self):
        for model_name, model in self.models.items():
            bash_script = os.path.join(self.fitdirs[model_name], 'build.sh')
            with open(bash_script, 'a') as file:
                combineCommand = '\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name _{} --cminDefaultMinimizerStrategy 2 --robustFit=1 --saveShapes --saveWithUncertainties --saveOverallShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r --rMin 1 --rMax 1'.format(model_name, self.signal_name[model_name])
                setParameters = 'r=1'
                freezeParameters = 'r'
                for par in self.freeze[model_name]:
                    setParameters += ',{}=1'.format(par)
                    freezeParameters += ',{}'.format(par)
                combineCommand = combineCommand.replace('--setParameters r=1', '--setParameters {}'.format(setParameters))
                combineCommand = combineCommand.replace('--freezeParameters r', '--freezeParameters {}'.format(freezeParameters))
                file.write(combineCommand)

    def run_fits(self):
        command = 'bash build.sh'
        parent_dir = os.getcwd()
        self.first = {'bb' : True, 'cc' : True}
        for model_name, fitdir in self.fitdirs.items():
            if fitdir:
                os.chdir(fitdir)
            else:
                sys.exit("The fit directory is not well defined or does not exist")
            print("Running fit of model '{}'".format(model_name))
            print("parameters:", self.parameters[model_name])
            os.system(command)
            self.save_results(model_name, fitdir)
        os.chdir(parent_dir)

    def save_results(self, model_name, fitdir):
        wp = model_name.split('wp')[0][-1]
        wpt = model_name.split('Pt-')[1]
        combineFile = uproot.open(os.path.join(fitdir, "higgsCombine_{}.FitDiagnostics.mH120.root".format(model_name)))

        combineTree = combineFile['limit']
        combineBranches = combineTree.arrays()
        results = combineBranches['limit']

        if len(results) < 4:
            print("FIT FAILED : ", model_name)

        combineCont, low, high, temp = results
        combineErrUp = high - combineCont
        combineErrDown = combineCont - low
        d = {}

        POI = self.signal_name[model_name]
        columns = ['year', 'selection', 'wp', 'pt',
            POI, '{}ErrUp'.format(POI), '{}ErrDown'.format(POI),
            'SF({})'.format(POI)]
        columns_for_latex = ['year', 'pt', 'SF({})'.format(POI)]
        d = {'year' : [self.year], 'selection' : [model_name], 'tagger' : [self.tagger],
            'wp' : [wp], 'pt' : [wpt],
            POI : [combineCont], '{}ErrUp'.format(POI) : [combineErrUp], '{}ErrDown'.format(POI) : [combineErrDown],
            'SF({})'.format(POI) : ['{}$^{{+{}}}_{{-{}}}$'.format(combineCont, combineErrUp, combineErrDown)]}

        value, lo, hi = (self.parameters[model_name][POI]['value'], self.parameters[model_name][POI]['lo'], self.parameters[model_name][POI]['hi'])
        f = open(os.path.join(fitdir, "fitResults_{}Pt.txt".format(model_name)), 'w')
        lineIntro = 'Best fit '
        firstline = '{}{}: {}  -{}/+{}  (68%  CL)  range = [{}, {}]\n'.format(lineIntro, POI, combineCont, combineErrDown, combineErrUp, lo, hi)
        f.write(firstline)
        fitResults = ROOT.TFile.Open(os.path.join(fitdir, "fitDiagnostics_{}.root".format(model_name)))
        fit_s = fitResults.Get('fit_s')

        for flavor in self.flavors:
            if (flavor == POI): continue
            par_result = fit_s.floatParsFinal().find(flavor)
            columns.append(flavor)
            columns.append('{}Err'.format(flavor))
            columns.append('SF({})'.format(flavor))
            columns_for_latex.append('SF({})'.format(flavor))
            if par_result == None:
                d.update({flavor : -999, '{}Err'.format(flavor) : -999, 'SF({})'.format(flavor) : r'{}$\pm${}'.format(-999, -999)})
                continue
            parVal = par_result.getVal()
            parErr = par_result.getAsymErrorHi()
            value, lo, hi = (self.parameters[model_name][flavor]['value'], self.parameters[model_name][flavor]['lo'], self.parameters[model_name][flavor]['hi'])
            gapSpace = ''.join( (len(lineIntro) + len(POI) - len(flavor) )*[' '])
            lineResult = '{}{}: {}  -+{}'.format(gapSpace, flavor, parVal, parErr)
            gapSpace2 = ''.join( (firstline.find('(') - len(lineResult) )*[' '])
            line = lineResult + gapSpace2 + '(68%  CL)  range = [{}, {}]\n'.format(lo, hi)
            f.write(line)
            #columns.append(flavor)
            #columns.append('{}Err'.format(flavor))
            #columns.append('SF({})'.format(flavor))
            #columns_for_latex.append('SF({})'.format(flavor))
            d.update({flavor : parVal, '{}Err'.format(flavor) : parErr, 'SF({})'.format(flavor) : r'{}$\pm${}'.format(parVal, parErr)})
        f.close()
        df = pd.DataFrame(data=d)
        if self.first[POI]:
            df.to_csv(self.fitResults[POI], columns=columns, mode='w', header=True)
            self.first[POI] = False
        else:
            df.to_csv(self.fitResults[POI], columns=columns, mode='a', header=False)
