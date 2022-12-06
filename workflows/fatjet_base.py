import numpy as np
import awkward as ak
from collections import defaultdict

from pocket_coffea.workflows.base import BaseProcessorABC
from pocket_coffea.utils.configurator import Configurator

#from pocket_coffea.parameters.jec import JECversions, JERversions
from pocket_coffea.lib.objects import (
    jet_correction,
    lepton_selection,
    jet_selection,
    btagging,
    get_dilepton,
)
from config.fatjet_base.custom.leptons import lepton_selection_noniso
from lib.sv import *
from pocket_coffea.lib.hist_manager import HistManager, Axis, HistConf


class fatjetBaseProcessor(BaseProcessorABC):
    def __init__(self, cfg: Configurator):
        super().__init__(cfg)
        # Define dictionary to save fatjet JER seeds
        self.output_format.update({"seed_fatjet_chunk": defaultdict(str)})

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
    """
    def load_metadata_extra(self):
        self._JECversion = JECversions[self._year]['MC' if self._isMC else 'Data']
        self._JERversion = JERversions[self._year]['MC' if self._isMC else 'Data']

    def apply_JERC(self, JER=True, verbose=False):
        if not self._isMC:
            return
        if int(self._year.split('_')[0]) > 2018:
            sys.exit("Warning: Run 3 JEC are not implemented yet.")
        # N.B.: We don't apply JER to 2017 MC since the JER scale factor and resolution are not saved in the JSON
        if JER & (self._year != '2017'):
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
    """
    def apply_object_preselection(self, variation):
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
        # Define di-muon object used for di-muon pT ratio object selection
        self.events = ak.with_field(self.events, ak.pad_none(self.events.MuonGood, 2)[:, 0] + ak.pad_none(self.events.MuonGood, 2)[:, 1], "dimuon")
        self.events["dimuon"] = ak.with_field(self.events.dimuon, self.events.dimuon.mass, "mass")
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
        #self.apply_JERC()
        self.events["JetGood"], self.jetGoodMask = jet_selection(
            self.events, "Jet", self.cfg.finalstate
        )

        self.events["FatJetGood"], self.fatjetGoodMask = jet_selection(
            self.events, "FatJet", self.cfg.finalstate
        )

    def count_objects(self, variation):
        self.events["nMuonGood"] = ak.num(self.events.MuonGood)
        self.events["nElectronGood"] = ak.num(self.events.ElectronGood)
        self.events["nLeptonGood"] = (
            self.events["nMuonGood"] + self.events["nElectronGood"]
        )
        self.events["nJetGood"] = ak.num(self.events.JetGood)
        self.events["nFatJetGood"] = ak.num(self.events.FatJetGood)
        self.events["nSV"] = ak.num(self.events.SV)

    def define_common_variables_after_presel(self, variation):
        
        fatjet_sv_fields = {
            "nsv1"    : get_nsv(self.events.FatJetGood, self.events.SV, pos=0),
            "nsv2"    : get_nsv(self.events.FatJetGood, self.events.SV, pos=1),
        }

        for field, value in fatjet_sv_fields.items():
            self.events = ak.with_field(self.events, value, field)

        Xbb = self.events.FatJetGood.particleNetMD_Xbb
        Xcc = self.events.FatJetGood.particleNetMD_Xcc
        QCD = self.events.FatJetGood.particleNetMD_QCD
        fatjet_fields = {
            "tau21"   : self.events.FatJetGood.tau2 / self.events.FatJetGood.tau1,
            "subjet1" : self.events.FatJetGood.subjets[:, :, 0],
            "subjet2" : self.events.FatJetGood.subjets[:, :, 1],
            "particleNetMD_Xbb_QCD" : Xbb / (Xbb + QCD),
            "particleNetMD_Xcc_QCD" : Xcc / (Xcc + QCD),
        }

        for field, value in fatjet_fields.items():
            self.events["FatJetGood"] = ak.with_field(self.events.FatJetGood, value, field)

        self.events.FatJetGood.subjet1 = ak.with_field(self.events.FatJetGood.subjet1, self.events.FatJetGood.subjet1.nearest(self.events.MuonGood, threshold=0.4)[:, 0], "MuonLeading")
        self.events.FatJetGood.subjet2 = ak.with_field(self.events.FatJetGood.subjet2, self.events.FatJetGood.subjet2.nearest(self.events.MuonGood, threshold=0.4)[:, 0], "MuonLeading")

        # Define SV observables

        #self.events.SV = self.events.SV[get_sv_in_jet(self.events.FatJetGood[:,0], self.events.SV)]
        sv_in_jet1 = self.events.SV[get_sv_in_jet(self.events.FatJetGood, self.events.SV, pos=0)]
        sv_in_jet2 = self.events.SV[get_sv_in_jet(self.events.FatJetGood, self.events.SV, pos=1)]
        i1_maxPt     = ak.argsort(sv_in_jet1.pt, ascending=False)
        i2_maxPt     = ak.argsort(sv_in_jet2.pt, ascending=False)
        sv_in_jet1_sorted = sv_in_jet1[i1_maxPt]
        sv_in_jet2_sorted = sv_in_jet2[i2_maxPt]

        sv_fields = {}
        position = {'jet1' : 0, 'jet2' : 1}
        for jet_key, sv_in_jet_sorted in zip(['jet1', 'jet2'], [sv_in_jet1_sorted, sv_in_jet2_sorted]):
            summass, logsummass = get_summass(sv_in_jet_sorted)
            #projmass, logprojmass = get_projmass(self.events.FatJetGood, sv_in_jet_sorted, pos=position[jet_key])
            sv1mass, logsv1mass = get_sv1mass(sv_in_jet_sorted)
            sumcorrmass, logsumcorrmass = get_sumcorrmass(sv_in_jet_sorted)
            sv_fields[jet_key] = {
                "summass" : summass,
                "logsummass" : logsummass,
                #"projmass" : projmass,
                #"logprojmass" : logprojmass,
                "sv1mass" : sv1mass,
                "logsv1mass" : logsv1mass,
                "sumcorrmass" : sumcorrmass,
                "logsumcorrmass" : logsumcorrmass,
            }

        for field in sv_fields['jet1'].keys():
            value1_unflattened = ak.unflatten( sv_fields['jet1'][field], counts=1 )
            value2_unflattened = ak.unflatten( sv_fields['jet2'][field], counts=1 )
            value_concat = ak.concatenate( (value1_unflattened, value2_unflattened), axis=1 )
            self.events = ak.with_field(self.events, value_concat, field)

    def define_column_accumulators(self):
        pass

    def fill_column_accumulators(self, variation):
        pass

    def postprocess(self, accumulator):
        super().postprocess(accumulator=accumulator)

        #for histname, h in accumulator['variables'].items():
        #    samples = h.keys()
        #    print(samples)
        #    h_byflavor = {'DATA' : h['DATA']}
        #    for f in ['l', 'c', 'b', 'cc', 'bb']:
        #        subsamples_flavor = filter(lambda x : x.endswith(f"_{f}"), samples)
        #        for (i, s) in enumerate(subsamples_flavor):
        #            if i==0:
        #                h_byflavor[f] = h[s]
        #            else:
        #                h_byflavor[f] += h[s]
        #    accumulator['variables'][histname] = h_byflavor

        return accumulator
