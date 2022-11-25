import os
from collections import defaultdict

import numpy as np
import hist
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load

from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.utils.configurator import Configurator

from pocket_coffea.utils.plot_utils import dense_axes, get_axis_items, get_data_mc_ratio

pt_low = {
    'inclusive' : 350.,
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

class ptReweightProcessor(fatjetBaseProcessor):
    def __init__(self, cfg: Configurator):
        super().__init__(cfg)
        self.histname_pt = 'FatJetGood_pt_1'
        if not self.histname_pt in self.cfg.variables.keys():
            raise Exception(f"'{self.histname_pt}' is not present in the histogram keys.")

    def postprocess(self, accumulator):
        super().postprocess(accumulator=accumulator)

        h = accumulator['variables'][self.histname_pt]
        samples = h.keys()
        samples_data = list(filter(lambda d: 'DATA' in d, samples))
        samples_mc = list(filter(lambda d: 'DATA' not in d, samples))

        h_mc = h[samples_mc[0]]

        dense_axis = dense_axes(h_mc)[0]
        years = get_axis_items(h_mc, 'year')
        categories = get_axis_items(h_mc, 'cat')

        corr_dict = defaultdict(float)

        for year in years:
            for cat in categories:
                #slicing_mc = {'year': year, 'cat': cat}
                slicing_mc_nominal = {'year': year, 'cat': cat, 'variation': 'nominal'}
                #dict_mc = {d: h[d][slicing_mc] for d in samples_mc}
                dict_mc_nominal = {d: h[d][slicing_mc_nominal] for d in samples_mc}
                #stack_mc = hist.Stack.from_dict(dict_mc)
                stack_mc_nominal = hist.Stack.from_dict(dict_mc_nominal)

                if 'era' in h[samples_data[0]].axes.name:
                    slicing_data = {'year': year, 'cat': cat, 'era': sum}
                else:
                    slicing_data = {'year': year, 'cat': cat}
                dict_data = {d: h[d][slicing_data] for d in samples_data}
                stack_data = hist.Stack.from_dict(dict_data)
                if len(stack_data) > 1:
                    raise NotImplementedError
                else:
                    h_data = stack_data[0]
                ratio, unc = get_data_mc_ratio(stack_data, stack_mc_nominal)
                mod_ratio  = np.nan_to_num(ratio)
                bins = dense_axis.edges
                if cat not in pt_low.keys():
                    pt_low[cat] = 350.
                mod_ratio[bins[:-1] < pt_low[cat]] = 1
                mod_ratio[bins[:-1] > 1500] = 1

                efflookup = dense_lookup(mod_ratio, [bins])
                print(f"{cat}:")
                print(efflookup(np.array([50, 100, 400, 500, 2000, 10000])))
                corr_dict.update({ cat : efflookup })

            outfile_reweighting = os.path.join(self.cfg.output, f'pt_corr_{year}.coffea')
            outfile_reweighting = overwrite_check(outfile_reweighting)
            print(f"Saving pt reweighting factors in {outfile_reweighting}")
            save(corr_dict, outfile_reweighting)
            print(f"Loading correction from {outfile_reweighting}...")
            efflookup_check = load(outfile_reweighting)
            print("inclusive:")
            pt_corr = efflookup_check['inclusive']
            print(pt_corr(np.array([50, 100, 400, 500, 2000, 10000])))

        return accumulator
