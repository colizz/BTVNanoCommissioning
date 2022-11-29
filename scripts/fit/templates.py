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

from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.utils.plot_utils import dense_axes, get_axis_items

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('--cfg', default=os.getcwd() + "/config/test.json", help='Config file with parameters specific to the current run', required=False)
parser.add_argument('-v', '--version', type=str, default=None, help='Version of output (e.g. `v01`, `v02`, etc.)')
parser.add_argument('-l', '--label', type=str, default=None, help='Extra label for output file')

args = parser.parse_args()
config = Configurator(args.cfg, plot=True, plot_version=args.version)

if os.path.isfile( config.outfile ): accumulator = load(config.outfile)
else: sys.exit(f"Input file '{config.outfile}' does not exist")

flavors = {'l', 'c', 'b', 'cc', 'bb'}
output_templates = {}
fit_variables = [ 'events_logsummass',  'events_logsv1mass', 'events_logsumcorrmass' ]

for histname in fit_variables:
    h_5f = accumulator['variables'][histname]
    #print(h_5f)
    #print(h_5f.keys())
    h_3f = {'l' : h_5f['l'], 'b+bb' : h_5f['b'] + h_5f['bb'], 'c+cc' : h_5f['c'] + h_5f['cc'], 'DATA' : h_5f['DATA']}
    for scheme, h in zip(['3f', '5f'], [h_3f, h_5f]):
        print(f"Histogram: {histname}\tScheme: {scheme}")
        output_templates[scheme] = {}
        samples = h.keys()
        samples_data = list(filter(lambda d : 'DATA' in d, samples))
        flavors   = list(filter(lambda d : 'DATA' not in d, samples))

        h_mc = h[flavors[0]]

        dense_axis = dense_axes(h_mc)[0]
        years      = get_axis_items(h_mc, 'year')
        categories = get_axis_items(h_mc, 'cat')
        variations = get_axis_items(h_mc, 'variation')
        
        for year in years:
            for cat in categories:
                slicing = {'cat' : cat, 'year' : year}
                for f in samples_data:
                    sumw, sumw2 = h[f][slicing].values(), h[f][slicing].variances()
                    output_templates[scheme][f"{histname}_{year}_{cat}_{f}"] = [sumw, sumw2]
                for var in variations:
                    for f in flavors:
                        slicing.update({'variation' : var})
                        sumw, sumw2 = h[f][slicing].values(), h[f][slicing].variances()
                        output_templates[scheme][f"{histname}_{year}_{cat}_QCD_{f}_{var}"] = [sumw, sumw2]

#### Saving into pickle
output_dir = config.output
if not os.path.exists(config.output):
    os.makedirs(config.output)

for scheme, templates in output_templates.items():
    filename = config.outfile.replace('.coffea', f'_templates_{scheme}.pkl')

    if args.label:
        filename = filename.replace('.pkl', f'_{args.label}.pkl')
    print(f"Saving config file to {filename}")
    outfile = open( filename, 'wb' )
    pickle.dump( templates, outfile, protocol=2 )
    outfile.close()

    """
    key = 'hist_leadfatjet_pt'
    if not key in accumulator.keys():
        raise NotImplementedError
    h = accumulator[key]
    cats = [str(s) for s in h.axis('cat').identifiers() if str(s) != 'cat']
    categoriesFileName = '/'.join( config.outfile.split('/')[:-1] ) + '/categories.json'
    print("Saving categories file to " + categoriesFileName)
    categoriesFile = open( categoriesFileName, 'w' )
    json.dump(cats, categoriesFile, indent=1)
    """
