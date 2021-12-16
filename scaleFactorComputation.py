from __future__ import print_function, division
import sys
import os
import rhalphalib as rl
import numpy as np
import pandas as pd
import scipy.stats
import pickle
import uproot
import ROOT
from parameters import histogram_settings, fit_parameters, sample_names

nPtBins = 3

def exec_me(command, dryRun=False, folder=False):
    
    print(command)
    if not dryRun:
        if folder: os.chdir(folder)
        os.system(command)

def rebin(h_vals, h_sumw2, bins, lo, hi):

    mask = (bins >= lo) & (bins <= hi)
    h_vals = h_vals[mask[:-1]]
    h_sumw2 = h_sumw2[mask[:-1]]
    bins = bins[mask]

    return h_vals, h_sumw2, bins

def get_templ(f, sample, obs, lo, hi, syst=None, sumw2=True):
    
    hist_name = sample
    if syst is not None:
        hist_name += "_" + syst
    h_vals = f[hist_name][0]
    h_sumw2 = f[hist_name][1]
    bins = obs.binning
    mergeTail = False
    print("before:", bins)
    # HARDCODED
    if ('logsv1mass' in obs.name) & (len(h_vals) == 80) & (mergeTail == True):
        h_vals  = h_vals[32:-8]
        h_sumw2 = h_sumw2[32:-8]
        bins = bins[32:-8]
        # rebinning
        val_N     = np.sum(h_vals[-7:])
        val_N_1   = np.sum(h_vals[-14:-7])
        sumw2_N   = np.sum(h_sumw2[-7:])
        sumw2_N_1 = np.sum(h_sumw2[-14:-7])
        bin_N   = 3.2
        bin_N_1 = 2.5
        h_vals  = h_vals[:-14]
        h_sumw2 = h_sumw2[:-14]
        bins = bins[:-14]
        h_vals  = np.concatenate((h_vals, [val_N_1, val_N]))
        h_sumw2 = np.concatenate((h_sumw2, [sumw2_N_1, sumw2_N]))
        bins = np.concatenate((bins, [2.5, 3.2]))
    #elif ('logsv1mass' in obs.name) & (len(h_vals) == 40):
    elif ('logsv1mass' in obs.name):
        """
        h_vals  = h_vals[16:-4]
        h_sumw2 = h_sumw2[16:-4]
        bins = bins[16:-4]
        """
        #h_vals  = h_vals[16:-10]
        #h_sumw2 = h_sumw2[16:-10]
        #bins = bins[16:-10]

        h_vals, h_sumw2, bins = rebin(h_vals, h_sumw2, bins, lo, hi)
    #elif ('logsv1mass' in obs.name) & (len(h_vals) == 20):
    #    h_vals  = h_vals[8:-2]
    #    h_sumw2 = h_sumw2[8:-2]
    #    bins = bins[8:-2]

    print("after:", bins)

    if not sumw2:
        return (h_vals, bins, obs.name)
    else:
        return (h_vals, bins, obs.name, h_sumw2)


