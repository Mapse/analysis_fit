''' 
Config filed used to help TriggerProcessor script

The folders must be organized in the following way:

Folders with merged files must be inside the main path, ie, if the variable path is '/Charm', then
it should be,

/Charm/RunA/merged_files; /Charm/RunB/merged_files, etc.

On the main routine the main_path variable will provide its information to the path_output variable.

inside RunX folder you must have the merged_files folders containing merged coffea files produced by 
merged_data script.

To run you simply do: python3 TriggerProcessor.py

'''

# Mode of running: This is a special feature created for when the sum of the accumulators is very large.
# If mode = 'several' it will apply the trigger for each file separatedely
# If mode = 'sum' it will apply the trigger for the summed accumulator.
mode = 'several'

# Special name for save it (e.g: cate = 'prompt_jpsi')
#cate = 'inv_mass_high_cut_8'
#cate = 'vtx0p05_sigma_eff_signal_region'
cate = 'vtx0p05_sigma_eff'
#path_mode_several = '/home/mabarros/Analysis_2017/OniaOpenCharmRun2ULAna/output/Charmonium_2017/RunB_HIPM_ver2/merged_data'

# List with eras to run
#era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF', '9to30', '30to50', '50to100', 'sps',  ]
era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF',] # 2017: data
#era_list=['RunB', ] # 2017
#era_list=['RunB_HIPM', 'RunC_HIPM', 'RunD_HIPM', 'RunE_HIPM', 'RunF_HIPM',] # 2016-pre-VFP
#era_list=['RunF','RunG', 'RunH'] # 2016-pos-VFP
#era_list=['RunA', 'RunB', 'RunC', 'RunD'] # 2018
#era_list=['RunD',] # 2018
#era_list=['bquarkjpsi']
#era_list=['30to50',]   
#era_list=['9to30', '30to50', '50to100', 'sps']
#era_list=['30to50', '50to100', '100to150']

#era_list=['9to30']

""" bin = {'jpsi_pt_bin1' : [25, 30],
       'jpsi_pt_bin2' : [30, 50],} """

bin = {'jpsi_pt_bin1' : [25, 30],
       'jpsi_pt_bin2' : [30, 50],
       'jpsi_pt_bin3' : [50, 70],
       'jpsi_pt_bin4' : [70, 100], }

# Boolean to cut on small phase-space 
effec_sigma = True

# Path where the files produced by condor are stored.
# this path should point to the directory where RunX/merged_data is!!!
main_path = '/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/data/2017' 

# List of triggers to be applied
hlt_filter = ['HLT_Dimuon25_Jpsi']
hlt_year = 'HLT_2017'
