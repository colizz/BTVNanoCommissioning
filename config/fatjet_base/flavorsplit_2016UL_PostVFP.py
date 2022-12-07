from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.parameters.btag import btag_variations
from pocket_coffea.lib.weights_manager import WeightCustom
from pocket_coffea.lib.cartesian_categories import CartesianSelection, MultiCut
from pocket_coffea.parameters.custom.cuts import mutag_presel, get_ptbin, get_ptmsd, get_nObj_minmsd, get_flavor
from pocket_coffea.parameters.custom.functions import get_inclusive_wp, get_HLTsel
from pocket_coffea.parameters.custom.parameters import PtBinning, AK8TaggerWP, AK8Taggers
import numpy as np

PtBinning = PtBinning['UL']['2016_PostVFP']
wps = AK8TaggerWP['UL']['2016_PostVFP']

common_cats = {
    "inclusive" : passthrough,
    "pt350msd40" : get_ptmsd(350., 40.),
    "pt350msd40_ptreweight" : get_ptmsd(350., 40.),
    "pt450msd40" : get_ptmsd(450., 40.),
    "pt450msd40_ptreweight" : get_ptmsd(450., 40.),
}

cuts_pt = []
cuts_names_pt = []
for pt_low, pt_high in PtBinning.values():
    cuts_pt.append(get_ptbin(pt_low, pt_high))
    cuts_names_pt.append(f'Pt-{pt_low}to{pt_high}')
cuts_tagger = []
cuts_names_tagger = []
for tagger in AK8Taggers:
    for wp in ["L", "M", "H"]:
        for region in ["pass", "fail"]:
            cuts_tagger.append(get_inclusive_wp(tagger, wps[tagger][wp], region))
            cuts_names_tagger.append(f"msd40{tagger}{region}{wp}wp")

multicuts = [
    MultiCut(name="tagger",
             cuts=cuts_tagger,
             cuts_names=cuts_names_tagger),
    MultiCut(name="pt",
             cuts=cuts_pt,
             cuts_names=cuts_names_pt),
]

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
    "output"   : "output/pocket_coffea/templates/templates_2016UL_PostVFP",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 200,
        "queue"          : "short",
        "walltime"       : "1:00:00",
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
    "categories": CartesianSelection(multicuts=multicuts, common_cats=common_cats),

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
                "inclusive": [ "pileup" , "sf_L1prefiring" ],
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
        #**jet_hists(coll="JetGood"),
        #**jet_hists(coll="JetGood", pos=0),
        #**fatjet_hists(coll="FatJetGood"),
        **fatjet_hists(coll="FatJetGood", pos=0),
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

    "columns" : {}

}

# Here we update the weights dictionary such that 3 cross-check categories are not pt-reweighted
categories = cfg["categories"].categories
categories_to_reweight = [ cat for cat in categories if cat not in ["inclusive", "pt350msd40", "pt450msd40"] ]
cfg["weights"]["common"]["bycategory"] = { cat : ["pt_reweighting"] for cat in categories_to_reweight}
