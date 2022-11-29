from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.parameters.btag import btag_variations
from pocket_coffea.lib.weights_manager import WeightCustom
from config.fatjet_base.custom.cuts import mutag_presel, get_ptbin, get_ptmsd, get_nObj_minmsd, get_flavor
from config.fatjet_base.custom.functions import get_inclusive_wp, get_HLTsel
import numpy as np

from parameters import PtBinning, AK8TaggerWP, AK8Taggers
PtBinning = PtBinning['UL']['2016_PostVFP']
wps = AK8TaggerWP['UL']['2016_PostVFP']

categories = {
    "inclusive" : [passthrough],
    "pt350msd40" : [get_ptmsd(350., 40.)],
    "pt350msd40_ptreweight" : [get_ptmsd(350., 40.)],
    "pt400msd40" : [get_ptmsd(400., 40.)],
    "pt400msd40_ptreweight" : [get_ptmsd(400., 40.)],
}

for tagger in AK8Taggers:
    for wp in ["L", "M", "H"]:
        for pt_low, pt_high in PtBinning.values():
            for region in ["pass", "fail"]:
                cat = f"msd40{tagger}{region}{wp}wpPt-{pt_low}to{pt_high}"
                categories.update({ cat : [
                                            get_ptmsd(350., 40.),
                                            get_ptbin(pt_low, pt_high),
                                            get_inclusive_wp(tagger, wps[tagger][wp], region)
                                            ]
                                    })
print("# categories =", len(categories.keys()))
for item in categories.keys():
    print(item)

categories_to_reweight = { cat : v for cat, v in categories.items() if cat not in ["inclusive", "pt350msd40", "pt400msd40"]}

samples = ["QCD_Pt-170to300",
           "QCD_Pt-300to470",
           "QCD_Pt-470to600",
           "QCD_Pt-600to800",
           "QCD_Pt-800to1000",
           "QCD_Pt-1000toInf",
           "DATA"]
subsamples = {}
for s in filter(lambda x: 'DATA' not in x, samples):
    subsamples[s] = {f"{s}_{f}" : [get_flavor(f)] for f in ['l', 'c', 'b', 'cc', 'bb']}

cfg =  {
    "dataset" : {
        "jsons": ["datasets/MC_QCD_MuEnriched_local.json",
                  "datasets/DATA_BTagMu_local.json"],
        "filter" : {
            "samples": samples,
            "samples_exclude" : [],
            "year": ['2016_PostVFP']
        },
        "subsamples": subsamples
    },
    

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/pocket_coffea/flavorsplit/flavorsplit_2016UL_PostVFP_shapes",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "futures",
        "workers"        : 16,
        "scaleout"       : 125,
        "queue"          : "standard",
        "walltime"       : "8:00:00",
        "mem_per_worker" : "6GB", # GB
        "exclusive"      : False,
        "chunk"          : 100000,
        "retries"        : 50,
        "treereduction"  : 10,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : None,
        "adapt"          : False,
    },

    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim": [get_nObj_min(1, 200., "FatJet"),
             # TO BE CHECKED
             get_nObj_minmsd(1, 30., "FatJet"),
             get_nObj_min(2, 3., "Muon"),
             get_HLTsel("mutag")],
    "preselections" : [mutag_presel],
    "categories": categories,

    "weights": {
        "common": {
            "inclusive": ["genWeight","lumi","XS",
                          "pileup", "sf_L1prefiring"
                          ],
            "bycategory" : { cat : ["pt_reweighting"] for cat in categories_to_reweight.keys()}
        },
        "bysample": {
        }
    },

    "variations": {
        "weights": {
            "common": {
                "inclusive": [ "pileup", "sf_L1prefiring" ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        "shape": {
            "common":{
                "inclusive": [ "JES_Total" ]
            }
        }
    },

   "variables":
    {
        **muon_hists(coll="MuonGood"),
        **muon_hists(coll="MuonGood", pos=0),
        **jet_hists(coll="JetGood"),
        **jet_hists(coll="JetGood", pos=0),
        **fatjet_hists(coll="FatJetGood"),
        **fatjet_hists(coll="FatJetGood", pos=0),
        **sv_hists(coll="events"),
        **sv_hists(coll="events", pos=0),
        **count_hist(name="nElectronGood", coll="ElectronGood",bins=10, start=0, stop=10),
        **count_hist(name="nMuonGood", coll="MuonGood",bins=10, start=0, stop=10),
        **count_hist(name="nJets", coll="JetGood",bins=10, start=0, stop=10),
        **count_hist(name="nFatJets", coll="FatJetGood",bins=10, start=0, stop=10),
        **count_hist(name="nSV", coll="SV",bins=10, start=0, stop=10),
        "nmusj_fatjet1": HistConf(
            [ Axis(coll="events", field="nmusj_fatjet1", label=r"$N_{\mu, J1}$", bins=10, start=0, stop=10) ]
        ),
        "nmusj_fatjet2": HistConf(
            [ Axis(coll="events", field="nmusj_fatjet2", label=r"$N_{\mu, J2}$", bins=10, start=0, stop=10) ]
        ),
    },

    "columns" : {}

}
