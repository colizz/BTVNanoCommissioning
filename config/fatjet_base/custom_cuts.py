# Per-event cuts applied to each event
import awkward as ak
import PocketCoffea.lib.cut_functions as cuts_f
from PocketCoffea.lib.cut_definition import Cut
from config.fatjet_base.functions import mutag, ptbin, ptmsd, ptmsdtau

mutag_presel = Cut(
	name="mutag",
	params={
		"nmusj1" : 1,
		"nmusj2" : 1,
		"dimuon_pt_ratio" : 0.6
	},
	function=mutag
)

def get_ptbin(pt_low, pt_high, name=None):
	if name == None:
		name = f"Pt-{pt_low}to{pt_high}"
	return Cut(
		name=name,
		params= {"pt_low" : pt_low, "pt_high" : pt_high},
		function=ptbin
	)

def get_ptmsd(pt, msd, name=None):
	if name == None:
		name = f"pt{pt}msd{msd}"
	return Cut(
		name=name,
		params= {"pt" : pt, "msd" : msd},
		function=ptmsd
	)

def get_ptmsdtau(pt, msd, tau21, name=None):
	if name == None:
		name = f"msd{msd}tau{tau21}"
	return Cut(
		name=name,
		params= {"pt" : pt, "msd" : msd, "tau21" : tau21},
		function=ptmsdtau
	)
