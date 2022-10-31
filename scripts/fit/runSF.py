import os
import sys
import argparse
import json

#print(sys.path)
sys.path.append('/work/mmarcheg/BTVNanoCommissioning')
sys.path.append('/work/mmarcheg/BTVNanoCommissioning/PocketCoffea')

from utils.Fit import Fit

#from PocketCoffea.utils.Configurator import Configurator

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('--cfg', default=os.getcwd() + "/config/test.json", help='Config file with parameters specific to the current run', required=False)
parser.add_argument('-v', '--version', type=str, default=None, help='Version of output (e.g. `v01`, `v02`, etc.)', required=True)
parser.add_argument('--only', type=str, default=None, help='Filter categories by key', required=True)

args = parser.parse_args()
#config = Configurator(args.cfg, plot=True, plot_version=args.version)
config = json.load( open(args.cfg, 'r') )
if not args.version == '':
    config["output"] = "_".join([config["output"], args.version])

categories = json.load( open(os.path.join(config["output"], 'categories.json')) )
if args.only:
    categories = list(filter(lambda cat : all(f in cat for f in [args.only]), categories))
else:
    categories = list(filter(lambda cat : all(f in cat for f in config["sf_options"]["categories"]["filter"]), categories))

#categories = ["msd40btagDDCvLV2passHwpPt-600to800"]
print(categories)
#sys.exit(1)

for var in ['sv_logsumcorrmass']:
    fit = Fit(config, categories, var, (-1.0, 5.0))
    fit.run_fits()
