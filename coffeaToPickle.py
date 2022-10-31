import sys
import argparse
import json
import numpy as np
from coffea.util import load
import argparse
import numpy as np
from coffea.hist import plot
import coffea.hist as hist
import itertools
import os
import pickle

# Include PocketCoffea to python paths (needed if running from outside PocketCoffea)
PATH_TO_SCRIPT = '/'.join(sys.argv[0].split('/')[:-1])
PATH_TO_MODULE = os.path.abspath(os.path.join(os.path.abspath(PATH_TO_SCRIPT), "PocketCoffea"))
if not PATH_TO_MODULE in sys.path:
    sys.path.append(PATH_TO_MODULE)

print(sys.path)

from PocketCoffea.utils.Configurator import Configurator

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('--cfg', default=os.getcwd() + "/config/test.json", help='Config file with parameters specific to the current run', required=False)
parser.add_argument('-v', '--version', type=str, default=None, help='Version of output (e.g. `v01`, `v02`, etc.)')
parser.add_argument('-l', '--label', type=str, default=None, help='Extra label for output file')

args = parser.parse_args()
config = Configurator(args.cfg, plot=True, plot_version=args.version)
year = config.dataset["filter"]["year"]
if len(year) > 1:
    raise NotImplementedError
else: year = year[0]

if os.path.isfile( config.outfile ): accumulator = load(config.outfile)
else: raise NotImplementedError

print(accumulator.keys())

outputDict = {}
outputDict_bbcc = {}
fit_variables = [ 'sv_logsummass',  'sv_logprojmass', 'sv_logsv1mass', 'sv_logsumcorrmass' ]
fit_variables_veto = [ 'sv_logsv1massratio', 'sv_logsv1massres' ]
for histname, h in accumulator.items():
    if not histname.startswith('hist_'): continue
    variable = histname.split('hist_')[1]
    if variable.startswith(tuple(fit_variables)) & (not variable.startswith(tuple(fit_variables_veto))):
        print(sorted([varname for varname in fit_variables if varname in histname]))
        ivar = sorted([varname for varname in fit_variables if varname in histname])[-1]
        print(histname, ivar)
    else:
        continue
    if h.dense_dim() > 1: raise NotImplementedError
    print(f"Rebinning {histname}")
    h = h.rebin(h.dense_axes()[0], hist.Bin(h.dense_axes()[0].name, config.sf_options["rebin"][variable]['xlabel'], **config.sf_options["rebin"][variable]["binning"]))
    #h = h.rebin(h.fields[-1], hist.Bin(h.fields[-1], h.axis(h.fields[-1]).label, **histogram_settings[args.campaign]['variables'][ivar]['binning']))

    ##### grouping flavor
    mapping_flavor = {'l' : ['l'], 'bb' : ['b', 'bb'], 'cc' : ['c', 'cc']}
    h_bbcc = h.group("flavor", hist.Cat("flavor", "Flavor"), mapping_flavor)
    print(mapping_flavor)

    ##### grouping data and QCD histos
    samples = [str(s) for s in h.axis('sample').identifiers() if str(s) != 'sample']
    mapping = {
        r'QCD ($\mu$ enriched)' : [sample for sample in samples if 'QCD_Pt' in sample],
        r'DATA': [ idata for idata in samples if 'DATA' in idata ],
    }
    samples = mapping.keys()
    samples_data = [sample for sample in samples if 'DATA' in sample]
    samples_QCD  = [sample for sample in samples if (('DATA' not in sample) & ('GluGlu' not in sample))]
    
    h = h.group("sample", hist.Cat("sample", "sample"), mapping)
    h_bbcc = h_bbcc.group("sample", hist.Cat("sample", "sample"), mapping)
    QCD  = h[samples_QCD].sum('sample')
    DATA = h[samples_data].sum('sample')
    QCD_bbcc  = h_bbcc[samples_QCD].sum('sample')
    DATA_bbcc = h_bbcc[samples_data].sum('sample')
    print(QCD.sparse_axes())

    #### storing into dict for each cat
    cats    = [str(s) for s in h.axis('cat').identifiers() if str(s) != 'cat']
    flavors = [str(s) for s in h.axis('flavor').identifiers() if str(s) != 'Data']
    flavors_bbcc = [str(s) for s in h_bbcc.axis('flavor').identifiers() if str(s) != 'Data']
    years   = [str(s) for s in h.axis('year').identifiers() if str(s) != 'year']
    categories_to_sum_over = ['cat', 'year', 'flavor']
    for cat in cats:
        print("Category:", cat)
        for flavor in flavors:
            tmpValue, sumw2 = QCD[(cat, year, flavor)].sum(*categories_to_sum_over).values(sumw2=True)[()]
            outputDict[ histname+'_'+cat+'_QCD_'+flavor+'_'+year ] = [ tmpValue, sumw2 ]
        for flavor in flavors_bbcc:
            ### HARDCODED: when rebinning the flavor axis, it becomes the first sparse axis
            tmpValue, sumw2 = QCD_bbcc[(flavor, cat, year)].sum(*categories_to_sum_over).values(sumw2=True)[()]
            outputDict_bbcc[ histname+'_'+cat+'_QCD_'+flavor+'_'+year ] = [ tmpValue, sumw2 ]
        tmpValue, sumw2 = DATA[(cat, year, 'Data')].sum(*categories_to_sum_over).values(sumw2=True)[()]
        outputDict[ histname+'_'+cat+'_Data'+'_'+year ]      = [ tmpValue, sumw2 ]
        outputDict_bbcc[ histname+'_'+cat+'_Data'+'_'+year ] = [ tmpValue, sumw2 ]

#### Saving into pickle
output_dir = config.output
if not os.path.exists(config.output):
    os.makedirs(config.output)
outputFileName = config.outfile.replace('.coffea', '.pkl')
outputFileName_bbcc = outputFileName.replace('.pkl', '_bbcc.pkl')
for fname, d in zip([outputFileName, outputFileName_bbcc], [outputDict, outputDict_bbcc]):
    if args.label:
        fname = fname.replace('.pkl', f'_{args.label}.pkl')
    print("Saving config file to " + fname)
    outputFile = open( fname, 'wb' )
    pickle.dump( d, outputFile, protocol=2 )
    outputFile.close()

key = 'hist_leadfatjet_pt'
if not key in accumulator.keys():
    raise NotImplementedError
h = accumulator[key]
cats = [str(s) for s in h.axis('cat').identifiers() if str(s) != 'cat']
categoriesFileName = '/'.join( config.outfile.split('/')[:-1] ) + '/categories.json'
print("Saving categories file to " + categoriesFileName)
categoriesFile = open( categoriesFileName, 'w' )
json.dump(cats, categoriesFile, indent=1)
