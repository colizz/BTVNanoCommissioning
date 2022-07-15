import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_msdtau
#from PocketCoffea.PocketCoffea.lib.cut_functions import get_nObj
from PocketCoffea.lib.cut_functions import get_nObj
from config.fatjet_base.functions import get_tagger_passfail
from workflows.fatjet_base import fatjetBaseProcessor
from math import pi
import numpy as np

cfg =  {

    "dataset" : {
        "jsons": ["datasets/MC_QCD_MuEnriched_local.json", "datasets/DATA_BTagMu_local.json", ],
        "filter" : {
            "samples": ["QCD_Pt-170to300", "QCD_Pt-300to470", "QCD_Pt-470to600", "QCD_Pt-600to800", "QCD_Pt-800to1000", "QCD_Pt-1000toInf"],
            "samples_exclude" : [],
            "year": ["2018"]
        }
    },

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/fatjet_base/fatjet_base",

    # Executor parameters
    "run_options" : {
        "executor"       : "futures",
        "workers"        : 16,
        "scaleout"       : 75,
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
        "limit"          : 2,
    },

    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim" : [ get_nObj(1, 200., "FatJet"), get_nObj(1, 3., "Muon")],
    "preselections" : [mutag_presel],
    "categories": {
        "btagDDCvLV2_pass" : [get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        "btagDDCvLV2_fail" : [get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        #"msd40tau06_btagDDCvLV2_pass" : [get_msdtau(40., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        #"msd40tau06_btagDDCvLV2_fail" : [get_msdtau(40., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        #"msd60tau06_btagDDCvLV2_pass" : [get_msdtau(60., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        #"msd60tau06_btagDDCvLV2_fail" : [get_msdtau(60., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        #"msd100tau06_btagDDCvLV2_pass" : [get_msdtau(100., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        #"msd100tau06_btagDDCvLV2_fail" : [get_msdtau(100., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        "inclusive" : [passthrough],
    },

    "variables" : {
        "muon_pt" : None,
        "muon_eta" : None,
        "muon_phi" : None,
        "leadfatjet_pt" : None,
        "leadfatjet_eta" : None,
        "leadfatjet_phi" : None,
        "leadfatjet_mass" : None,
        "leadfatjet_tau21" : None,
        "nmuon" : None,
        "nelectron" : None,
        "nlep" : None,
        "njet" : None,
        "nfatjet" : None,
    },
    "variables2d" : {},
    "plot_options" : {
        #"only" : "hist_electron_",
        "only" : None,
        "workers" : 16,
        "scale" : "log",
        "fontsize" : 18,
        "fontsize_map" : 10,
        "dpi" : 150,
        "rebin" : {
            'leading_fatjet_tau21' : {'binning' : {'n_or_arr' : 40, 'lo' : 0, 'hi' : 1}, 'xlim' : (0,1), 'xlabel' : r'FatJet $\tau_{21}$'},
        },
    }
}
