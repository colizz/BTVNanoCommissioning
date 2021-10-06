from __future__ import print_function, division
import sys
import os
import rhalphalib as rl
import numpy as np
import scipy.stats
import pickle
import uproot

def exec_me(command, dryRun=False, folder=False):
    print(command)
    if not dryRun:
        if folder: os.chdir(folder)
        os.system(command)


def get_templ(f, sample, obs, syst=None, sumw2=True):
    hist_name = sample
    if syst is not None:
        hist_name += "_" + syst
    h_vals = f[hist_name][0]
    h_sumw2 = f[hist_name][1]
    binning = obs.binning
    # HARDCODED
    if (obs.name == 'logsv1mass') & (len(h_vals) == 80):
        h_vals  = h_vals[32:-8]
        h_sumw2 = h_sumw2[32:-8]
        binning = binning[32:-8]
        # rebinning
        val_N     = np.sum(h_vals[-7:])
        val_N_1   = np.sum(h_vals[-14:-7])
        sumw2_N   = np.sum(h_sumw2[-7:])
        sumw2_N_1 = np.sum(h_sumw2[-14:-7])
        bin_N   = 3.2
        bin_N_1 = 2.5
        h_vals  = h_vals[:-14]
        h_sumw2 = h_sumw2[:-14]
        binning = binning[:-14]
        h_vals  = np.concatenate((h_vals, [val_N_1, val_N]))
        h_sumw2 = np.concatenate((h_sumw2, [sumw2_N_1, sumw2_N]))
        binning = np.concatenate((binning, [2.5, 3.2]))
    elif (obs.name == 'logsv1mass') & (len(h_vals) == 40):
        """
        h_vals  = h_vals[16:-4]
        h_sumw2 = h_sumw2[16:-4]
        binning = binning[16:-4]
        """
        h_vals  = h_vals[16:-10]
        h_sumw2 = h_sumw2[16:-10]
        binning = binning[16:-10]
    elif (obs.name == 'logsv1mass') & (len(h_vals) == 20):
        h_vals  = h_vals[8:-2]
        h_sumw2 = h_sumw2[8:-2]
        binning = binning[8:-2]

    if not sumw2:
        return (h_vals, binning, obs.name)
    else:
        return (h_vals, binning, obs.name, h_sumw2)


