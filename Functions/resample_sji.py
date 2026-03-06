"""
resample_sji.py

Module to resample IRIS SJI maps to a reference pixel scale (e.g., AIA's 0.6 arcsec/pixel),
with automatic slit coordinate correction and file saving.

This is essential for aligning SJI data with AIA/SDO observations.

Author: [Your Name]  
Date: [YYYY-MM-DD]

Usage:
    from Functions.resample_sji import resample_m

    resample_m(
        files=['./D046/SJI_FILES_2832/*.fits'],
        out_dir='./D046/SJI_FILES_2832_0.6_arcsec'
    )

"""

import os
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from sunpy.map import Map as sm

def fix_sltpx_pos(m):
    """
    Fix slit pixel position (SLTPX1, SLTPX2) from world coords (SLT1, SLT2).

    Parameters:
        m (sunpy.map.Map): Input map with SLT1, SLT2

    Returns:
        sunpy.map.Map: Updated map with fixed slit pixel coordinates
    """
    hd_new = m.fits_header
    slt1 = hd_new['SLT1']
    slt2 = hd_new['SLT2']

    S = SkyCoord(slt1 * u.arcsec, slt2 * u.arcsec, frame=m.coordinate_frame)
    new_slt_px = m.world_to_pixel(S)
    hd_new['SLTPX1'] = new_slt_px.x.value
    hd_new['SLTPX2'] = new_slt_px.y.value

    return sm((m.data, hd_new))

def resample_m(files, out_dir, ref_scale=0.6 * u.arcsec / u.pixel):
    """
    Resamples a list of IRIS SJI maps to a target pixel scale (default: 0.6 arcsec/pixel).

    Parameters:
        files (list): List of FITS files (SJI maps)
        out_dir (str): Output directory to save resampled maps
        ref_scale (Quantity): Target pixel scale (default 0.6 arcsec/pixel)

    Output:
        Saves resampled FITS maps in the specified directory with slit alignment fixed.
    """
    os.makedirs(out_dir, exist_ok=True)

    for file in files:
        m = sm(file)

        file_name = m.fits_header['DATE_OBS'] + '.fits'
        file_path = os.path.join(out_dir, file_name)

        z_x = float((ref_scale / m.scale[0]).value)
        z_y = float((ref_scale / m.scale[1]).value)

        s0 = int(np.rint(m.data.shape[0] / z_y))
        s1 = int(np.rint(m.data.shape[1] / z_x))

        m_reshaped = m.resample((s1, s0) * u.pix)
        m_new = fix_sltpx_pos(m_reshaped)

        m_new.save(file_path, overwrite=True)
        print(f"Saved: {file_path}")

if __name__ == "__main__":
    import glob
    import matplotlib.pyplot as plt
    from Functions.utilities import get_extent

    D = 'D046'
    files = sorted(glob.glob(f"./{D}/SJI_FILES_2832/*.fits"))
    out_dir = f"./{D}/SJI_FILES_2832_0.6_arcsec"

    resample_m(files, out_dir)

    # === OPTIONAL: Visual Preview ===
    # file = files[0].replace('SJI_FILES_2832', 'SJI_FILES_2832_0.6_arcsec')
    # m = sm(file)
    # fig, ax = plt.subplots()
    # im = ax.imshow(m.data / m.fits_header['exptime'], origin="lower", extent=get_extent(m), vmin=0, vmax=20)
    # ax.axvline(m.fits_header['SLT1'])
    # plt.title(m.fits_header['DATE_OBS'])
    # plt.show()
