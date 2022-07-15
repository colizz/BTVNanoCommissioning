cfg =  {
    # Dataset parameters
    "dataset"  : "datasets/DAS/datasets_btag2018EOY.txt",
    "json"     : "datasets/RunIIAutumn18EOY18.json",
    "storage_prefix" : "/pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/BTVNanoCommissioning",
    "campaign" : "EOY",
    "year"     : "2018",

    # PU files
    "puFile"   : "correction_files/PileupHistogram-goldenJSON-13tev-2018-69200ub-99bins.root",
    "nTrueFile": "correction_files/nTrueInt_RunIIAutumn18EOY18_local_2018.coffea",

    # JEC
    "JECfolder": "correction_files/tmp",

    # Input and output files
    "workflow" : "fatjet_tagger_projmass",
    "input"    : "datasets/RunIIAutumn18EOY18_local.json",
    "output"   : "histograms/test_projmass_RunIIAutumn18EOY18_limit2.coffea",
    "plots"    : "plots/test_projmass_RunIIAutumn18EOY18_limit2",

    # Executor parameters
    "run_options" : {
        "executor"       : "futures",
        "workers"        : 8,
        "scaleout"       : 10,
        "partition"      : "standard",
        "walltime"       : "12:00:00",
        "mem_per_worker" : None, # GB
        "exclusive"      : True,
        "chunk"          : 50000,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : 2,
    },

    # Processor parameters
    "checkOverlap" : False,
    "hist2d"       : False,
    "mupt"         : 5,
}
