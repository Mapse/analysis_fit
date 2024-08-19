''' 
Config filed used to help merge_data script

The folders must be organized in the following way:

Folders with files must be inside the main path, ie, if the variable path is '/Charm', then
it should be,

/Charm/RunA; /Charm/RunB, etc.

inside RunX folder you must have the coffea files produced by your condor script.

To run you simply do: python3 merge_data

'''

# List with eras to be runned
#era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF', '9to30', '30to50', '50to100', '100to150', 'sps',  ]
era_list=['RunB', 'RunC', 'RunD', 'RunE', 'RunF',] #2017
#era_list=['RunA','RunB', 'RunC', 'RunD'] # 2018
#era_list=['RunB_HIPM', 'RunC_HIPM', 'RunD_HIPM', 'RunE_HIPM', 'RunF_HIPM',] # 2016-pre-VFP
#era_list=['RunF','RunG', 'RunH'] # 2016-pos-VFP
#era_list=['dps_9to30', 'dps_30to50', 'dps_50to100']
#era_list=['sps_3fs_4fs_9to30', 'sps_3fs_4fs_30to50', 'sps_3fs_4fs_50to100']
#era_list=['dps_9to30']
#era_list=['bquarkjpsi']
#era_list=['sps_vfns_9to30', 'sps_vfns_30to50', ]
#bin = {'jpsi_pt_bin1' : [25, 30], 'jpsi_pt_bin1' : [30, 50], 'jpsi_pt_bin1' : [50, 100],}
bin = {'jpsi_pt_bin1' : [25, 30],
       'jpsi_pt_bin2' : [30, 50],
       'jpsi_pt_bin3' : [50, 70],
       'jpsi_pt_bin4' : [70, 100], }
# Special name for save it (e.g: cate = 'prompt_jpsi')
cate = 'vtx0p05_sigma_eff'
#cate = 'inv_mass_high_cut_8'
#cate = 'dy_vtx0p05_sigma_eff_dstar_rapidity_pt_jpsi_dl_test'

nevts_data = 4950 # 2016-pre-VFP: 2321; 2016-pos-VFP: 1993; 2017: 4950; 2018: 6891

# Path where the files produced by condor are stored.
main_path = '/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/data/2017' 

# Analysis condition: trigger or no_trigger
condition = 'trigger'

# Path to store the root file
path_output = 'data_root_files/2017/'
