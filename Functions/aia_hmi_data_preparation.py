from sunpy.map import Map as sm
import matplotlib.pyplot as plt
import glob
import numpy as np
import astropy.units as u
import datetime
from dateutil.relativedelta import relativedelta
import copy
import os
import time


def get_warning_message(file_path):
    import sunpy.map
    import warnings

    # Enable all warnings for a moment to catch the specific warning message
    warnings.simplefilter("default")

    # Your SunPy Map creation code that triggers the warning
    m = sunpy.map.Map(file_path)

    # Now, catch the warning and print its message
    with warnings.catch_warnings(record=True) as w:
        m.verify()
        if w:
            print("Warning message:", w[0].message)

    # Disable warnings again
    warnings.simplefilter("ignore")


def extract_obs_date(file,return_datetime_obj = False):
    import datetime
    m = sm(file)
    hd = m.fits_header
    date_obs = hd['DATE-OBS']

    if return_datetime_obj:
        date_obj = datetime.datetime.strptime(date_obs,'%Y-%m-%dT%H:%M:%S.%f')
        return date_obj
    else:
        return date_obs


def mask_off_disc(m,substituted_value=0):
    """
    m is sunpy map
    """
    from sunpy.map.maputils import all_coordinates_from_map , coordinate_is_on_solar_disk
    all_coordinates = all_coordinates_from_map(m)
    mask = coordinate_is_on_solar_disk(all_coordinates)
    data = m.data
    data[~mask] = substituted_value
    new_m = sm((data,m.fits_header))

    return new_m


def split_array_of_times(times, dt, t0, t1):
    '''
    times are 1d array of datetime object
    dt is timedelta object
    t0 is the start time (datetime object)
    t1 is the end time (datetime object)
    '''
    times = np.array(times)

    t = copy.deepcopy(t0)
    Splitted_T = []
    Mid_t  = []
    while t < t1:
        cond = np.logical_and(times >= t, times < t + dt)
        Splitted_T.append(times[cond].tolist())
        Mid_t.append(t+dt/2)
        t = t + dt

    return Splitted_T,Mid_t


def get_equispaced_times(dt, t0, t1):
    '''
    dt is timedelta object
    t0 is the start time (datetime object)
    t1 is the end time (datetime object)
    '''
    t = copy.deepcopy(t0)
    del_t  = []
    while t < t1:

        del_t.append([t,t+dt])
        t = t + dt

    return del_t


def normalize_map_by_exposure_time(m,hmi_input = False):
    """
    m is tha sunpy map
    """
    if hmi_input:
        return m
    else:
        data = copy.deepcopy(m.data)
        hd = copy.deepcopy(m.fits_header)
        new_data = data/hd['exptime']
        hd['EXPTIME'] = 1.0
        m_new = sm((new_data,hd))

        return m_new


def Average_map(M,hmi_input=False):
    """
    Automatically nomalize to exposure time
    """
    for m in M:

        m = normalize_map_by_exposure_time(m,hmi_input=hmi_input)

        data1 = m.data
        data1[data1<=0.001]

        try:
            data+=data1
        except:
            data = data1

    data_av = data/len(M)

    hd = copy.deepcopy(m.fits_header)

    av_m = sm((data_av,hd))

    return av_m


def get_min_max_time(files:list,return_datetime_obj = True):
    """
    files is list of files.\n
    Usefulness : One can determine minimum and maximum time for \ntime binning
    using aia171 and hmi files together.
    """
    files = sorted(files)
    min_time = extract_obs_date(files[0],return_datetime_obj=return_datetime_obj)
    max_time = extract_obs_date(files[-1],return_datetime_obj=return_datetime_obj)

    return min_time , max_time


def prepare_files(files,del_T,hmi_input=False):
    times = [extract_obs_date(f,return_datetime_obj=True) for f in files]
    times  = np.array(times)
    for dT in del_T:
        try:
            sort_ind = np.logical_and(times>=dT[0],times<dT[-1])


            mid_t = dT[0] + (dT[-1]-dT[0])/2

            sorted_files = files[sort_ind].tolist()

            if len(sorted_files) != 0:  # Assuring some files are there.
                # Fix target directory

                data_dir = os.path.dirname(sorted_files[0]).replace("./data","./data_av")

                if not os.path.isdir(data_dir):
                    os.makedirs(data_dir)

                date_obs = mid_t.strftime("%Y-%m-%dT%H:%M:%S")

                file_name = date_obs+'.fits'

                file_path = os.path.join(data_dir,file_name)

                M = sm(sorted_files)

                if np.sum(sort_ind) == 1:
                    av_m = normalize_map_by_exposure_time(M,hmi_input=hmi_input)
                else:
                    av_m = Average_map(M,hmi_input=hmi_input)

                av_hd = copy.deepcopy(av_m.fits_header)

                av_hd['DATE-OBS'] =  date_obs

                av_m = sm((av_m.data,av_hd))

                if hmi_input:
                    av_m = mask_off_disc(av_m)

                av_m.save(file_path,overwrite=True)
        except Exception as error:
            print(f"{error} at {dT}")


if __name__ == "__main__":
    # get_min_max_time(files.tolist())


    # Select time interval to be considered for binning
    dt = datetime.timedelta(days=0,hours=0,minutes=1)       #*
    t0 = datetime.datetime(year=2019,month=6,day=29,hour=21,minute=59,second=35)    #*
    t1 = datetime.datetime(year=2019,month=6,day=30,hour=1,minute=00,second=35)     #*
    del_T = get_equispaced_times(dt,t0,t1)


    DIRS = ['hmi_data','94','131','171','193','211','304','335']

    for i,d in enumerate(DIRS):
        files = glob.glob(f"./data/T2/{d}/*.fits")      #*
        files = sorted(files)
        files = np.array(files)
        if i == 0:
            prepare_files(files,del_T,hmi_input=True)
        else:
            prepare_files(files,del_T,hmi_input=False)

        time.sleep(15)



