import numpy as np
import pandas as pd
import mplhep as hep
import matplotlib.pyplot as plt
hep.style.use(hep.style.ROOT) # For now ROOT defaults to CMS

plt.figure(figsize=[10,10])
hep.cms.text("Preliminary", loc=0)
plt.xlim(200, 900)
plt.ylim(0.6, 1.3)
plt.xticks(np.arange(200, 1000, 100))
plt.xlabel(r"p$_T$ [GeV]")
plt.ylabel("SF")
xlow = 450
xrange = 900 - xlow
xerr=xrange/2
xcenter = 675
SF = np.array([1.0, 0.96, 0.8])
SFerr = np.array([[0.10, 0.05, 0.08], [0.20, 0.07, 0.09]])
x = np.array(len(SF)*[xcenter]) + np.arange(0, 15, 5)
xerr = np.array(len(SF)*[xerr])

colormap = ['red', 'green', 'blue']
categories = [0, 1, 2]
for i in range(len(SF)):
    plt.errorbar(x[i:i+1], SF[i:i+1], xerr=xerr[i:i+1], yerr=SFerr[:,i:i+1], capsize=8, linestyle='', marker='o', markersize=5, c=colormap[i])

plt.savefig(filepath, dpi=300, format="png")