def test_sfmodel(tmpdir, var, lo, hi, inputFile, year, campaign, sel, wp, wpt='', pt=500, pars_key=None, epsilon=0.0001, passonly=False, fittype='single', scale=1, smear=0.1):
    lumi = rl.NuisanceParameter('CMS_lumi', 'lnN')
    jecs = rl.NuisanceParameter('CMS_jecs', 'lnN')
    pu = rl.NuisanceParameter('CMS_pu', 'lnN')

    pt_bins = {
        #'L' : [0, 350],
        'M' : (350, pt),
        'H' : (pt, 'Inf'),
    }
    name_map = {'n_or_arr' : 'num', 'lo' : 'start', 'hi' : 'stop'}
    arguments = dict((name_map[name], val) for name, val in histogram_settings['variables'][var]['binning'].iteritems())
    arguments['num'] += 1
    bins = np.linspace(**arguments)
    #if var == 'fatjet_jetproba':
    #    bins = np.linspace(0, 2.5, 26)
        #jetproba = rl.Observable('jetproba', jetprobabins)
    #if 'sv_logsv1mass' in var:
        #bins = np.linspace(-4, 4, 81)
    #    bins = np.linspace(-4, 4, 41)
        #bins = np.linspace(-4, 4, 21)
        #binwidth = 0.1
        #logsv1massbins = np.arange(-0.8, 3.2 + binwidth, binwidth)
    #    binwidth = float(bins[1] - bins[0])

    # Indeps
    if not pars_key:
        pars = fit_parameters['{}pt{}'.format(campaign, pt)]
    else:
        pars = fit_parameters[pars_key]
    if wpt in pars[year][sel[-3:]].keys():
        pars = pars[year][sel[-3:]][wpt]
    else:
        pars = pars[year][sel[-3:]]
    (indep_c_cc, indep_b_bb, indep_l) = (rl.IndependentParameter(sName, **pars[sName]) for sName in sample_names)
    print('cc', indep_c_cc.name)
    print('bb', indep_b_bb.name)
    print('l', indep_l.name)
    
    observable = rl.Observable(var.split('_')[-1], bins)
    model = rl.Model("sfModel")

    regions = ['pass', 'fail']
    if passonly:
        regions = ['pass']
    fout = np.load(inputFile, allow_pickle=True)
    if sel.endswith('DDB'):
        signalName = 'b_bb'
    else:
        signalName = 'c_cc'
    print("signalName", signalName)
    Nevts = 0
    Nl = 0
    for region in regions:
        ch = rl.Channel("sf{}".format(region))
        for sName in sample_names:
            if wpt == 'Inclusive':
                template = get_templ(fout, '{}_{}{}{}wp_QCD_{}'.format(var, sel, region, wp, sName), observable, lo, hi)
            else:
                (pt_low, pt_high) = pt_bins[wpt]
                template = get_templ(fout, '{}_{}{}{}wpPt-{}to{}_QCD_{}'.format(var, sel, region, wp, pt_low, pt_high, sName), observable, lo, hi)
            #print('template', template)
            if region == 'pass':
                Nevts += np.sum(template[0])
                if sName == 'l':
                    Nl += np.sum(template[0])

            #isSignal = True if sName == ('bb' if sel.endswith('DDB') else 'cc') else False

            isSignal = True if sName == signalName else False
            sType = rl.Sample.SIGNAL if isSignal else rl.Sample.BACKGROUND
            sample = rl.TemplateSample("{}_{}".format(ch.name, sName), sType, template)
            #print('sample',sample)
            
            sample.setParamEffect(lumi, 1.023)
            sample.setParamEffect(jecs, 1.02)
            sample.setParamEffect(pu, 1.05)
            
            if isSignal:
                sample.autoMCStats(epsilon=args.epsilon)
            #    fracX = rl.NuisanceParameter('frac_'+sName, 'shape')
            #    sample.setParamEffect(fracX, 1.2*template[0])
            else:
                sample.autoMCStats(lnN=True)
            ch.addSample(sample)

        if wpt == 'Inclusive':
            #data_obs = get_templ(fout, 'fatjet_jetproba_{}{}{}wp_BtagMu'.format(sel, region, wp), jetproba, lo, hi)[:-1]
            data_obs = get_templ(fout, '{}_{}{}{}wp_BtagMu'.format(var, sel, region, wp), observable, lo, hi)[:-1]
        else:
            data_obs = get_templ(fout, '{}_{}{}{}wpPt-{}to{}_BtagMu'.format(var, sel, region, wp, pt_low, pt_high), observable, lo, hi)[:-1]
        ch.setObservation(data_obs)

        model.addChannel(ch)

    fractionL = float(Nl)/float(Nevts)
    print("fractionL = ", fractionL)
    if fractionL < 4e-3:
        args.freezeL = True
        print("The parameter 'l' will be frozen.")

    if not passonly:
        for sample, SF in zip(sample_names, [indep_c_cc, indep_b_bb, indep_l]):
            if sample != SF.name:
                sys.exit("Sample and scale factor names are not matching.")
            pass_sample = model['sfpass'][sample]
            fail_sample = model['sffail'][sample]
            pass_fail = pass_sample.getExpectation(nominal=True).sum() / fail_sample.getExpectation(nominal=True).sum()
            pass_sample.setParamEffect(SF, 1.0 * SF)
            fail_sample.setParamEffect(SF, (1 - SF) * pass_fail + 1)
    else:
        for sample, SF in zip(sample_names, [indep_c_cc, indep_b_bb, indep_l]):
            if sample != SF.name:
                sys.exit("Sample and scale factor names are not matching.")
            pass_sample = model['sfpass'][sample]
            pass_sample.setParamEffect(SF, 1.0 * SF)

    model.renderCombine(tmpdir)
    with open(tmpdir+'/build.sh', 'a') as ifile:
        #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes  --rMin 0.5 --rMax 1.5'.format(wpt))
        if args.freezeL:
            #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --redefineSignalPOIs={} --setParameters r=1,l=1 --freezeParameters r,l'.format(wp, wpt, signalName))
            ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 2 --robustFit=1 --saveShapes --saveWithUncertainties --saveOverallShapes --redefineSignalPOIs={} --setParameters r=1,l=1 --freezeParameters r,l --rMin 1 --rMax 1'.format(wp, wpt, signalName))
        else:
            #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r'.format(wp, wpt, signalName))
            ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 2 --robustFit=1 --saveShapes --saveWithUncertainties --saveOverallShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r --rMin 1 --rMax 1'.format(wp, wpt, signalName))
        #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --robustHesse 1 --saveShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r'.format(wpt, signalName))

    exec_me( 'bash build.sh', folder=tmpdir )

