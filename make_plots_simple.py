import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import mplhep as hep
from coffea.util import load
from coffea.hist import plot
import coffea.hist as hist
import itertools
import os
import time
from multiprocessing import Pool
from parameters import histogram_settings, flavors_color, flavor_opts, flavors_order, lumi, xsecs, PtBinning, AK8Taggers, AK8TaggerWP, FinalMask

parser = argparse.ArgumentParser(description='Plot histograms from coffea file')
parser.add_argument('-i', '--input', type=str, help='Input histogram filename', required=True)
parser.add_argument('-o', '--output', type=str, default='', help='Output directory')
parser.add_argument('--outputDir', type=str, default=None, help='Output directory')
parser.add_argument('-s', '--scale', type=str, default='linear', help='Plot y-axis scale', required=False)
parser.add_argument('-d', '--dense', action='store_true', default=False, help='Normalized plots')
parser.add_argument('--year', type=str, choices=['2016', '2017', '2018'], help='Year of data/MC samples', required=True)
parser.add_argument('--campaign', type=str, choices={'EOY', 'UL'}, help='Dataset campaign.', required=True)
parser.add_argument('--proxy', action='store_true', help='Plot proxy and signal comparison')
parser.add_argument('--only', action='store', default='', help='Plot only one histogram')
parser.add_argument('--test', action='store_true', default=False, help='Test with lower stats.')
parser.add_argument('--data', type=str, default='BTagMu', help='Data sample name')
parser.add_argument('--selection', type=str, default='all', help='Plot only plots with this selection. ("all" to plot all the selections in file)')
parser.add_argument('--tagger', type=str, default='btagDDCvLV2', help="Tagger corresponding to additional histogram's axis.")
parser.add_argument('--mergeflavor', action='store_true', default=False, help='Merge b+bb and c+cc')
parser.add_argument('--passfail', action='store_true', default=False, help='Plots in pass + fail regions')
parser.add_argument('--lumiscale', action='store_true', default=False, help='Scale MC by x-section times luminoisity.', required=False)
parser.add_argument('-n', '--normed', action='store_true', default=False, help='Normalized overlayed plots')
parser.add_argument('-j', '--workers', type=int, default=12, help='Number of workers (cores/threads) to use for multi-worker execution (default: %(default)s)')

args = parser.parse_args()

print("Starting ", end='')
print(time.ctime())
start = time.time()
print("Running with options:")
print("    ", args)

if os.path.isfile( args.input ): accumulator = load(args.input)
else:
    files_list = [ifile for ifile in os.listdir(args.input) if ifile != args.output]
    accumulator = load(args.input + files_list[0])
    histograms = accumulator.keys()
    for ifile in files_list[1:]:
        output = load(args.input + ifile)
        for histname in histograms:
            accumulator[histname].add(output[histname])

totalLumi = 'TEST' if args.test else lumi[args.campaign][args.year]
#scaleXS = {}
#for isam in accumulator[next(iter(accumulator))].identifiers('dataset'):
#    isam = str(isam)
#    if args.lumiscale:
#        scaleXS[isam] = 1 if isam.startswith('BTag') else xsecs[isam]/accumulator['sumw'][isam] * 1000 * totalLumi
#    else:
#        scaleXS[isam] = 1 if isam.startswith('BTag') else xsecs[isam]/accumulator['sumw'][isam]

data_err_opts = {
    'linestyle': 'none',
    'marker': '.',
    'markersize': 10.,
    'color': 'k',
    'elinewidth': 1,
}

qcd_opts = {
    'facecolor': 'None',
    'edgecolor': 'blue',
    'linestyle': '-',
    'linewidth': 2,
    'alpha': 0.7
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
    'basic' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 250 GeV$"+"\n"+
                  r"$m_{SD} > 20 GeV$"+"\n"),
    'pt350msd50' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 50 GeV$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'msd100tau06' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 100 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'msd100tau06ggHcc' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 100 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"+
                  r"DDCvB > 0.03"+"\n"),
    'msd60tau06' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 60 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'msd60tau06ggHcc' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 60 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"+
                  r"DDCvB > 0.03"+"\n"),
    'msd40tau06' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 40 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"),
    'msd40tau06ggHcc' : (r"$\geq$1 AK8 jets"+"\n"+
                  r"$p_T > 350 GeV$"+"\n"+
                  r"$m_{SD} > 40 GeV$"+"\n"+
                  r"$\tau_{21} < 0.6$"+"\n"+
                  r"$\geq$2 $\mu$-tagged AK4 subjets"+"\n"+
                  r"DDCvB > 0.03"+"\n"),
}

