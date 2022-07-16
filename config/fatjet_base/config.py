import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_ptmsdtau
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
            "samples": ["QCD_Pt-170to300", "QCD_Pt-300to470", "QCD_Pt-470to600", "QCD_Pt-600to800", "QCD_Pt-800to1000", "QCD_Pt-1000toInf", "DATA"],
            "samples_exclude" : [],
            "year": ["2018"]
        }
    },

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/fatjet_base/fatjet_base",

    # Executor parameters
    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
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
        "limit"          : None,
    },

    # Cuts and plots settings
    "finalstate" : "mutag",
    "skim" : [ get_nObj(1, 200., "FatJet"), get_nObj(2, 3., "Muon")],
    "preselections" : [mutag_presel],
    "categories": {
        "btagDDCvLV2_pass" : [get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        "btagDDCvLV2_fail" : [get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        "msd40tau06_btagDDCvLV2_pass" : [get_ptmsdtau(350., 40., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        "msd40tau06_btagDDCvLV2_fail" : [get_ptmsdtau(350., 40., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        "msd60tau06_btagDDCvLV2_pass" : [get_ptmsdtau(350., 60., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        "msd60tau06_btagDDCvLV2_fail" : [get_ptmsdtau(350., 60., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        "msd100tau06_btagDDCvLV2_pass" : [get_ptmsdtau(350., 100., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "pass")],
        "msd100tau06_btagDDCvLV2_fail" : [get_ptmsdtau(350., 100., 0.6), get_tagger_passfail(["btagDDCvLV2"], 0.45, "fail")],
        "msd40tau06" : [get_ptmsdtau(350., 40., 0.6)],
        "msd60tau06" : [get_ptmsdtau(350., 60., 0.6)],
        "msd100tau06" : [get_ptmsdtau(350., 100., 0.6)],
        "inclusive" : [passthrough],
    },

    "variables" : {
        "muon_pt" : None,
        "muon_eta" : None,
        "muon_phi" : None,
        "leadfatjet_pt" : None,
        "leadfatjet_eta" : None,
        "leadfatjet_phi" : None,
        "leadfatjet_msoftdrop" : None,
        "leadfatjet_tau21" : None,
        "leadfatjet_btagDDBvLV2" : None,
        "leadfatjet_btagDDCvLV2" : None,
        "leadfatjet_btagDDCvBV2" : None,
        "leadfatjet_particleNetMD_Xbb" : None,
        "leadfatjet_particleNetMD_Xcc" : None,
        "leadfatjet_particleNetMD_Xbb_QCD" : None,
        "leadfatjet_particleNetMD_Xcc_QCD" : None,
        "sv_summass" : None,
        "sv_logsummass" : None,
        "sv_projmass" : None,
        "sv_logprojmass" : None,
        "sv_sv1mass" : None,
        "sv_logsv1mass" : None,
        "sv_sumcorrmass" : None,
        "sv_logsumcorrmass" : None,
        "nmuon" : None,
        "nelectron" : None,
        "nlep" : None,
        "njet" : None,
        "nfatjet" : None,
        "nsv" : {'binning' : {'n_or_arr' : 20, 'lo' : 0, 'hi' : 20},    'xlim' : (0,20),   'xlabel' : "$N_{SV}$"},
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
