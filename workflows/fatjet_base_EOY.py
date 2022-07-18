import os

import numpy as np
import coffea
from coffea import hist, processor, lookup_tools
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load

from workflows.fatjet_base import fatjetBaseProcessor
from parameters import jecTarFiles, FinalMask, PtBinning, AK8Taggers, AK8TaggerWP

#from PocketCoffea.lib.triggers import get_trigger_mask
#from PocketCoffea.lib.objects import jet_correction, lepton_selection, lepton_selection_noniso, jet_selection, btagging, get_dilepton
#from PocketCoffea.lib.pileup import sf_pileup_reweight
#from PocketCoffea.lib.scale_factors import sf_ele_reco, sf_ele_id, sf_mu
#from PocketCoffea.lib.fill import fill_histograms_object_with_flavor
from PocketCoffea.parameters.triggers import triggers_EOY
from PocketCoffea.parameters.btag import btag
from PocketCoffea.parameters.jec import JECversions_EOY
#from PocketCoffea.parameters.jec import JECversions_EOY, JERversions_EOY
#from PocketCoffea.parameters.event_flags import event_flags, event_flags_data
from PocketCoffea.parameters.lumi import lumi, goldenJSON
#from PocketCoffea.parameters.samples import samples_info
#from PocketCoffea.parameters.allhistograms import histogram_settings

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

        JECversion = self._JECversion
        jets = self.events[{'AK8PFPuppi' : 'FatJet'}[typeJet]]
        fixedGridRhoFastjetAll = self.events.fixedGridRhoFastjetAll
        events_cache = self.events.caches[0]
        isData = not self._isMC
        JECversion = self._JECversion

        ext = lookup_tools.extractor()
        JECtypes = [ 'L1FastJet', 'L2Relative', 'L2Residual', 'L3Absolute', 'L2L3Residual' ]
        jec_stack_names = [ JECversion+'_'+k+'_'+typeJet for k in JECtypes ]
        JECtypesfiles = [ '* * '+self.corrJECfolder+'/'+k+'.txt' for k in jec_stack_names ]
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
