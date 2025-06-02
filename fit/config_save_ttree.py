''' 
Config filed used to help merge_data script

The folders must be organized in the following way:

Folders with files must be inside the main path, ie, if the variable path is '/Charm', then
it should be,

/Charm/RunA; /Charm/RunB, etc.

inside RunX folder you must have the coffea files produced by your condor script.

To run you simply do: python3 merge_data

'''

### List with eras to be ran

#era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF', '9to30', '30to50', '50to100', '100to150', 'sps',  ]
#era_list=['dps_9to30', 'dps_30to50', 'dps_50to100']
#era_list=['sps_3fs_4fs_9to30', 'sps_3fs_4fs_30to50', 'sps_3fs_4fs_50to100']
#era_list=['dps_9to30']
#era_list=['bquarkjpsi']
#era_list=['sps_vfns_9to30', 'sps_vfns_30to50', ]


## Run 2: 2016-pre-VFP, 2016-pos-VFP, 2017, 2018

#era_list=['RunB_HIPM', 'RunC_HIPM', 'RunD_HIPM', 'RunE_HIPM', 'RunF_HIPM',] # 2016-pre-VFP
#era_list=['RunF','RunG', 'RunH'] # 2016-pos-VFP
#era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF',] #2017
#era_list=['RunA','RunB', 'RunC', 'RunD'] # 2018
era_list=["sps_3fs_ccbar_25to100"]
## Bins
bin = {'jpsi_pt_bin1' : [25, 100]}
""" bin = {'jpsi_pt_bin1' : [30, 40],
       'jpsi_pt_bin2' : [40, 50],
       'jpsi_pt_bin3' : [50, 100],} """

#bin = {'jpsi_pt_bin1' : [25, 100], }

### Special name for save it (e.g: cate = 'prompt_jpsi')

cate = 'usual'

nevts_data = 4950 # 2016-pre-VFP: 2321; 2016-pos-VFP: 1993; 2017: 4950; 2018: 6891

# Path where the files produced by condor are stored.
main_path = '/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/data/2017' 

# Analysis condition: trigger or no_trigger
condition = 'trigger'

# Path to store the root file
path_output = 'data_root_files/2017/'

# splot save_ttree
splot = False
splot_path = '/home/mapse/Documents/temp/analysis_fit/fit/splot_coffea_files'
splot_coffea = 'signal_sweight_inv_mass_high_cut_8.coffea'