for mask_f in FinalMask:
    for tagger in AK8TaggerWP[args.campaign][args.year].keys():
        for wp, cut in AK8TaggerWP[args.campaign][args.year][tagger].items():
            selection[f'{mask_f}{tagger}pass{wp}wp'] = selection[mask_f]
            selection[f'{mask_f}{tagger}pass{wp}wp'] += f"{tagger}vLV2 > {str(cut)}"+"\n"
            selection[f'{mask_f}{tagger}fail{wp}wp'] = selection[mask_f]
            selection[f'{mask_f}{tagger}fail{wp}wp'] += f"{tagger}vLV2 < {str(cut)}"+"\n"
            for wpt, (pt_low, pt_high) in PtBinning[args.campaign][args.year].items():
                selection[f'{mask_f}{tagger}pass{wp}wpPt-{pt_low}to{pt_high}'] = selection[f'{mask_f}{tagger}pass{wp}wp']
                selection[f'{mask_f}{tagger}pass{wp}wpPt-{pt_low}to{pt_high}'] += r"$p_T$ bin:" + f" ({pt_low}, {pt_high}) [GeV]"+"\n"
                selection[f'{mask_f}{tagger}fail{wp}wpPt-{pt_low}to{pt_high}'] = selection[f'{mask_f}{tagger}fail{wp}wp']
                selection[f'{mask_f}{tagger}fail{wp}wpPt-{pt_low}to{pt_high}'] += r"$p_T$ bin:" + f" ({pt_low}, {pt_high}) [GeV]"+"\n"

plt.style.use([hep.style.ROOT, {'font.size': 16}])
plot_dir = args.outputDir if args.outputDir else os.getcwd()+"/plots/" + args.output + "/"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

