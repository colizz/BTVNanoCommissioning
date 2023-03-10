import os
import sys
import time
import json
import argparse

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
matplotlib.use('Agg')


import matplotlib.pyplot as plt
import math
import mplhep as hep
from coffea.util import load
from coffea.hist import plot
import coffea.hist as hist

from multiprocessing import Pool
from pocket_coffea.parameters.lumi import lumi, femtobarn

from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.utils.plot_utils import slice_accumulator, plot_data_mc_hist1D

parser = argparse.ArgumentParser(description='Plot histograms from coffea file')
parser.add_argument('--cfg', default=None, help='Config file with parameters specific to the current run', required=False)
parser.add_argument('-i', '--input', type=str, default=None, help='Specify input file')
parser.add_argument('-o', '--output', type=str, default=None, help='Specify output folder')
parser.add_argument('-v', '--version', type=str, default=None, help='Version of output (e.g. `v01`, `v02`, etc.)')
parser.add_argument('--test', default=False, action='store_true', help='Test mode')
parser.add_argument('-j', '--workers', type=int, default=8, help='Number of parallel workers to use for plotting')
parser.add_argument('--only', type=str, default='', help='Filter histograms name with string')
parser.add_argument('--log', default=False, action='store_true', help='Set log scale on y-axis', required=False)

args = parser.parse_args()
if args.cfg:
    config = Configurator(args.cfg, plot=True, plot_version=args.version)

#finalstate = config.finalstate
#categories_to_sum_over = config.plot_options["sum_over"]
#var = config.plot_options["var"]

print("Starting ", end='')
print(time.ctime())
start = time.time()

if args.input == None:
    inputfile = config.outfile
else:
    inputfile = args.input
if os.path.isfile( inputfile ): accumulator = load(inputfile)
else: sys.exit(f"Input file '{inputfile}' does not exist")

data_err_opts = {
    'linestyle': 'none',
    'marker': '.',
    'markersize': 10.,
    'color': 'k',
    'elinewidth': 1,
}

mc_opts = {
    #'facecolor': 'None',
    'edgecolor': 'black',
    #'linestyle': '-',
    'linewidth': 1,
}

signal_opts = {
    'facecolor': 'None',
    'edgecolor': ['green', 'red'],
    'linestyle': ['--', '-'],
    'linewidth': 2,
    'alpha': 0.7
}

ggH_opts = {
    'bb' : {
        'facecolor': 'None',
        'edgecolor': 'green',
        'linestyle': '--',
        'linewidth': 2,
        'alpha': 0.7
    },
    'cc': {
        'facecolor': 'None',
        'edgecolor': 'red',
        'linestyle': '--',
        'linewidth': 2,
        'alpha': 0.7
    }
}

selection = {
    'trigger'  : (r'Trigger'),
    'dilepton_SR' : (r'Trigger'+'\n'+
                     r'Dilepton cuts'+'\n'+
                     r'SR'),
    'dilepton_CR' : (r'Trigger'+'\n'+
                     r'Dilepton cuts'+'\n'+
                     r'CR'),
    'semileptonic_SR' : (r'Trigger'+'\n'+
                     r'Semileptonic cuts'+'\n'+
                     r'SR'),
    'semileptonic_CR' : (r'Trigger'+'\n'+
                     r'Semileptonic cuts'+'\n'+
                     r'CR'),
    'semileptonic_triggerSF_Ele32_EleHT_fail' : 'Trigger fail',
    'semileptonic_triggerSF_Ele32_EleHT_pass' : 'Trigger pass',
    'semileptonic_triggerSF_inclusive' : 'Inclusive',
}

plt.style.use([hep.style.ROOT, {'font.size': 16}])
if args.output == None:
    plot_dir = config.plots
else:
    plot_dir = args.output
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)


if args.only:
    args.only = args.only.split(',')
    histnames = accumulator['variables'].keys()
    # Filter dictionary of histograms with `args.only`
    histnames_to_plot = list(filter(lambda histname : any(f in histname for f in args.only), histnames ))
    accumulator['variables'] = { k : v for k,v in accumulator['variables'].items() if k in histnames_to_plot }

def make_plots(entrystart, entrystop):
    _accumulator = slice_accumulator(accumulator, entrystart, entrystop)
    for (histname, h) in _accumulator['variables'].items():
        if args.cfg:
            plot_data_mc_hist1D(h, histname, config, flavorsplit='5f', log=args.log)
        else:
            plot_data_mc_hist1D(h, histname, plot_dir=plot_dir, flavorsplit='5f', log=args.log)


NHistsToPlot = len(accumulator['variables'].keys())
HistsToPlot = [k for k in accumulator['variables'].keys()]
print("# histograms to plot = ", NHistsToPlot)
print("Histograms to plot:", HistsToPlot)

# Parallelization of plotting
delimiters = np.linspace(0, NHistsToPlot, args.workers + 1).astype(int)
chunks = [(delimiters[i], delimiters[i+1]) for i in range(len(delimiters[:-1]))]
pool = Pool()
pool.starmap(make_plots, chunks)
pool.close()

end = time.time()
runTime = round(end-start)
print("Finishing ", end='')
print(time.ctime())
print(f"Drawn {NHistsToPlot} plots in {runTime} s")
