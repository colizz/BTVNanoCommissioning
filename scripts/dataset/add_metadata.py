import json
import argparse
import numpy as np
from coffea.util import load

genweights_files = {
    "2018" : "/work/mmarcheg/BTVNanoCommissioning/output/pocket_coffea/VJets/VJets_2018UL_skim_v08/output_all.coffea",
    "2017" : "/work/mmarcheg/BTVNanoCommissioning/output/pocket_coffea/VJets/VJets_2017UL_skim_v01/output_all.coffea",
    "2016_PostVFP" : "/work/mmarcheg/BTVNanoCommissioning/output/pocket_coffea/VJets/VJets_2016UL_PostVFP_skim/output_all.coffea",
    "2016_PreVFP" : "/work/mmarcheg/BTVNanoCommissioning/output/pocket_coffea/VJets/VJets_2016UL_PreVFP_skim/output_all.coffea",
}

xsec_file = "/work/mmarcheg/BTVNanoCommissioning/datasets/datasets_definitions_RunIISummer20UL.json"

datasets_skimmed_files = {
    "2018" : "2018UL/skimmed_dataset_definition_VJets.json",
    "2017" : "2017UL/skimmed_dataset_definition_VJets.json",
    "2016_PostVFP" : "2016UL_PostVFP/skimmed_dataset_definition_VJets.json",
    "2016_PreVFP" : "2016UL_PreVFP/skimmed_dataset_definition_VJets.json",
}

parser = argparse.ArgumentParser(description='Append genweights and xsec to the datasets_definition_skim.json file where the skimmed datasets are defined.')
parser.add_argument(
    '--cfg',
    help='Config file with datasets parameters',
    required=True,
)

args = parser.parse_args()
dataset = json.load(open(args.cfg, 'r'))
output_dict = {}

for year, file in datasets_skimmed_files.items():
    dataset_skimmed = json.load(open(datasets_skimmed_files[year], 'r'))
    genweights_dict = load(genweights_files[year])['sum_genweights']
    xsec_dict = {f"{k}_{year}" : d["files"][0]["metadata"]["xsec"] for k, d in json.load(open(xsec_file, 'r')).items() if not k.startswith("DATA")}

    dataset.update(dataset_skimmed)

    dataset_DATA = {k : d for k,d in dataset.items() if k.startswith('DATA')}
    dataset_QCD  = {k : d for k,d in dataset.items() if k.startswith('QCD')}
    dataset_ggH  = {k : d for k,d in dataset.items() if k.startswith('GluGluH')}
    dataset_VJets  = {k : d for k,d in dataset.items() if (k.startswith('WJets') | k.startswith('ZJets'))}

    for k, d in dataset_DATA.items():
        era = k.split('Era')[-1]
        if not "metadata" in dataset_DATA[k]:
            dataset_DATA[k]["metadata"] = {
                                            "sample": "DATA",
                                            "year": year,
                                            "isMC": "False",
                                            "primaryDataset": "BTagMu",
                                            "era": era
                                            }

    for k, d in dataset_QCD.items():
        sample = k.split(f"_{year}")[0]
        if not "metadata" in dataset_QCD[k]:
            dataset_QCD[k]["metadata"] = {
                                            "sample": sample,
                                            "year": year,
                                            "isMC": "True",
                                            }
        if k in genweights_dict:
            dataset_QCD[k]["metadata"]["sum_genweights"] = np.float64(genweights_dict[k])
        if k in xsec_dict:
            dataset_QCD[k]["metadata"]["xsec"] = np.float64(xsec_dict[k])

    for k, d in dataset_VJets.items():
        if not "metadata" in dataset_VJets[k]:
            dataset_VJets[k]["metadata"] = {
                                            "sample": "VJets",
                                            "year": year,
                                            "isMC": "True",
                                            }
        if k in genweights_dict:
            dataset_VJets[k]["metadata"]["sum_genweights"] = np.float64(genweights_dict[k])
        if k in xsec_dict:
            dataset_VJets[k]["metadata"]["xsec"] = np.float64(xsec_dict[k])

    for k, d in dataset_ggH.items():
        sample = k.split(f"_{year}")[0]
        if not "metadata" in dataset_ggH[k]:
            dataset_ggH[k]["metadata"] = {
                                            "sample": sample,
                                            "year": year,
                                            "isMC": "True",
                                            }
        if k in genweights_dict:
            dataset_ggH[k]["metadata"]["sum_genweights"] = np.float64(genweights_dict[k])
        if k in xsec_dict:
            dataset_ggH[k]["metadata"]["xsec"] = np.float64(xsec_dict[k])

    for d in [dataset_DATA, dataset_QCD, dataset_VJets, dataset_ggH]:
        output_dict.update(d)

outfilename = f"skimmed_dataset_definition_with_metadata.json"
with open(outfilename, 'w') as f:
    json.dump(output_dict, f, indent=4)
