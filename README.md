# BTVNanoCommissioning
Repository for Commissioning studies in the BTV POG based on (custom) nanoAOD samples

## Structure
A Coffea processor targeting the computation of AK8 taggers scale factors for dedicated working points and $p_T$ bins is implemented.

# PocketCoffea
The framework implements a declarative analysis workflow based on the package PocketCoffea (https://github.com/PocketCoffea/PocketCoffea).

## Installation
Clone the forked repository and move to the dedicated branch `btv`.
```
git clone https://github.com/mmarchegiani/PocketCoffea.git
git checkout btv
```

In order to install `pocket_coffea` as a package, create a dedicated conda environment:
```
conda env create --name pocket-coffea python=3.8
conda activate pocket-coffea
```

Then move to the `PocketCoffea` folder and run the command:
```
pip install -e .
```

which will install the package locally in the editable mode.

## How to run
To run the fatjet workflow, use the `runner.py` command with one of the config files in `config/fatjet_base/` as argument:
```
runner.py --cfg config/fatjet_base/flavorsplit_2018UL_particleNetMD_Xbb.py
```
