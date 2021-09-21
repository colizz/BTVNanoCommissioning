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
parser.add_argument('--var', type=str, default='logsv1mass', help='Variable used in the template fit.', required=True)
#parser.add_argument('--wpt', type=str, choices={'', 'M', 'H'}, default='', help='Pt bin')
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

flavors_color = {'l' : 'blue', 'b' : 'red', 'c' : 'green', 'bb' : 'cyan', 'cc' : 'magenta'}

flavor_opts = {
    'facecolor': [flavors_color[f] for f in flavors_color.keys()],
    'edgecolor': 'black',
    'alpha': 1.0
}

flavor_normed_opts = {
    'facecolor': 'None',
    'edgecolor': 'green',
    'linestyle': '-',
    'linewidth': 2,
    'alpha': 0.7
}

err_opts = {
    'linestyle': '-',
    'marker': '.',
    'markersize': 10,
    'color': 'k',
    'elinewidth': 0,
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

xlabel = {
    'fatjet_jetproba' : r"jet Probability",
    'sv_logsv1mass'   : r"lead. FatJet log($m_{SV,1}$/GeV)",
}

for mask_f in _final_mask:
    for DDX in _mask_DDX.keys():
        for wp, cut in _mask_DDX[DDX].items():
            selection['{}{}pass{}wp'.format(mask_f, DDX, wp)] = selection[mask_f]
            selection['{}{}pass{}wp'.format(mask_f, DDX, wp)] += "{}vLV2 > {}".format(DDX, cut)+"\n"
            selection['{}{}fail{}wp'.format(mask_f, DDX, wp)] = selection[mask_f]
            selection['{}{}fail{}wp'.format(mask_f, DDX, wp)] += "{}vLV2 < {}".format(DDX, cut)+"\n"
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

if 'MPt' in args.input:
    wpt = 'MPt'
elif 'HPt' in args.input:
    wpt = 'HPt'
elif 'InclusivePt' in args.input:
    wpt = 'InclusivePt'
filename = "fitDiagnostics{wpt}.root"
tagger = 'DDB' if 'DDB' in args.selection else 'DDC'
#flavors = ['bb', 'cc', 'b', 'c', 'l']
flavors = ['l', 'b', 'c', 'bb', 'cc']
#if tagger == 'DDC':
#flavor_opts['facecolor'].pop(flavors.index('b'))
#flavor_opts['facecolor'].pop(flavors.index('c')-1)
#flavors = ['b_bb', 'c_cc', 'l']
if tagger == 'DDB':
    flavors = ['l', 'c_cc', 'b_bb']
elif tagger == 'DDC':
    flavors = ['l', 'b_bb', 'c_cc']
flavor_opts['facecolor'] = [flavors_color[f.split('_')[-1]] for f in flavors]
flavors_to_remove = []
flavor_axis  = hist.Cat("flavor",   "Flavor")
#jetproba_axis  = hist.Bin("jetproba",  r"jet Probability", **histogram_settings['variables']['fatjet_jetproba']['binning'])
#logsv1mass_axis  = hist.Bin("logsv1mass",  r"lead. FatJet log($m_{SV,1}$/GeV)", **histogram_settings['variables']['sv_logsv1mass']['binning'])
observable_axis  = hist.Bin(args.var.split('_')[1],  xlabel[args.var], **histogram_settings['variables'][args.var]['binning'])
output = {}

for region in ['sfpass', 'sffail']:
    for fit in ['prefit', 'fit_s']:
        output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)] = hist.Hist("entries", flavor_axis, observable_axis)

