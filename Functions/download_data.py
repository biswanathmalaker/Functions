
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
import datetime
import sunpy.map
from sunpy.net import attrs as a
from sunpy.net import jsoc
import time
from Functions.net import download_from_url
import os
from dateutil.relativedelta import relativedelta
import copy
from sunpy.net import Fido
from Functions.mails import mails

def download_aia_euv_data(t_start, t_end, extent, extra_pad=40, wavelength=171,cadance = 12*u.s, email='biswanath@iucaa.in'):
    """
    t_start --->    '2019-06-30T00:00'\n
    t_end   --->    '2019-06-30T00:05'\n
    cadance is astropy time unit.\n
    if wavelenth=None; all euv wavelenths will be provided.

    """
    xcen = (extent[1] + extent[0]) // 2
    ycen = (extent[3] + extent[2]) // 2
    fovx = extent[1] - extent[0] + extra_pad
    fovy = extent[3] - extent[2] + extra_pad

    client = jsoc.JSOCClient()

    bottom_left = SkyCoord((xcen - fovx // 2) * u.arcsec, (ycen - fovy // 2) * u.arcsec, frame='helioprojective', obstime=t_start, observer='earth')
    top_right = SkyCoord((xcen + fovx // 2) * u.arcsec, (ycen + fovy // 2) * u.arcsec, obstime=t_start, observer="earth", frame="helioprojective")

    cutout = a.jsoc.Cutout(bottom_left, top_right=top_right, tracking=False, nan_off_limb=False)
    
    try:
        if wavelength is None:
            q = client.search(
                a.Time(t_start, t_end),
                a.Sample(cadance),
                a.jsoc.Series('aia.lev1_euv_12s'),
                a.jsoc.Notify(email),
                a.jsoc.Segment("image"),
                cutout,
            )
        else:
            q = client.search(
                a.Time(t_start, t_end),
                a.Sample(cadance),
                a.jsoc.Series('aia.lev1_euv_12s'),
                a.Wavelength(wavelength*u.AA),
                a.jsoc.Notify(email),
                a.jsoc.Segment("image"),
                cutout,
            )

        requests = client.request_data(q, method='url-tar')

        return len(q), requests.id, requests.status
    except Exception as error:
        return error, None, None


def download_aia_euv_data_full(t_start, t_end,wavelength=171,cadance=12*u.s,email='biswanath@iucaa.in'):
    """
    t_start --->    '2019-06-30T00:00'\n
    t_end   --->    '2019-06-30T00:05'\n
    cadance is astropy time unit.\n
    if wavelenth=None; all euv wavelenths will be provided.

    """

    client = jsoc.JSOCClient()

    try:
        if wavelength is None:
            q = client.search(
                a.Time(t_start, t_end),
                a.Sample(cadance),
                a.jsoc.Series('aia.lev1_euv_12s'),
                a.jsoc.Notify(email),
                a.jsoc.Segment("image"),
            )
        else:
            q = client.search(
                a.Time(t_start, t_end),
                a.Sample(cadance),
                a.jsoc.Series('aia.lev1_euv_12s'),
                a.Wavelength(wavelength*u.AA),
                a.jsoc.Notify(email),
                a.jsoc.Segment("image"),
            )

        requests = client.request_data(q, method='url-tar')

        return len(q), requests.id, requests.status
    except Exception as error:
        return error, None, None


def download_hmi_data(t_start, t_end, extent, extra_pad=40,cadance=45*u.s, email='biswanath@iucaa.in'):
    """
    t_start --->    '2019-06-30T00:00'\n
    t_end   --->    '2019-06-30T00:05'\n
    cadance is astropy time unit.\n
    """

    xcen = (extent[1] + extent[0]) // 2
    ycen = (extent[3] + extent[2]) // 2
    fovx = extent[1] - extent[0] + extra_pad
    fovy = extent[3] - extent[2] + extra_pad

    client = jsoc.JSOCClient()

    bottom_left = SkyCoord((xcen - fovx // 2) * u.arcsec, (ycen - fovy // 2) * u.arcsec, frame='helioprojective', obstime=t_start, observer='earth')
    top_right = SkyCoord((xcen + fovx // 2) * u.arcsec, (ycen + fovy // 2) * u.arcsec, obstime=t_start, observer="earth", frame="helioprojective")

    cutout = a.jsoc.Cutout(bottom_left, top_right=top_right, tracking=False, nan_off_limb=False)
    
    try:
        q = client.search(
            a.Time(t_start, t_end),
            a.Sample(cadance),
            a.jsoc.Series('hmi.m_45s'),
            a.jsoc.Notify(email),
            a.jsoc.Segment("magnetogram"),
            a.Resolution('0.25'),
            cutout,
        )

        requests = client.request_data(q, method='url-tar')

        return len(q), requests.id, requests.status
    except Exception as error:
        return error, None, None


def download_hmi_data_full(t_start, t_end,cadance=45*u.s,email='biswanath@iucaa.in'):
    """
    t_start --->    '2019-06-30T00:00'\n
    t_end   --->    '2019-06-30T00:05'\n
    cadance is astropy time unit.\n
    """

    client = jsoc.JSOCClient()
    
    try:
        q = client.search(
            a.Time(t_start, t_end),
            a.Sample(cadance),
            a.jsoc.Series('hmi.m_45s'),
            a.jsoc.Notify(email),
            a.jsoc.Segment("magnetogram"),
            # a.Resolution('0.25'),
        )

        requests = client.request_data(q, method='url-tar')

        return len(q), requests.id, requests.status
    except Exception as error:
        return error, None, None


def download_suntoday_images(start_date , end_date , wavelengths:list=[171],download_directory='./suntoday_files'):
    """
    start_date and end_date are datetime object\n wavelengths are list of wavelengths\n
    download_directory ---> default = "./"
    """

    t0 = copy.deepcopy(start_date)
    Image_dates = [t0]
    while t0<end_date:
        t0+=relativedelta(days=1)
        Image_dates.append(t0)



    for wavelength in wavelengths:
        image_dir = download_directory + f'/{wavelength}'
        if not os.path.isdir(image_dir):
            os.makedirs(image_dir)
        for d in Image_dates:
            # print(d)
            url = d.strftime(f"https://suntoday.lmsal.com/sdomedia/SunInTime/%Y/%m/%d/f{wavelength:0>4}.jpg")
            file_name = d.strftime("%Y_%m_%d.jpg")
            file_path = os.path.join(image_dir,file_name)
            file = download_from_url(url,file_path)


def download_data_using_Fido(start_time,end_time,series='aia.lev1_euv_12s',wavelength=171*u.angstrom,cadance = 12*u.s, mail = mails[0] , download_path = './data/Fido/',overwrite=False , hmi=False):
    """
    Requires full modifications.\n
    start_time = '2024-02-22 20:00:00'\n
    end_time = '2024-02-23 01:00:00'\n
    available series = [
        \n'aia.lev1_uv_24s,
        \naia.lev1_euv_12s'
        \n]\n
    wavelength = 171*u.angstrom ; Astropy unit

    NOTE : If series = aia.lev1_uv_24s then wavelength must be 1600 , 1700 
    """
    if hmi:
        res = Fido.search(
            a.Time(start_time,end_time),
            a.jsoc.Series('hmi.m_45s'),
            a.Sample(cadance),
            a.jsoc.Segment("magnetogram"),
            a.jsoc.Notify(mail)
            )
    else:
        if wavelength == None:
            res = Fido.search(
                a.Time(start_time,end_time),
                a.Sample(cadance),
                a.jsoc.Series(series),
                a.jsoc.Segment("image"),
                a.jsoc.Notify(mail)
                )
        else:
            res = Fido.search(
                a.Time(start_time,end_time),
                a.jsoc.Series(series),
                a.Sample(cadance),
                a.Wavelength(wavelength),
                a.jsoc.Segment("image"),
                a.jsoc.Notify(mail)
                )


    downloaded = Fido.fetch(res,path=f'{download_path}', overwrite=overwrite)

    while(len(downloaded.errors)>0):
        downloaded = Fido.fetch(downloaded ,path=f'{download_path}', overwrite=overwrite)




def download_cutout_data_using_Fido(start_time,end_time,extent,extra_pad,series='aia.lev1_euv_12s',wavelength=171*u.angstrom,cadance = 12*u.s, mail = mails[0] , download_path = './data/Fido/',overwrite=False , hmi=False):
    """
    Requires full modifications.\n
    start_time = '2024-02-22 20:00:00'\n
    end_time = '2024-02-23 01:00:00'\n
    available series = [
        \n'aia.lev1_uv_24s,
        \naia.lev1_euv_12s'
        \n]\n
    wavelength = 171*u.angstrom ; Astropy unit

    NOTE : If series = aia.lev1_uv_24s then wavelength must be 1600 , 1700 
    """
    from astropy.time import Time
    t_start = Time(start_time, scale='utc', format='isot')

    xcen = (extent[1] + extent[0]) // 2
    ycen = (extent[3] + extent[2]) // 2
    fovx = extent[1] - extent[0] + extra_pad
    fovy = extent[3] - extent[2] + extra_pad

    # bottom_left = SkyCoord((xcen - fovx // 2) * u.arcsec, (ycen - fovy // 2) * u.arcsec, frame='helioprojective', obstime=t_start, observer='earth')
    # top_right = SkyCoord((xcen + fovx // 2) * u.arcsec, (ycen + fovy // 2) * u.arcsec, obstime=t_start, observer="earth", frame="helioprojective")

    bottom_left = SkyCoord(extent[0] * u.arcsec, extent[2] * u.arcsec, frame='helioprojective', obstime=t_start, observer='earth')
    top_right = SkyCoord(extent[1] * u.arcsec, extent[3] * u.arcsec, obstime=t_start, observer="earth", frame="helioprojective")
    
    cutout = a.jsoc.Cutout(bottom_left, top_right=top_right, tracking=False, nan_off_limb=False)
    if not hmi:
        cutout = a.jsoc.Cutout(bottom_left, top_right=top_right, tracking=False, nan_off_limb=False)
    else:
        cutout = a.jsoc.Cutout(bottom_left, top_right=top_right, tracking=False, nan_off_limb=True)

    if hmi:
        res = Fido.search(
            a.Time(start_time,end_time),
            a.jsoc.Series('hmi.m_45s'),
            a.Sample(cadance),
            a.jsoc.Segment("magnetogram"),
            a.jsoc.Notify(mail),
            cutout
            )
    else:
        if wavelength == None:
            res = Fido.search(
                a.Time(start_time,end_time),
                a.Sample(cadance),
                a.jsoc.Series(series),
                a.jsoc.Segment("image"),
                a.jsoc.Notify(mail),
                cutout
                )
        else:
            res = Fido.search(
                a.Time(start_time,end_time),
                a.jsoc.Series(series),
                a.Sample(cadance),
                a.Wavelength(wavelength),
                a.jsoc.Segment("image"),
                a.jsoc.Notify(mail),
                cutout
                )


    downloaded = Fido.fetch(res,path=f'{download_path}', overwrite=overwrite)

    while(len(downloaded.errors)>0):
        downloaded = Fido.fetch(downloaded ,path=f'{download_path}', overwrite=overwrite)




# query = Fido.search(
#     a.Time(start_time - 6*u.h, start_time + 6*u.h),
#     a.Wavelength(171*u.angstrom),
#     a.Sample(2*u.h),
#     a.jsoc.Series.aia_lev1_euv_12s,
#     a.jsoc.Notify(jsoc_email),
#     a.jsoc.Segment.image,
#     cutout,
# )
# print(query)

if __name__ == "__main__":
    t_start  = '2019-06-30T00:00'
    t_end    = '2019-07-02T00:00'

    start_time = '2024-02-22 20:00:00'
    end_time = '2024-02-22 20:05:00'
    # download_data_using_Fido(start_time , end_time)
    download_cutout_data_using_Fido(start_time,end_time,[-450,250,655,1105],0,wavelength=211*u.angstrom,cadance=24*u.s,mail=mails[0],download_path="./data/Fido/hmi1/",hmi=True)

    # l,r_id,r_st = download_hmi_data_full(t_start=t_start,t_end=t_end)
    # l,r_id,r_st = download_hmi_data(t_start=t_start,t_end=t_end,extent=[-500,500,800,1100],extra_pad=0)
    # l,r_id,r_st = download_aia_euv_data_full(t_start=t_start,t_end=t_end)
    # l,r_id,r_st = download_aia_euv_data(t_start=t_start,t_end=t_end,extent=[-220,-60,780,920])

    # print(l)
    # print(r_id)
    # print(r_st)

    # start_date = datetime.datetime(year=2018,month=9,day=10)
    # end_date = datetime.datetime(year=2018,month=9,day=14)

    # download_suntoday_images(start_date,end_date)
    pass



    


