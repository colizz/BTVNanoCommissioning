#!/usr/bin/env python
import argparse, os, shutil, sys
import numpy as np
import uproot
import coffea.hist as hist
from coffea.util import save
import concurrent.futures
import json, psutil

# Include PocketCoffea to python paths (needed if running from outside PocketCoffea)
PATH_TO_SCRIPT = '/'.join(sys.argv[0].split('/')[:-1])
PATH_TO_MODULE = os.path.abspath(os.path.join(os.path.abspath(PATH_TO_SCRIPT), "PocketCoffea"))
if not PATH_TO_MODULE in sys.path:
    sys.path.append(PATH_TO_MODULE)

from PocketCoffea.utils.Configurator import Configurator

#####################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', default=os.getcwd() + "/config/test.py", required=True, type=str,
                        help='Config file with parameters specific to the current run')
    #parser.add_argument('--samples', '--json', dest='samplejson', default='dummy_samples.json', help='JSON file containing dataset and file locations (default: %(default)s)')
    parser.add_argument('--year', type=int, choices=[2016, 2017, 2018], help='Year of data/MC samples', required=True)
    parser.add_argument('--only', type=str, default=None, help='Only process specific sample or file')
    parser.add_argument('--outputDir', type=str, default=None, help='Output directory')
    parser.add_argument('--outputName', type=str, default=None, help='Output directory')

    try: args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    print("Running with options:")
    print("    ", args)

    if args.cfg[-3:] == ".py":
        config = Configurator(args.cfg)
    elif args.cfg[-4:] == ".pkl":
        config = pickle.load(open(args.cfg,"rb"))
    else:
        raise sys.exit("Please provide a .py/.pkl configuration file")

    # load dataset
    #with open(args.samplejson) as f:
    #    sample_dict = json.load(f)

    sample_dict = config.fileset

    # For debugging
    if args.only is not None:
        if args.only in sample_dict.keys():  # is dataset
            sample_dict = dict([(args.only, sample_dict[args.only])])
        if "*" in args.only: # wildcard for datasets
            _new_dict = {}
            print("Will only proces the following samples:")
            for k, v in sample_dict.items():
                if k.lstrip("/").startswith(args.only.rstrip("*")):
                    print("    ", k)
                    _new_dict[k] = v
            sample_dict = _new_dict
        else:  # is file
            for key in sample_dict.keys():
                if args.only in sample_dict[key]:
                    sample_dict = dict([(key, [args.only])])

    if len(sample_dict)==0: print ('No sample found. \n Have a nice day :)')

    puHisto = hist.Hist( 'nTrueInt', hist.Cat('sample', 'Sample'), hist.Bin('x', 'nTrueInt', 99, 0, 99) )

    for isample in sample_dict:
        print(f'processing {isample}')
        if isample.startswith('DATA'): continue
        if isinstance(sample_dict[isample], dict):
            ifiles = sample_dict[isample]['files']
        elif isinstance(sample_dict[isample], list):
            ifiles = sample_dict[isample]
        else:
            raise NotImplemented
        if not ifiles:
            print('|--------> Sample '+isample+' does not have files to process')
            continue
        filesToProcess = { k:'Events' for k in ifiles[:10] }
        for array in uproot.iterate([filesToProcess], ['Pileup_nTrueInt']): #, executor=executor):
            puHisto.fill(sample=sample_dict[isample]['metadata']['sample'], x=array['Pileup_nTrueInt'])

    #outFolder = os.path.join(os.getcwd(), '/correction_files/nTrueForPU') if args.outputDir is None else args.outputDir
    outFolder = config.output_PUreweighting
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    outName = os.path.join( outFolder, ( args.outputName if args.outputName else f'nTrueInt_{args.year}.coffea' ) )
    save( puHisto, outName )

    print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

