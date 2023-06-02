import os
import sys
import argparse
import json
import subprocess
import numpy as np

sys.path.append('/home/pku/licq/calib/mutag/BTVNanoCommissioning')

from utils.Fit import Fit
from utils.Processor import StandaloneMultiThreadedUnit
from utils.WebMaker import WebMaker
from utils.Logger import _logger

from parameters import categories

parser = argparse.ArgumentParser(description='Save histograms in pickle format for combine fit')
parser.add_argument('-i', '--input', default=None, help='Input templates', required=True)
parser.add_argument('-o', '--output', default="/work/mmarcheg/BTVNanoCommissioning/output/fit", help='Output folder', required=True)
parser.add_argument('--year', type=str, choices=["2015", "2016", "2017", "2018"], help='Specify the data-taking year', required=True)
parser.add_argument('--routine', type=str, default='main', choices=["all", "main", "fit_var_rwgt", "tau21p40", "tau21p35", "tau21p30", "tau21p25", "tau21p20"], help='Fit routine (subfolder to read the input cards)', required=True)
parser.add_argument('--only', type=str, default=None, help='Filter categories by key', required=False)
parser.add_argument('--run-impact', action='store_true', help='Run impact plots', required=False)
args = parser.parse_args()

categories = list(set([cat.replace('pass', '').replace('fail', '') for cat in categories if cat.startswith('msd40')]))
var = 'events_logsumcorrmass_1'
if args.only:
    args.only = args.only.split('*')
    categories = list(filter(lambda cat : all(f in cat for f in args.only), categories))
categories = sorted(categories)
_logger.info('Running categories... ' + ', '.join(categories))
_logger.info('Routine: ' + args.routine)

def fit_type(category):
    if any([s in category for s in ['Hbb', 'Xbb', 'DDBvL']]):
        return 'bb'
    elif any([s in category for s in ['Hcc', 'Xcc', 'DDCvL']]):
        return 'cc'
    else:
        raise RuntimeError('Unidentifable fit type')

