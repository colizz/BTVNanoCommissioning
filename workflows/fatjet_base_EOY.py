import os

import numpy as np
import awkward as ak

import coffea
from coffea import hist, processor, lookup_tools
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load
from coffea.analysis_tools import Weights
from coffea.jetmet_tools import FactorizedJetCorrector, JetCorrectionUncertainty
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory

from workflows.fatjet_base import fatjetBaseProcessor
from parameters import jecTarFiles, FinalMask, PtBinning, AK8Taggers, AK8TaggerWP

from PocketCoffea.lib.pileup import sf_pileup_reweight_EOY
from PocketCoffea.parameters.triggers import triggers_EOY
from PocketCoffea.parameters.btag import btag
from PocketCoffea.parameters.jec import JECversions_EOY
from PocketCoffea.parameters.lumi import lumi_EOY, goldenJSON
from PocketCoffea.parameters.samples import samples_info

class fatjetEOYProcessor(fatjetBaseProcessor):    
    # Function to load year-dependent parameters
    def load_metadata(self):
        self._dataset = self.events.metadata["dataset"]
        self._sample = self.events.metadata["sample"]
        self._year = self.events.metadata["year"]
        self._triggers = triggers_EOY[self.cfg.finalstate][self._year]
        self._btag = btag[self._year]
        self._isMC = 'genWeight' in self.events.fields
        # JEC
        self._JECversion = JECversions_EOY[self._year]['MC' if self._isMC else 'Data']
        #self._JERversion = JERversions_EOY[self._year]['MC' if self._isMC else 'Data']
        self._goldenJSON = goldenJSON[self._year]

    def apply_JERC( self, JER=False, typeJet='AK8PFPuppi' ):
        '''Based on https://coffeateam.github.io/coffea/notebooks/applying_corrections.html#Applying-energy-scale-transformations-to-Jets'''
        if not self._isMC: return

        jets = self.events[{'AK8PFPuppi' : 'FatJet'}[typeJet]]
        fixedGridRhoFastjetAll = self.events.fixedGridRhoFastjetAll
        events_cache = self.events.caches[0]
        isData = not self._isMC
        JECversion = self._JECversion
        JECfolder  = self.cfg.JECfolder

        ext = lookup_tools.extractor()
        JECtypes = [ 'L1FastJet', 'L2Relative', 'L2Residual', 'L3Absolute', 'L2L3Residual' ]
        jec_stack_names = [ JECversion+'_'+k+'_'+typeJet for k in JECtypes ]
        JECtypesfiles = [ '* * '+JECfolder+'/'+k+'.txt' for k in jec_stack_names ]
        ext.add_weight_sets( JECtypesfiles )
        ext.finalize()
        evaluator = ext.make_evaluator()

        jec_inputs = {name: evaluator[name] for name in jec_stack_names}
        corrector = FactorizedJetCorrector( **jec_inputs )
        # for i in jec_inputs: print(i,'\n',evaluator[i])

        #print(dir(evaluator))
        #print()
        jec_stack = JECStack(jec_inputs)
        name_map = jec_stack.blank_name_map
        name_map['JetPt'] = 'pt'
        name_map['JetMass'] = 'mass'
        name_map['JetEta'] = 'eta'
        name_map['JetA'] = 'area'

        jets['pt_raw'] = (1 - jets['rawFactor']) * jets['pt']
        jets['mass_raw'] = (1 - jets['rawFactor']) * jets['mass']
        jets['rho'] = ak.broadcast_arrays(fixedGridRhoFastjetAll, jets.pt)[0]
        name_map['ptRaw'] = 'pt_raw'
        name_map['massRaw'] = 'mass_raw'
        name_map['Rho'] = 'rho'
        if not isData:
            jets['pt_gen'] = ak.values_astype(ak.fill_none(jets.matched_gen.pt, 0), np.float32)
            name_map['ptGenJet'] = 'pt_gen'

        jet_factory = CorrectedJetsFactory(name_map, jec_stack)
        corrected_jets = jet_factory.build(jets, lazy_cache=events_cache)

        self.events[typeJet] = corrected_jets

    def compute_weights(self):
        self.weights = Weights(self.nEvents_after_presel)
        if self._isMC:
            self.weights.add('genWeight', self.events.genWeight)
            self.weights.add('lumi', ak.full_like(self.events.genWeight, lumi_EOY[self._year]))
            self.weights.add('XS', ak.full_like(self.events.genWeight, samples_info[self._sample]["XS"]))
            # Pileup reweighting with nominal, up and down variations
            self.weights.add('pileup', sf_pileup_reweight_EOY(self.events, self.cfg.nTrueFile, self._sample, self._year))
            # Electron reco and id SF with nominal, up and down variations
            #self.weights.add('sf_ele_reco', *sf_ele_reco(self.events, self._year))
            #self.weights.add('sf_ele_id',   *sf_ele_id(self.events, self._year))
            # Muon id and iso SF with nominal, up and down variations
            #self.weights.add('sf_mu_id',  *sf_mu(self.events, self._year, 'id'))
            #self.weights.add('sf_mu_iso', *sf_mu(self.events, self._year, 'iso'))
