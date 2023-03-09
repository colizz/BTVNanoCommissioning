from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.pt_reweighting import ptReweightProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.parameters.btag import btag_variations
from pocket_coffea.lib.weights_manager import WeightCustom
from config.fatjet_base.custom.cuts import mutag_presel, get_ptbin, get_ptmsd, get_nObj_minmsd, get_flavor
from config.fatjet_base.custom.functions import get_inclusive_wp, get_HLTsel
import numpy as np

from parameters import PtBinning, AK8TaggerWP
PtBinning = PtBinning['UL']['2016_PreVFP']
wp = AK8TaggerWP['UL']['2016_PreVFP']


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
        "jsons": ["datasets/skim/datasets_definition_skim.json"],
        "filter" : {
            "samples": samples,
            "samples_exclude" : [],
            "year": ['2016_PreVFP']
        },
        "subsamples": subsamples
    },

    # Input and output files
    "workflow" : ptReweightProcessor,
    "output"   : "output/commissioning/pt_reweighting/pt_reweighting_2d_pt_eta_2016UL_PreVFP",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 100,
        "queue"          : "short",
        "walltime"       : "1:00:00",
        "mem_per_worker" : "2GB", # GB
        "exclusive"      : False,
        "chunk"          : 20000,
        "retries"        : 50,
        "treereduction"  : 10,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : None,
        "adapt"          : False,
        "env"            : "conda",
    },

    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim": [get_nObj_min(1, 200., "FatJet"),
             # TO BE CHECKED
             get_nObj_minmsd(1, 30., "FatJet"),
             get_nObj_min(2, 3., "Muon"),
             get_HLTsel("mutag")],
    "save_skimmed_files": None,
    "preselections" : [mutag_presel],
    "categories": {
        "inclusive" : [passthrough],
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt350msd60" : [get_ptmsd(350., 60.)],
        "pt350msd80" : [get_ptmsd(350., 80.)],
        "pt350msd100" : [get_ptmsd(350., 100.)],
    },

    "weights": {
        "common": {
            "inclusive": ["genWeight","lumi","XS",
                          "pileup", "sf_L1prefiring"
                          ],
            "bycategory" : {
            }
        },
        "bysample": {
        }
    },

    "variations": {
        "weights": {
            "common": {
                "inclusive": [ ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        "shape": {
            "common":{
                "inclusive": [ ]
            }
        }
    },

   "variables":
    {
        **fatjet_hists(coll="FatJetGood"),
        **fatjet_hists(coll="FatJetGood", pos=0),
        **sv_hists(coll="events"),
        **sv_hists(coll="events", pos=0),
        **count_hist(name="nFatJets", coll="FatJetGood",bins=10, start=0, stop=10),
        "FatJetGood_pt_1_FatJetGood_pt_2": HistConf(
            [ Axis(name="FatJetGood_pt_1", coll="FatJetGood", field="pt", pos=0, label=r"Leading FatJet $p_{T}$ [GeV]", bins=150, start=0, stop=1500),
              Axis(name="FatJetGood_pt_2", coll="FatJetGood", field="pt", pos=1, label=r"Subleading FatJet $p_{T}$ [GeV]", bins=75, start=0, stop=1500) ]
        ),
        "FatJetGood_pt_1_FatJetGood_eta_1": HistConf(
            [ Axis(name="FatJetGood_pt_1", coll="FatJetGood", field="pt", pos=0, label=r"Leading FatJet $p_{T}$ [GeV]", bins=150, start=0, stop=1500),
              Axis(name="FatJetGood_eta_1", coll="FatJetGood", field="eta", pos=0, label=r"Leading FatJet $\eta$", bins=40, start=-4, stop=4) ]
        ),
    },

    "columns" : {}

}
