cfg =  {
    # Dataset parameters
    "dataset"  : "datasets/DAS/datasets_btag2016ULPreVFP.txt",
    "json"     : "datasets/datasets_btag2016ULPreVFP.json",
    "storage_prefix" : "/pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/BTVNanoCommissioning",
    "campaign" : "UL",
    "year"     : "2016",

    # Input and output files
    "workflow" : "fatjet_tagger",
    "input"    : "datasets/datasets_btag2016ULPreVFP_local.json",
    "output"   : "histograms/RunIISummer20UL16-PreVFP.coffea",
    "plots"    : "plots/test",

    # Executor parameters
    "run_options" : {
        "executor"     : "futures",
        "workers"      : 12,
        "scaleout"     : 10,
        "chunk"        : 50000,
        "max"          : None,
        "skipbadfiles" : None,
        "voms"         : None,
        "limit"        : 2,        
    },

    # Processor parameters
    "checkOverlap" : False,
    "hist2d"       : False,
}
