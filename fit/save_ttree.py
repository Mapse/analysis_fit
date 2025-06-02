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
        if 'sps' not in era_list[0] and 'dps' not in era_list[0]:
            with os.scandir(main_path) as it:
                for file in it:                
                    # Stores all other files finished with .coffea
                    if file.name.endswith('.coffea') and b[8:] in file.name and  (file.stat().st_size != 0):
                        files.append(file.path)
        else:
            with os.scandir(main_path) as it:
                for file in it:                
                    # Stores all other files finished with .coffea
                    if file.name.endswith('.coffea') and  (file.stat().st_size != 0):
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
        print(f'bin {bin}')
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

    # Takes the accumulator and the trigger name
    if splot:
        acc = accumulator
        trigger_name = ''
    else:
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

            #!!!! no need to take out wrong charge as it was already done (in real data we do this)

            # Takes wrong and right charge Dstars
            dstar_mass = acc['DimuDstar']['dstar_deltamr'].value
            dstar_pt = acc['DimuDstar']['dstar_pt'].value
            dstar_rap = acc['DimuDstar']['dstar_rap'].value
            dstar_phi = acc['DimuDstar']['dstar_phi'].value
            dstar_d0dlsig = acc['DimuDstar']['dstar_d0dlsig'].value
            dstar_d0dl = acc['DimuDstar']['dstar_d0dl'].value
            dstar_d0dca = acc['DimuDstar']['dstar_d0dca'].value

            ## Jpsi
            all_asso_jpsi_mass = acc['DimuDstar']['jpsi_mass'].value
            all_asso_jpsi_pt = acc['DimuDstar']['jpsi_pt'].value
            all_asso_jpsi_rap = acc['DimuDstar']['jpsi_rap'].value
            all_asso_jpsi_phi = acc['DimuDstar']['jpsi_phi'].value
            all_asso_jpsi_dl = acc['DimuDstar']['jpsi_dl'].value
            all_asso_jpsi_dl_err = acc['DimuDstar']['jpsi_dlErr'].value

            # DimuDstar           
            jpsi_dstar_mass = acc['DimuDstar']['dimu_dstar_mass'].value
            jpsi_dstar_pt = acc['DimuDstar']['dimu_dstar_pt'].value
            jpsi_dstar_deltarap = acc['DimuDstar']['dimu_dstar_deltarap'].value
            jpsi_dstar_deltaphi = acc['DimuDstar']['dimu_dstar_deltaphi'].value
            jpsi_dstar_deltapt = acc['DimuDstar']['dimu_dstar_deltapt'].value

            # Pileup, muon ID, and muon reco weights
            weight = acc['weight'].value
            print(f'weight: {weight}')
            
        elif 'splot' in era:
            print('working with splot file')
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
            jpsi_dstar_deltamass = acc['DimuDstar']['dimu_dstar_deltamass'].value[~wrg_chg]

    # If the variable condition is not give it will raise an exception
    else:
        raise Exception(f' The variable condition is {condition}, which is not valid! You should provide a valide one, either no_trigger or trigger!')
    
    # Creates the root file for reach input.
    if splot:
        root_name = path_output + config.splot_coffea[:config.splot_coffea.find('coffea')-1] + '_' + config.cate + '.root'

    else:
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

    if splot:

        # import uproot to write hist packages into root files.
        import uproot

        ## Takes the variables

        # Dstar delta mass
        dstar_mass = acc['JpsiDstar']['Dstar_deltamr'].sum('chg')
        dstar_mass_hist = dstar_mass.to_hist()

        # Dstar d0 dca
        dstar_d0dca = acc['JpsiDstar']['Dstar_D0dca'].sum('chg')
        dstar_d0dca_hist = dstar_d0dca.to_hist()

        # Jpsi pt 
        jpsi_pt = acc['JpsiDstar']['Jpsi_pt']
        jpsi_pt_hist = jpsi_pt.to_hist()

        # Jpsi dl 
        jpsi_dl = acc['JpsiDstar']['Jpsi_dl']
        jpsi_dl_hist = jpsi_dl.to_hist()

        # JpsiDstar inv mass
        jpsi_dstar_mass = acc['JpsiDstar']['JpsiDstar_mass']
        jpsi_dstar_mass_hist = jpsi_dstar_mass.to_hist()

        # JpsiDstar delta rapidity
        jpsi_dstar_deltarap = acc['JpsiDstar']['JpsiDstar_deltarap']
        jpsi_dstar_deltarap_hist = jpsi_dstar_deltarap.to_hist()

        
        with uproot.recreate(root_name) as ds:
           ds['dstar_mass'] = dstar_mass_hist
           ds['dstar_d0dca'] = dstar_d0dca_hist
           ds['jpsi_pt'] = jpsi_pt_hist
           ds['jpsi_dl'] = jpsi_dl_hist
           ds['jpsi_dstar_mass'] = jpsi_dstar_mass_hist
           ds['jpsi_dstar_deltarap'] = jpsi_dstar_deltarap_hist

    else:
        with uproot3.recreate(root_name) as ds:
            
            
            if 'dps' in era or 'sps' in era:

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
                                        "jpsi_dstar_mass" : "float32,",   
                                        "jpsi_dstar_pt" : "float32,",                                 
                                        "jpsi_dstar_deltarap": "float32", 
                                        "jpsi_dstar_deltaphi" : "float32", 
                                        "jpsi_dstar_deltapt" : "float32",
                                        #"jpsi_dstar_deltamass" : "float32",
                                        "weight": "float32",})
                ds['asso'].extend({"dstar_mass": dstar_mass, 
                                "dstar_pt": dstar_pt, 
                                "dstar_rap": dstar_rap,   
                                "dstar_phi": dstar_rap,   
                                "dstar_d0dl": dstar_d0dl,  
                                "dstar_d0dlsig": dstar_d0dlsig, 
                                "dstar_d0dca" : dstar_d0dca,
                                "jpsi_mass": all_asso_jpsi_mass, 
                                "jpsi_pt": all_asso_jpsi_pt, 
                                "jpsi_rap": all_asso_jpsi_rap,
                                "jpsi_phi": all_asso_jpsi_rap,
                                "jpsi_dl": all_asso_jpsi_dl,
                                "jpsi_dlErr": all_asso_jpsi_dl_err,
                                "jpsi_dstar_mass": jpsi_dstar_mass,    
                                "jpsi_dstar_pt" : jpsi_dstar_pt,                    
                                "jpsi_dstar_deltarap": jpsi_dstar_deltarap,
                                "jpsi_dstar_deltaphi": jpsi_dstar_deltaphi,
                                "jpsi_dstar_deltapt": jpsi_dstar_deltapt,
                                #"jpsi_dstar_deltamass": jpsi_dstar_deltamass,
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
                                        "jpsi_dstar_deltamass": "float32", 
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
                                "jpsi_dstar_deltamass": jpsi_dstar_deltamass,
                                })

if __name__ == '__main__':

    '''
    Main function. In the end it will create root files with the needed information to
    perform the fits
    '''
    # splots
    splot = config.splot
    # Takes a list with eras to be runned
    era_list= config.era_list
    # bins
    bin = config.bin

    if splot:

        path_merged_data = config.splot_path 
        print('Reading files from:')
        print(path_merged_data)
        # Analysis condition: trigger or no_trigger
        condition = config.condition
        
        
        # Calls load_accumulator function to load the accumulator
        acc = load(path_merged_data + '/'  + config.splot_coffea)

        # Path to store the root file
        path_output = config.path_output
        print(f'Creating files on:')
        print(path_output)

        # Create the root files
        create_root(acc, path_output, 'splot', bin, condition)
    else:
        # Loop over the era list defined on config_trigger_procesor 
        for b in bin:   
            for era in era_list:
                # Path to the files
                main_path = config.main_path
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