import os
import sys
import argparse
import json

import numpy as np

#print(sys.path)
sys.path.append('/work/mmarcheg/BTVNanoCommissioning')
sys.path.append('/work/mmarcheg/BTVNanoCommissioning/PocketCoffea')

from utils.Fit import Fit

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('--cfg', default=os.getcwd() + "/config/test.json", help='Config file with parameters specific to the current run', required=False)
parser.add_argument('-v', '--version', type=str, default=None, help='Version of output (e.g. `v01`, `v02`, etc.)', required=True)
parser.add_argument('--only', type=str, default=None, help='Filter categories by key', required=True)
parser.add_argument('--scheme', type=str, default=None, choices=['3f', '5f'],  help='3-flavor scheme', required=False)

args = parser.parse_args()

config = json.load(open(args.cfg, 'r'))
if args.version:
    config['output'] = config['output'] + '_{}'.format(args.version)

categories = config["categories"]
if args.only:
    categories = list(filter(lambda cat : all(f in cat for f in [args.only]), categories))

print(categories)

for var in ['events_logsumcorrmass']:
    fit = Fit(config, categories, var, (-1.0, 5.0), scheme=args.scheme)
    fit.run_fits()
