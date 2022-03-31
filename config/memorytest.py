cfg =  {
    # Dataset parameters
    "dataset"  : "datasets/DAS/datasets_btag2016ULPreVFP.txt",
    "json"     : "datasets/RunIISummer20UL16-PreVFP.json",
    "storage_prefix" : "/pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/BTVNanoCommissioning",
    "campaign" : "UL",
    "year"     : "2016",

    # PU files
    "puFile"   : "correction_files/UltraLegacy/PileupHistogram-goldenJSON-13tev-2016-69200ub-99bins.root",
    "nTrueFile": "correction_files/nTrueInt_RunIISummer20UL16-PreVFP_local_2016.coffea",

    # JEC
    "JECfolder": "correction_files/tmp",

    # Input and output files
    "workflow" : "fatjet_tagger",
    "input"    : "datasets/RunIISummer20UL16-PreVFP_local.json",
    "output"   : "histograms/memorytest.coffea",
    "plots"    : "plots/test",

    # Executor parameters
    "run_options" : {
        "executor"     : "futures",
        "workers"      : 1,
        "scaleout"     : 50,
        "partition"    : "standard",
        "walltime"     : "4:00:00",
        "chunk"        : 5000,
        "max"          : None,
        "skipbadfiles" : None,
        "voms"         : None,
        "limit"        : 2,
    },

    # Processor parameters
    "checkOverlap" : False,
    "hist2d"       : False,
    "mupt"         : 5,
}
