import numpy as np
from PocketCoffea.lib.cut_definition import Cut

def tagger_mask(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetLeading[tagger] > params["wp"])
    assert (params["category"] in ["pass", "fail"]), "The allowed categories for the tagger selection are 'pass' and 'fail'"
    if params["category"] == "fail":
        mask = ~mask
    return mask

def tagger_pass(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetLeading[tagger] > params["wp"])

    return mask

def tagger_fail(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetLeading[tagger] < params["wp"])

    return mask

def tagger_mask_exclusive_wp(events, params, **kwargs):
    assert (len(params["wp"]) == 2), "The 'wp' parameter has to be a 2D tuple"
    cut_low, cut_high = params["wp"]
    assert (cut_low < cut_high), "The lower bound of the WP has to be smaller than the higher bound"
    mask = np.zeros(len(events), dtype='bool')
    mask = (events.FatJetLeading[params["tagger"]] > cut_low) & (events.FatJetLeading[params["tagger"]] <= cut_high)

    assert (params["category"] in ["pass", "fail"]), "The allowed categories for the tagger selection are 'pass' and 'fail'"
    if params["category"] == "fail":
        mask = ~mask & (events.FatJetLeading[params["tagger"]] >= 0) & (events.FatJetLeading[params["tagger"]] <= 1)

    return mask

def get_tagger_pass(taggers, wp):
    return Cut(
        name=f"{'_'.join(taggers)}_pass",
        params={"taggers": taggers, "wp" : wp},
        function=tagger_pass
    )

def get_tagger_fail(taggers, wp):
    return Cut(
        name=f"{'_'.join(taggers)}_fail",
        params={"taggers": taggers, "wp" : wp},
        function=tagger_fail
    )

def get_tagger_passfail(taggers, wp, category):
    return Cut(
        name=f"{'_'.join(taggers)}_{category}",
        params={"taggers": taggers, "wp" : wp, "category": category},
        function=tagger_mask
    )

def get_exclusive_wp(tagger, wp, category):
    return Cut(
        name=f"{'_'.join(tagger)}_{category}",
        params={"tagger": tagger, "wp" : wp, "category": category},
        function=tagger_mask_exclusive_wp
    )

def mutag(events, params, **kwargs):
    # Mask to select events with leading fatjet having at least `nmusj1` subjets in its leading subjet
    # and `nmusj2` subjets in its subleading subjet. Additionally, a requirement on the dimuon pt ratio to the fatjet pt is required.
    fatjet_mutag = (events.FatJetLeading.nmusj1 >= params["nmusj1"]) & (events.FatJetLeading.nmusj2 >= params["nmusj2"]) & (events.dimuon.pt/events.FatJetLeading.pt < params["dimuon_pt_ratio"])

    return fatjet_mutag

def ptbin(events, params, **kwargs):
    # Mask to select events in a fatjet pt bin
    if params["pt_high"] == 'Inf':
        return (events.FatJetLeading.pt > params["pt_low"])
    elif type(params["pt_high"]) != str:
        return (events.FatJetLeading.pt > params["pt_low"]) & (events.FatJetLeading.pt < params["pt_high"])
    else:
        raise NotImplementedError

def ptmsd(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    return (events.FatJetLeading.pt > params["pt"]) & (events.FatJetLeading.msoftdrop > params["msd"])

def ptmsdtau(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    return (events.FatJetLeading.pt > params["pt"]) & (events.FatJetLeading.msoftdrop > params["msd"]) & (events.FatJetLeading.tau21 < params["tau21"])

def ptmsdtauDDCvB(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21 and a requirement on the DDCvB score
    return (events.FatJetLeading.pt > params["pt"]) & (events.FatJetLeading.msoftdrop > params["msd"]) & (events.FatJetLeading.tau21 < params["tau21"]) & (events.FatJetLeading.btagDDCvBV2 > params["DDCvB"])
