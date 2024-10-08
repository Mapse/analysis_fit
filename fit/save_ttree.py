from coffea.util import load, save
import numpy as np
import os

import uproot3

from tqdm import tqdm

import config_save_ttree as config

def load_accumulator(main_path, era, condition, bin):

    '''
    This function is used load the accumulator for file and sum everything together. There are two conditions,
    if the condition is 'no_trigger' then it will sum all chunks produced with merge_data script. If the condition
    is 'trigger' it will simply take the accumulator produced on TriggerProcessor script.
    
    main_path (str): Path to the directories named RunX, where for 2018 data X = [A, B, C, D]

    era (str): Name of the era one wants to run the code, where for 2018 data X = [A, B, C, D]

    condition (str): It is two options: no_trigger and trigger.

    It returns the desired accumulator and the name of the trigger used (if it exists).

    '''

    # If the condition is without trigger it will sum the accumulators produced with merge_coffea.py
    if condition == 'no_trigger':

        print('Running no_trigger option')
        
        # List to store final paths
        files = []        
        # With statement to open scan more efficiently
        with os.scandir(main_path) as it:
            for file in it:
                # Stores all other files finished with .coffea
                if file.name.endswith('.coffea') and b[8:] in file.name and  (file.stat().st_size != 0):
                    files.append(file.path)

        # Loads the first file on the list.
        acc = load(files[0])

        # Loop over the list (starts from 1 because we have already called the first file!) using tqdm
        # in order to monitor the loop progress.
        for i in tqdm(files[1:], desc="Loading " + era, unit=" files", total=len(files)-1):
            acc += load(i)
        trigger_name = ''


        return acc, trigger_name

    if condition == 'trigger':

        print('Running trigger option')
        # List to store final paths
        files = []
        # With statement to open scan more efficiently
        with os.scandir(main_path) as it:
            for file in it:
                # Stores all other files finished with .coffea
                if file.name.endswith('.coffea') and b[8:] in file.name and  (file.stat().st_size != 0):
                    files.append(file.path)
        # Strategy to take the trigger name and store on trigger_name variable.
        # Ex: trigger_name = 'HLT_Dimuon25'
        try:
            trigger_name = files[0]
            trigger_name = trigger_name.split('HLT', 1)
            trigger_name = trigger_name[1]
            trigger_name = 'HLT' + trigger_name.replace('.coffea', '')
            trigger_name = trigger_name[:12]    
        except:
            trigger_name = era

        # Loads the first file on the list.
        acc = load(files[0])

        # Loop over the list (starts from 1 because we have already called the first file!) using tqdm
        # in order to monitor the loop progress.
        for i in tqdm(files[1:], desc="Loading " + era, unit=" files", total=len(files)-1):
            acc += load(i)
        #print(trigger_name)
        print(f'bin {bin}')
        print(files)
    
        return acc, trigger_name

    
