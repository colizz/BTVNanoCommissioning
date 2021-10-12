import numpy as np

lumi = {
    2016 : 35.5,
    2017 : 41.5,
    2018 : 59.2,
}

# Cross-sections in pb
xsecs = {
    #"QCD_Pt-15to20_MuEnrichedPt5"    : 2799000.0,
    #"QCD_Pt-20to30_MuEnrichedPt5"    : 2526000.0,
    #"QCD_Pt-30to50_MuEnrichedPt5"    : 1362000.0,
    #"QCD_Pt-50to80_MuEnrichedPt5"    : 376600.0,
    #"QCD_Pt-80to120_MuEnrichedPt5"   : 88930.0,
    "QCD_Pt-120to170_MuEnrichedPt5"  : 21230.0,
    "QCD_Pt-170to300_MuEnrichedPt5"  : 7055.0,
    "QCD_Pt-300to470_MuEnrichedPt5"  : 619.3,
    "QCD_Pt-470to600_MuEnrichedPt5"  : 59.24,
    "QCD_Pt-600to800_MuEnrichedPt5"  : 18.21,
    "QCD_Pt-800to1000_MuEnrichedPt5" : 3.275,
    "QCD_Pt-1000toInf_MuEnrichedPt5" : 1.078,
    "QCD_Pt-120to170_MuEnrichedPt5_TuneCP5_13TeV_pythia8"  : 21230.0,
    "QCD_Pt-170to300_MuEnrichedPt5_TuneCP5_13TeV_pythia8"  : 7055.0,
    "QCD_Pt-300to470_MuEnrichedPt5_TuneCP5_13TeV_pythia8"  : 619.3,
    "QCD_Pt-470to600_MuEnrichedPt5_TuneCP5_13TeV_pythia8"  : 59.24,
    "QCD_Pt-600to800_MuEnrichedPt5_TuneCP5_13TeV_pythia8"  : 18.21,
    "QCD_Pt-800to1000_MuEnrichedPt5_TuneCP5_13TeV_pythia8" : 3.275,
    "QCD_Pt-1000toInf_MuEnrichedPt5_TuneCP5_13TeV_pythia8" : 1.078,

    "QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 25700.0,
    "QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 8683.0,
    "QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 800.9,
    "QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 79.25,
    "QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 25.25,
    "QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 4.723,
    "QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8" : 1.613,

    "GluGluHToBB_M-125_13TeV"  : 27.8,
    "GluGluHToCC_M-125_13TeV"  : 27.8,
    "GluGluHToBB_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8"  : 27.8,
    "GluGluHToCC_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8"  : 27.8,
}

JECversions = {
        'EOY': {
            '2016' : {
                'MC' : 'Summer16_07Aug2017_V11_MC',
                'Data' : {
                    'B' : 'Summer16_07Aug2017BCD_V11_DATA',
                    'C' : 'Summer16_07Aug2017BCD_V11_DATA',
                    'D' : 'Summer16_07Aug2017BCD_V11_DATA',
                    'E' : 'Summer16_07Aug2017EF_V11_DATA',
                    'F' : 'Summer16_07Aug2017EF_V11_DATA',
                    'G' : 'Summer16_07Aug2017GH_V11_DATA',
                    'H' : 'Summer16_07Aug2017GH_V11_DATA'
                    }
                },
            '2017' : {
                'MC' : 'Fall17_17Nov2017_V32_MC',
                'Data' : {
                    'B' : 'Fall17_17Nov2017B_V32_DATA',
                    'C' : 'Fall17_17Nov2017C_V32_DATA',
                    'D' : 'Fall17_17Nov2017DE_V32_DATA',
                    'E' : 'Fall17_17Nov2017DE_V32_DATA',
                    'F' : 'Fall17_17Nov2017F_V32_DATA'
                    }
                },
            '2018' : {
                'MC' : 'Autumn18_V19_MC',
                'Data' : {
                    'A' : 'Autumn18_RunA_V19_DATA',
                    'B' : 'Autumn18_RunB_V19_DATA',
                    'C' : 'Autumn18_RunC_V19_DATA',
                    'D' : 'Autumn18_RunD_V19_DATA'
                    }
                }
            },
        'UL': {
            '2017' : {
                'MC' : 'Summer19UL17_V5_MC',
                'Data' : {
                    'B' : 'Summer19UL17_RunB_V5_DATA',
                    'C' : 'Summer19UL17_RunC_V5_DATA',
                    'D' : 'Summer19UL17_RunD_V5_DATA',
                    'E' : 'Summer19UL17_RunE_V5_DATA',
                    'F' : 'Summer19UL17_RunF_V5_DATA'
                    }
                },
            '2018' : {
                'MC' : 'Summer19UL18_V5_MC',
                'Data' : {
                    'A' : 'Summer19UL18_RunA_V5_DATA',
                    'B' : 'Summer19UL18_RunB_V5_DATA',
                    'C' : 'Summer19UL18_RunC_V5_DATA',
                    'D' : 'Summer19UL18_RunD_V5_DATA',
                    }
                }
            },


        }

#logsv1mass_bins = np.concatenate( ( (-4, -3.6, -3.2, -2.8, -2.4, -2, -1.59, -1.2, -0.8, -0.4), np.arange(0., 1.8, 0.1), (1.8, 2.5, 3.2) ) )