fitdir = '/work/mmarcheg/BTVNanoCommissioning/fitdir/{}/msd100tau06{}_{}/'.format(args.year, tagger, args.var.split('_')[1])
f = uproot.open(args.input)
for region in ['sfpass', 'sffail']:
    #fig, axes = plt.subplots(2, 2, figsize=(12,8), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
    #fig_normed, axes_normed = plt.subplots(2, 2, figsize=(12,8), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
    fig, axes = plt.subplots(2, 2, figsize=(12,7), gridspec_kw={"height_ratios": (2.5, 1)}, sharex=True)
    fig_normed, axes_normed = plt.subplots(2, 2, figsize=(12,7), gridspec_kw={"height_ratios": (2.5, 1)}, sharex=True)
    #fig, axes = plt.subplots(1, 2, figsize=(16,6), sharey=True)
    for i, fit in enumerate(['prefit', 'fit_s']):
        #ax = axes[i]
        for (j, flavor) in enumerate(flavors):
            histname = 'shapes_{}/{}/{};1'.format(fit, region, flavor)
            if histname not in f.keys():
                flavors_to_remove.append(flavor)
                continue
            h = f[histname]
            weights, bins = h.to_numpy()
            #binwidth = bins[1] - bins[0]
            binwidth = np.diff(bins)
            weights = weights*binwidth
            values = (bins[1:] - 0.5*binwidth)
            print(flavor, weights)
            
            values_to_fill = np.concatenate(np.array([values[i]*np.ones(round(abs(w))) for i,w in enumerate(weights)], dtype=object))
            weights_to_fill = np.concatenate(np.array([w/round(abs(w))*np.ones(round(abs(w))) for i,w in enumerate(weights)], dtype=object))
            #output[f'shape_{fit}_{region}{tagger}{args.year}'].fill(flavor=flavor, jetproba=values, weight=weights)
            #output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)].fill(flavor=flavor, logsv1mass=values, weight=weights)
            output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)].fill(flavor=flavor, logsv1mass=values_to_fill, weight=weights_to_fill)
            axes_normed[0][i].hist(values, bins, weights=weights, edgecolor=flavor_opts['facecolor'][j], histtype='step', density=True, stacked=False, label=flavor)

        for flavor in flavors:
            if flavor in flavors_to_remove:
                flavor_opts['facecolor'].pop(flavors.index(flavor))
                flavors.remove(flavor)
        plot.plot1d(output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][flavors], ax=axes[0][i], legend_opts={'loc':1}, fill_opts=flavor_opts, order=flavors, stack=True)
        #for (j, flavor) in enumerate(flavors):
            #flavor_normed_opts['facecolor'] = flavor_opts['facecolor'][j]
            #flavor_normed_opts['edgecolor'] = flavor_opts['facecolor'][j]
            #err_opts['color'] = flavor_opts['facecolor'][j]
            #plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][flavor], ax=axes_normed[0][i], density=True, legend_opts={'loc':1}, fill_opts=flavor_normed_opts, error_opts=err_opts, stack=False, clear=False)
            #plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][flavor], ax=axes_normed[0][i], density=True, legend_opts={'loc':1}, error_opts=err_opts, stack=False, clear=False)
        data = f['shapes_{}/{}/data;1'.format(fit, region)]
        data_values = data.values()[0]
        data_weights = data.values()[1]*binwidth
        data_values_to_fill = np.concatenate(np.array([data_values[i]*np.ones(round(w)) for i,w in enumerate(data_weights)], dtype=object))
        data_sum = np.sum(data_weights*binwidth)
        data_weights_normed = data.values()[1]*binwidth/data_sum
        errors = data.errors('mean')[1]*binwidth
        errors_normed = data.errors('mean')[1]*binwidth/data_sum
        #output[f'shape_{fit}_{region}{tagger}{args.year}'].fill(flavor=args.data, jetproba=data.values()[0], weight=data_weights)
        #output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)].fill(flavor=args.data, logsv1mass=data_values, weight=data_weights)
        output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)].fill(flavor=args.data, logsv1mass=data_values_to_fill)
        axes[0][i].errorbar(data_values, data_weights, yerr=errors, marker='.', linestyle='', markersize=10, elinewidth=1, color='black', label=args.data)
        axes_normed[0][i].errorbar(data_values, data_weights_normed, yerr=errors_normed, marker='.', linestyle='', markersize=10, elinewidth=1, color='black', label=args.data)
        #plot.plot1d(output[f'shape_{fit}_{region}{tagger}{args.year}'][args.data], ax=ax'es[0][i], legend_opts={'loc':1}, error_opts=data_err_opts, clear=False)
        axes[0][i].set_title('shapes_{} '.format(fit) + region + ' ({}, {})'.format(tagger, args.year))
        axes_normed[0][i].set_title('shapes_{} '.format(fit) + region + ' ({}, {})'.format(tagger, args.year))
        if i == 1:
            axes[0][i].set_ylim(axes[0][0].get_ylim())
            axes_normed[0][i].set_ylim(axes_normed[0][0].get_ylim())
        axes[0][i].legend(loc='upper right')
        axes_normed[0][i].legend(loc='upper right')
        num = output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][args.data].sum('flavor')
        plot.plotratio(num=output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][args.data].sum('flavor'),
                       denom=output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][flavors].sum('flavor'),
                       ax=axes[1][i],
                       error_opts=data_err_opts, denom_fill_opts={}, guide_opts={},
                       unc='num')
        plot.plotratio(num=output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][args.data].sum('flavor'),
                       denom=output['shape_{}_{}{}{}'.format(fit, region, tagger, args.year)][flavors].sum('flavor'),
                       ax=axes_normed[1][i],
                       error_opts=data_err_opts, denom_fill_opts={}, guide_opts={},
                       unc='num')
        axes[1][i].set_xlim(**histogram_settings['variables']['sv_logsv1mass']['xlim'])
        axes_normed[1][i].set_xlim(**histogram_settings['variables']['sv_logsv1mass']['xlim'])
        axes[1][i].set_ylim(0.0, 2.0)
        axes_normed[1][i].set_ylim(0.0, 2.0)
        axes[1][i].set_yticks([0.5, 1.0, 1.5])
        axes_normed[1][i].set_yticks([0.5, 1.0, 1.5])
        axes[1][i].hlines([0.5, 1.5], **histogram_settings['variables']['sv_logsv1mass']['xlim'], colors='grey', linestyles='dashed', linewidth=1)
        axes_normed[1][i].hlines([0.5, 1.5], **histogram_settings['variables']['sv_logsv1mass']['xlim'], colors='grey', linestyles='dashed', linewidth=1)
    histname = 'shapes_{}{}{}_{}.png'.format(region, tagger, wpt, args.year)
    fig.savefig(plot_dir + histname, dpi=300, format="png")
    fig_normed.savefig(plot_dir + histname.replace('.png', '_normed.png'), dpi=300, format="png")
