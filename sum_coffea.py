# This code is used to merge the coffea files that are produced from a condor processing
from coffea.util import save, load
from tqdm import tqdm
import os

# Function to create a list with all coffea files in a path
  
def merge_files(path, name, plc):


    files = []
    with os.scandir(path) as aux:
        for file in aux:
            if file.name.endswith('.coffea') and (file.stat().st_size != 0):
                files.append(file.path)
    # Takes the first to start the accumulator
    acc = load(files[0])    
    # Take the length of the list
    le_files = len(files) 

    for i in tqdm(range(1, le_files), desc="Processing", unit="files"):
        # Suns the accumulator for each file

        acc += load(files[i])
    save(acc, plc + '/' + name + '.coffea')
    # For accumulate the files
   
    print ("Finished")


if __name__ == '__main__':

    import config_sum_data as config

    cond = config.cond
    cate = config.cate
    
    for dt in config.cond:
        
        if dt == '2017' or dt == '2016-pre-VFP'  or dt == '2016-pos-VFP' or dt == '2018':
            ct = 1
            len_dt = len(cond[dt])
            path = cond[dt][-1] 
            for run in cond[dt]:
                if ct == len_dt: continue
                ct = ct + 1

                if cate == '':
                    #print('cp ' + run + '/*.coffea ' + path)
                    os.system('cp ' + run + '/*.coffea ' + path)
                    name = 'Charmonium_' + dt 
                else:
                    os.system('cp ' + run + '/' + cate + '/*.coffea ' + path) 
                    name = 'Charmonium_' + dt + '_' + cate
                    #print('cp ' + run + '/' + cate + '/*.coffea ' + path)
                     
            merge_files(path, name, dt)
            os.system('rm '+ dt + '/Run*.coffea')

        elif dt == 'DPS':
            
            ct = 1
            len_dt = len(cond[dt])
            
            for run in cond[dt]:
                #print(run + cate)
                print(cate)
                if ct == len_dt: continue
                ct = ct + 1

                bf = run.index('fit/data/')
                af = run.index('/merged_data')

                if cate == '':
                    print('empty')
                    name = 'DPS_' + run[bf+6:af]
                  
                else:
                    print('cate')
                    name = 'DPS' + '_' + cate

                plc = dt + '/' + run[bf+9:af]
                print('before merge')
                merge_files(run + cate, name, plc)


        elif dt == 'SPS':
           
            path = cond[dt][0] + cate

            bf = path.index('fit/data/')
            af = path.index('/merged_data')
            
            if cate == '':
                name = 'SPS'
                  
            else:
                name = 'SPS_' + cate
            plc = dt + '/' + path[bf+9:af-3]

            merge_files(path, name, plc)
        
        elif dt == 'bquark':
            path = cond[dt][0] + cate
            
            if cate == '':
                name = 'bquark'
                  
            else:
                name = 'bquark_' + cate
            #print(f'path: {path}')
            #print(f'name: {name}')
            #print(f'dt: {dt}')
            

            merge_files(path, name, dt) 
        else:
            print(f"{dt} is not registered in config_merge_data.py! Valid options: 2017, DPS, SPS, bquark")


""" import os
from coffea.util import load
import tqdm

files = []
path = '/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/OniaOpenCharmRun2ULAna/cross_section/2017/data_mc_comp/DPS/2017/30to50'
with os.scandir(path) as aux:
    for file in aux:
        if file.name.endswith('.coffea') and (file.stat().st_size != 0):
            files.append(file.path)
# Takes the first to start the accumulator
acc = load(files[0])    
# Take the lenaccgth of the list
le_files = len(files) 

for i in tqdm(range(1, le_files), desc="Processing", unit="files"):
    acc += load(files[i])

acc += load(files[1])
acc += load(files[2])
acc += load(files[3])
acc += load(files[4])
acc += load(files[5])
acc += load(files[6])
acc += load(files[7])
acc += load(files[8])
acc += load(files[9])
acc += load(files[10])
acc += load(files[11])
acc += load(files[12])
acc += load(files[13])
acc += load(files[14])
acc += load(files[15])
acc += load(files[16])
acc += load(files[17])
acc += load(files[18])
acc += load(files[19]) """