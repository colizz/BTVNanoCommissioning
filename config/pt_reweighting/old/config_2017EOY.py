import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_ptmsd
#from PocketCoffea.PocketCoffea.lib.cut_functions import get_nObj
from PocketCoffea.lib.cut_functions import get_nObj
from workflows.pt_reweighting_EOY import ptReweightProcessor
from math import pi
import numpy as np

cfg =  {

    "dataset" : {
        "jsons": ["datasets/MC_QCD_MuEnriched_EOY_local.json", "datasets/DATA_BTagMu_EOY_local.json", ],
        "filter" : {
            "samples": ["QCD_Pt-170to300", "QCD_Pt-300to470", "QCD_Pt-470to600", "QCD_Pt-600to800", "QCD_Pt-800to1000", "QCD_Pt-1000toInf", "DATA"],
            "samples_exclude" : [],
            "year": ["2017"]
        }
    },

    # Input and output files
    "workflow" : ptReweightProcessor,
    "output"   : "output/pt_reweighting/pt_reweighting_2017EOY_pt350",
    "output_reweighting" : "correction_files/pt_reweighting/pt_reweighting_2017EOY_pt350",
    "output_PUreweighting" : "correction_files/pu_reweighting/pu_reweighting_2017EOY",
    "nTrueFile"            : "correction_files/pu_reweighting/pu_reweighting_2017EOY/nTrueInt_2017.coffea",
    "JECfolder": "correction_files/tmp_2017",

    # Executor parameters
    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 125,
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
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt350msd60" : [get_ptmsd(350., 60.)],
        "pt350msd80" : [get_ptmsd(350., 80.)],
        "mspt350d100" : [get_ptmsd(350., 100.)],
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
