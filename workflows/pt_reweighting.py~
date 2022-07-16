import os

import numpy as np
import coffea
from coffea import hist, processor, lookup_tools
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load

from workflows.fatjet_tagger_projmass import ggHccProcessor
from lib.luminosity import rescale
from lib.sv import get_nsv, get_sv_in_jet
from parameters import triggers, JECversions, jecTarFiles, FinalMask, PtBinning, AK8Taggers, AK8TaggerWP

class ptReweightProcessor(ggHccProcessor):
    # Define histograms
    def __init__(self, cfg):
        self.cfg = cfg
        self._year = self.cfg['year']
        self._campaign = self.cfg['campaign']
        self._mask_fatjets = {
            'basic'       : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 20.,
                'tau21_cut' : 1.1,
                'DDCvB_cut' : -1
                    },
            'msd100tau06'       : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 100.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : -1
                    },
            'msd100tau06ggHcc'       : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 100.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : 0.03
                    },            
            'msd60tau06' : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 60.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : -1
                    },
            'msd60tau06ggHcc' : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 60.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : 0.03
                    },
            'msd40tau06' : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 40.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : -1
                    },
            'msd40tau06ggHcc' : {
                'pt_cut' : 350.,
                'eta_cut': 2.4,
                'jetId_cut': 2,
                'mass_cut' : 40.,
                'tau21_cut' : 0.6,
                'DDCvB_cut' : 0.03
                    },
        }
        self._final_mask = FinalMask
        #self._final_mask = ['msd100tau06', 'msd100tau03']
        self._AK8TaggerWP = AK8TaggerWP[self._campaign][self._year]
        self._PtBinning = PtBinning[self._campaign][self._year]
        self.mupt = cfg['mupt']
        self.corrJECfolder = cfg['JECfolder']
        self.hist2d = self.cfg['hist2d']
        self.checkOverlap = self.cfg['checkOverlap']
        if self.checkOverlap:
            self.eventTags = {'run' : None, 'lumi' : None, 'event' : None}

        ##############
        # Trigger level
        self.triggers = triggers[self._campaign][self._year]

        # Define axes
        # Should read axes from NanoAOD config
        dataset_axis = hist.Cat("dataset", "Primary dataset")
        # flavor_axis  = hist.Cat("flavor",   "Flavor")
        flavor_axis  = hist.Cat("flavor", "Flavor")
        region_axis  = hist.Cat("region", "Region")

        # FatJet
        fatjet_pt_axis    = hist.Bin("pt",   r"lead. FatJet $p_{T}$ [GeV]", 600, 0, 3000)
        fatjet_eta_axis   = hist.Bin("eta",  r"lead. FatJet $\eta$", 60, -3, 3)
        fatjet_phi_axis   = hist.Bin("phi",  r"lead. FatJet $\phi$", 60, -np.pi, np.pi)
        fatjet_mass_axis  = hist.Bin("mass", r"lead. FatJet $m_{SD}$ [GeV]", 1000, 0, 1000)

        _hist_fatjet_dict = {
                'fatjet_pt'  : hist.Hist("Events", dataset_axis, region_axis, flavor_axis, fatjet_pt_axis),
                'fatjet_eta' : hist.Hist("Events", dataset_axis, region_axis, flavor_axis, fatjet_eta_axis),
                'fatjet_phi' : hist.Hist("Events", dataset_axis, region_axis, flavor_axis, fatjet_phi_axis),
                'fatjet_mass': hist.Hist("Events", dataset_axis, region_axis, flavor_axis, fatjet_mass_axis),
            }

        _sumw_dict = {'sum_genweights': processor.defaultdict_accumulator(float),
                      'nbtagmu': processor.defaultdict_accumulator(float),
            }

        self.muon_hists = []
        #self.jet_hists = []
        self.fatjet_hists = list(_hist_fatjet_dict.keys())
        self.sv_hists = []
        self.sv_inclusive_hists = []
        self.event_hists = []
        self.nd_hists = []

        self._hist_dict = {**_hist_fatjet_dict}
        self._accumulator_dict = {}
        self._accumulator_dict.update(self._hist_dict)
        self._accumulator_dict.update({**_sumw_dict})
        self._accumulator = processor.dict_accumulator(self._accumulator_dict)
        if self.checkOverlap:
            for var in self.eventTags.keys():
                self._accumulator.add(processor.dict_accumulator({var : processor.column_accumulator(np.array([]))}))

    def postprocess(self, accumulator):
        super().postprocess(accumulator=accumulator)

        h_pt = accumulator['fatjet_pt']
        datasets_data = [str(s) for s in h_pt.identifiers('dataset') if 'BTagMu' in str(s)]
        datasets_mc   = [str(s) for s in h_pt.identifiers('dataset') if 'QCD' in str(s)]
        regions       = [str(s) for s in h_pt.axis('region').identifiers() if str(s) != 'region']
        corr_dict = processor.defaultdict_accumulator(float)
        for region in regions:
            h_data = h_pt[datasets_data].sum('dataset')[region].sum('region', 'flavor')
            h_mc   = h_pt[datasets_mc].sum('dataset')[region].sum('region', 'flavor')
            n_data = h_data.values()[()]
            n_mc   = h_mc.values()[()]
            print("n_data", n_data)
            print("n_mc", n_mc)
            rat    = n_data/n_mc
            mod_rat = np.nan_to_num(rat)
            print("rat", rat)
            print("mod_rat", mod_rat)
            bins = h_pt.axes()[-1].edges()
            mod_rat[bins[:-1] < 350] = 1
            mod_rat[bins[:-1] > 1500] = 1
            #hep.histplot(mod_rat, nbins)

            efflookup = dense_lookup(mod_rat, [bins])
            print(efflookup(np.array([50, 100, 400, 500, 2000, 10000])))
            corr_dict.update({ region : efflookup })

        if not os.path.exists(self.cfg['output_reweighting']):
            os.makedirs(self.cfg['output_reweighting'])
        outfile_reweighting = os.path.join(self.cfg['output_reweighting'], f'pt_corr_{self._year}.coffea')
        save(corr_dict, outfile_reweighting)
        efflookup_check = load(outfile_reweighting)
        pt_corr = efflookup_check['basic']
        print(pt_corr(np.array([50, 100, 400, 500, 2000, 10000])))

        return accumulator
