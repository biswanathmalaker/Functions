import tarfile
import os
import glob
import time


def de_tar(tar_files_dir,dump_dir,hmi=False):
    """
    e.g. 
        tar_files_dir is the directory where the tar files are residing.\n
        dump_dir = './data'\n
        if dump_dir = './data then all files will be dumped in ./data/{wave} directory.\n

    """
    tar_files = glob.glob(f"{tar_files_dir}/*.tar")
    tar_files = sorted(tar_files)

    for i,tar_file in enumerate(tar_files):

        file = tarfile.open(tar_file)

        for f in file.getmembers():
            if ".fits" in f.name:
                try:
                    wave = f.name.split(".")[4]
                    if hmi:
                        wave = f.name.split(".")[1]
                    extract_dir = extract_dir = f"{dump_dir}/{wave}"
                    if os.path.isdir(extract_dir):
                        pass
                    else:
                        os.makedirs(extract_dir)

                    file.extract(f,path=extract_dir)
                except Exception as error:
                    print(error)

        file.close()
        print(f"{i+1}.{tar_file} done.")
        



