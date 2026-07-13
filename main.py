# This file is a MNE python-based brainlife.io App

# Author: Guiomar Niso Galán
# Author: Carlota Juárez Alonso
# Neuroimaging Group, Cajal Neuroscience Center, CSIC

# 03/07/2026

# Set up enviroment

import json
from pathlib import Path
import subprocess
from shutil import copyfile, rmtree, copytree
import mne
import mne_bids
import logging

# Logger configuration

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

# Current path 

__location__ = Path(__file__).resolve().parent

# Read the parameters from Brainlife 

config_path = __location__/'config.json'
if not config_path.exists():
    raise FileNotFoundError(f"The configuration file could not be found in {config_path}")

with open (config_path, 'r') as f:
    config = json.load(f)

# Input paths 
# The output of the last app is now configurated as the input (bids_root key)
bids_root = config.get('bids_dir')
if not bids_root:
    raise ValueError("'bids_dir' parameter is required")

bids_root_path = Path(bids_root).resolve()

# Output paths

deriv_root = __location__/'out_dir'
html_report_dir = __location__/'html_report'

# Ensure output directories exist

if deriv_root.exists():
    rmtree(deriv_root)
html_report_dir.mkdir(parents = True, exist_ok = True)


# Copy the input folder ('bids_dir') in the output folder ('out_dir') to have all the data there

copytree(bids_root_path, deriv_root, dirs_exist_ok = True)

# Rewrite the info in the .json file into a .py file

file_name = __location__/'pipeline_config.py'

# Inputs from the interface web to MNE variables

