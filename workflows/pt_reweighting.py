import os
from collections import defaultdict

import numpy as np
import hist
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea.util import save, load

import correctionlib, rich
import correctionlib.convert

from workflows.fatjet_base import fatjetBaseProcessor
from pocket_coffea.utils.configurator import Configurator

from pocket_coffea.utils.plot_utils import dense_axes, get_axis_items, get_data_mc_ratio
from pocket_coffea.parameters.custom.genweights.genweights import genweights_files

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
        self.histname_pt_1d = 'FatJetGood_pt_1'
        self.histname_pt_2d = 'FatJetGood_pt_1_FatJetGood_pt_2'
        if not self.histname_pt_1d in self.cfg.variables.keys():
            raise Exception(f"'{self.histname_pt_1d}' is not present in the histogram keys.")

    def pt_reweighting(self, accumulator, mode):
        if mode == '1D':
            histname = self.histname_pt_1d
        elif mode == '2D':
            histname = self.histname_pt_2d
        else:
            raise Exception("pT reweighting mode not recognized. Available modes: '1D', '2D'")
        h = accumulator['variables'][histname]
        samples = h.keys()
        samples_data = list(filter(lambda d: 'DATA' in d, samples))
        samples_mc = list(filter(lambda d: 'DATA' not in d, samples))

        h_mc = h[samples_mc[0]]

        axes = dense_axes(h_mc)
        years = get_axis_items(h_mc, 'year')
        categories = get_axis_items(h_mc, 'cat')

        #corr_dict = defaultdict(float)
        ratio_dict = defaultdict(float)

        year = self.get_year(accumulator)

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
            if cat not in pt_low.keys():
                pt_low[cat] = 350.
            if mode == '1D':
                bins = axes[0].edges
                mod_ratio[bins[:-1] < pt_low[cat]] = 1
                mod_ratio[bins[:-1] > 1500] = 1
            elif mode == '2D':
                mod_ratio[mod_ratio == 0.0] = 1

            ratio_dict.update({ cat : mod_ratio })

        axis_category = hist.axis.StrCategory(list(ratio_dict.keys()), name="cat")
        sfhist = hist.Hist(axis_category, *axes, data=np.stack(list(ratio_dict.values())))
        sfhist.label = "out"
        sfhist.name = f"pt_corr_{year}"
        clibcorr = correctionlib.convert.from_histogram(sfhist)
        clibcorr.description = "Reweighting SF matching the leading fatjet pT MC distribution to data."
        cset = correctionlib.schemav2.CorrectionSet(
            schema_version=2,
            description="Semileptonic trigger efficiency SF",
            corrections=[clibcorr],
        )
        rich.print(cset)

        outfile_reweighting = os.path.join(self.cfg.output, f'pt_corr_{mode}_{year}.json')
        outfile_reweighting = overwrite_check(outfile_reweighting)
        print(f"Saving pt reweighting factors in {outfile_reweighting}")
        with open(outfile_reweighting, "w") as fout:
            fout.write(cset.json(exclude_unset=True))
        fout.close()
        print(f"Loading correction from {outfile_reweighting}...")
        cset = correctionlib.CorrectionSet.from_file(outfile_reweighting)
        print("inclusive:")
        pt_corr = cset[f'pt_corr_{year}']
        if mode == '1D':
            pt1 = np.array([50, 100, 400, 500, 1000], dtype=float)
            print("pt1 =", pt1)
            print(pt_corr.evaluate('inclusive', pt1))
        elif mode == '2D':
            pt1 = np.array([50, 100, 400, 500, 1000], dtype=float)
            pt2 = np.array([40, 75, 300, 400, 750], dtype=float)
            print("pt1 =", pt1)
            print("pt2 =", pt2)
            print(pt_corr.evaluate('inclusive', pt1, pt2))

    def postprocess(self, accumulator):
        '''
        Rescale MC histograms by the total sum of the genweights, read from the
        output computed before skimming.
        '''

        years = self.cfg.dataset["filter"]["year"]
        if len(years) > 1:
            raise Exception("Only one data-taking year can be processed at a time.")
        else:
            year = years[0]
        genweights_dict = load(genweights_files[year])['sum_genweights']

        scale_genweight = {}

        for sample in self._totalSamplesSet:
            if (not sample.startswith('DATA')) & (sample not in genweights_dict):
                continue
            scale_genweight[sample] = (
                1
                if sample.startswith('DATA')  # BEAWARE OF THIS HARDCODING
                else 1.0 / genweights_dict[sample]
            )
            # correct also the sumw (sum of weighted events) accumulator
            for cat in self._categories:
                if sample in accumulator["sumw"][cat]:
                    accumulator["sumw"][cat][sample] *= scale_genweight[sample]

        for var, hists in accumulator["variables"].items():
            # Rescale only histogram without no_weights option
            if self.cfg.variables[var].no_weights:
                continue
            for sample, h in hists.items():
                h *= scale_genweight[sample]
        accumulator["scale_genweight"] = scale_genweight

        self.pt_reweighting(accumulator=accumulator, mode='1D')
        self.pt_reweighting(accumulator=accumulator, mode='2D')

        return accumulator