def save_results(output_dir, year, campaign, sel, wp, wpt, pt, pars_key=None, createcsv=False, createtex=False):

    combineFile = uproot.open(output_dir + "higgsCombine{}wp{}Pt.FitDiagnostics.mH120.root".format(wp, wpt))
    combineTree = combineFile['limit']
    combineBranches = combineTree.arrays()
    results = combineBranches['limit']

    combineCont, low, high, temp = results
    combineErrUp = high - combineCont
    combineErrDown = combineCont - low
    d = {}

    if 'DDB' in sel:
        POI = 'b_bb'
    elif 'DDC' in sel:
        POI = 'c_cc'
    columns = ['year', 'campaign', 'selection', 'wp', 'pt',
                POI, '{}ErrUp'.format(POI), '{}ErrDown'.format(POI),
                'SF({})'.format(POI)]
    columns_for_latex = ['year', 'pt', 'SF({})'.format(POI)]
    d = {'year' : [year], 'campaign' : [campaign], 'selection' : [sel], 'wp' : [wp], 'pt' : [wpt],
        POI : [combineCont], '{}ErrUp'.format(POI) : [combineErrUp], '{}ErrDown'.format(POI) : [combineErrDown],
        'SF({})'.format(POI) : ['{}$^{{+{}}}_{{-{}}}$'.format(combineCont, combineErrUp, combineErrDown)]}

    if not pars_key:
        pars = fit_parameters['{}pt{}'.format(campaign, pt)]
    else:
        pars = fit_parameters[pars_key]
    if wpt in pars[year][sel[-3:]].keys():
        pars = pars[year][sel[-3:]][wpt]
    else:
        pars = pars[year][sel[-3:]]
    value, lo, hi = (pars[POI]['value'], pars[POI]['lo'], pars[POI]['hi'])
    f = open(output_dir + "fitResults{}wp{}Pt.txt".format(wp, wpt), 'w')
    lineIntro = 'Best fit '
    firstline = '{}{}: {}  -{}/+{}  (68%  CL)  range = [{}, {}]\n'.format(lineIntro, POI, combineCont, combineErrDown, combineErrUp, lo, hi)
    f.write(firstline)
    fitResults = ROOT.TFile.Open(output_dir + "fitDiagnostics{}wp{}Pt.root".format(wp, wpt))
    fit_s = fitResults.Get('fit_s')
    for sName in sample_names:
        if (sName == POI): continue
        par_result = fit_s.floatParsFinal().find(sName)
        if par_result == None: continue
        parVal = par_result.getVal()
        parErr = par_result.getAsymErrorHi()
        value, lo, hi = (pars[sName]['value'], pars[sName]['lo'], pars[sName]['hi'])
        gapSpace = ''.join( (len(lineIntro) + len(POI) - len(sName) )*[' '])
        lineResult = '{}{}: {}  -+{}'.format(gapSpace, sName, parVal, parErr)
        gapSpace2 = ''.join( (firstline.find('(') - len(lineResult) )*[' '])
        line = lineResult + gapSpace2 + '(68%  CL)  range = [{}, {}]\n'.format(lo, hi)
        f.write(line)
        columns.append(sName)
        columns.append('{}Err'.format(sName))
        columns.append('SF({})'.format(sName))
        columns_for_latex.append('SF({})'.format(sName))
        d.update({sName : parVal, '{}Err'.format(sName) : parErr, 'SF({})'.format(sName) : r'{}$\pm${}'.format(parVal, parErr)})
    f.close()
    df = pd.DataFrame(data=d)
    csv_file = output_dir + "fitResults{}wp.csv".format(wp)
    if createcsv:
        df.to_csv(csv_file, columns=columns, mode='w', header=True)
    else:
        df.to_csv(csv_file, columns=columns, mode='a', header=False)
    if createtex:
        df_csv = pd.read_csv(csv_file)
        f = open(csv_file.replace('.csv', '.tex'), 'w')
        with pd.option_context("max_colwidth", 1000):
            f.write(df_csv.to_latex(columns=columns_for_latex, header=True, index=False, escape=False, float_format="%.4f"))
        f.close()

    return combineCont, combineErrDown, combineErrUp

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--outputDir', type=str, default=None, help='Output directory')
    parser.add_argument('--campaign', type=str, choices={'EOY', 'UL'}, help='Dataset campaign.', required=True)
    parser.add_argument('--year', type=str, choices=['2016', '2017', '2018'], help='Year of data/MC samples', required=True)
    parser.add_argument('--pt', type=int, default=500, help='Pt cut.', required=True)
    parser.add_argument('--var', type=str, default='sv_logsv1mass', help='Variable used in the template fit.')
    parser.add_argument('--lo', type=float, default=-1.2, help='Variable used in the template fit.')
    parser.add_argument('--hi', type=float, default=2.0, help='Variable used in the template fit.')
    parser.add_argument('--selection', type=str, default='msd100tau06DDB', help='Selection to compute SF.', required=True)
    parser.add_argument('--wp', type=str, default='M', help='Working point', required=True)
    parser.add_argument('--wpt', type=str, choices={'Inclusive', 'M', 'H'}, default='', help='Pt bin', required=True)
    parser.add_argument("--freezeL", action='store_true', default=False, help="Freeze the light component in all fits")
    parser.add_argument("--fit", type=str, choices={'single', 'double'}, default='double',
                        help="Fit type")  ##not used
    parser.add_argument("--scale", type=float, default='1',
                        help="Datacard magnitude for scale shift.")  ##not used yet
    parser.add_argument("--smear", type=float, default='0.1',
                        help="Datacard magnitude for smear shift.")  ##not used yet

    #parser.add_argument("--tp", "--template-pass", dest='tp', type=str,
    #                    default='histograms/hists_fattag_pileupJEC_2017_WPcuts_v01.pkl',
    #                    help="Pass(Pass/Pass) templates")  ##not used

    parser.add_argument("--tpf", "--template-passfail", dest='tpf', type=str,
                        default='histograms/hists_fattag_pileupJEC_2017_WPcuts_v01.pkl',
                        help="Pass/Fail templates, only for `fit=double`")
    parser.add_argument('--createcsv', action='store_true', default=False, help='Create new csv file')
    parser.add_argument('--createtex', action='store_true', default=False, help='Create tex file with table')
    parser.add_argument("--parameters", type=str, default=None, help='Run with custom parameters')
    parser.add_argument("--epsilon", type=float, default=0.0001, help='Epsilon parameter for MC shape uncertainties')
    parser.add_argument('--passonly', action='store_true', default=False, help='Fit pass region only')

    #parser.add_argument("--tf", "--template-fail", dest='tf', type=str,
    #                    default='histograms/hists_fattag_pileupJEC_2017_WPcuts_v01.pkl',
    #                    help="Fail templates")  ##not used

    args = parser.parse_args()

    print("Running with options:")
    print("    ", args)

    if not args.selection[-3:] in ['DDB', 'DDC']:
        raise NotImplementedError
    if args.parameters:
        if not args.parameters in fit_parameters.keys():
            raise NotImplementedError
    output_dir = args.outputDir if args.outputDir else os.getcwd()+"/fitdir/"+args.year+'/'+args.selection+'/'
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    test_sfmodel(output_dir, args.var, args.lo, args.hi, args.tpf, args.year, args.campaign, args.selection, args.wp, args.wpt, args.pt, args.parameters, args.epsilon, args.passonly, args.freezeL)
    save_results(output_dir, args.year, args.campaign, args.selection, args.wp, args.wpt, args.pt, args.parameters, args.createcsv, args.createtex)
