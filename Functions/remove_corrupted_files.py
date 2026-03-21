import os
import statistics


def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)

def remove_corrupted_files(files):
    """
    Remove files having size less and greater than 20% of mode size.
    """

    # remove corrupted files
    szs = [get_size(file,'mb') for file in files]

    mode = statistics.mode(szs)
    d_mode = mode/20    # 5% of mode
    for file in files:
        s = get_size(file,'mb')
        if s<mode-d_mode or s>mode+d_mode:
            os.remove(file)
            print(file , "removed")


def remove_corrupted_files1(files,s1,s2):
    """
    files having size less than s1 MB and greater than s2 MB  would be removed. 
    """

    # remove corrupted files
    szs = [get_size(file,'mb') for file in files]
    for file in files:
        s = get_size(file,'mb')
        if s<s1 or s>s2:
            os.remove(file)
            print(file , "removed")


def remove_corrupted_files2(files,s1):
    """
    files having size less than s1 MB would be removed. 
    """

    # remove corrupted files
    szs = [get_size(file,'mb') for file in files]
    for file in files:
        s = get_size(file,'mb')
        if s<s1:
            os.remove(file)
            print(file , "removed")

if __name__=="__main__":
    import glob
    files = glob.glob("./data/171/*.fits")
    files = sorted(files)

    remove_corrupted_files(files)
