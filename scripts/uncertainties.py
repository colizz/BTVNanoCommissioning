import argparse
import numpy as np
import uproot

parser = argparse.ArgumentParser(description='Extract uncertainty from combine output file')
parser.add_argument('-i', '--input', type=str, help='Input histogram filename', required=True)

args = parser.parse_args()

f = uproot.open(args.input)

covar = f["shapes_fit_s/sfpass/total_covar"]

print(covar)
