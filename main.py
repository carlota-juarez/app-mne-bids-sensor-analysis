# This file is a MNE python-based brainlife.io App

# Carlota Juárez Alonso

# Set up enviroment

import json
import os
import subprocess
from shutil import copyfile
from distutils.dir_util import copy_tree


# Current path

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Read the parameters from Brainlife 

with open (os.path.join(__location__, 'config.json')) as f:
    config = json.load(f)

# Entry and output paths 

bids_root = str(config['bids'])
deriv_root = os.path.join(__location__, 'out_dir')
html_report_dir = os.path.join(__location__, 'html_report')

# Ensure output directories exist

if not os.path.exists(deriv_root):
    os.makedirs(deriv_root)
if not os.path.exists(html_report_dir):
    os.makedirs(html_report_dir)

# Copy the input folder ('app2_output') in the output folder ('out_dir') to have all the data there

if config['app2_output'] and os.path.exists(config['app2_output']):
    copy_tree(config['app2_output'], deriv_root)

# Rewrite the info in the .json file into a .py file

file_name = os.path.join(__location__, 'pipeline_config.py')

# Inputs from the interface web to MNE variables

with open(file_name, 'w') as f:
    # -- General settings --

    f.write(f"bids_root = '{bids_root}'\n")
    f.write(f"deriv_root = '{deriv_root}'\n")

    # Condition contrast

    if config['contrasts']:
        f.write(f"contrasts = {config['contrasts']}\n")
    
    # Decoding / MVPA

    if config['decode']:
        f.write(f"decode = {config['decode']}\n")
        if config['decoding_which_epochs']:
            f.write(f"decoding_which_epochs = '{config['decoding_which_epochs']}'\n")
        if config['decoding_epochs_tmin']:
            f.write(f"decoding_epochs_tmin = {config['decoding_epochs_tmin']}\n")
        if config['decoding_epochs_tmax']:
            f.write(f"decoding_epochs_tmax = {config['decoding_epochs_tmax']}\n")
        if config['decoding_metric']:
            f.write(f"decoding_metric = '{config['decoding_metric']}'\n")
        if config['decoding_n_splits']:
            f.write(f"decoding_n_splits = {config['decoding_n_splits']}\n")                
        if config['decoding_time']:
            f.write(f"decoding_time = {config['decoding_time']}\n")
            if config['decoding_time_decim']:
                f.write(f"decoding_time_decim = {config['decoding_time_decim']}\n")   
        if config['decoding_time_generalization']:
            f.write(f"decoding_time_generalization = {config['decoding_time_generalization']}\n") 
            if config['decoding_time_generalization_decim']:
                f.write(f"decoding_time_generalization_decim = {config['decoding_time_generalization_decim']}\n")   
        if config['decoding_csp']:
            f.write(f"decoding_csp = {config['decoding_csp']}\n")   
            if config['decoding_csp_times']:
                f.write(f"decoding_csp_times = {config['decoding_csp_times']}\n")   
            if config['decoding_csp_freqs']:
                f.write(f"decoding_csp_freqs = {config['decoding_csp_freqs']}\n")  
        if config['n_boot']:
            f.write(f"n_boot = {config['n_boot']}\n")
        if config['cluster_forming_t_threshold']:
            f.write(f"cluster_forming_t_threshold = {config['cluster_forming_t_threshold']}\n")
        if config['cluster_n_permutations']:
            f.write(f"cluster_n_permutations = {config['cluster_n_permutations']}\n")
        if config['cluster_permutation_p_threshold']:
            f.write(f"cluster_permutation_p_threshold = {config['cluster_permutation_p_threshold']}\n")
        
    # Time-frequency analysis

    if config['time_frequency_conditions']:
        f.write(f"time_frequency_conditions = {config['time_frequency_conditions']}\n")
    if config['time_frequency_freq_min']:
        f.write(f"time_frequency_freq_min = {config['time_frequency_freq_min']}\n")
    if config['time_frequency_freq_max']:
        f.write(f"time_frequency_freq_max = {config['time_frequency_freq_max']}\n")
    if config['time_frequency_subtract_evoked']:
        f.write(f"time_frequency_subtract_evoked = {config['time_frequency_subtract_evoked']}\n")
    if config['time_frequency_baseline']:
        f.write(f"time_frequency_baseline = {config['time_frequency_baseline']}\n")
    if config['time_frequency_baseline_mode']:
        f.write(f"time_frequency_baseline_mode = {config['time_frequency_baseline_mode']}\n")
    if config['time_frequency_crop']:
        f.write(f"time_frequency_crop = {config['time_frequency_crop']}\n")
    
    # Group level analysis

    if config['interpolate_bads_grand_average']:
        f.write(f"interpolate_bads_grand_average = {config['interpolate_bads_grand_average']}\n")

    f.close()

# Run python script

command = ["mne_bids_pipeline", f"--config={file_name}", "--steps=sensor,report"]

try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    raise e

# Find the reports and make a copy in out_html folder

for dirpaths, dirnames, filenames in os.walk(deriv_root):
    for filename in [f for f in filenames if f.endswith(".html")]:
        print(filename)
        copyfile(os.path.join(dirpaths, filename), os.path.join(html_report_dir, filename))