histogram_settings = {
    'variables' : {
        'fatjet_pt'    : {'binning' : {'n_or_arr' : 40,  'lo' : 0,      'hi' : 2000},  'xlim' : {'xmin' : 0,      'xmax' : 2000}},
        'fatjet_eta'   : {'binning' : {'n_or_arr' : 30,  'lo' : -3,     'hi' : 3},     'xlim' : {'xmin' : -2.4,   'xmax' : 2.4}},
        'fatjet_phi'   : {'binning' : {'n_or_arr' : 30,  'lo' : -np.pi, 'hi' : np.pi}, 'xlim' : {'xmin' : -np.pi, 'xmax' : np.pi}},
        #'fatjet_phi'   : {'binning' : {'n_or_arr' : 30,  'lo' : -3,     'hi' : 3},     'xlim' : {'xmin' : -3, 'xmax' : 3}},
        'fatjet_mass'  : {'binning' : {'n_or_arr' : 20,  'lo' : 0,      'hi' : 400},   'xlim' : {'xmin' : 0, 'xmax' : 400}},
        'fatjet_btagDDBvLV2'  : {'binning' : {'n_or_arr' : 20,  'lo' : 0,      'hi' : 1},     'xlim' : {'xmin' : 0, 'xmax' : 1}},
        'fatjet_btagDDCvLV2'  : {'binning' : {'n_or_arr' : 20,  'lo' : 0,      'hi' : 1},     'xlim' : {'xmin' : 0, 'xmax' : 1}},
        'fatjet_btagDDCvBV2'  : {'binning' : {'n_or_arr' : 20,  'lo' : 0,      'hi' : 1},     'xlim' : {'xmin' : 0, 'xmax' : 1}},
        'fatjet_nsv1'         : {'binning' : {'n_or_arr' : 30,  'lo' : 0,      'hi' : 30},    'xlim' : {'xmin' : 0, 'xmax' : 10}},
        'fatjet_nsv2'         : {'binning' : {'n_or_arr' : 30,  'lo' : 0,      'hi' : 30},    'xlim' : {'xmin' : 0, 'xmax' : 10}},
        'fatjet_nmusj1'       : {'binning' : {'n_or_arr' : 30,  'lo' : 0,      'hi' : 30},    'xlim' : {'xmin' : 0, 'xmax' : 10}},
        'fatjet_nmusj2'       : {'binning' : {'n_or_arr' : 30,  'lo' : 0,      'hi' : 30},    'xlim' : {'xmin' : 0, 'xmax' : 10}},
        'fatjet_jetproba'     : {'binning' : {'n_or_arr' : 25,  'lo' : 0,      'hi' : 2.5},   'xlim' : {'xmin' : 0, 'xmax' : 2.5}},
        'sv_sv1mass'          : {'binning' : {'n_or_arr' : 50,  'lo' : 0,      'hi' : 50},    'xlim' : {'xmin' : 0, 'xmax' : 50}},
        'sv_logsv1mass'       : {'binning' : {'n_or_arr' : 80,  'lo' : -4,     'hi' : 4},     'xlim' : {'xmin' : -0.8, 'xmax' : 3.2}},
        #'sv_logsv1mass'       : {'binning' : {'n_or_arr' : 40,  'lo' : -4,     'hi' : 4},     'xlim' : {'xmin' : -0.8, 'xmax' : 3.2}},
        #'sv_logsv1mass'       : {'binning' : {'n_or_arr' : 20,  'lo' : -4,     'hi' : 4},     'xlim' : {'xmin' : -0.8, 'xmax' : 3.2}},
        #'sv_logsv1mass'       : {'binning' : {'n_or_arr' : np.concatenate((np.arange(-4,1.9,0.1), [2.5,3.2]))},     'xlim' : {'xmin' : -0.8, 'xmax' : 3.2}},
    },
    'postfit' : {
        'sv_logsv1mass'       : {'binning' : {'n_or_arr' : np.concatenate((np.arange(-4,1.9,0.1), [2.5,3.2]))},     'xlim' : {'xmin' : -0.8, 'xmax' : 3.2}},
    }
}

#sample_names = ['bb', 'cc', 'b', 'c', 'l']
sample_names = ['c_cc', 'b_bb', 'l']

fit_parameters = {
    'EOYpt500': {
        '2016': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        },
        '2017': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        },
        '2018': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        }
    },
    'EOYpt450': {
        '2016': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 10}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        },
        '2017': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 10}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -50, 'hi' : 50}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        },
        '2018': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 10}, 'b_bb': {'value' : 1, 'lo' : 0, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        }
    },
    'UL': {
        #'2016': {
        #    'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
        #    'DDC': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        #},
        #'2017': {
        #    'DDB': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
        #    'DDC': {'c_cc': {'value' : 1, 'lo' : 0, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : 0, 'hi' : 2}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        #},
        '2018': {
            'DDB': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}},
            'DDC': {'c_cc': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'b_bb': {'value' : 1, 'lo' : -20, 'hi' : 20}, 'l': {'value' : 1, 'lo' : 0, 'hi' : 2}}
        }
    }
}
