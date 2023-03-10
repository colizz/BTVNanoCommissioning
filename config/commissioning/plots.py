import numpy as np
from math import pi

cfg_plot = {
    "variables" : {
        "MuonGood_pt_1" : {'xlim' : (0, 200), 'scale' : "log"},
        "MuonGood_pt_2" : {'xlim' : (0, 200), 'scale' : "log"},
        "MuonGood_eta_1" : {'xlim' : (-2.4, 2.4), 'ylim' : 1.5},
        "MuonGood_eta_2" : {'xlim' : (-2.4, 2.4), 'ylim' : 1.5},
        "MuonGood_phi_1" : {'xlim' : (-pi, pi), 'ylim' : 1.5, 'binning' : np.linspace(-pi, pi, 33).tolist()},
        "MuonGood_phi_2" : {'xlim' : (-pi, pi), 'ylim' : 1.5, 'binning' : np.linspace(-pi, pi, 33).tolist()},

        "FatJetGood_pt_1" : {'xlim' : (350, 1000), 'ylim' : (1, 10**6), 'scale' : "log"},
        "FatJetGood_eta_1" : {'xlim' : (-2.4, 2.4), 'ylim' : 1.5},
        "FatJetGood_phi_1" : {'xlim' : (-pi, pi), 'ylim' : 1.5, 'binning' : np.linspace(-pi, pi, 33).tolist()},
        "FatJetGood_msoftdrop_1" : {'xlim' : (40, 300), 'ylim' : (1, 10**6), 'scale' : "log"},
        "FatJetGood_tau21_1" : {'xlim' : (0, 1), 'ylim' : 1.5},

        "FatJetGood_DDX_tau1_flightDistance2dSig_1" : {'xlim' : (0, 500), 'binning' : np.concatenate((np.arange(0, 200, 5), np.arange(200, 520, 20))).tolist(), 'scale' : "log"},
        "FatJetGood_DDX_tau2_flightDistance2dSig_1" : {'xlim' : (0, 500), 'binning' : np.concatenate((np.arange(0, 200, 5), np.arange(200, 520, 20))).tolist(), 'scale' : "log"},
        "FatJetGood_DDX_jetNTracks_1" : {'xlim' : (0, 50), 'ylim' : 1.3},
        "FatJetGood_DDX_jetNSecondaryVertices_1" : {'xlim' : (0, 10)},
        "FatJetGood_DDX_trackSip2dSigAboveBottom_0_1" : {'xlim' : (-1, 40), 'scale' : "log"},
        "FatJetGood_DDX_trackSip2dSigAboveBottom_1_1" : {'xlim' : (-1, 40), 'scale' : "log"},
        "FatJetGood_DDX_trackSip2dSigAboveCharm_1" : {'xlim' : (-1, 40), 'scale' : "log"},
        "FatJetGood_DDX_trackSip3dSig_0_1" : {'xlim' : (-5, 100), 'ylim' : (1, 10**6), 'scale' : "log"},
        "FatJetGood_DDX_trackSip3dSig_1_1" : {'xlim' : (-5, 100), 'ylim' : (1, 10**6), 'scale' : "log"},
        "FatJetGood_DDX_trackSip3dSig_2_1" : {'xlim' : (-5, 100), 'ylim' : (1, 10**6), 'scale' : "log"},
        "FatJetGood_DDX_trackSip3dSig_3_1" : {'xlim' : (-5, 100), 'ylim' : (1, 10**6), 'scale' : "log"},

        "events_logsumcorrmass_1" : {'xlim' : (-1.5, 5), 'ylim' : (0, 4000)},
        "events_logsv1mass_1" : {'xlim' : (-1.5, 4), 'ylim' : (0, 5000)},

        "nFatJets" : {'xlim' : (1, 8)},
        "nMuonGood" : {'xlim' : (2, 8)},
        "nmusj_fatjet1" : {'xlim' : (1, 6)}
    }
}

taggers_DDX = ["btagDDBvLV2", "btagDDCvLV2", "btagDDCvBV2", "btagDDBvL", "btagDDCvL", "btagDDCvB", "btagDDBvL_noMD", "btagDDCvL_noMD", "btagDDCvB_noMD"]
taggers_pNet = ['particleNetMD_Xbb_QCD', 'particleNetMD_Xcc_QCD', 'particleNetMD_Xbb', 'particleNetMD_Xcc',
                'particleNetMD_QCD', 'particleNetMD_Xqq', 'particleNet_H4qvsQCD', 'particleNet_HbbvsQCD',
                'particleNet_HccvsQCD', 'particleNet_QCD', 'particleNet_TvsQCD', 'particleNet_WvsQCD', 'particleNet_ZvsQCD']

for tagger in taggers_DDX + taggers_pNet:
    for label in ['', '_1']:
        cfg_plot[f"FatJetGood_{tagger}{label}"] = {}
        cfg_plot[f"FatJetGood_{tagger}{label}"]['xlim'] = (0,1)
        cfg_plot[f"FatJetGood_{tagger}{label}"]['ylim'] = (1,10**6)
        cfg_plot[f"FatJetGood_{tagger}{label}"]['scale'] = "log"
