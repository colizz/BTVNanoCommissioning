from pocket_coffea.parameters.cuts.preselection_cuts import *
from pocket_coffea.workflows.genweights import genWeightsProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from config.fatjet_base.custom.cuts import mutag_presel, get_nObj_minmsd
from config.fatjet_base.custom.functions import get_inclusive_wp, get_HLTsel
import numpy as np

samples = [ "VJets" ]

cfg =  {
    "dataset" : {
        "jsons": ["datasets/MC_VJets_RunIISummer20UL_redirector.json"],
        "filter" : {
            "samples": samples,
            "samples_exclude" : [],
            "year": ['2017']
        }
    },

    # Input and output files
    "workflow" : genWeightsProcessor,
    "output"   : "output/pocket_coffea/VJets/VJets_2017UL_skim",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 150,
        "queue"          : "standard",
        "walltime"       : "8:00:00",
        "mem_per_worker" : "12GB", # GB
        "exclusive"      : False,
        "chunk"          : 200000,
        "retries"        : 50,
        "treereduction"  : 20,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : None,
        "adapt"          : False,
        "env"            : "conda"
    },


    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim": [get_nObj_min(1, 200., "FatJet"),
             get_nObj_minmsd(1, 30., "FatJet"),
             get_nObj_min(2, 3., "Muon"),
             get_HLTsel("mutag")],

    "save_skimmed_files": 'root://t3dcachedb03.psi.ch:1094//pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/BTVNanoCommissioning/skim/skim_2017_chunk200k/',
    
    "preselections" : [mutag_presel],
    "categories": {
        "inclusive" : [passthrough]
    },

    "weights": {
        "common": {
            "inclusive": [ ],
            "bycategory" : {
            }
        },
        "bysample": {
        }
    },

    "variations": {
        "weights": {
            "common": {
                "inclusive": [  ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        "shape": {
            "common":{
                "inclusive": [  ]
            }
        }
    },

   "variables": {},

    "columns" : {}

}
