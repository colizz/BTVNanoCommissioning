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

def get_tagger_passfail(taggers, wp, category):
    return Cut(
        name=f"{'_'.join(taggers)}_{category}",
        params={"taggers": taggers, "wp" : wp, "category": category},
        function=tagger_mask
    )

def mutag(events, params, **kwargs):
    # Mask to select events with leading fatjet having at least `nmusj1` subjets in its leading subjet
    # and `nmusj2` subjets in its subleading subjet. Additionally, a requirement on the dimuon pt ratio to the fatjet pt is required.
    fatjet_mutag = (events.FatJetLeading.nmusj1 >= params["nmusj1"]) & (events.FatJetLeading.nmusj2 >= params["nmusj2"]) & (events.dimuon.pt/events.FatJetLeading.pt < params["dimuon_pt_ratio"])

    return fatjet_mutag

def msdtau(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    return (events.FatJetLeading.msoftdrop > params["msd"]) & (events.FatJetLeading.msoftdrop < params["tau21"])

def msdtauDDCvB(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21 and a requirement on the DDCvB score
    return (events.FatJetLeading.msoftdrop > params["msd"]) & (events.FatJetLeading.msoftdrop < params["tau21"]) & (events.FatJetLeading.msoftdrop > params["DDCvB"])
