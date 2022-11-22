import sys

import collections
import numpy as np
import awkward as ak

def get_nsv(sj, sv, R=0.4):

    # Compute the number of SV inside the subjet of the leading and subleading FatJet (nsv1, nsv2)
    # and return the concatenated array
    sv_dr1 = ak.pad_none(sj, 2)[:,0].delta_r(sv.p4)
    sv_dr2 = ak.pad_none(sj, 2)[:,1].delta_r(sv.p4)
    nsv1 = ak.unflatten( ak.count(sv_dr1[sv_dr1 < R], axis=1), counts=1 )
    nsv2 = ak.unflatten( ak.count(sv_dr2[sv_dr2 < R], axis=1), counts=1 )

    return ak.concatenate((nsv1, nsv2), axis=1)

def get_sv_in_jet(jet, sv, R=0.8):

    sv_dr = jet.delta_r(sv.p4)
    sv_in_jet = sv_dr < R

    return sv_in_jet

def get_nmu_in_subjet(sj, muon, R=0.4):

    # Compute the number of muons inside the subjet of the leading and subleading FatJet (nmusj1, nmusj2)
    # and return the concatenated array
    mu_dr1 = ak.pad_none(sj, 2)[:,0].delta_r(muon)
    mu_dr2 = ak.pad_none(sj, 2)[:,1].delta_r(muon)
    nmusj1 = ak.unflatten( ak.count(mu_dr1[mu_dr1 < R], axis=1), counts=1 )
    nmusj2 = ak.unflatten( ak.count(mu_dr2[mu_dr2 < R], axis=1), counts=1 )

    return ak.concatenate((nmusj1, nmusj2), axis=1)
