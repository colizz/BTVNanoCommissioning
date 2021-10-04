import argparse
import uproot
import json
import sys
import os

parser = argparse.ArgumentParser(description='Save json files without broken files')
parser.add_argument('-i', '--input', type=str, default='datasets_local.json', help='Input file with file list')
parser.add_argument('-o', '--output', type=str, default='datasets_fixed.json', help='Output file without broken files')
parser.add_argument('--outputDir', default='', help='Output directory')

args = parser.parse_args()

outDir = args.outputDir if args.outputDir else os.getcwd() + '/datasets/'
if not os.path.exists(outDir): os.makedirs(outDir)
outName = outDir + args.output

outputjson = {}
if ((not args.input.endswith(".json")) | (not args.output.endswith(".json"))):
	sys.exit("Only json files allowed as input/output.")
if (os.path.exists(args.output)):
	sys.exit(f"Output file {args.output} is already existing.")
files = None
with open(args.input) as f:
	files = json.load(f)
f.close()

nBroken = 0
for name in files.keys():
	outputjson[ name ] = []
	for ifile in files[ name ]:
		f = uproot.open(ifile)['Events'].keys()
		if len(f) > 10:
			outputjson[ name ].append( ifile )
		else:
			nBroken += 1

print(f'{nBroken} broken files found')
print(f'Saving file {args.output}')
with open(outName, 'w') as outFile:
	json.dump(outputjson, outFile, indent=4)
outFile.close()
