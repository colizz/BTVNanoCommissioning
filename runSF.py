import os
import sys
from parameters import fit_parameters

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--outputDir', type=str, default=None, help='Output directory', required=True)
    parser.add_argument('--campaign', type=str, choices={'EOY', 'UL'}, help='Dataset campaign.', required=True)
    parser.add_argument('--year', type=str, choices=['2016', '2017', '2018'], help='Year of data/MC samples', required=True)
    parser.add_argument('--pt', type=int, default=500, help='Pt cut.', required=True)
    parser.add_argument("--freezeL", action='store_true', default=False, help="Freeze the light component in all fits")
    parser.add_argument('--var', type=str, choices=['sv_logsv1mass', 'sv_logsv1mass_maxdxySig'], default='sv_logsv1mass', help='Variable used in the template fit.')
    parser.add_argument("--tpf", "--template-passfail", dest='tpf', type=str,
                        default='histograms/hists_fattag_pileupJEC_2017_WPcuts_v01.pkl',
                        help="Pass/Fail templates, only for `fit=double`", required=True)
    parser.add_argument("--parameters", type=str, default=None, help='Run with custom parameters')
    parser.add_argument("--epsilon", type=float, default=0.0001, help='Epsilon parameter for MC shape uncertainties')
    parser.add_argument('--impacts', action='store_true', default=False, help='Compute parameters impact')
    parser.add_argument('--passonly', action='store_true', default=False, help='Fit pass region only')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Show combine log to stdout')
    args = parser.parse_args()

    if args.parameters:
        print("{} : {}".format(args.parameters, fit_parameters[args.parameters]))

    #for year in ['2016', '2017', '2018']:
    for tagger in ['DDC', 'DDB']:
        for wp in [ 'M' ]:
            for wpt in ['Inclusive', 'M', 'H']:
                subDir = "{}/msd100tau06{}{}wp".format(args.outputDir, tagger, wp)
                if not os.path.exists(subDir):
                    os.makedirs(subDir)
                logFile = "{}/sf{}{}{}wp{}Pt.log".format(subDir, args.year, tagger, wp, wpt)
                
                submissionCommand = ( "python scaleFactorComputation.py --campaign {} --year {} --tpf {} --outputDir {}".format(args.campaign, args.year, args.tpf, subDir) +
                                      " --selection msd100tau06{} --wp {} --wpt {} --pt {} --var {}".format(tagger, wp, wpt, args.pt, args.var) +
                                      " | tee {}".format(logFile) )
                if args.parameters:
                    submissionCommand = submissionCommand.replace(' | tee', ' --parameters {} | tee'.format(args.parameters))
                if args.epsilon:
                    submissionCommand = submissionCommand.replace(' | tee', ' --epsilon {} | tee'.format(args.epsilon))
                if args.freezeL:
                    submissionCommand = submissionCommand.replace(' | tee', ' --freezeL | tee')
                if args.passonly:
                    submissionCommand = submissionCommand.replace(' | tee', ' --passonly | tee')
                if wpt == 'Inclusive':
                    submissionCommand = submissionCommand.replace(' | tee', ' --createcsv | tee')
                if wpt == 'H':
                    submissionCommand = submissionCommand.replace(' | tee', ' --createtex | tee')
                if not args.verbose:
                    submissionCommand = submissionCommand.split('|')[0] + " &> {}".format(logFile)

                line = ''.join(100*['-'])
                print(line)
                print( submissionCommand + '\n' )
                ret = os.system( submissionCommand )
                if ret != 0:
                    print("Fit failed.")
                    continue
                print("{} {} {} wp {} Pt".format(args.year, tagger, wp, wpt))
                os.system('cat {}/msd100tau06{}{}wp/fitResults{}wp{}Pt.txt'.format(args.outputDir, tagger, wp, wp, wpt))
                print("")

                if args.impacts:
                    with open(subDir + "/build.sh") as file:
                        combineCommand = file.readlines()[-1]
                    p = []
                    for par in combineCommand.split('--'):
                        if ("redefineSignalPOIs" in par) | ("setParameters" in par) | ("freezeParameters" in par) | ("rMin" in par) | ("rMax" in par):
                            p.append('--' + par)
                    extraPars = ' '.join(p)
                    w = subDir + "/model_combined.root"
                    impactsFile = "impacts{}wp{}Pt.json".format(wp, wpt)
                    out = subDir + '/' + impactsFile
                    cwd = os.getcwd()
                    commands = []
                    #os.chdir(subDir)
                    commands.append("combineTool.py -M Impacts -d {} -m 125 --doInitialFit --robustFit 1 {}".format(w, extraPars))
                    commands.append("combineTool.py -M Impacts -d {} -m 125 --doFits --robustFit 1 --parallel 10 {}".format(w, extraPars))
                    commands.append("combineTool.py -M Impacts -d {} -m 125 -o {} {}".format(w, out, extraPars))
                    commands.append("plotImpacts.py -i {} -o {}".format(out, subDir.strip(cwd) + '/' + impactsFile.replace('.json', '')))
                    #commands.append("plotImpacts.py -i {} -o impacts".format(out))
                    #os.chdir(cwd)
                    for com in commands:
                        com = com + " | tee {}".format(logFile)
                        if not args.verbose:
                            com = com.split('|')[0] + " &> {}".format(logFile)
                        print( com + '\n' )
                        ret = os.system( com )


    #if args.plots:
    #    for tagger in ['DDC', 'DDB']:
    #        for wp in [ 'M' ]:
    #            for wpt in ['Inclusive', 'M', 'H']:
    #                subDir = "{}/msd100tau06{}{}wp".format(args.outputDir, tagger, wp)
    #                print("Saving pre/post-fit plots in {}".format(subDir))
    #                logFile = "{}/plots{}{}{}wp{}Pt.log".format(subDir, args.year, tagger, wp, wpt)
    #                submissionCommand = ("python make_SFplots.py -i {}/fitDiagnostics{}wp{}Pt.root -o {}".format(subDir, wp, wpt, subDir) +
    #                                     " --year {} --selection msd100tau06{}".format(args.year, tagger) +
    #                                     " | tee {}".format(logFile) )
    #                if not args.verbose:
    #                    submissionCommand = submissionCommand.split('|')[0] + " > {}".format(logFile)
                    