def make_plots(entrystart, entrystop):
    _accumulator = dict(list(accumulator.items())[entrystart:entrystop])
    for histname in _accumulator:
        if 'hist2d' in histname: continue
        if args.only and not (args.only in histname): continue
        if not args.passfail and (any(r in histname for r in ['pass', 'fail'])): continue
        if type(_accumulator[histname]) is not hist.Hist: continue
        if histname in ["sumw", "sum_genweights", "nbtagmu", "nbtagmu_event_level", "nfatjet"]: continue

        if any([histname.startswith('cutflow')]): break

        h = _accumulator[histname]
        varname = h.fields[-1]
        varlabel = h.axis(varname).label
        print(histname)
        if histname.startswith( tuple(histogram_settings[args.campaign]['variables'].keys()) ):
            h = h.rebin(varname, hist.Bin(varname, varlabel, **histogram_settings[args.campaign]['variables'][histname]['binning']))
        #h.scale( scaleXS, axis='dataset' )
        
        ##### grouping flavor
        flavors = [str(s) for s in h.axis('flavor').identifiers() if str(s) != 'flavor']
        if args.mergeflavor:
            mapping_flavor = {f : [f] for f in flavors}
            flavors_to_merge = ['bb', 'b', 'cc', 'c']
            for flav in flavors_to_merge:
                mapping_flavor.pop(flav)
            mapping_flavor['b_bb'] = ['b', 'bb']
            mapping_flavor['c_cc'] = ['c', 'cc']
            
            h = h.group("flavor", hist.Cat("flavor", "Flavor"), mapping_flavor)
            flavors = [item for item in list(mapping_flavor.keys()) if 'Data' not in item]
            #flavors = ['b_bb', 'c_cc', 'l']
        order = flavors_order['btagDDBvLV2']
        if ('btagDDCvLV2' in histname) | ('particleNetMD_Xcc' in histname):
            order = flavors_order['btagDDCvLV2']

        flavor_opts['facecolor'] = [flavors_color[f.split('_')[-1]] for f in order if 'Data' not in f]

        ##### grouping data and QCD datasets
        datasets = [str(s) for s in h.axis('dataset').identifiers() if str(s) != 'dataset']
        mapping = {
            r'QCD ($\mu$ enriched)' : [dataset for dataset in datasets if 'QCD_Pt' in dataset],
            r'BTagMu': [ idata for idata in datasets if args.data in idata ],
        }
        for dataset in datasets:
            if 'QCD' in dataset: continue
            if args.data in dataset: continue
            mapping[dataset] = [dataset]
        datasets = mapping.keys()
        datasets_data  = [dataset for dataset in datasets if args.data in dataset]
        datasets_QCD = [dataset for dataset in datasets if ((args.data not in dataset) & ('GluGlu' not in dataset))]
        datasets_ggH = [dataset for dataset in datasets if 'GluGlu' in dataset]
        h = h.group("dataset", hist.Cat("dataset", "Dataset"), mapping)

        print("Plotting", histname)

        #if not args.lumiscale:
        #    dataSum = np.sum( h_fail[args.data].sum('flavor').values()[('BTagMu',)] )
        #    QCDSum = np.sum( h_fail[datasets_QCD].sum('dataset', 'flavor').values()[()] )
        #    QCD = h[datasets_QCD].sum('dataset')
        #    QCD.scale( dataSum/QCDSum )
        #else:
        #    QCD = h[datasets_QCD].sum('dataset')
        
        QCD = h[datasets_QCD].sum('dataset')

        ##### plotting histograms for each region
        regions = [str(s) for s in h.axis('region').identifiers() if str(s) != 'region']
        for region in regions:
            if not args.selection.startswith('all') and not ( args.selection in region ): continue
            selection_text = selection[region]
            QCD_region  = QCD[[region]].sum('region')
            if (args.tagger in QCD_region.axes()) & (QCD_region.dense_dim() >= 2):
                QCD_region  = QCD_region.sum(args.tagger)
            #print(QCD_region.values())
            #data_region = h[(args.data, 'Data', region )].sum('flavor', 'region')
            #data_region = h[[args.data]].sum('flavor', 'region')
            data_region = h[(args.data, region)].sum('dataset', 'region')
            if (args.tagger in data_region.axes()) & (data_region.dense_dim() >= 2):
                data_region  = data_region.sum(args.tagger)
            maxY = 1.2 *max( [ max(data_region.sum('flavor').values()[()]),  max(QCD_region.sum('flavor').values()[()]) ] )

            fig, (ax, rax) = plt.subplots(2, 1, figsize=(12,12), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
            #fig_normed, (ax_normed, rax_normed) = plt.subplots(2, 1, figsize=(12,12), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
            fig.subplots_adjust(hspace=.07)
            plot.plot1d(QCD_region, ax=ax, legend_opts={'loc':1}, fill_opts=flavor_opts, order=order, stack=True)
            plot.plot1d(data_region, ax=ax, legend_opts={'loc':1}, error_opts=data_err_opts, clear=False)
            #plot.plot1d(ggH_rescaled, ax=ax, legend_opts={'loc':1}, fill_opts=signal_opts, stack=False, clear=False)
            #plot.plotratio(num=h[datasets_data].sum('dataset', 'flavor'), denom=QCD.sum('flavor'), ax=rax,
            #               error_opts=data_err_opts, denom_fill_opts={}, guide_opts={}, unc='num')
            plot.plotratio(num=data_region.sum('flavor'), denom=QCD_region.sum('flavor'), ax=rax,
                           error_opts=data_err_opts, denom_fill_opts={}, guide_opts={}, unc='num')
            handles, labels = ax.get_legend_handles_labels()
            
            hep.cms.text("Preliminary", ax=ax)
            hep.cms.lumitext(text=f'{totalLumi}' + r' fb$^{-1}$, 13 TeV,' + f' {args.year}', fontsize=18, ax=ax)
            ax.legend(handles, labels)
            rax.set_ylabel('Data/MC')
            rax.set_ylim(0.0,2.0)
            rax.set_yticks([0.5, 1.0, 1.5])
            #rax.set_ylim(0.0,5.0)
            #rax.set_yticks(np.arange(0, 5.5, 0.5))
            if histname.startswith( tuple(histogram_settings[args.campaign]['variables'].keys()) ):
                ax.set_xlim(**histogram_settings[args.campaign]['variables'][histname]['xlim'])
                rax.set_xlim(**histogram_settings[args.campaign]['variables'][histname]['xlim'])
            x_low, x_high = rax.get_xlim()
            rax.hlines([0.5, 1.5], x_low, x_high, colors='grey', linestyles='dashed', linewidth=1)
            at = AnchoredText(selection_text, loc=2, frameon=False)
            ax.add_artist(at)
            if histname.startswith("btag"):
                ax.semilogy()
            if (not args.dense) & (args.scale == "log"):
                ax.semilogy()                
                ax.set_ylim(0.1, 10**7)
            else: ax.set_ylim(0,maxY)
            #hep.mpl_magic(ax)
            filepath = f"{plot_dir}{histname}_{region}.png"
            if args.scale != parser.get_default('scale'):
                #rax.set_ylim(0.1,10)
                filepath = filepath.replace(".png", "_" + args.scale + ".png")
            print("Saving", filepath)
            plt.savefig(filepath, dpi=300, format="png")
            plt.close(fig)

            if args.proxy & (any(tagger in histname for tagger in AK8Taggers) | ('logsv1mass' in histname)):
                ggH_rescaled = h[datasets_ggH].sum('flavor')
                scale_ggH = 100
                ggH_rescaled.scale(scale_ggH)
                if any(r in histname for r in ['pass', 'fail']): continue
                QCD = {}
                ggH = {}
                for dataset in datasets:
                    if 'QCD' in dataset:
                        histo_QCD = h[dataset]
                        QCD['bb'] = h[(dataset, 'bb')]
                        QCD['cc'] = h[(dataset, 'cc')]
                    if 'GluGluHToBB' in dataset:
                        histo_BB  = h[dataset]
                        ggH['bb'] = h[(dataset, 'bb')]
                    if 'GluGluHToCC' in dataset:
                        histo_CC  = h[dataset]
                        ggH['cc'] = h[(dataset, 'cc')]

                for xx in QCD.keys():
                    for scale in ['linear', 'log']:
                        fig, ax = plt.subplots(1, 1, figsize=(9,9))
                        plot.plot1d(QCD[xx].sum('flavor'), ax=ax, legend_opts={'loc':1}, density=True, fill_opts=qcd_opts, stack=True)
                        plot.plot1d(ggH[xx].sum('flavor'), ax=ax, legend_opts={'loc':1}, density=True, fill_opts=ggH_opts[xx], stack=False, clear=False)
                        hep.cms.text("Simulation", ax=ax)
                        hep.cms.lumitext(text=f'{totalLumi}' + r' fb$^{-1}$, 13 TeV,' + f' {args.year}', fontsize=18, ax=ax)
                        ax.set_yscale(scale)
                        if scale == 'log':
                            ax.set_ylim(10**(-3), 10**3)
                        ax.set_ylabel('a.u.')
                        handles, labels = ax.get_legend_handles_labels()
                        for (i, label) in enumerate(labels):
                            if "QCD" in label:
                                labels[i] = rf"g$\rightarrow${xx}"
                            if "GluGlu" in label:
                                #labels[i] = r"ggH$\rightarrow${xx} ({xx} component)"
                                labels[i] = rf"ggH$\rightarrow${xx}"
                        ax.legend(handles, labels)

                        at = AnchoredText(selection_text, loc=2, frameon=False)
                        ax.add_artist(at)
                        filepath = f"{plot_dir}{histname}_{region}_ggH{xx}_{scale}.png"
                        print("Saving", filepath)
                        plt.savefig(filepath, dpi=300, format="png")
                        plt.close(fig)

NtotHists = len(accumulator.keys())
NHistsToPlot = len([key for key in accumulator.keys() if args.only in key])
print("# tot histograms = ", NtotHists)
print("# histograms to plot = ", NHistsToPlot)
delimiters = np.linspace(0, NtotHists, args.workers + 1).astype(int)
chunks = [(delimiters[i], delimiters[i+1]) for i in range(len(delimiters[:-1]))]
pool = Pool()
pool.starmap(make_plots, chunks)
pool.close()

end = time.time()
runTime = round(end-start)
print("Finishing ", end='')
print(time.ctime())
print(f"Drawn {NHistsToPlot} plots in {runTime} s")