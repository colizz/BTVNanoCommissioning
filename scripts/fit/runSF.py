import os
import sys
import argparse
import json

sys.path.append('/home/pku/licq/calib/mutag/BTVNanoCommissioning')

from utils.Fit import Fit
from parameters import categories

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('-i', '--input', default=None, help='Input templates', required=True)
parser.add_argument('-o', '--output', default="/work/mmarcheg/BTVNanoCommissioning/output/fit", help='Output folder', required=True)
parser.add_argument('--only', type=str, default=None, help='Filter categories by key', required=False)
parser.add_argument('--scheme', type=str, choices=['3f', '5f'],  help='3-flavor scheme', required=True)
parser.add_argument('--binwidth', type=float, default=0.4, choices=[0.1, 0.2, 0.4],  help='Specify the binwidth of the logsumcorrmass distribution', required=False)
parser.add_argument('--year', type=str, choices=["2016_PreVFP", "2016_PostVFP", "2017", "2018"], help='Specify the data-taking year', required=True)
parser.add_argument('-m', '--mode', type=str, default="FitDiagnostics", choices=["FitDiagnostics", "MultiDimFit", "all"], help='Specify combine mode', required=False)
args = parser.parse_args()

if args.only:
    args.only = args.only.split('*')
    categories = list(filter(lambda cat : all(f in cat for f in args.only), categories))

# if os.path.exists(args.output):
#     sys.exit("The output folder {} is already existing. Please choose a different folder name.".format(args.output))

failed_fits = []
for var in ['events_logsumcorrmass_1']:
    fit = Fit(args.input, args.output, categories, var, args.year, xlim=(-1.2, 5.2), binwidth=args.binwidth, scheme=args.scheme, rwgt_fitvar=False)
    if args.mode == "all":
        fit.run_fits("FitDiagnostics")
        fit.run_fits("MultiDimFit")
    else:
        fit.run_fits(args.mode)