def test_sfmodel(tmpdir, var, inputFile, sel, wp, wpt='', pt=500, fittype='single', scale=1, smear=0.1):
    lumi = rl.NuisanceParameter('CMS_lumi', 'lnN')
    jecs = rl.NuisanceParameter('CMS_jecs', 'lnN')
    pu = rl.NuisanceParameter('CMS_pu', 'lnN')

    pt_bins = {
        #'L' : [0, 350],
        'M' : (350, pt),
        'H' : (pt, 'Inf'),
    }

    if var == 'fatjet_jetproba':
        bins = np.linspace(0, 2.5, 26)
        #jetproba = rl.Observable('jetproba', jetprobabins)
    if var == 'sv_logsv1mass':
        bins = np.linspace(-4, 4, 81)
        #bins = np.linspace(-4, 4, 41)
        #bins = np.linspace(-4, 4, 21)
        #binwidth = 0.1
        #logsv1massbins = np.arange(-0.8, 3.2 + binwidth, binwidth)
        binwidth = float(bins[1] - bins[0])

    # Indeps
    if abs(binwidth - 0.1) < 0.01:
        if 'DDB' in sel:
            indep_l = rl.IndependentParameter('l', 1., 0, 2)
            indep_b_bb = rl.IndependentParameter('b_bb', 1., -20, 20)
            if '2018' in inputFile:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., -20, 20)
            else:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., 0, 2)
        elif 'DDC' in sel:
            indep_l = rl.IndependentParameter('l', 1., 0, 2)
            if '2018' in inputFile:
                indep_b_bb = rl.IndependentParameter('b_bb', 1., -20, 20)
            #elif '2017' in inputFile:
            else:
                indep_b_bb = rl.IndependentParameter('b_bb', 1., 0, 2)
                #indep_b_bb = rl.IndependentParameter('b_bb', 1., -20, 20)
            #if '2016' in inputFile:
            #    indep_l = rl.IndependentParameter('l', 1., -20, 20)
            if '2016' in inputFile:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., 0, 20)
            else:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., -20, 20)
            #indep_c_cc = rl.IndependentParameter('c_cc', 1., -20, 20)
    elif abs(binwidth - 0.2) < 0.01:
        if 'DDB' in sel:
            indep_l = rl.IndependentParameter('l', 1., -20, 20)
            indep_b_bb = rl.IndependentParameter('b_bb', 1., 0, 20)
            if '2017' in inputFile:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., 0, 20)
            else:
                indep_c_cc = rl.IndependentParameter('c_cc', 1., -20, 20)
        elif 'DDC' in sel:
            if '2016' in inputFile:
                indep_l = rl.IndependentParameter('l', 1., -20, 20)
                indep_b_bb = rl.IndependentParameter('b_bb', 1., -20, 20)
            else:
                indep_b_bb = rl.IndependentParameter('b_bb', 1., -20, 20)
                indep_l = rl.IndependentParameter('l', 1., -20, 20)
            indep_c_cc = rl.IndependentParameter('c_cc', 1., 0, 20)
    
    observable = rl.Observable(var.split('_')[-1], bins)
    model = rl.Model("sfModel")

    regions = ['pass', 'fail']
    fout = np.load(inputFile, allow_pickle=True)
    #tagger = 'DDB' if 'DDB' in sel else 'DDC'
    #sample_names = ['bb', 'cc', 'b', 'c', 'l']
    #if tagger == 'DDC':
    sample_names = ['b_bb', 'c_cc', 'l']
    if sel.endswith('DDB'):
        signalName = 'b_bb'
    else:
        signalName = 'c_cc'
    Nevts = 0
    Nl = 0
    for region in regions:
        ch = rl.Channel("sf{}".format(region))
        for sName in sample_names:
            if wpt == 'Inclusive':
                template = get_templ(fout, '{}_{}{}{}wp_QCD_{}'.format(var, sel, region, wp, sName), observable)
            else:
                (pt_low, pt_high) = pt_bins[wpt]
                template = get_templ(fout, '{}_{}{}{}wpPt-{}to{}_QCD_{}'.format(var, sel, region, wp, pt_low, pt_high, sName), observable)
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
            sample.autoMCStats(lnN=True)
            #sample.autoMCStats(epsilon=1e-4)
            ch.addSample(sample)

        if wpt == 'Inclusive':
            #data_obs = get_templ(fout, 'fatjet_jetproba_{}{}{}wp_BtagMu'.format(sel, region, wp), jetproba)[:-1]
            data_obs = get_templ(fout, '{}_{}{}{}wp_BtagMu'.format(var, sel, region, wp), observable)[:-1]
        else:
            data_obs = get_templ(fout, '{}_{}{}{}wpPt-{}to{}_BtagMu'.format(var, sel, region, wp, pt_low, pt_high), observable)[:-1]
        ch.setObservation(data_obs)

        model.addChannel(ch)

    fractionL = float(Nl)/float(Nevts)
    freezeL = False
    print("fractionL = ", fractionL)
    if fractionL < 1.5e-3:
        freezeL = True
        print("The parameter 'l' will be frozen.")

    #parameters = [indep_bb, indep_cc, indep_b, indep_c, indep_l]
    #if tagger == 'DDC':
    parameters = [indep_b_bb, indep_c_cc, indep_l]
    for sample, SF in zip(sample_names, parameters):
        pass_sample = model['sfpass'][sample]
        fail_sample = model['sffail'][sample]
        pass_fail = pass_sample.getExpectation(nominal=True).sum() / fail_sample.getExpectation(nominal=True).sum()
        pass_sample.setParamEffect(SF, 1.0 * SF)
        fail_sample.setParamEffect(SF, (1 - SF) * pass_fail + 1)

    model.renderCombine(tmpdir)
    with open(tmpdir+'/build.sh', 'a') as ifile:
        #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes  --rMin 0.5 --rMax 1.5'.format(wpt))
        if freezeL:
            ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --redefineSignalPOIs={} --setParameters r=1,l=1 --freezeParameters r,l'.format(wp, wpt, signalName))
        else:
            ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}wp{}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r'.format(wp, wpt, signalName))
        #ifile.write('\ncombine -M FitDiagnostics --expectSignal 1 -d model_combined.root --name {}Pt --cminDefaultMinimizerStrategy 0 --robustFit=1 --robustHesse 1 --saveShapes --redefineSignalPOIs={} --setParameters r=1 --freezeParameters r'.format(wpt, signalName))

    exec_me( 'bash build.sh', folder=tmpdir )

def save_results(output_dir, sel, wp, wpt):

    combineFile = uproot.open(output_dir + "higgsCombine{}wp{}Pt.FitDiagnostics.mH120.root".format(wp, wpt))
    combineTree = combineFile['limit']
    combineBranches = combineTree.arrays()
    results = combineBranches['limit']

    combineCont, low, high, temp = results
    combineErrUp = high - combineCont
    combineErrDown = combineCont - low

    if 'DDB' in sel:
        POI = 'b_bb'
    elif 'DDC' in sel:
        POI = 'c_cc'
    f = open(output_dir + "fitResults{}wp{}Pt.txt".format(wp, wpt), 'w')
    f.write('Best fit {}: {}  -{}/+{}  (68%  CL)\n'.format(POI, combineCont, combineErrDown, combineErrUp))
    f.close()

    return combineCont, combineErrDown, combineErrUp

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--outputDir', type=str, default=None, help='Output directory')
    parser.add_argument('--year', type=str, choices=['2016', '2017', '2018'], help='Year of data/MC samples')
    parser.add_argument('--pt', type=int, default=500, help='Pt cut.')
    parser.add_argument('--var', type=str, default='sv_logsv1mass', help='Variable used in the template fit.')
    parser.add_argument('--selection', type=str, default='msd100tau06DDB', help='Selection to compute SF.')
    parser.add_argument('--wp', type=str, default='M', help='Working point')
    parser.add_argument('--wpt', type=str, choices={'Inclusive', 'M', 'H'}, default='', help='Pt bin')
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

    #parser.add_argument("--tf", "--template-fail", dest='tf', type=str,
    #                    default='histograms/hists_fattag_pileupJEC_2017_WPcuts_v01.pkl',
    #                    help="Fail templates")  ##not used

    args = parser.parse_args()

    print("Running with options:")
    print("    ", args)

    output_dir = args.outputDir if args.outputDir else os.getcwd()+"/fitdir/"+args.year+'/'+args.selection+'/'
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    test_sfmodel(output_dir, args.var, args.tpf, args.selection, args.wp, args.wpt, args.pt)
    save_results(output_dir, args.selection, args.wp, args.wpt)
