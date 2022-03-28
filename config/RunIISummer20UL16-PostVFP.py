cfg =  {
    # Dataset parameters
    "dataset"  : "datasets/DAS/datasets_btag2016ULPostVFP.txt",
    "json"     : "datasets/RunIISummer20UL16-PostVFP.json",
    "storage_prefix" : "/pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/BTVNanoCommissioning",
    "campaign" : "UL",
    "year"     : "2016",

    # PU files
    "puFile"   : "correction_files/UltraLegacy/PileupHistogram-goldenJSON-13tev-2016-69200ub-99bins.root",
    "nTrueFile": "correction_files/nTrueInt_RunIISummer20UL16-PostVFP_local_2016.coffea",

    # JEC
    "JECfolder": "correction_files/tmp",

    # Input and output files
    "workflow" : "fatjet_tagger",
    "input"    : "datasets/RunIISummer20UL16-PostVFP_local.json",
    "output"   : "histograms/RunIISummer20UL16-PostVFP.coffea",
    "plots"    : "plots/test",

    # Executor parameters
    "run_options" : {
        "executor"     : "parsl/slurm",
        "workers"      : 12,
        "scaleout"     : 64,
        "partition"    : "short",
        "walltime"     : "45:00",
        "chunk"        : 50000,
        "max"          : None,
        "skipbadfiles" : None,
        "voms"         : None,
        "limit"        : None,
    },

    # Processor parameters
    "checkOverlap" : False,
    "hist2d"       : False,
    "mupt"         : 5,
}
