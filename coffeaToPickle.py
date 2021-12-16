import argparse
import numpy as np
from coffea.util import load
from coffea.hist import plot
import coffea.hist as hist
import itertools
import os
import pickle
from utils import rescale
from parameters import histogram_settings, lumi, xsecs

parser = argparse.ArgumentParser(description='Plot histograms from coffea file')
parser.add_argument('-i', '--input', type=str, help='Input histogram filename', required=True)
parser.add_argument('-o', '--output', type=str, default='', help='Output file')
parser.add_argument('--outputDir', type=str, default=None, help='Output directory')
parser.add_argument('--year', type=int, choices=[2016, 2017, 2018], help='Year of data/MC samples', required=True)
parser.add_argument('--data', type=str, default='BTagMu', help='Data sample name')
parser.add_argument('--pt', type=int, default=500, help='Pt cut.')
parser.add_argument('--scaleFail', type=float, default=None, help='Artificial scaling factor for distributions in the fail region.', required=False)

args = parser.parse_args()
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

scaleXS = {}
for isam in accumulator[next(iter(accumulator))].identifiers('dataset'):
    isam = str(isam)
    scaleXS[isam] = 1 if isam.startswith('BTag') else xsecs[isam]/accumulator['sumw'][isam]

outputDict = {}
for ivar in [ 'fatjet_jetproba', 'sv_logsv1mass', 'sv_logsv1mass_maxdxySig' ]:
    for isel in [ 'msd100tau06' ]:
        for DDX in [ 'DDB', 'DDC' ]:
            for wp in [ 'M' ]:
                for (pt_low, pt_high) in [('', ''), (350, args.pt), (args.pt, 'Inf')]:
                    for passfail in ['pass', 'fail']:

                        if pt_low == '':
                            histname=f'{ivar}_{isel}{DDX}{passfail}{wp}wp'
                        else:
                            histname=f'{ivar}_{isel}{DDX}{passfail}{wp}wpPt-{pt_low}to{pt_high}'
                        if histname not in accumulator.keys():
                            h = accumulator[histname.replace(f'{args.pt}', f'{args.pt}.0')]
                        else:
                            h = accumulator[histname]                            
                        h.scale( scaleXS, axis='dataset' )
                        if (args.scaleFail != None) & (passfail == 'fail'):
                            print(f"Scaling fail distributions by a factor {args.scaleFail}")
                            #h.scale( args.scaleFail, axis='dataset' )
                            h.scale( args.scaleFail )
                        h = h.rebin(h.fields[-1], hist.Bin(h.fields[-1], h.axis(h.fields[-1]).label, **histogram_settings['variables']['_'.join(histname.split('_')[:-1])]['binning']))

                        ##### grouping flavor
                        flavors = [str(s) for s in h.axis('flavor').identifiers() if str(s) != 'flavor']
                        mapping_flavor = {f : [f] for f in flavors}
                        flavors_to_merge = ['bb', 'b', 'cc', 'c']
                        for flav in flavors_to_merge:
                            mapping_flavor.pop(flav)
                        mapping_flavor['b_bb'] = ['b', 'bb']
                        mapping_flavor['c_cc'] = ['c', 'cc']
                        h = h.group("flavor", hist.Cat("flavor", "Flavor"), mapping_flavor)

                        ##### grouping data and QCD histos
                        datasets = [str(s) for s in h.axis('dataset').identifiers() if str(s) != 'dataset']
                        mapping = {
                            r'QCD ($\mu$ enriched)' : [dataset for dataset in datasets if 'QCD_Pt' in dataset],
                            r'BTagMu': [ idata for idata in datasets if args.data in idata ],
                        }
                        datasets = mapping.keys()
                        datasets_data  = [dataset for dataset in datasets if args.data in dataset]
                        datasets_QCD = [dataset for dataset in datasets if ((args.data not in dataset) & ('GluGlu' not in dataset))]
                        
                        h = h.group("dataset", hist.Cat("dataset", "Dataset"), mapping)

                        #### rescaling QCD to data
                        dataSum = np.sum( h[args.data].sum('flavor').values()[('BTagMu',)] )
                        QCDSum = np.sum( h[datasets_QCD].sum('dataset', 'flavor').values()[()] )
                        QCD_rescaled = h[datasets_QCD].sum('dataset')
                        QCD_rescaled.scale( dataSum/QCDSum )

                        #### storing into dict
                        for iflav in QCD_rescaled.values():
                            tmpValue, sumw2 = QCD_rescaled[iflav].sum('flavor').values(sumw2=True)[()]
                            #outputDict[ histname+'_QCD_'+iflav[0] ] = np.array( value )
                            outputDict[ histname+'_QCD_'+iflav[0] ] = [ tmpValue, sumw2  ]
                        tmpValue, sumw2 = h[args.data].sum('flavor').values(sumw2=True)[('BTagMu',)]
                        outputDict[ histname+'_BtagMu' ] = [ tmpValue, sumw2 ]

#### Saving into pickle
output_dir = args.outputDir if args.outputDir else os.getcwd()+"/histograms/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
#outputFileName = output_dir + ( args.output if args.output else args.input.split('/')[-1].replace('coffea7', 'pkl')  )
outputFileName = output_dir + ( args.output if args.output else args.input.split('/')[-1].replace(args.input.split('.')[-1], 'pkl')  )
outputFile = open( outputFileName, 'wb'  )
pickle.dump( outputDict, outputFile, protocol=2 )
outputFile.close()

