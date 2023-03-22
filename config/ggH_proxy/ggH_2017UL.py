from pocket_coffea.parameters.cuts.preselection_cuts import *
from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.lib.cut_functions import get_nObj_min
from pocket_coffea.parameters.histograms import *
from pocket_coffea.lib.categorization import StandardSelection, CartesianSelection
from config.fatjet_base.custom.cuts import twojets_presel, mutag_sel, get_ptmsd, get_nObj_minmsd, get_flavor
from config.fatjet_base.custom.functions import get_HLTsel

common_cats = {
    "inclusive" : [passthrough],
    "pt350msd40" : [get_ptmsd(350., 40.)],
    "pt450msd40" : [get_ptmsd(450., 40.)],
    "pt600msd40" : [get_ptmsd(600., 40.)],
    "pt800msd40" : [get_ptmsd(800., 40.)],
    "pt350msd40_mutag" : [get_ptmsd(350., 40.), mutag_sel],
    "pt450msd40_mutag" : [get_ptmsd(450., 40.), mutag_sel],
    "pt600msd40_mutag" : [get_ptmsd(600., 40.), mutag_sel],
    "pt800msd40_mutag" : [get_ptmsd(800., 40.), mutag_sel],
}

samples = ["QCD_MuEnriched",
           "VJets",
           "GluGluHToBB",
           "GluGluHToCC",
           ]
subsamples = {}
for s in filter(lambda x: 'DATA' not in x, samples):
    subsamples[s] = {f"{s}_{f}" : [get_flavor(f)] for f in ['l', 'c', 'b', 'cc', 'bb']}

cfg =  {
    "dataset" : {
        "jsons": ["datasets/skim/datasets_definition_skim.json"],
        "filter" : {
            "samples": samples,
            "samples_exclude" : [],
            "year": ['2017']
        },
        "subsamples": subsamples
    },
    

    # Input and output files
    "workflow" : fatjetBaseProcessor,
    "output"   : "output/pocket_coffea/ggH_proxy/ggH_proxy_2017UL_VJets",
    "workflow_options" : {},

    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 250,
        "queue"          : "standard",
        "walltime"       : "12:00:00",
        "mem_per_worker" : "12GB", # GB
        "exclusive"      : False,
        "chunk"          : 100000,
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
    "preselections" : [twojets_presel],
    "categories": common_cats,

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
                "inclusive": [ ],#, "sf_L1prefiring" ],
                "bycategory" : {
                }
            },
        "bysample": {
        }    
        },
        "shape": {
            "common":{
                "inclusive": [ ]
            }
        }
    },

   "variables":
    {
        **muon_hists(coll="MuonGood", pos=0),
        **muon_hists(coll="MuonGood", pos=1),
        #**jet_hists(coll="JetGood"),
        #**jet_hists(coll="JetGood", pos=0),
        **fatjet_hists(coll="FatJetGood"),
        **fatjet_hists(coll="FatJetGood", pos=0),
        **fatjet_hists(coll="FatJetGood", pos=1),
        **sv_hists(coll="events"),
        **sv_hists(coll="events", pos=0),
        **sv_hists(coll="events", pos=1),
        #**count_hist(name="nElectronGood", coll="ElectronGood",bins=10, start=0, stop=10),
        **count_hist(name="nMuonGood", coll="MuonGood",bins=10, start=0, stop=10),
        #**count_hist(name="nJets", coll="JetGood",bins=10, start=0, stop=10),
        **count_hist(name="nFatJets", coll="FatJetGood",bins=10, start=0, stop=10),
        **count_hist(name="nSV", coll="SV",bins=10, start=0, stop=10),
        "nmusj_fatjet1": HistConf(
            [ Axis(coll="events", field="nmusj_fatjet1", label=r"$N_{\mu, J1}$", bins=10, start=0, stop=10) ]
        ),
        "nmusj_fatjet2": HistConf(
            [ Axis(coll="events", field="nmusj_fatjet2", label=r"$N_{\mu, J2}$", bins=10, start=0, stop=10) ]
        ),
    },

    "columns" : {}

}
