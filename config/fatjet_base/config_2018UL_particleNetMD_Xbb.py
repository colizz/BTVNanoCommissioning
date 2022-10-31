import sys
#from PocketCoffea.PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from PocketCoffea.parameters.cuts.baseline_cuts import passthrough
from config.fatjet_base.custom_cuts import mutag_presel, get_ptbin, get_ptmsd
#from PocketCoffea.PocketCoffea.lib.cut_functions import get_nObj
from PocketCoffea.lib.cut_functions import get_nObj
from config.fatjet_base.functions import get_tagger_passfail, get_exclusive_wp
from workflows.fatjet_base import fatjetBaseProcessor
from math import pi
import numpy as np

from parameters import PtBinning, AK8TaggerWP
PtBinning = PtBinning['UL']['2018']
wp = AK8TaggerWP['UL']['2018']

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
    "output"   : "output/fatjet_base/fatjet_base_2018UL_particleNetMD_Xbb",
    # pT reweighting
    "pt_reweighting": "correction_files/pt_reweighting/pt_reweighting_2018UL_pt350/pt_corr.coffea",

    # Executor parameters
    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 175,
        "partition"      : "standard",
        "walltime"       : "12:00:00",
        "mem_per_worker" : "8GB", # GB
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
    "skim" : [ get_nObj(1, minpt=200., coll="FatJet"), get_nObj(1, minmsd=30., coll="FatJet"), get_nObj(2, minpt=3., coll="Muon")],
    "preselections" : [mutag_presel],
    "categories": {
        "inclusive" : [passthrough],
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt350msd60" : [get_ptmsd(350., 60.)],
        "pt350msd100" : [get_ptmsd(350., 100.)],

        ## Inclusive pt categories
        # particleNetMD_Xbb_QCD
        "msd40particleNetMD_Xbb_QCDpassLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],

        "msd40particleNetMD_Xbb_QCDfailLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_exclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],

        ## Pt binning split + WPs + pass/fail
        # particleNetMD_Xbb_QCD
        "msd40particleNetMD_Xbb_QCDpassLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'pass')],

        "msd40particleNetMD_Xbb_QCDfailLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['L'], 'fail')],

        "msd40particleNetMD_Xbb_QCDpassMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'pass')],

        "msd40particleNetMD_Xbb_QCDfailMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['M'], 'fail')],

        "msd40particleNetMD_Xbb_QCDpassHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'pass')],
        "msd40particleNetMD_Xbb_QCDpassHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'pass')],

        "msd40particleNetMD_Xbb_QCDfailHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'fail')],
        "msd40particleNetMD_Xbb_QCDfailHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_exclusive_wp("particleNetMD_Xbb_QCD", wp["particleNetMD_Xbb_QCD"]['H'], 'fail')],
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
        #"sum_over" : ['cat', 'year', 'flavor'],
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
        }
    },
    "sf_options" : {
        "parameters" : None,
        "merge_x_xx" : True,
        "categories" : {"filter" : ["msd40particleNetMD_Xbb"]},
        "rebin" : {
            'sv_logsummass'        : {'binning' : {'n_or_arr' : 30, 'lo' : -6, 'hi' : 6},   'xlim' : (-2.5,6), 'xlabel' : r"FatJet log($\sum({m_{SV}})$) [GeV]"},
            'sv_logsv1mass'        : {'binning' : {'n_or_arr' : 30, 'lo' : -6, 'hi' : 6},   'xlim' : (-4,4),   'xlabel' : r"FatJet log($m_{SV,1}$/GeV)"},
            'sv_logprojmass'       : {'binning' : {'n_or_arr' : 30, 'lo' : -6, 'hi' : 6},   'xlim' : (-2.5,6), 'xlabel' : r"FatJet log($m_{SV}^{proj}$) [GeV]"},
            'sv_logsumcorrmass'    : {'binning' : {'n_or_arr' : 30, 'lo' : -6, 'hi' : 6},   'xlim' : (-1.2,4.8), 'xlabel' : r"FatJet log($\sum({m^{corr}_{SV}})$) [GeV]"},
        }
    }
}
