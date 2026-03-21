import numpy as np
from sunpy.map import Map as sm
import glob
from iris_obj.utilities import utilities as utils
from Functions.sunpy_map_cut import sunpy_map_cut
import astropy.units as u
import matplotlib.pyplot as plt
from Functions.utilities import get_extent
import os
import logging
logging.getLogger('sunpy').setLevel(logging.WARNING)
logging.getLogger('sunpy.map.mapbase').setLevel(logging.WARNING)
from sunpy.map import Map as sm

def compute_shift_from_template(aia_map, sji_map_resampled, bottom_left, top_right):
    """
    Computes pixel shift between SJI and AIA map using template matching.

    Parameters:
        aia_map (sunpy.map.Map): Reference AIA map (low-res)
        sji_map_resampled (sunpy.map.Map): Resampled SJI map to AIA resolution
        bottom_left (list or tuple): [x_arcsec, y_arcsec] of template bottom-left corner
        top_right (list or tuple): [x_arcsec, y_arcsec] of template top-right corner

    Returns:
        dx (int): pixel shift along x (columns)
        dy (int): pixel shift along y (rows)
    """
    from skimage.feature import match_template
    import numpy as np
    from Functions.sunpy_map_cut import sunpy_map_cut

    # Step 1: Cut template from AIA map
    template = sunpy_map_cut(aia_map, bottom_left, top_right)

    # Step 2: Match template in SJI map (resampled) and AIA map
    corr1 = match_template(sji_map_resampled.data, template.data)
    y1, x1 = np.unravel_index(np.argmax(corr1), corr1.shape)

    corr2 = match_template(aia_map.data, template.data)
    y2, x2 = np.unravel_index(np.argmax(corr2), corr2.shape)

    # Step 3: Compute pixel shifts (dx = x2 - x1, dy = y2 - y1)
    dx = x2 - x1
    dy = y2 - y1

    return int(dx), int(dy)




def shift_image(data, dx, dy):
    """
    Shift an image by integer dx (columns) and dy (rows) with zero-padding.
    """
    import numpy as np
    import copy
    from sunpy.map import Map
    from astropy.units import Quantity


    shifted = np.roll(data, dx, axis=1)
    if dx > 0:
        shifted[:, :dx] = 0
    elif dx < 0:
        shifted[:, dx:] = 0

    shifted = np.roll(shifted, dy, axis=0)
    if dy > 0:
        shifted[:dy, :] = 0
    elif dy < 0:
        shifted[dy:, :] = 0

    return shifted

def align_sji_maps_from_shift(dx, dy, sji_map_low_res, sji_map_high_res, factor: int):
    """
    Aligns both low-res and high-res SJI maps based on shifts (dx, dy) computed at low-res scale.
    
    Parameters:
        dx, dy: shift in pixels (low-res)
        sji_map_low_res: downsampled SunPy map of SJI (same scale as AIA)
        sji_map_high_res: original high-res SJI map
        factor: resolution factor (high_res = low_res * factor)
    
    Returns:
        aligned_sji_map_low_res: shifted low-res map (SunPy Map)
        aligned_sji_map_high_res: shifted high-res map (SunPy Map)
    """
    DX = int(np.rint(dx * factor))
    DY = int(np.rint(dy * factor))

    # Align low-res map
    shifted_low_data = shift_image(sji_map_low_res.data, dx, dy)
    aligned_sji_map_low_res = sm(shifted_low_data, sji_map_low_res.meta)

    # Align high-res map
    shifted_high_data = shift_image(sji_map_high_res.data, DX, DY)
    aligned_sji_map_high_res = sm(shifted_high_data, sji_map_high_res.meta)

    return aligned_sji_map_low_res, aligned_sji_map_high_res



