from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.parameters.btag import btag_variations
from pocket_coffea.lib.weights_manager import WeightCustom
from config.fatjet_base.custom.cuts import mutag_presel, get_ptbin, get_ptmsd, get_nObj_minmsd, get_flavor
from config.fatjet_base.custom.functions import get_inclusive_wp, get_HLTsel
import numpy as np

from parameters import PtBinning, AK8TaggerWP
PtBinning = PtBinning['UL']['2018']
wp = AK8TaggerWP['UL']['2018']


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
            "year": ['2018']
        },
        "subsamples": subsamples
    },
    

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/test/flavorsplit",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "futures",
        "workers"        : 16,
        "scaleout"       : 125,
        "queue"          : "standard",
        "walltime"       : "8:00:00",
        "mem_per_worker" : "4GB", # GB
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
    "categories": {
        "inclusive" : [passthrough],
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt350msd60" : [get_ptmsd(350., 60.)],
        "pt350msd100" : [get_ptmsd(350., 100.)],

        ## Inclusive pt categories
        # btagDDCvLV2
        "msd40btagDDCvLV2passLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'pass')],
        "msd40btagDDCvLV2passMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'pass')],
        "msd40btagDDCvLV2passHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'pass')],

        "msd40btagDDCvLV2failLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'fail')],
        "msd40btagDDCvLV2failMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'fail')],
        "msd40btagDDCvLV2failHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'fail')],

        # btagDDBvLV2
        "msd40btagDDBvLV2passLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],
        "msd40btagDDBvLV2passMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],
        "msd40btagDDBvLV2passHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],

        "msd40btagDDBvLV2failLwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],
        "msd40btagDDBvLV2failMwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],
        "msd40btagDDBvLV2failHwpPt-400toInf" : [get_ptmsd(350., 40.), get_ptbin(400, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],

        ## Pt binning split + WPs + pass/fail
        # btagDDCvLV2
        "msd40btagDDCvLV2passLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'pass')],
        "msd40btagDDCvLV2passLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'pass')],
        "msd40btagDDCvLV2passLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'pass')],
        "msd40btagDDCvLV2passLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'pass')],

        "msd40btagDDCvLV2failLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'fail')],
        "msd40btagDDCvLV2failLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'fail')],
        "msd40btagDDCvLV2failLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'fail')],
        "msd40btagDDCvLV2failLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['L'], 'fail')],

        "msd40btagDDCvLV2passMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'pass')],
        "msd40btagDDCvLV2passMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'pass')],
        "msd40btagDDCvLV2passMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'pass')],
        "msd40btagDDCvLV2passMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'pass')],

        "msd40btagDDCvLV2failMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'fail')],
        "msd40btagDDCvLV2failMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'fail')],
        "msd40btagDDCvLV2failMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'fail')],
        "msd40btagDDCvLV2failMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['M'], 'fail')],

        "msd40btagDDCvLV2passHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'pass')],
        "msd40btagDDCvLV2passHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'pass')],
        "msd40btagDDCvLV2passHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'pass')],
        "msd40btagDDCvLV2passHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'pass')],

        "msd40btagDDCvLV2failHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'fail')],
        "msd40btagDDCvLV2failHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'fail')],
        "msd40btagDDCvLV2failHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'fail')],
        "msd40btagDDCvLV2failHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDCvLV2", wp["btagDDCvLV2"]['H'], 'fail')],

        # btagDDBvLV2
        "msd40btagDDBvLV2passLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],
        "msd40btagDDBvLV2passLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],
        "msd40btagDDBvLV2passLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],
        "msd40btagDDBvLV2passLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'pass')],

        "msd40btagDDBvLV2failLwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],
        "msd40btagDDBvLV2failLwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],
        "msd40btagDDBvLV2failLwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],
        "msd40btagDDBvLV2failLwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['L'], 'fail')],

        "msd40btagDDBvLV2passMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],
        "msd40btagDDBvLV2passMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],
        "msd40btagDDBvLV2passMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],
        "msd40btagDDBvLV2passMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'pass')],

        "msd40btagDDBvLV2failMwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],
        "msd40btagDDBvLV2failMwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],
        "msd40btagDDBvLV2failMwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],
        "msd40btagDDBvLV2failMwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['M'], 'fail')],

        "msd40btagDDBvLV2passHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],
        "msd40btagDDBvLV2passHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],
        "msd40btagDDBvLV2passHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],
        "msd40btagDDBvLV2passHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'pass')],

        "msd40btagDDBvLV2failHwpPt-400to600" : [get_ptmsd(350., 40.), get_ptbin(400, 600), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],
        "msd40btagDDBvLV2failHwpPt-600to800" : [get_ptmsd(350., 40.), get_ptbin(600, 800), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],
        "msd40btagDDBvLV2failHwpPt-600toInf" : [get_ptmsd(350., 40.), get_ptbin(600, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],
        "msd40btagDDBvLV2failHwpPt-800toInf" : [get_ptmsd(350., 40.), get_ptbin(800, 'Inf'), get_inclusive_wp("btagDDBvLV2", wp["btagDDBvLV2"]['H'], 'fail')],
    },

    

    "weights": {
        "common": {
            "inclusive": ["genWeight","lumi","XS",
                          "pileup"#, "sf_L1prefiring"
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
                "inclusive": [ "pileup"],#, "sf_L1prefiring" ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        
    },

   "variables":
    {
        #**muon_hists(coll="MuonGood"),
        #**muon_hists(coll="MuonGood", pos=0),
        #**jet_hists(coll="JetGood"),
        #**jet_hists(coll="JetGood", pos=0),
        **fatjet_hists(coll="FatJetGood"),
        **fatjet_hists(coll="FatJetGood", pos=0),
        **sv_hists(coll="events"),
        **sv_hists(coll="events", pos=0),
        #**count_hist(name="nElectronGood", coll="ElectronGood",bins=10, start=0, stop=10),
        #**count_hist(name="nMuonGood", coll="MuonGood",bins=10, start=0, stop=10),
        #**count_hist(name="nJets", coll="JetGood",bins=10, start=0, stop=10),
        #**count_hist(name="nFatJets", coll="FatJetGood",bins=10, start=0, stop=10),
        #**count_hist(name="nSV", coll="SV",bins=10, start=0, stop=10),
        #"nmusj1": HistConf(
        #    [ Axis(coll="events", field="nmusj1", label=r"$N_{\mu, SJ1}$", bins=10, start=0, stop=10) ]
        #),
        #"nmusj2": HistConf(
        #    [ Axis(coll="events", field="nmusj2", label=r"$N_{\mu, SJ2}$", bins=10, start=0, stop=10) ]
        #),
    },

    "columns" : {}

}
