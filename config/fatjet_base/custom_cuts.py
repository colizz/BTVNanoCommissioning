# Per-event cuts applied to each event
import awkward as ak
import PocketCoffea.lib.cut_functions as cuts_f
from PocketCoffea.lib.cut_definition import Cut
from config.fatjet_base.functions import mutag, msdtau

mutag_presel = Cut(
	name="mutag",
	params={
		"nmusj1" : 1,
		"nmusj2" : 1,
		"dimuon_pt_ratio" : 0.6
	},
	function=mutag
)

def get_msdtau(msd, tau21, name=None):
	if name == None:
		name = f"msd{msd}tau{tau21}"
	return Cut(
		name=name,
		params= {"msd" : msd, "tau21" : tau21},
		function=msdtau
	)
