import sys
import argparse
from ROOT import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run analysis on baconbits files using processor coffea files')

    parser.add_argument( '-i', '--input', type=str, help='Input file', required=True)
    args = parser.parse_args()

    f = TFile(args.input)
    h = f.Get("shapes_fit_s/sfpass/b_bb")
    total_covar = f.Get("shapes_fit_s/sfpass/total_covar")
    for i in range(h.GetNbinsX()):
        print('Bin {}'.format(i), h.GetBinContent(i), ' +- ', h.GetBinError(i))
    #i = 0
    #while(1):
    #    try:
    #        print(total_covar.GetBinContent(i,i))
    #    except:
    #        sys.exit(1)
    #    i += 1
