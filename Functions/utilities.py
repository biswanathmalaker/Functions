from sunpy.map import Map as sm
from sunpy.map.maputils import all_coordinates_from_map , coordinate_is_on_solar_disk
import astropy.units as u
import warnings
warnings.filterwarnings('ignore')
from astropy.io.fits.verify import VerifyWarning
warnings.simplefilter('ignore',category=VerifyWarning)
import numpy as np
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.wcs.utils import wcs_to_celestial_frame
from .normalize_arr import rescale_and_translate


def mask_off_limb(m,replaced_value = -100):
    hpc_coords = all_coordinates_from_map(m)
    mask = coordinate_is_on_solar_disk(hpc_coords)
    data = m.data
    data[~mask] =replaced_value
    masked_m = sm((data,m.fits_header))

    return masked_m


def aia_prep(file):
    import sunpy.map
    from aiapy.calibrate import register, update_pointing

    m = sunpy.map.Map(file)
    m_updated_pointing = update_pointing(m)


    m_registered = register(m_updated_pointing)
    
    return m_registered

def mask_disc(m,replaced_value = -100):
    hpc_coords = all_coordinates_from_map(m)
    mask = coordinate_is_on_solar_disk(hpc_coords)
    data = m.data
    data[mask] =replaced_value
    masked_m = sm((data,m.fits_header))

    return masked_m




def px2arcsec(m,px:list):
    l = m.pixel_to_world(px[0]*u.pix,px[1]*u.pix)
    return l.Tx.value,l.Ty.value

def px2arcsec1(m,px:list):
    """
    Uses extent rescaling method to get arsec.
    """
    extent = get_extent(m)
    s0,s1 = m.data.shape

    l0x = 0
    m0x = s1
    l1x = extent[0]
    m1x = extent[1]

    l0y = 0
    m0y = s0
    l1y = extent[2]
    m1y = extent[3]

    x = rescale_and_translate(l0x,m0x,l1x,m1x,px[0])
    y = rescale_and_translate(l0y,m0y,l1y,m1y,px[1])

    return [x,y]




def arcsec2px(m,coord:list):
    '''
    coord = [x,y] in [arcsec,arcsec]
    '''
    c = SkyCoord(coord[0]*u.arcsec,coord[1]*u.arcsec,frame=m.coordinate_frame)
    l = m.world_to_pixel(c)

    return int(np.rint(l.x.value)),int(np.rint(l.y.value))

 

def cut_data_hd(data,header,bottom_left,top_right):
    from astropy.wcs import WCS

    wcs = WCS(header)
    x0,y0 = arcsec2px(data,header,bottom_left)
    x1,y1 = arcsec2px(data,header,top_right)

    d1 = data[y0:y1,x0:x1]
    wcs1 = wcs[y0:y1,x0:x1]

    header.update(wcs1.to_header())

    return d1 , header

def get_extent(m):
    x0 = m.bottom_left_coord.Tx.value
    x1 = m.top_right_coord.Tx.value

    y0 = m.bottom_left_coord.Ty.value
    y1 = m.top_right_coord.Ty.value

    return [x0,x1,y0,y1]

def get_nearest_time_index(time_list , time):
    """
    time_list is a list of datetime object\n
    time is datetime object\n
    return index of the time_list nearest to t\n
    """
    import numpy as np

    time_list = np.array(time_list)
    dt = np.abs(time_list-time)
    i = np.argmin(dt)
    
    return i

if __name__=="__main__":
    from sunpy.map import Map as sm
    # file = './data/cut/aia.lev1_euv_12s.2019-06-30T235959Z.171.image.fits'
    # m = sm(file)
    # S = px2arcsec1(m,[200,100])
    # print(S)

