import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_ptmsd
#from PocketCoffea.PocketCoffea.lib.cut_functions import get_nObj
from PocketCoffea.lib.cut_functions import get_nObj
from config.fatjet_base.functions import get_tagger_pass, get_tagger_fail
from workflows.fatjet_base_EOY import fatjetEOYProcessor
from math import pi
import numpy as np

cfg =  {

    "dataset" : {
        "jsons": ["datasets/MC_QCD_MuEnriched_EOY_local.json", "datasets/DATA_BTagMu_EOY_local.json", ],
        "filter" : {
            "samples": ["QCD_Pt-170to300", "QCD_Pt-300to470", "QCD_Pt-470to600", "QCD_Pt-600to800", "QCD_Pt-800to1000", "QCD_Pt-1000toInf", "DATA"],
            "samples_exclude" : [],
            "year": ["2016"]
        }
    },

    # Input and output files
    "workflow" : fatjetEOYProcessor,
    "output"   : "output/fatjet_base/fatjet_base_2016EOY_pt350",
    # corrections
    "pt_reweighting" : "correction_files/pt_reweighting/pt_reweighting_2016EOY_pt350/pt_corr.coffea",
    "nTrueFile"      : "correction_files/pu_reweighting/pu_reweighting_2016EOY/nTrueInt_2016.coffea",
    "JECfolder"      : "correction_files/tmp_2016",

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
        "inclusive" : [passthrough],
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt350msd60" : [get_ptmsd(350., 60.)],
        "pt350msd100" : [get_ptmsd(350., 100.)],
        "btagDDCvLV2_pass" : [get_tagger_pass(["btagDDCvLV2"], 0.45)],
        "btagDDCvLV2_fail" : [get_tagger_fail(["btagDDCvLV2"], 0.45)],
        "btagDDBvLV2_pass" : [get_tagger_pass(["btagDDBvLV2"], 0.60)],
        "btagDDBvLV2_fail" : [get_tagger_fail(["btagDDBvLV2"], 0.60)],

        "pt350msd40_btagDDCvLV2_pass" : [get_ptmsd(350., 40.), get_tagger_pass(["btagDDCvLV2"], 0.45)],
        "pt350msd40_btagDDCvLV2_fail" : [get_ptmsd(350., 40.), get_tagger_fail(["btagDDCvLV2"], 0.45)],
        "pt350msd60_btagDDCvLV2_pass" : [get_ptmsd(350., 60.), get_tagger_pass(["btagDDCvLV2"], 0.45)],
        "pt350msd60_btagDDCvLV2_fail" : [get_ptmsd(350., 60.), get_tagger_fail(["btagDDCvLV2"], 0.45)],
        "pt350msd100_btagDDCvLV2_pass" : [get_ptmsd(350., 100.), get_tagger_pass(["btagDDCvLV2"], 0.45)],
        "pt350msd100_btagDDCvLV2_fail" : [get_ptmsd(350., 100.), get_tagger_fail(["btagDDCvLV2"], 0.45)],

        "pt350msd40_btagDDBvLV2_pass" : [get_ptmsd(350., 40.), get_tagger_pass(["btagDDBvLV2"], 0.60)],
        "pt350msd40_btagDDBvLV2_fail" : [get_ptmsd(350., 40.), get_tagger_fail(["btagDDBvLV2"], 0.60)],
        "pt350msd60_btagDDBvLV2_pass" : [get_ptmsd(350., 60.), get_tagger_pass(["btagDDBvLV2"], 0.60)],
        "pt350msd60_btagDDBvLV2_fail" : [get_ptmsd(350., 60.), get_tagger_fail(["btagDDBvLV2"], 0.60)],
        "pt350msd100_btagDDBvLV2_pass" : [get_ptmsd(350., 100.), get_tagger_pass(["btagDDBvLV2"], 0.60)],
        "pt350msd100_btagDDBvLV2_fail" : [get_ptmsd(350., 100.), get_tagger_fail(["btagDDBvLV2"], 0.60)],
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
        "sum_over" : ['cat', 'year', 'sample'],
        "only" : None,
        "workers" : 8,
        "scale" : None,
        "fontsize" : 18,
        "fontsize_map" : 10,
        "dpi" : 150,
        "rebin" : {
            'leadfatjet_pt'        : {'binning' : {'n_or_arr' : 20, 'lo' : 0, 'hi' : 1000}, 'xlim' : (0,1000), 'xlabel' : "FatJet $p_T$"},
            'leading_fatjet_tau21' : {'binning' : {'n_or_arr' : 40, 'lo' : 0, 'hi' : 1},    'xlim' : (0,1),    'xlabel' : r'FatJet $\tau_{21}$'},
            'sv_logsummass'        : {'binning' : {'n_or_arr' : 60, 'lo' : -6, 'hi' : 6},   'xlim' : (-2.5,6), 'xlabel' : r"FatJet log($\sum({m_{SV}})$) [GeV]"},
            'sv_logsv1mass'        : {'binning' : {'n_or_arr' : 60, 'lo' : -6, 'hi' : 6},   'xlim' : (-4,4),   'xlabel' : r"FatJet log($m_{SV,1}$/GeV)"},
            'sv_logprojmass'       : {'binning' : {'n_or_arr' : 60, 'lo' : -6, 'hi' : 6},   'xlim' : (-2.5,6), 'xlabel' : r"FatJet log($m_{SV}^{proj}$) [GeV]"},
            'sv_logsumcorrmass'    : {'binning' : {'n_or_arr' : 60, 'lo' : -6, 'hi' : 6},   'xlim' : (-2.5,6), 'xlabel' : r"FatJet log($\sum({m^{corr}_{SV}})$) [GeV]"},
        },
    }
}