if __name__=="__main__":

    d = 'D046'
    files1600 = sorted(glob.glob(f"./data_av_cad/{d}/aia_prepped1600/*.fits"))
    files_sji_low_res = sorted(glob.glob(f"./{d}/SJI_FILES_0.6_arcsec/*.fits"))
    files_sji_2832_low_res = sorted(glob.glob(f"./{d}/SJI_FILES_2832_0.6_arcsec/*.fits"))
    files_sji_high_res = sorted(glob.glob(f"./{d}/SJI_FILES/*.fits"))
    files_sji_2832_high_res = sorted(glob.glob(f"./{d}/SJI_FILES_2832/*.fits"))

    times1600 = np.load(f"./TIMES/{d}/aia1600_times.npy",allow_pickle=True)
    times_sji = np.load(f"./TIMES/{d}/sji_times.npy",allow_pickle=True)
    times_sji_2832 = np.load(f"./TIMES/{d}/sji_2832_times.npy",allow_pickle=True)


    BLTR = {

        'D042':{
            'bl' : [-40,320],
            'tr' : [50,410]
        },
        'D044':{
            'bl' : [-20,320],
            'tr' : [70,420]
        },
        'D046':{
            'bl' : [-20,320],
            'tr' : [80,420]
        },
        'D048':{
            'bl' : [380,320],
            'tr' : [470,400]
        }
    }

    # D046
    bl = BLTR[d]['bl']
    tr = BLTR[d]['tr']


    # # # D044
    # bl = [-20,320]
    # tr = [70,420]

    # # # D042

    # bl = [-40,320]
    # tr = [50,410]

    # # D048
    # bl = [380,320]
    # tr = [470,400]

    save_dir = f"./colaigned_sjis/{d}"
    dir_sji_1400 = os.path.join(save_dir,'1400')
    dir_sji_2832 = os.path.join(save_dir,'2832')
    os.makedirs(dir_sji_1400,exist_ok=True)
    os.makedirs(dir_sji_2832,exist_ok=True)

    XSHIFTS = []
    YSHIFTS = []
    prev_xshift = 1*u.pix
    prev_yshift = 1*u.pix


    for i,t_sji in enumerate(times_sji[0:1]):
        t_1600_ind = utils.get_nearest_time_index(times1600,t_sji)
        t_sji_2832_ind = utils.get_nearest_time_index(times_sji_2832,t_sji)

        file_aia = files1600[t_1600_ind]
        file_sji_low_res = files_sji_low_res[i]
        file_sji_high_res = files_sji_high_res[i]

        file_sji_2832_low_res = files_sji_2832_low_res[t_sji_2832_ind]
        file_sji_2832_high_res = files_sji_2832_high_res[t_sji_2832_ind]

        m_sji_low_res = sm(file_sji_low_res)
        m_sji_high_res = sm(file_sji_high_res)
        m_aia = sm(file_aia)

        m_sji_2832_low_res = sm(file_sji_2832_low_res)
        m_sji_2832_high_res = sm(file_sji_2832_high_res)


        m_sji_low_res_cut = sunpy_map_cut(m_sji_low_res,bl,tr)
        m_sji_high_res_cut = sunpy_map_cut(m_sji_high_res,bl,tr)

        m_aia_cut = sunpy_map_cut(m_aia,bl,tr)
        m_sji_2832_low_res_cut = sunpy_map_cut(m_sji_2832_low_res,bl,tr)
        m_sji_2832_high_res_cut = sunpy_map_cut(m_sji_2832_high_res,bl,tr)


        factor1 = (m_sji_low_res.scale[0]/m_sji_high_res.scale[0]).value
        factor2 = (m_sji_2832_low_res.scale[0]/m_sji_2832_high_res.scale[0]).value


        dx = 5
        dy = 5
        bl_ = [bl[0]+dx,bl[1]+dy]
        tr_ = [tr[0]-dx,tr[1]-dy]

        xshift , yshift = compute_shift_from_template(m_aia_cut,m_sji_low_res_cut,bl_,tr_)

        aligned_sji_map_low_res, aligned_sji_map_high_res = align_sji_maps_from_shift(
            xshift,yshift,m_sji_low_res,m_sji_high_res,factor1
        )


        AL_aia = sunpy_map_cut(m_aia_cut,bl_,tr_)
        AL_sji = sunpy_map_cut(aligned_sji_map_high_res,bl_,tr_)

        fig1= plt.figure()
        ax1 = fig1.add_subplot(1,2,1)
        ax2 = fig1.add_subplot(1,2,2)

        im1 = ax1.imshow(AL_aia.data,origin="lower",extent=get_extent(AL_aia),vmin=0,vmax=150)
        im2 = ax2.imshow(AL_sji.data,origin="lower",extent=get_extent(AL_sji),vmin=0,vmax=150)

        plt.show()