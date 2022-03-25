import collections
import numpy as np
import awkward as ak
from parameters import lumi, xsecs

def rescale(accumulator, xsecs=xsecs, lumi=lumi, data="BTagMu"):
#def rescale(accumulator, xsecs=xsecs, data="BTagMu"):
    """Scale by lumi"""
    #lumi = 1000*lumi    # Convert lumi to pb^-1
    from coffea import hist
    scale = {}
    sumxsecs = ak.sum(xsecs.values())
    #N_data = accumulator['nbtagmu_event_level'][data]
    #print("N_data =", N_data)
    for dataset, N_mc in collections.OrderedDict(sorted(accumulator['sumw'].items())).items():
        if dataset in xsecs:
            print(" ", dataset, "\t", N_mc, "events\t", xsecs[dataset], "pb")
            #scale[dataset] = (xsecs[dataset]/sumxsecs)*(N_data/N_mc)
            scale[dataset] = (xsecs[dataset]*lumi)/N_mc
        else:
            print(" ", "X ", dataset)
            scale[dataset] = 0#lumi / N_mc
    print(scale)

    datasets_mc = [item for item in list(xsecs.keys()) if not 'GluGlu' in item]
    for h in accumulator.values():
        if isinstance(h, hist.Hist):
            h.scale(scale,       axis="dataset")
            N_data = ak.sum(h[data].values().values())
            N_mc = ak.sum(h[datasets_mc].sum('dataset', 'flavor').values().values())
            #scaletodata = dict(zip(scale.keys(), len(scale)*[1./N_data]))
            scaletodata = dict(zip(scale.keys(), len(scale)*[N_data/N_mc]))
            h.scale(scaletodata, axis="dataset")
    return accumulator