def runcmd(cmd, shell=True):
    """Run a shell command"""
    p = subprocess.Popen(
        cmd, shell=shell, universal_newlines=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    out, _ = p.communicate()
    return (out, p.returncode)


def read_sf_from_log(flist, sf):
    r"""Read the SFs from each of the log file in the given list. Return the list of center, errl, errh values
    """
    if isinstance(flist, str):
        flist = [flist]
    out = []
    for f in flist:
        out.append(open(f).readlines())
    
    center, errl, errh = [], [], []
    for file, content in zip(flist, out):
        for l in content:
            l = l.split()
            if len(l)>0 and l[0]==f'SF_flv{sf}':
                center.append(float(l[2]))
                errl.append(float(l[3].split('/')[0]))
                errh.append(float(l[3].split('/')[1]))
                break
        else:
            center.append(np.nan)
            errl.append(np.nan)
            errh.append(np.nan)
            _logger.error("Failed fit point found: " + file)
    return np.array(center), np.array(errl), np.array(errh)


def concurrent_fit_unit(arg):
    r"""A unit function to run a single fit point for the given workdir.
    This function is launched in the multiprocessing pool.
    Inherit from the fit code from https://github.com/colizz/boohft-calib/blob/main/fit_unit.py

    Sealed arguments:
        workdir: the base directory path for the fit point
        args: args used to make plots
        is_central: is the central fit point
    """
    inputdir, workdir, is_central, mode, type, kwargs = arg
    # OpenBLAS' multithreading may confict with the main program's multithreading
    os.environ['OPENBLAS_NUM_THREADS'] = '1'

    # 1. Launch the fit
    # _logger.debug("Run fit point " + workdir)
    if is_central:
        ext_args = ''
        if kwargs.get('run_impact_for_central_fit', None):
            ext_args += '--run-impact --run-unce-breakdown '
        if kwargs.get('run_full_unce_breakdown_for_central_fit', None):
            ext_args += '--run-full-unce-breakdown '
        if os.path.exists(os.path.join(workdir, '.fit_automc_threshold')):
            ext_args += '--automc-threshold {} '.format(open(os.path.join(workdir, '.fit_automc_threshold')).read().strip())
        cmd = f"bash scripts/fit/launch_fit.sh {inputdir} {workdir} --bound 0.25,4 --type={type} --mode={mode} {ext_args}"
    else:
        cmd = f"bash scripts/fit/launch_fit.sh {inputdir} {workdir} --bound 0.25,4 --type={type} --mode={mode}"
    
    # run fit cmd
    out, ret = runcmd(cmd)
    if ret != 0:
        _logger.error("Error running the fit point: " + workdir + "\n" + \
            "See the following output (from last few lines):\n\n" + '\n'.join(out.splitlines()[-20:]))
        return (workdir, ret)

    ## try again if the fit fails
    automc_thres_list = [20, 50, 100, 200, 500, 1000, 2000, 5000]
    ipos = 0
    while np.isnan(read_sf_from_log(os.path.join(workdir, 'fit.log'), type[0].upper())[0]):
        ipos += 1
        if ipos >= len(automc_thres_list):
            break
        _logger.warning('Error running fit point in: ' + workdir + '\nTrying autoMC threshold: ' + str(automc_thres_list[ipos]))
        cmd = f"bash scripts/fit/launch_fit.sh {inputdir} {workdir} --bound 0.25,4 --type={type} --mode={mode} --automc-threshold {automc_thres_list[ipos]}"
        out, ret = runcmd(cmd)

    with open(os.path.join(workdir, '.fit_automc_threshold'), 'w') as f:
        f.write(str(automc_thres_list[ipos]))

    # # 2. Make plots if fit succeeds and is the central fit point
    # if is_central:
    #     if args.use_helvetica == True or (args.use_helvetica == 'auto' and any(['Helvetica' in font for font in mpl.font_manager.findSystemFonts()])):
    #         plt.style.use({"font.sans-serif": 'Helvetica'})

    #     make_stacked_plots(inputdir, workdir, args, save_plots=True)
    #     make_prepostfit_plots(inputdir, workdir, args, save_plots=True)

    #     for unce_type in args.unce_list:
    #         make_shape_unce_plots(inputdir, workdir, args, unce_type=unce_type, save_plots=True)

    return (workdir, 0)

fit_handler = StandaloneMultiThreadedUnit(workers=80, use_unordered_mapping=True)

run_routines = [args.routine] if args.routine != 'all' else ["main", "fit_var_rwgt", "tau21p40", "tau21p35", "tau21p30", "tau21p25", "tau21p20"]
for rout in run_routines:
    if rout == 'fit_var_rwgt':
        input_subdir, output_subdir, mode = 'main', 'fit_var_rwgt', 'fit_var_rwgt'
    else:
        input_subdir, output_subdir, mode = rout, rout, 'main'
    for cat in categories:
        name = f'{var}_{args.year}_{cat}'
        fit_handler.book((
            os.path.join(args.input, input_subdir, name), os.path.join(args.output, output_subdir, name), True, mode, fit_type(cat),
            dict(run_full_unce_breakdown_for_central_fit=(rout=='main' or rout=='fit_var_rwgt'), run_impact_for_central_fit=(args.run_impact)),
        ))
        # _logger.info("Writing to " + os.path.join(args.output, output_subdir, name))
result = fit_handler.run(concurrent_fit_unit)

# # write results
web = WebMaker('mutag_fit')
web.add_h1('Summary of fit results')
web.add_text('|  | main | fitvarrwgt | tau21p40 | tau21p35 | tau21p30 | tau21p25 | tau21p20 |')
web.add_text('| -- | -- | -- | -- | -- | -- | -- | -- |')
for cat in categories:
    name = f'{var}_{args.year}_{cat}'
    text = f'| {cat} | '
    for subfolder in ['main', 'fit_var_rwgt', 'tau21p40', 'tau21p35', 'tau21p30', 'tau21p25', 'tau21p20']:
        center, errl, errh = read_sf_from_log(os.path.join(args.output, subfolder, name, 'fit.log'), fit_type(cat)[0].upper())
        text += f'**{center[0]}** [{errl[0]}/+{errh[0]}] | '
    web.add_text(text)
web.add_text('\n')
web.write_to_file(args.output)
_logger.info('Summary write to file: ' + os.path.join(args.output, 'index.html'))