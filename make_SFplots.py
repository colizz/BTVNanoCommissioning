import argparse
import numpy as np
import uproot
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import mplhep as hep
from coffea.util import load
from coffea.hist import plot
import coffea.hist as hist
import os
import sys
from utils import histogram_settings, lumi, rescale, xsecs

parser = argparse.ArgumentParser(description='Plot histograms from FitDiagnostic file')
parser.add_argument('-i', '--input', type=str, help='Input histogram filename', required=True)
parser.add_argument('-o', '--outputDir', type=str, default='', help='Output directory')
#parser.add_argument('-s', '--scale', type=str, default='linear', help='Plot y-axis scale', required=False)
#parser.add_argument('-d', '--dense', action='store_true', default=False, help='Normalized plots')
parser.add_argument('--year', type=int, choices=[2016, 2017, 2018], help='Year of data/MC samples', required=True)
parser.add_argument('--data', type=str, default='BTagMu', help='Data sample name')
parser.add_argument('--selection', type=str, default='all', help='Plot only plots with this selection. ("all" to plot all the selections in file)', required=True)

args = parser.parse_args()

if not args.input.endswith('.root'):
    sys.exit("Only ROOT files are accepted as an input")

data_err_opts = {
    'linestyle': 'none',
    'marker': '.',
    'markersize': 10.,
    'color': 'k',
    'elinewidth': 1,
}

qcd_opts = {
    'facecolor': 'yellow',
    'edgecolor': 'black',
    'alpha': 1.0
}

flavor_opts = {
    'facecolor': ['cyan', 'magenta', 'red', 'green', 'blue'],
    'edgecolor': 'black',
    'alpha': 1.0
}

selection = {
    'basic' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 250 GeV$"+"\n"+
                  r"$m_{SD} > 20 GeV$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'pt350msd50' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 50 GeV$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'msd100tau06' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 100 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'pt400msd100tau06' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 400 GeV$"+"\n"+
                  r"$m_{SD} > 100 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
}

_final_mask = ['msd100tau06', 'pt400msd100tau06']
_mask_DDX = {
            'DDB' : {
                #'L' : XX,
                'M' : 0.7
            },
            'DDC' : {
                #'L' : XX,
                'M' : 0.45
            }, 
}
for mask_f in _final_mask:
    for DDX in _mask_DDX.keys():
        for wp, cut in _mask_DDX[DDX].items():
            selection[f'{mask_f}{DDX}pass{wp}wp'] = selection[mask_f]
            selection[f'{mask_f}{DDX}pass{wp}wp'] += f"{DDX}vLV2 > {str(cut)}"+"\n"
            selection[f'{mask_f}{DDX}fail{wp}wp'] = selection[mask_f]
            selection[f'{mask_f}{DDX}fail{wp}wp'] += f"{DDX}vLV2 < {str(cut)}"+"\n"
"""
selection_basic = (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 250 GeV$"+"\n"+
                  r"$m_{SD} > 20 GeV$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n")

selection_msd100tau06 = (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 250 GeV$"+"\n"+
                  r"$m_{SD} > 100 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n")
"""

plt.style.use([hep.style.ROOT, {'font.size': 16}])
plot_dir = args.outputDir if args.outputDir else ('/').join(args.input.split('/')[:-1])
if not plot_dir.endswith('/'): plot_dir = plot_dir + '/'
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

filename = "fitDiagnosticsTest.root"
flavors = ['bb', 'cc', 'b', 'c', 'l']
flavor_axis  = hist.Cat("flavor",   "Flavor")
jetproba_axis  = hist.Bin("jetproba",  r"jet Probability", 50, 0, 2.55)
tagger = 'DDB' if 'DDB' in args.selection else 'DDC'
output = {}

for region in ['sfpass', 'sffail']:
    for fit in ['prefit', 'fit_s']:
        output[f'shape_{fit}_{region}{tagger}{args.year}'] = hist.Hist("entries", flavor_axis, jetproba_axis)

fitdir = f'/work/mmarcheg/BTVNanoCommissioning/fitdir/{args.year}/msd100tau06{tagger}/'
f = uproot.open(args.input)
for region in ['sfpass', 'sffail']:
    fig, axes = plt.subplots(1, 2, figsize=(16,6), sharey=True)
    #print(axes)
    #fig, (ax1, ax2, rax1, rax2) = plt.subplots(2, 2, figsize=(16,6), sharey=True)
    #fig, axes = plt.subplots(1, 2, figsize=(16,6), sharey=True)
    for i, fit in enumerate(['prefit', 'fit_s']):
        ax = axes[i]
        for (j, flavor) in enumerate(flavors):
            h = f[f'shapes_{fit}/{region}/{flavor};1']
            weights, bins = h.to_numpy()
            binsize = bins[1] - bins[0]
            values = (bins - 0.5*binsize)[1:]
            output[f'shape_{fit}_{region}{tagger}{args.year}'].fill(flavor=flavor, jetproba=values, weight=weights)
            #ax.hist(values, bins, weights=weights, color=flavor_opts['facecolor'][::-1][j], stacked=True, label=flavor)

        plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][flavors], ax=ax, legend_opts={'loc':1}, fill_opts=flavor_opts, order=flavors, stack=True)
        data = f[f'shapes_{fit}/{region}/data;1']
        output[f'shape_{fit}_{region}{tagger}{args.year}'].fill(flavor=args.data, jetproba=data.values()[0], weight=data.values()[1])
        errors = data.errors('mean')[1]
        #plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][args.data], ax=ax, legend_opts={'loc':1}, fill_opts=data_err_opts, clear=False)
        #plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][args.data], ax=ax, legend_opts={'loc':1}, clear=False)
        ax.errorbar(data.values()[0], data.values()[1], yerr=errors, marker='.', linestyle='', markersize=10, elinewidth=1, color='black', label=args.data)
        ax.set_title(f'shapes_{fit} ' + region + f' ({tagger}, {args.year})')
        ax.legend(loc='upper right')
        #plot.plotratio(num=output[f'shape_{fit}_{selection}{tagger}{year}']['data'].sum('flavor'), denom=output[f'shape_{fit}_{selection}{tagger}{year}'][flavors].sum('flavor'), ax=axes[i+2],
               #unc='num')
    histname = f'shapes_{region}{tagger}_{args.year}.png'
    plt.savefig(plot_dir + histname, dpi=300, format="png")
