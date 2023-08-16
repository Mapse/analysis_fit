
'''
Config filed used to help merge_root script

The merge_root script is used to merge the root files
produced by the sabe_ttree script:

Ex: RunA.root + RunB.root = RunAB.root

'''

# Path to the RunX.root files
path='/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/fit/data_root_files/2016-pos-VFP'

# last characters of the file name (this is similar to the cate variable on the triggerprocessor config)
end_name = '_sigma_eff_vtx0p05.root' # Ex: RunC_HLT_Dimuon25_sigma_eff_vtx0p05.root

# Name of the merged file 
final_name = 'Charmonium2016-pos-VFP_HLT_Dimuon16'