def create_root(accumulator, path_output, era, b, condition=None):

    '''
    This function is used to produce root ntuple from coffea files.
    
    accumulator (dict_accumulator): Accumulator with the particle information.

    era (str): Name of the era one wants to run the code, where for 2018 data X = [A, B, C, D]

    condition (str): It is two options: no_trigger and trigger.

    It creates a root ntuple with a branch called asso with the following variables:
    Dstar_deltamr, jpsi_pt and jpsi_mass -> All from the associated object.

    '''

    # Taks the accumulator and the trigger name
    acc, trigger_name = accumulator
    nevts_data = config.nevts_data
    
    print(f'Processing bin {b}')
    # If the option is 'no_trigger' it will take the original accumulator that comes from the
    # files produced via condor
    if condition == 'no_trigger':
        
        # Takes wrong charge flags
        wrg_chg = acc['DimuDstar']['Dstar']['wrg_chg'].value
        # Takes wrong and right charge Dstars
        dstar_wrong_charge = acc['DimuDstar']['Dstar']['deltamr'].value[wrg_chg]
        dstar_right_charge = acc['DimuDstar']['Dstar']['deltamr'].value[~wrg_chg]
        # Jpsi
        all_asso_jpsi_mass = acc['DimuDstar']['Dimu']['mass'].value
        all_asso_jpsi_pt = acc['DimuDstar']['Dimu']['pt'].value
        
    
    # If the option is 'trigger' it will take the accumulator saved on the TriggerProcessor.py
    if condition == 'trigger':

        # Conditions for MC        
        if 'dps' in era or 'sps' in era:

            # Takes wrong and right charge Dstars
            dstar_mass = acc['DimuDstar']['dstar_deltamr'].value
            dstar_pt = acc['DimuDstar']['dstar_pt'].value
            dstar_rap = acc['DimuDstar']['dstar_rap'].value
            dstar_d0dlsig = acc['DimuDstar']['dstar_d0dlsig'].value
            dstar_d0dl = acc['DimuDstar']['dstar_d0dl'].value
            dstar_d0dca = acc['DimuDstar']['dstar_d0dca'].value

            ## Jpsi
            all_asso_jpsi_mass = acc['DimuDstar']['jpsi_mass'].value
            all_asso_jpsi_pt = acc['DimuDstar']['jpsi_pt'].value
            all_asso_jpsi_rap = acc['DimuDstar']['jpsi_rap'].value
            all_asso_jpsi_dl = acc['DimuDstar']['jpsi_dl'].value
            all_asso_jpsi_dl_err = acc['DimuDstar']['jpsi_dlErr'].value

            # DimuDstar           
            jpsi_dstar_mass = acc['DimuDstar']['dimu_dstar_mass'].value
            jpsi_dstar_deltarap = acc['DimuDstar']['dimu_dstar_deltarap'].value
            jpsi_dstar_deltaphi = acc['DimuDstar']['dimu_dstar_deltaphi'].value
            jpsi_dstar_deltapt = acc['DimuDstar']['dimu_dstar_deltapt'].value

            # Pileup, muon ID, and muon reco weights
            weight = acc['weight'].value
            #xsec_weight = nevts_data/len(all_asso_jpsi_mass)
            #weight = np.full_like(all_asso_jpsi_mass, xsec_weight) 
            #print(f"d:{len(dstar_mass)}")
            #print(f"w:{len(weight)}")

            #print(f'weight: {xsec_weight}')

        
        # Conditions for data
        else:
            
            ## Dstar
            # Takes wrong charge flags
            wrg_chg = acc['DimuDstar']['wrg_chg'].value
            # Takes wrong and right charge Dstars
            dstar_mass = acc['DimuDstar']['dstar_deltamr'].value[~wrg_chg]
            dstar_pt = acc['DimuDstar']['dstar_pt'].value[~wrg_chg]
            dstar_rap = acc['DimuDstar']['dstar_rap'].value[~wrg_chg]
            dstar_phi = acc['DimuDstar']['dstar_phi'].value[~wrg_chg]
            dstar_d0dlsig = acc['DimuDstar']['dstar_d0dlsig'].value[~wrg_chg]
            dstar_d0dl = acc['DimuDstar']['dstar_d0dl'].value[~wrg_chg]
            dstar_d0dca = acc['DimuDstar']['dstar_d0dca'].value[~wrg_chg]

            ## Jpsi
            all_asso_jpsi_mass = acc['DimuDstar']['jpsi_mass'].value[~wrg_chg]
            all_asso_jpsi_pt = acc['DimuDstar']['jpsi_pt'].value[~wrg_chg]
            all_asso_jpsi_rap = acc['DimuDstar']['jpsi_rap'].value[~wrg_chg]
            all_asso_jpsi_phi = acc['DimuDstar']['jpsi_phi'].value[~wrg_chg]
            all_asso_jpsi_dl = acc['DimuDstar']['jpsi_dl'].value[~wrg_chg]
            all_asso_jpsi_dl_err = acc['DimuDstar']['jpsi_dlErr'].value[~wrg_chg]

            # DimuDstar           
            jpsi_dstar_mass = acc['DimuDstar']['dimu_dstar_mass'].value[~wrg_chg]
            jpsi_dstar_pt = acc['DimuDstar']['dimu_dstar_pt'].value[~wrg_chg]
            jpsi_dstar_deltarap = acc['DimuDstar']['dimu_dstar_deltarap'].value[~wrg_chg]
            jpsi_dstar_deltaphi = acc['DimuDstar']['dimu_dstar_deltaphi'].value[~wrg_chg]
            jpsi_dstar_deltapt = acc['DimuDstar']['dimu_dstar_deltapt'].value[~wrg_chg]

        
        ## Applying weighs

        """ dstar_mass = np.repeat(dstar_mass, xsec_weight)
        dstar_d0dl = np.repeat(dstar_d0dl, xsec_weight)
        dstar_d0dlsig = np.repeat(dstar_d0dlsig, xsec_weight)
        all_asso_jpsi_mass12 = np.repeat(all_asso_jpsi_mass, xsec_weight)
        all_asso_jpsi_pt = np.repeat(all_asso_jpsi_pt, xsec_weight)
        all_asso_jpsi_dl = np.repeat(all_asso_jpsi_dl, xsec_weight)
        all_asso_jpsi_dl_err = np.repeat(all_asso_jpsi_dl_err, xsec_weight)
        jpsi_dstar_mass = np.repeat(jpsi_dstar_mass, xsec_weight)
        jpsi_dstar_deltarap = np.repeat(jpsi_dstar_deltarap, xsec_weight) """


    # If the variable condition is not give it will raise an exception
    else:
        raise Exception(f' The variable condition is {condition}, which is not valid! You should provide a valide one, either no_trigger or trigger!')
    
    # Creates the root file for reach input.
    if config.cate == '':
        if 'dps' in era or 'sps' in era:
            root_name = path_output + trigger_name  + config.cate  + '.root'
        else:
            root_name = path_output + era + '_' + trigger_name  + config.cate + '_' + b + '_' + str(bin[b][0]) + '_' + str(bin[b][1]) + '.root'
    else:
        if 'dps' in era or 'sps' in era:
            root_name = path_output + trigger_name  + '_' + config.cate  + '.root'
        else:
            root_name = path_output + era + '_' + trigger_name  + '_' + config.cate + '_' + b + '_' + str(bin[b][0]) + '_' + str(bin[b][1])  + '.root'

    with uproot3.recreate(root_name) as ds:
        
        
        if 'dps' in era or 'sps' in era:

            ds['asso'] = uproot3.newtree({"dstar_mass": "float32",
                                    "dstar_pt": "float32",
                                    "dstar_rap": "float32",
                                    "dstar_d0dl" : "float32",
                                    "dstar_d0dlsig" : "float32",
                                    "dstar_d0dca" : "float32",
                                    "jpsi_mass": "float32", 
                                    "jpsi_pt": "float32",
                                    "jpsi_rap": "float32",
                                    "jpsi_dl": "float32",
                                    "jpsi_dlErr": "float32",  
                                    "jpsi_dstar_mass" : "float32,",                                 
                                    "jpsi_dstar_deltarap": "float32", 
                                    "jpsi_dstar_deltaphi" : "float32", 
                                    "jpsi_dstar_deltapt" : "float32",
                                    "weight": "float32",})
            ds['asso'].extend({"dstar_mass": dstar_mass, 
                            "dstar_pt": dstar_pt, 
                            "dstar_rap": dstar_rap,   
                            "dstar_d0dl": dstar_d0dl,  
                            "dstar_d0dlsig": dstar_d0dlsig, 
                            "dstar_d0dca" : dstar_d0dca,
                            "jpsi_mass": all_asso_jpsi_mass, 
                            "jpsi_pt": all_asso_jpsi_pt, 
                            "jpsi_rap": all_asso_jpsi_rap,
                            "jpsi_dl": all_asso_jpsi_dl,
                            "jpsi_dlErr": all_asso_jpsi_dl_err,
                            "jpsi_dstar_mass": jpsi_dstar_mass,                        
                            "jpsi_dstar_deltarap": jpsi_dstar_deltarap,
                            "jpsi_dstar_deltaphi": jpsi_dstar_deltaphi,
                            "jpsi_dstar_deltapt": jpsi_dstar_deltapt,
                            "weight": weight,})
        
        else:
            ds['asso'] = uproot3.newtree({"dstar_mass": "float32",
                                    "dstar_pt": "float32",
                                    "dstar_rap": "float32",
                                    "dstar_phi": "float32",
                                    "dstar_d0dl" : "float32",
                                    "dstar_d0dlsig" : "float32",
                                    "dstar_d0dca" : "float32",
                                    "jpsi_mass": "float32", 
                                    "jpsi_pt": "float32",
                                    "jpsi_rap": "float32",
                                    "jpsi_phi": "float32",
                                    "jpsi_dl": "float32",
                                    "jpsi_dlErr": "float32",
                                    "jpsi_dstar_mass": "float32",
                                    "jpsi_dstar_pt" : "float32",
                                    "jpsi_dstar_deltarap": "float32",
                                    "jpsi_dstar_deltaphi": "float32",
                                    "jpsi_dstar_deltapt": "float32", 
                                    })
            ds['asso'].extend({"dstar_mass": dstar_mass, 
                            "dstar_pt": dstar_pt, 
                            "dstar_rap": dstar_rap, 
                            "dstar_phi": dstar_phi,   
                            "dstar_d0dl": dstar_d0dl,  
                            "dstar_d0dlsig": dstar_d0dlsig, 
                            "dstar_d0dca" : dstar_d0dca,
                            "jpsi_mass": all_asso_jpsi_mass, 
                            "jpsi_pt": all_asso_jpsi_pt, 
                            "jpsi_rap": all_asso_jpsi_rap,
                            "jpsi_phi": all_asso_jpsi_phi,
                            "jpsi_dl": all_asso_jpsi_dl,
                            "jpsi_dlErr": all_asso_jpsi_dl_err,
                            "jpsi_dstar_mass": jpsi_dstar_mass, 
                            "jpsi_dstar_pt": jpsi_dstar_pt, 
                            "jpsi_dstar_deltarap": jpsi_dstar_deltarap,
                            "jpsi_dstar_deltaphi": jpsi_dstar_deltaphi,
                            "jpsi_dstar_deltapt": jpsi_dstar_deltapt,
                            })

