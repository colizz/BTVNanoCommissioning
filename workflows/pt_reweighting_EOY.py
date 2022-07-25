import os

import numpy as np
import coffea
from coffea import hist, processor, lookup_tools
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load

from workflows.fatjet_base_EOY import fatjetEOYProcessor

pt_low = {
    'inclusive' : 250.,
    'pt350msd40' : 350.,
    'pt350msd60' : 350.,
    'pt350msd80' : 350.,
    'pt350msd100' : 350.,
}

def overwrite_check(outfile):
    path = outfile
    version = 1
    while os.path.exists(path):
        tag = str(version).rjust(2, '0')
        path = outfile.replace('.coffea', f'_v{tag}.coffea')
        version += 1
    if path != outfile:
        print(f"The output will be saved to {path}")
    return path

class ptReweightProcessor(fatjetEOYProcessor):
    def __init__(self, cfg) -> None:
        super().__init__(cfg=cfg)
        self._pt_reweighting = False

    def apply_pt_reweighting(self):
        pass

    def postprocess(self, accumulator):
        super().postprocess(accumulator=accumulator)

        h_pt = accumulator['hist_leadfatjet_pt']
        categories_to_sum_over = ['cat', 'year', 'flavor']
        samples_data = [str(s) for s in h_pt.identifiers('sample') if 'DATA' in str(s)]
        samples_mc   = [str(s) for s in h_pt.identifiers('sample') if 'QCD' in str(s)]
        categories    = [str(s) for s in h_pt.axis('cat').identifiers() if str(s) != 'cat']
        corr_dict = processor.defaultdict_accumulator(float)
        for cat in categories:
            h_data = h_pt[samples_data].sum('sample')[cat].sum(*categories_to_sum_over)
            h_mc   = h_pt[samples_mc].sum('sample')[cat].sum(*categories_to_sum_over)
            n_data = h_data.values()[()]
            n_mc   = h_mc.values()[()]
            print("n_data", n_data)
            print("n_mc", n_mc)
            rat    = n_data/n_mc
            mod_rat = np.nan_to_num(rat)
            print("rat", rat)
            print("mod_rat", mod_rat)
            bins = h_pt.axes()[-1].edges()
            if cat not in pt_low.keys():
                pt_low[cat] = 350.
            mod_rat[bins[:-1] < pt_low[cat]] = 1
            mod_rat[bins[:-1] > 1500] = 1
            #hep.histplot(mod_rat, nbins)

            efflookup = dense_lookup(mod_rat, [bins])
            print(efflookup(np.array([50, 100, 400, 500, 2000, 10000])))
            corr_dict.update({ cat : efflookup })

        if not os.path.exists(self.cfg.output_reweighting):
            os.makedirs(self.cfg.output_reweighting)
        outfile_reweighting = os.path.join(self.cfg.output_reweighting, f'pt_corr.coffea')
        outfile_reweighting = overwrite_check(outfile_reweighting)
        print(f"Saving pt reweighting factors in {outfile_reweighting}")
        save(corr_dict, outfile_reweighting)
        efflookup_check = load(outfile_reweighting)
        pt_corr = efflookup_check['inclusive']
        print(pt_corr(np.array([50, 100, 400, 500, 2000, 10000])))

        return accumulator