with open(file_name, 'w') as f:

    f.write(f"bids_root = '{bids_root_path}'\n")
    f.write(f"deriv_root = '{deriv_root}'\n")

    # General settings (always nedeed)

    data_type = config.get('data_type')
    if not data_type:
        raise ValueError("'data_type' parameter is required (must be 'eeg' or 'meg')")
    f.write(f"data_type = '{data_type}'\n")

    if data_type == 'eeg':
        ch_types = ['eeg']
        eeg_template_montage = config.get('eeg_template_montage', None)
        if eeg_template_montage:
            f.write(f"eeg_template_montage = '{eeg_template_montage}'\n")    
    else:
        meg_ch_types = config.get('meg_ch_types', 'meg')
        ch_types = [meg_ch_types]
        # Avoid the empty room error, since the BIDS structure returned by the preprocessing App does not have the associated .json
        f.write("process_empty_room = False\n")
    f.write(f"ch_types = {ch_types}\n")

    subject = '01'
    f.write(f"subjects = ['{subject}']\n")

    task = config.get('task', None)
    if task:
        f.write(f"task = '{task}'\n")
    else:
        raise ValueError("'task' parameter is required")  

    task_is_rest = config.get('task_is_rest', False)
    f.write(f"task_is_rest = {task_is_rest}\n")

    conditions = config.get('conditions', None)
    if conditions:
        f.write(f"conditions = {conditions}\n")
    else:
        raise ValueError("'conditions' parameter is required unless task_is_rest is True")

    interactive = config.get('interactive', False)
    f.write(f"interactive = {interactive}\n")

    proc = config.get('proc', None)
    if proc:
        f.write(f"proc = '{proc}'\n")

    # Condition contrast

    contrasts = config.get('contrasts', [])
    if contrasts:
        f.write(f"contrasts = {contrasts}\n")
    
    # Decoding / MVPA

    decode = config.get('decode', True)
    if not contrasts:
        decode = False
    f.write(f"decode = {decode}\n")
    if decode:
        decoding_which_epochs = config.get('decoding_which_epochs', 'cleaned')
        if decoding_which_epochs:
            f.write(f"decoding_which_epochs = '{decoding_which_epochs}'\n")
            
        decoding_epochs_tmin = config.get('decoding_epochs_tmin', None)
        if decoding_epochs_tmin:
            f.write(f"decoding_epochs_tmin = {decoding_epochs_tmin}\n")
            
        decoding_epochs_tmax = config.get('decoding_epochs_tmax', None)
        if decoding_epochs_tmax:
            f.write(f"decoding_epochs_tmax = {decoding_epochs_tmax}\n")
            
        decoding_metric = config.get('decoding_metric', 'roc_auc')
        if decoding_metric:
            f.write(f"decoding_metric = '{decoding_metric}'\n")
            
        decoding_n_splits = config.get('decoding_n_splits')
        if decoding_n_splits in [None, ""]:
            decoding_n_splits = 5
        f.write(f"decoding_n_splits = {decoding_n_splits}\n")                
            
        decoding_time = config.get('decoding_time', True)
        f.write(f"decoding_time = {decoding_time}\n")
        if decoding_time:    
            decoding_time_decim = config.get('decoding_time_decim')
            if decoding_time_decim in [None, ""]:
                decoding_time_decim = 1
            f.write(f"decoding_time_decim = {decoding_time_decim}\n")   
                
        decoding_time_generalization = config.get('decoding_time_generalization', False)
        f.write(f"decoding_time_generalization = {decoding_time_generalization}\n") 
        if decoding_time_generalization:    
            decoding_time_generalization_decim = config.get('decoding_time_generalization_decim')
            if decoding_time_generalization_decim in [None, ""]:
                decoding_time_generalization_decim = 1
            f.write(f"decoding_time_generalization_decim = {decoding_time_generalization_decim}\n")   
                
        decoding_csp = config.get('decoding_csp', False)
        f.write(f"decoding_csp = {decoding_csp}\n")   
        if decoding_csp:    
            decoding_csp_times = config.get('decoding_csp_times', None)
            if decoding_csp_times:
                f.write(f"decoding_csp_times = {decoding_csp_times}\n")   
                
            decoding_csp_freqs = config.get('decoding_csp_freqs', None)
            if decoding_csp_freqs:
                f.write(f"decoding_csp_freqs = {decoding_csp_freqs}\n")  
                
        n_boot = config.get('n_boot')
        if n_boot in [None, ""]:
            n_boot = 5000
        f.write(f"n_boot = {n_boot}\n")

    # Only for group level       
    '''
        cluster_forming_t_threshold = config.get('cluster_forming_t_threshold', None)
        if cluster_forming_t_threshold:
            f.write(f"cluster_forming_t_threshold = {cluster_forming_t_threshold}\n")
            
        cluster_n_permutations = config.get('cluster_n_permutations')
        if cluster_n_permutations in [None, ""]:
            cluster_n_permutations = 10000
        f.write(f"cluster_n_permutations = {cluster_n_permutations}\n")
            
        cluster_permutation_p_threshold = config.get('cluster_permutation_p_threshold')
        if cluster_permutation_p_threshold in [None, ""]:
            cluster_permutation_p_threshold = 0.05
        f.write(f"cluster_permutation_p_threshold = {cluster_permutation_p_threshold}\n")
    '''

    # Time-frequency analysis

    time_frequency_conditions = config.get('time_frequency_conditions', [])
    if time_frequency_conditions:
        f.write(f"time_frequency_conditions = {time_frequency_conditions}\n")
        
    time_frequency_freq_min = config.get('time_frequency_freq_min')
    if time_frequency_freq_min in [None, ""]:
        time_frequency_freq_min = 8
    f.write(f"time_frequency_freq_min = {time_frequency_freq_min}\n")
        
    time_frequency_freq_max = config.get('time_frequency_freq_max')
    if time_frequency_freq_max in [None, ""]:
        time_frequency_freq_max = 40
    f.write(f"time_frequency_freq_max = {time_frequency_freq_max}\n")
        
    time_frequency_cycles = config.get('time_frequency_cycles', None)
    if time_frequency_cycles:
        f.write(f"time_frequency_cycles = {time_frequency_cycles}\n")

    time_frequency_subtract_evoked = config.get('time_frequency_subtract_evoked', False)
    f.write(f"time_frequency_subtract_evoked = {time_frequency_subtract_evoked}\n")
        
    time_frequency_baseline = config.get('time_frequency_baseline', None)
    if isinstance(time_frequency_baseline, list) and len(time_frequency_baseline) == 2 and time_frequency_baseline[0] not in [None, 'null', ''] and time_frequency_baseline[1] not in [None, 'null', ""]:
        p1, p2 = time_frequency_baseline
        f.write(f"time_frequency_baseline = ({p1}, {p2})\n")
    elif task_is_rest:
        f.write("time_frequency_baseline = None\n")
    else:
        f.write("time_frequency_baseline = None\n")
        
    time_frequency_baseline_mode = config.get('time_frequency_baseline_mode', 'mean')
    if time_frequency_baseline_mode:
        f.write(f"time_frequency_baseline_mode = '{time_frequency_baseline_mode}'\n")
        
    time_frequency_crop = config.get('time_frequency_crop', None)
    if time_frequency_crop:
        f.write(f"time_frequency_crop = {time_frequency_crop}\n")
    
    # Group level analysis
    '''
    interpolate_bads_grand_average = config.get('interpolate_bads_grand_average', True)
    f.write(f"interpolate_bads_grand_average = {interpolate_bads_grand_average}\n")
    '''

# Run python script

command = ["mne_bids_pipeline", f"--config={file_name}", "--steps=sensor"]

try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    raise e

# Find the reports and make a copy in out_html folder

real_deriv_root = deriv_root.resolve()

for path in real_deriv_root.rglob("*.html"):
    if "sub-average" not in path.name:
        logger.info(f"{path.name} copied to the output")
        copyfile(path, html_report_dir/path.name)