if __name__ == '__main__':

    '''
    Main function. In the end it will create root files with the needed information to
    perform the fits
    '''

    # Takes a list with eras to be runned
    era_list= config.era_list
    # Path to the files
    main_path = config.main_path
    # bins
    bin = config.bin

    # Loop over the era list defined on config_trigger_procesor 
    for b in bin:   
        for era in era_list:

            # Built the path to files with trigger applied
            if 'dps' in era or 'sps' in era:
                path_merged_data = main_path  + '/' + era + '/' + 'merged_data/'
                print('Reading files from:')
                print(path_merged_data) 
            else:
                path_merged_data = main_path  + '/' + era + '/' + 'merged_data/trigger' + '/' + config.cate 
                print('Reading files from:')
                print(path_merged_data)

            # Analysis condition: trigger or no_trigger
            condition = config.condition
            
            # Calls load_accumulator function to load the accumulator
            acc = load_accumulator(path_merged_data, era, condition, b)

            # Path to store the root file
            path_output = config.path_output
            print(f'Creating files on:')
            print(path_output)

            # Create the root files
            create_root(acc, path_output, era, b, condition)

""" import os
main_path = '/home/mabarros/Analysis_2018/OniaOpenCharmRun2ULAna/output/Charmonium_2018/RunA/merged_data'
files = []
with os.scandir(main_path) as it:
    for file in it:
        if file.name.endswith('.coffea') and (file.stat().st_size != 0):
            files.append(file.path)

print(files) """




