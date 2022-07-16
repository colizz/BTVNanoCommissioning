import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_ptmsdtau
#from PocketCoffea.PocketCoffea.lib.cut_functions import get_nObj
from PocketCoffea.lib.cut_functions import get_nObj
from config.fatjet_base.functions import get_tagger_passfail
from workflows.pt_reweighting import ptReweightProcessor
from math import pi
import numpy as np

cfg =  {

    "dataset" : {
        "jsons": ["datasets/MC_QCD_MuEnriched_local.json", "datasets/DATA_BTagMu_local.json", ],
        "filter" : {
            "samples": ["QCD_Pt-170to300", "QCD_Pt-300to470", "QCD_Pt-470to600", "QCD_Pt-600to800", "QCD_Pt-800to1000", "QCD_Pt-1000toInf", "DATA"],
            "samples_exclude" : [],
            "year": ["2017"]
        }
    },

    # Input and output files
    "workflow" : ptReweightProcessor,
    "output"   : "output/pt_reweighting/pt_reweighting_2017UL",
    "output_reweighting" : "correction_files/pt_reweighting/pt_reweighting_2017UL",

    # Executor parameters
    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 100,
        "partition"      : "standard",
        "walltime"       : "12:00:00",
        "mem_per_worker" : "5GB", # GB
        "exclusive"      : False,
        "chunk"          : 50000,
        "retries"        : 30,
        "treereduction"  : 10,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : None,
    },

    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim" : [ get_nObj(1, 200., "FatJet"), get_nObj(2, 3., "Muon")],
    "preselections" : [mutag_presel],
    "categories": {
        "msd40tau06" : [get_ptmsdtau(350., 40., 0.6)],
        "msd60tau06" : [get_ptmsdtau(350., 60., 0.6)],
        "msd80tau06" : [get_ptmsdtau(350., 80., 0.6)],
        "msd100tau06" : [get_ptmsdtau(350., 100., 0.6)],
        "inclusive" : [passthrough],
    },

    "variables" : {
        "leadfatjet_pt" : {'binning' : {'n_or_arr' : 100, 'lo' : 0, 'hi' : 1000}, 'xlim' : (0,1000), 'xlabel' : "FatJet $p_T$"},
        "leadfatjet_eta" : None,
        "leadfatjet_phi" : None,
        "leadfatjet_msoftdrop" : None,
        "leadfatjet_tau21" : None,
    },
    "variables2d" : {},
    "plot_options" : {
        #"only" : "hist_electron_",
        "only" : None,
        "workers" : 32,
        "scale" : None,
        "fontsize" : 18,
        "fontsize_map" : 10,
        "dpi" : 150,
        "rebin" : {
            'leading_fatjet_tau21' : {'binning' : {'n_or_arr' : 40, 'lo' : 0, 'hi' : 1}, 'xlim' : (0,1), 'xlabel' : r'FatJet $\tau_{21}$'},
        },
    }
}
