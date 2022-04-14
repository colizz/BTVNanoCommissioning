import argparse
from multiprocessing import Pool
import json
import uproot

parser = argparse.ArgumentParser(description='Plot histograms from FitDiagnostic file')
parser.add_argument('-i', '--input', type=str, help='Input JSON dataset file', required=True)
parser.add_argument('-o', '--output', type=str, default=None, help='Output JSON with broken files', required=False)

args = parser.parse_args()

dataset = json.load(open(args.input))

if args.output == None:
    args.output = args.input.replace('.json', '_broken.json')

dataset_broken = {}
dataset_broken = {}
for sample in dataset.keys():
    dataset_broken[sample] = {}
    for key, item in dataset[sample].items():
        if key == 'files':
            dataset_broken[sample][key] = []
        else:
            dataset_broken[sample][key] = item

def check_broken_files(sample):
    print("Processing", sample)

    for i, file in enumerate(dataset[sample]['files']):
        #dataset_broken[sample]['files'].append('aaaaa')
        try:
            uproot.open(file)
        except:
            print(file)
            dataset_broken[sample]['files'].append(file)
        #if i == 5: return len(dataset_broken[sample]['files']) > 0
    return {sample: dataset_broken[sample]}

samples = dataset.keys()
p = Pool()
dictionaries = p.map(check_broken_files, samples)

dataset_broken = {}
for d in dictionaries:
    dataset_broken.update(d)

with open(args.output, 'w') as f:
    json.dump(dataset_broken, f, indent=4)
