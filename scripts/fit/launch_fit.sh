#!/bin/bash

WORKDIR=$PWD

# trick for SWAN: unset previous python env
unset PYTHONPATH
unset PYTHONHOME
# load CMSSW environment
source /cvmfs/cms.cern.ch/cmsset_default.sh

cd /home/pku/licq/hcc/calib/CMSSW_10_2_27/src; eval `scram runtime -sh`; cd -

# launch the fit
python /home/pku/licq/calib/mutag/BTVNanoCommissioning/scripts/fit/runFit_sfbdt.py $@