
'''
Config filed used to help merge_root script

The merge_root script is used to merge the root files
produced by the sabe_ttree script:

Ex: RunA.root + RunB.root = RunAB.root

'''

# Path to the RunX.root files
path='/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/fit/data_root_files'

# last characters of the file name (this is similar to the cate variable on the triggerprocessor config)
end_name = '_vtx0p1.root'

# Name of the merged file 
final_name = 'Charmonium2017_HLT_Dimuon25'
