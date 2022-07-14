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

    # pT reweighting
    "pt_reweighting": None,

    # Input and output files
    "workflow" : "pt_reweighting",
    "input"    : "datasets/RunIIAutumn18EOY18_local.json",
    "output"   : "histograms/pt_reweighting_2018.coffea",
    "plots"    : "plots/pt_reweighting_2018",
    "output_reweighting" : "correction_files/pt_reweighting/pt_reweighting_2018_v03",

    # Executor parameters
    "run_options" : {
        "executor"       : "dask/slurm",
        "workers"        : 1,
        "scaleout"       : 100,
        "partition"      : "short",
        "walltime"       : "1:00:00",
        "mem_per_worker" : "4GB", # GB
        "exclusive"      : False,
        "chunk"          : 50000,
        "max"            : None,
        "skipbadfiles"   : None,
        "voms"           : None,
        "limit"          : None,
    },

    # Processor parameters
    "checkOverlap" : False,
    "hist2d"       : False,
    "minimal"      : True,
    "mupt"         : 5,
}
