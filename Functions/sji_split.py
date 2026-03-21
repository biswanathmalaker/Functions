"""
sji_split.py

This module contains utility functions for splitting IRIS SJI datacubes (e.g., 1400/2832 Å) into individual SunPy map files,
rotating and aligning them, applying cropping, and saving the outputs.

Author: [Biswanath Malaker]  
Date: [2025-08-06]  
Usage: For batch processing of IRIS data for scientific analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
import sunpy.map
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from sunpy.map import Map as sm
from Functions.sunpy_map_cut import sunpy_map_cut
import warnings
warnings.filterwarnings("ignore")

def split_sjicube_to_maps(sji_file):
    """
    Splits a 3D IRIS SJI datacube into a list of 2D SunPy maps.

    Parameters:
        sji_file (str): Path to the SJI FITS file.

    Returns:
        List[sunpy.map.Map]: List of individual 2D maps with appropriate metadata.
    """
    hduls = fits.open(sji_file)
    data_cube = hduls[0].data
    header = hduls[0].header
    header2 = hduls[1].header
    data2 = hduls[1].data

    TIME = data2[:, header2['TIME']]
    EXPTIMES = data2[:, header2['EXPTIMES']]
    XCENIX = data2[:, header2['XCENIX']]
    YCENIX = data2[:, header2['YCENIX']]
    PC1_1IX = data2[:, header2['PC1_1IX']]
    PC1_2IX = data2[:, header2['PC1_2IX']]
    PC2_1IX = data2[:, header2['PC2_1IX']]
    PC2_2IX = data2[:, header2['PC2_2IX']]
    PC3_1IX = data2[:, header2['PC3_1IX']]
    PC3_2IX = data2[:, header2['PC3_2IX']]
    SLTPX1IX = data2[:, header2['SLTPX1IX']]
    SLTPX2IX = data2[:, header2['SLTPX2IX']]

    t0 = Time(header['STARTOBS'])
    maps = []

    for i in range(data_cube.shape[0]):
        hdr_2d = header.copy()
        hdr_2d['NAXIS'] = 2
        frame_time = t0 + TIME[i] * u.s
        hdr_2d['DATE_OBS'] = frame_time.isot
        hdr_2d['EXPTIME'] = EXPTIMES[i]
        hdr_2d['XCEN'] = XCENIX[i]
        hdr_2d['YCEN'] = YCENIX[i]
        hdr_2d['PC1_1'] = PC1_1IX[i]
        hdr_2d['PC1_2'] = PC1_2IX[i]
        hdr_2d['PC2_1'] = PC2_1IX[i]
        hdr_2d['PC2_2'] = PC2_2IX[i]
        hdr_2d['PC3_1'] = PC3_1IX[i]
        hdr_2d['PC3_2'] = PC3_2IX[i]
        hdr_2d['SLTPX1'] = SLTPX1IX[i]
        hdr_2d['SLTPX2'] = SLTPX2IX[i]

        for key in ['NAXIS3', 'CTYPE3', 'CUNIT3', 'CRPIX3', 'CRVAL3', 'CDELT3']:
            hdr_2d.pop(key, None)

        img = data_cube[i]
        m = sm(img, hdr_2d)
        maps.append(m)

    return maps

def rotate_and_add_slt(m):
    """
    Rotates a SunPy map and adds the slit position to the header.

    Parameters:
        m (sunpy.map.Map): Input map.

    Returns:
        sunpy.map.Map: Rotated map with slit info.
    """
    m_rotated = m.rotate(order=0)
    sltpx1 = m_rotated.fits_header['SLTPX1']
    sltpx2 = m_rotated.fits_header['SLTPX2']
    slt = m_rotated.pixel_to_world(sltpx1 * u.pix, sltpx2 * u.pix)
    hd_old = m_rotated.fits_header
    hd_old['SLT1'] = slt.Tx.value
    hd_old['SLT2'] = slt.Ty.value
    return sm((m_rotated.data, hd_old))

def fix_sltpx_pos(m):
    """
    Updates SLTPX1/SLTPX2 from slit world coordinates (SLT1/SLT2).

    Parameters:
        m (sunpy.map.Map): Input map with SLT1/SLT2.

    Returns:
        sunpy.map.Map: Map with updated slit pixel coordinates.
    """
    hd_new = m.fits_header
    S = SkyCoord(hd_new['SLT1'] * u.arcsec, hd_new['SLT2'] * u.arcsec, frame=m.coordinate_frame)
    new_slt_px = m.world_to_pixel(S)
    hd_new['SLTPX1'] = new_slt_px.x.value
    hd_new['SLTPX2'] = new_slt_px.y.value
    return sm((m.data, hd_new))

def cut_map(m, bl, tr):
    """
    Crops a map using bottom-left and top-right arcsec coordinates and updates slit.

    Parameters:
        m (sunpy.map.Map): Input map
        bl (list): Bottom-left [x, y] in arcsec
        tr (list): Top-right [x, y] in arcsec

    Returns:
        sunpy.map.Map: Cropped and updated map.
    """
    return fix_sltpx_pos(sunpy_map_cut(m, bl, tr))

def fix_splitted_sji(maps, bl, tr):
    """
    Applies rotation, slit correction, and cropping to a list of SJI maps.

    Parameters:
        maps (list): List of SunPy maps from split_sjicube_to_maps
        bl (list): Bottom-left [x, y] in arcsec
        tr (list): Top-right [x, y] in arcsec

    Returns:
        list: List of corrected SunPy maps.
    """
    return [cut_map(rotate_and_add_slt(m), bl, tr) for m in maps]

def save_fixed_splitted_maps(maps, output_dir):
    """
    Saves each map as a FITS file named by its DATE_OBS.

    Parameters:
        maps (list): List of SunPy maps
        output_dir (str): Directory to save outputs
    """
    os.makedirs(output_dir, exist_ok=True)
    for m in maps:
        file_name = m.fits_header['DATE_OBS'] + '.fits'
        file_path = os.path.join(output_dir, file_name)
        m.save(file_path, overwrite=True)
        print(f'{file_path} saved!')

def find_bltr(sji_file):
    """
    Visual aid to help manually identify the crop region in SJI data.

    Parameters:
        sji_file (str): Path to the SJI FITS file
    """
    hdu = fits.open(sji_file)[0]
    wcs = WCS(hdu.header).dropaxis(-1)
    fig = plt.figure()
    ax0 = fig.add_subplot(1, 2, 1, projection=wcs)
    ax1 = fig.add_subplot(1, 2, 2, projection=wcs)
    ax0.imshow(hdu.data[0] / hdu.header['exptime'], origin="lower", vmin=0, vmax=20)
    ax1.imshow(hdu.data[-1] / hdu.header['exptime'], origin="lower", vmin=0, vmax=20)
    plt.show()

if __name__ == "__main__":
    import glob

    # === USAGE EXAMPLE ===
    D = "D048"
    sji_files = glob.glob(f"./{D}/SJI_FILE/*.fits")
    sji_file = sorted(sji_files)[0]

    # find_bltr(sji_file)  # Manually determine bottom-left, top-right

    BLTR = {
        'D042': {'bl': [-60, 310], 'tr': [70, 420]},
        'D044': {'bl': [-40, 310], 'tr': [90, 425]},
        'D046': {'bl': [-30, 315], 'tr': [100, 430]},
        'D048': {'bl': [360, 300], 'tr': [490, 410]}
    }

    bl = BLTR[D]['bl']
    tr = BLTR[D]['tr']
    out_dir = f"./{D}/SJI_FILES_test"

    maps0 = split_sjicube_to_maps(sji_file)
    maps1 = fix_splitted_sji(maps0, bl, tr)
    save_fixed_splitted_maps(maps1, out_dir)


