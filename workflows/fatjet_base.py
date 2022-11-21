import numpy as np
import awkward as ak

from pocket_coffea.workflows.base import BaseProcessorABC
from pocket_coffea.utils.configurator import Configurator

from pocket_coffea.parameters.jec import JECversions, JERversions
from pocket_coffea.lib.objects import (
    jet_correction,
    lepton_selection,
    jet_selection,
    btagging,
    get_dilepton,
)
from config.fatjet_base.custom.leptons import lepton_selection_noniso
from lib.sv import get_nsv, get_sv_in_jet, get_nmu_in_subjet
from pocket_coffea.lib.hist_manager import HistManager, Axis, HistConf


class fatjetBaseProcessor(BaseProcessorABC):
    def __init__(self, cfg: Configurator):
        super().__init__(cfg)
        # Additional axis for the year
        self.custom_axes.append(
            Axis(
                coll="metadata",
                field="year",
                name="year",
                bins=set(sorted(self.cfg.years)),
                type="strcat",
                growth=False,
                label="Year",
            )
        )
        self.custom_axes.append(
            Axis(
                coll="metadata",
                field="flavor",
                name="flavor",
                bins={'l', 'c', 'b', 'cc', 'bb'},
                type="strcat",
                growth=False,
                label="Flavor",
            )
        )

    def apply_JERC(self, JER=True, verbose=False):
        if not self._isMC:
            return
        if int(self._year) > 2018:
            sys.exit("Warning: Run 3 JEC are not implemented yet.")
        if JER:
            self.events.Jet, seed_dict = jet_correction(
                self.events,
                "Jet",
                "AK4PFchs",
                self._year,
                self._JECversion,
                self._JERversion,
                verbose=verbose,
            )
            self.events.FatJet, seed_fatjet_dict = jet_correction(
                self.events,
                "FatJet",
                "AK8PFPuppi",
                self._year,
                self._JECversion,
                self._JERversion,
                verbose=verbose,
            )
            self.output['seed_chunk'].update(seed_dict)
            self.output['seed_fatjet_chunk'].update(seed_fatjet_dict)
        else:
            self.events.Jet = jet_correction(
                self.events,
                "Jet",
                "AK4PFchs",
                self._year,
                self._JECversion,
                verbose=verbose,
            )
            self.events.FatJet = jet_correction(
                self.events,
                "FatJet",
                "AK8PFPuppi",
                self._year,
                self._JECversion,
                verbose=verbose,
            )

    def apply_object_preselection(self):
        '''
        The ttHbb processor cleans
          - Electrons
          - Muons
          - Jets -> JetGood
          - BJet -> BJetGood

        '''
        # Include the supercluster pseudorapidity variable
        electron_etaSC = self.events.Electron.eta + self.events.Electron.deltaEtaSC
        self.events["Electron"] = ak.with_field(
            self.events.Electron, electron_etaSC, "etaSC"
        )
        # Build masks for selection of muons, electrons, jets, fatjets

        ################################################
        # Dedicated Muon selection for mutag final state
        self.events["MuonGood"] = lepton_selection_noniso(
            self.events, "Muon", self.cfg.finalstate
        )
        ################################################
        self.events["ElectronGood"] = lepton_selection(
            self.events, "Electron", self.cfg.finalstate
        )
        leptons = ak.with_name(
            ak.concatenate((self.events.MuonGood, self.events.ElectronGood), axis=1),
            name='PtEtaPhiMCandidate',
        )
        self.events["LeptonGood"] = leptons[ak.argsort(leptons.pt, ascending=False)]

        # Apply JEC + JER
        self.apply_JERC()
        self.events["JetGood"], self.jetGoodMask = jet_selection(
            self.events, "Jet", self.cfg.finalstate
        )
        self.events["FatJetGood"], self.fatjetGoodMask = jet_selection(
            self.events, "FatJet", self.cfg.finalstate
        )

        # Define di-muon object used for di-muon pT ratio object selection
        self.events = ak.with_field(self.events, ak.pad_none(self.events.MuonGood, 2)[:, 0] + ak.pad_none(self.events.MuonGood, 2)[:, 1], "dimuon")
        self.events["dimuon"] = ak.with_field(self.events.dimuon, self.events.dimuon.mass, "mass")

        # Apply di-muon pT ratio cut on FatJets
        dimuon_pt_ratio = 0.6
        mask_ptratio = (self.events.dimuon.pt / self.events.FatJet.pt < dimuon_pt_ratio)
        mask_ptratio = ak.where( ak.is_none(mask_ptratio), False, mask_ptratio )
        print("******************") 
        print(mask_ptratio)
        self.events["FatJetGood"] = self.events.FatJetGood[mask_ptratio]

    def count_objects(self):
        self.events["nMuonGood"] = ak.num(self.events.MuonGood)
        self.events["nElectronGood"] = ak.num(self.events.ElectronGood)
        self.events["nLeptonGood"] = (
            self.events["nMuonGood"] + self.events["nElectronGood"]
        )
        self.events["nJetGood"] = ak.num(self.events.JetGood)
        self.events["nFatJetGood"] = ak.num(self.events.FatJetGood)
        self.events["nSV"] = ak.num(self.events.SV)

    # Function that defines common variables employed in analyses and save them as attributes of `events`
    def define_common_variables_before_presel(self):
        Xbb = self.events.FatJet.particleNetMD_Xbb
        Xcc = self.events.FatJet.particleNetMD_Xcc
        QCD = self.events.FatJet.particleNetMD_QCD
        fatjet_fields = {
            "tau21"   : self.events.FatJet.tau2 / self.events.FatJet.tau1,
            "subjet1" : self.events.FatJet.subjets[:, :, 0],
            "subjet2" : self.events.FatJet.subjets[:, :, 1],
            "particleNetMD_Xbb_QCD" : Xbb / (Xbb + QCD),
            "particleNetMD_Xcc_QCD" : Xcc / (Xcc + QCD),
        }

        for field, value in fatjet_fields.items():
            self.events["FatJet"] = ak.with_field(self.events.FatJet, value, field)

        fatjet_subjet_fields = {
            "nsv1"    : get_nsv(self.events.FatJet.subjet1, self.events.SV),
            "nsv2"    : get_nsv(self.events.FatJet.subjet2, self.events.SV),
            "nmusj1"  : get_nmu_in_subjet(self.events.FatJet.subjet1, self.events.MuonGood),
            "nmusj2"  : get_nmu_in_subjet(self.events.FatJet.subjet2, self.events.MuonGood),
        }

        for field, value in fatjet_subjet_fields.items():
            #print("*********************")
            #print(ak.num(self.events.FatJet.subjet1, axis=1))
            #print(ak.num(value, axis=1))
            #print(value)
            self.events[field] = ak.with_field(self.events, value, field)

        self.events.FatJet.subjet1 = ak.with_field(self.events.FatJet.subjet1, self.events.FatJet.subjet1.nearest(self.events.MuonGood, threshold=0.4)[:, 0], "MuonLeading")
        self.events.FatJet.subjet2 = ak.with_field(self.events.FatJet.subjet2, self.events.FatJet.subjet2.nearest(self.events.MuonGood, threshold=0.4)[:, 0], "MuonLeading")

        # Define SV observables
        def project(a, b):
            return a.dot(b)/b.dot(b) * b

        self.events.SV = self.events.SV[get_sv_in_jet(self.events.FatJet[:,0], self.events.SV)]
        i_maxPt     = ak.argsort(self.events.SV.pt, ascending=False)
        i_maxdxySig = ak.argsort(self.events.SV.dxySig, ascending=False)
        sv_pt_sorted = self.events.SV[i_maxPt]
        leadsv = ak.firsts(sv_pt_sorted)
        self.events["SVLeading"] = leadsv
        
        sv_fields = {
            "summass" : sv_pt_sorted.p4.sum().mass,
            "logsummass" : np.log(sv_pt_sorted.p4.sum().mass),
            "projmass" : project(sv_pt_sorted.p4.sum(), self.events.FatJet[:,0]).mass,
            "logprojmass" : np.log(project(sv_pt_sorted.p4.sum(), self.events.FatJet[:,0]).mass),
            "sv1mass" : leadsv.mass,
            "logsv1mass" : np.log(leadsv.mass),
        }

        corrmass = np.sqrt(sv_pt_sorted.p4.mass**2 + sv_pt_sorted.p4.pt**2 * np.sin(sv_pt_sorted.pAngle)**2) + sv_pt_sorted.p4.pt * np.sin(sv_pt_sorted.pAngle)
        sv_pt_sorted['mass'] = corrmass

        sv_corrmass_fields = {
            "sumcorrmass" : sv_pt_sorted.p4.sum().mass,
            "logsumcorrmass" : np.log(sv_pt_sorted.p4.sum().mass),
        }
        sv_fields.update(sv_corrmass_fields)

        for field, value in sv_fields.items():
            self.events["SVLeading"] = ak.with_field(self.events.SVLeading, value, field)

    def process_extra_after_presel(self):
        # The function assigns a flavor to the fatjets depending on the hadron flavor, and the number of B and C hadrons
        self._flavors = {}
        if self._isMC:
            self._flavors['b'] = (self.events.FatJet[:,0].hadronFlavour == 5)
            self._flavors['c'] = (self.events.FatJet[:,0].hadronFlavour == 4)
            self._flavors['l'] = (self.events.FatJet[:,0].hadronFlavour < 4)
            self._flavors['bb'] = abs(self.events.FatJet[:,0].hadronFlavour == 5) & (self.events.FatJet[:,0].nBHadrons >= 2) #& (self.events.FatJet[:,0].nCHadrons == 0)
            self._flavors['cc'] = abs(self.events.FatJet[:,0].hadronFlavour == 4) & (self.events.FatJet[:,0].nBHadrons == 0) & (self.events.FatJet[:,0].nCHadrons >= 2)
            #self._flavors['ll'] = abs(self.events.FatJet[:,0].hadronFlavour < 4) & (self.events.FatJet[:,0].nBHadrons == 0) & (self.events.FatJet[:,0].nCHadrons == 0)
            self._flavors['b'] = self._flavors['b'] & ~self._flavors['bb']
            self._flavors['c'] = self._flavors['c'] & ~self._flavors['cc']
            self._flavors['l'] = self._flavors['l'] & ~self._flavors['bb'] & ~self._flavors['cc'] & ~self._flavors['b'] & ~self._flavors['c']
            #self._flavors['others'] = ~self._flavors['l'] & ~self._flavors['bb'] & ~self._flavors['cc'] & ~self._flavors['b'] & ~self._flavors['c']
        else:
            self._flavors['Data'] = np.ones(self.nEvents_after_presel, dtype='bool')

    def define_histograms_extra(self):
        '''
        Function that get called after the creation of the HistManager.
        The user can redefine this function to manipulate the HistManager
        histogram configuration to add customizations directly to the histogram
        objects before the filling.
        This function should also be redefined to fill the `self.custom_histogram_fields`
        that are passed to the histogram filling.
        '''
        flavor_array = ak.Array(self.nevents*['others'])
        for flavor, mask in self._flavors.items():
            flavor_array = ak.where(mask, flavor, flavor_array)
        self.custom_histogram_fields = {
            'flavor' : flavor_array
        }
