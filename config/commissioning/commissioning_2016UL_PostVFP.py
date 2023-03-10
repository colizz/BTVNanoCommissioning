from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.parameters.btag import btag_variations
from pocket_coffea.lib.weights_manager import WeightCustom
from pocket_coffea.lib.cartesian_categories import CartesianSelection, MultiCut
from pocket_coffea.parameters.custom.cuts import mutag_presel, get_ptbin, get_ptmsd, get_nObj_minmsd, get_flavor
from pocket_coffea.parameters.custom.functions import get_inclusive_wp, get_HLTsel
from config.commissioning.plots import cfg_plot
import numpy as np

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
            "year": ['2016_PostVFP']
        },
        "subsamples": subsamples
    },

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/commissioning/commissioning/2016UL_PostVFP",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 125,
        "queue"          : "standard",
        "walltime"       : "12:00:00",
        "mem_per_worker" : "12GB", # GB
        "exclusive"      : False,
        "chunk"          : 10000,
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
             get_nObj_minmsd(1, 30., "FatJet"),
             get_nObj_min(2, 3., "Muon"),
             get_HLTsel("mutag")],
    "save_skimmed_files" : None,
    "preselections" : [mutag_presel, get_ptmsd(250, 40)],
    "categories": {
        "inclusive" : [passthrough],
        "pt350msd40_noreweight" : [get_ptmsd(350., 40.)],
        "pt350msd40" : [get_ptmsd(350., 40.)],
        "pt450msd40_noreweight" : [get_ptmsd(450., 40.)],
        "pt450msd40" : [get_ptmsd(450., 40.)],
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
                "inclusive": [ "pileup", "sf_L1prefiring" ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        "shape": {
            "common":{
                "inclusive": [ "JES_Total", "JER" ]
            }
        }
    },

   "variables":
    {
        **muon_hists(coll="MuonGood", pos=0),
        **muon_hists(coll="MuonGood", pos=1),
        
        **fatjet_hists(coll="FatJetGood", pos=0),
        # Flight distance between PV and SV
        "FatJetGood_DDX_tau1_flightDistance2dSig_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_tau1_flightDistance2dSig", label="DDX_tau1_flightDistance2dSig", pos= 0,bins=100, start=0, stop=500) ]
        ),
        "FatJetGood_DDX_tau2_flightDistance2dSig_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_tau2_flightDistance2dSig", label="DDX_tau2_flightDistance2dSig", pos= 0, bins=100, start=0, stop=500) ]
        ),
        # Number of tracks associated with the fatjet
        "FatJetGood_DDX_jetNTracks_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_jetNTracks", label="DDX_jetNTracks", pos= 0, bins=50, start=0, stop=50) ]
        ),
        # Number of SVs
        "FatJetGood_DDX_jetNSecondaryVertices_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_jetNSecondaryVertices", label=r"$N_{SV}$", pos= 0, bins=10, start=0, stop=10) ]
        ),
        # Track 2D signed impact parameter significance
        "FatJetGood_DDX_trackSip2dSigAboveBottom_0_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip2dSigAboveBottom_0", label=r"DDX_trackSip2dSigAboveBottom_0", pos= 0, bins=100, start=-10, stop=90) ]
        ),
        "FatJetGood_DDX_trackSip2dSigAboveBottom_1_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip2dSigAboveBottom_1", label=r"DDX_trackSip2dSigAboveBottom_1", pos= 0, bins=100, start=-10, stop=90) ]
        ),
        "FatJetGood_DDX_trackSip2dSigAboveCharm_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip2dSigAboveCharm", label=r"DDX_trackSip2dSigAboveCharm", pos= 0, bins=100, start=-10, stop=90) ]
        ),
        # Track 3D signed impact parameter significance
        "FatJetGood_DDX_trackSip3dSig_0_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip3dSig_0", label=r"DDX_trackSip3dSig_0", pos= 0, bins=110, start=-50, stop=500) ]
        ),
        "FatJetGood_DDX_trackSip3dSig_1_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip3dSig_1", label=r"DDX_trackSip3dSig_1", pos= 0, bins=110, start=-50, stop=500) ]
        ),
        "FatJetGood_DDX_trackSip3dSig_2_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip3dSig_2", label=r"DDX_trackSip3dSig_2", pos= 0, bins=110, start=-50, stop=500) ]
        ),
        "FatJetGood_DDX_trackSip3dSig_3_1": HistConf(
            [ Axis(coll="FatJetGood", field="DDX_trackSip3dSig_3", label=r"DDX_trackSip3dSig_3", pos= 0, bins=110, start=-50, stop=500) ]
        ),
        #**sv_hists(coll="events"),
        **sv_hists(coll="events", pos=0),
        #**count_hist(name="nElectronGood", coll="ElectronGood",bins=10, start=0, stop=10),
        **count_hist(name="nMuonGood", coll="MuonGood",bins=10, start=0, stop=10),
        #**count_hist(name="nJets", coll="JetGood",bins=10, start=0, stop=10),
        **count_hist(name="nFatJets", coll="FatJetGood",bins=10, start=0, stop=10),
        **count_hist(name="nSV", coll="SV",bins=10, start=0, stop=10),
        "nmusj_fatjet1": HistConf(
            [ Axis(coll="events", field="nmusj_fatjet1", label=r"$N_{\mu, J1}$", bins=10, start=0, stop=10) ]
        ),
        #"nmusj_fatjet2": HistConf(
        #    [ Axis(coll="events", field="nmusj_fatjet2", label=r"$N_{\mu, J2}$", bins=10, start=0, stop=10) ]
        #),
    },

    "columns" : {},

    "plot_options" : cfg_plot,

}

# Note: in 2016UL samples there is no btagDDX branch (v1)
taggers_DDX = []#"btagDDBvL", "btagDDCvL", "btagDDCvB", "btagDDBvL_noMD", "btagDDCvL_noMD", "btagDDCvB_noMD"]
taggers_pNet = ['particleNetMD_QCD', 'particleNetMD_Xbb', 'particleNetMD_Xcc', 'particleNetMD_Xqq',
                'particleNet_H4qvsQCD', 'particleNet_HbbvsQCD', 'particleNet_HccvsQCD',
                'particleNet_QCD', 'particleNet_TvsQCD', 'particleNet_WvsQCD', 'particleNet_ZvsQCD']
for tagger in taggers_DDX + taggers_pNet:
    cfg["variables"][f"FatJetGood_{tagger}_1"] = HistConf( [ Axis(coll="FatJetGood", field=tagger, label=tagger, pos=0, bins=80, start=0, stop=1) ] )
# Here we update the weights dictionary such that 3 cross-check categories are not pt-reweighted
categories = cfg["categories"].keys()
categories_to_reweight = [ cat for cat in categories if cat not in ["inclusive", "pt350msd40_noreweight", "pt450msd40_noreweight"] ]
cfg["weights"]["common"]["bycategory"] = { cat : ["pteta_reweighting"] for cat in categories_to_reweight}
