import os
import config_merge_root as config


def merge_file(path, end_name, final_name):
   
    files = []
    with os.scandir(path) as it:
        for file in it:
            # Stores all files finished with end_name
            if file.name.endswith(end_name) and (file.stat().st_size != 0):
                files.append(file.path)

    # Creates a string with all files to be merged to be provided
    # to the hadd command 
    files_merge = ''
    for f in files:
        files_merge = files_merge + ' ' + f
    # Uses system to call hadd command and merge the files.    
    os.system('hadd ' + final_name +  end_name +  files_merge)


if __name__ == '__main__':
    
    path = config.path
    end_name = config.end_name
    final_name = config.final_name

    merge_file(path, end_name, final_name)

