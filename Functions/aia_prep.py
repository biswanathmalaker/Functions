import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

import sunpy.map
from sunpy.map import Map as sm
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time
from astropy.utils.data import download_file

from aiapy.calibrate import register, fix_observer_location

"""
Functions for updating header keywords based on pointing table data.
"""

import copy
import warnings

import numpy as np
import astropy.time
import astropy.units as u
from aiapy.util.exceptions import AiapyUserWarning
from Functions.utilities import get_extent
from Functions.sunpy_map_cut import sunpy_map_cut



def update_pointing(smap, pointing_table=None):
    """
    Update pointing information in the `smap` header using a pointing table.

    Parameters
    ----------
    smap : `~sunpy.map.sources.sdo.AIAMap`
        Solar Dynamics Observatory map.
    pointing_table : `~astropy.table.QTable`, optional
        Table of pointing information. If not provided, a table will
        be retrieved for the relevant time range.

    Returns
    -------
    `~sunpy.map.sources.sdo.AIAMap`
        Updated map with corrected pointing metadata.
    """
    # Ensure the input map is a full-resolution, full-disk image
    # if not contains_full_disk(smap):
    #     raise ValueError("Input map must be a full-disk image.")
    # if smap.dimensions != (4096 * u.pixel, 4096 * u.pixel):
    #     raise ValueError("Input map must be at 4096x4096 resolution.")

    # Retrieve pointing table if not provided
    # if pointing_table is None:
    #     pointing_table = get_pointing_table(smap.date - 12 * u.h, smap.date + 12 * u.h)

    # Get observation time and locate the appropriate row in the pointing table
    t_obs = smap.meta.get("T_OBS", smap.date)
    t_obs = astropy.time.Time(t_obs)
    valid_rows = np.logical_and(
        t_obs >= pointing_table["T_START"], t_obs < pointing_table["T_STOP"]
    )
    # if not valid_rows.any():
    #     raise IndexError(f"No matching pointing table entry for T_OBS={t_obs}.")

    # Extract nearest entry
    nearest_idx = np.where(valid_rows)[0][0]
    wavelength_str = f"{smap.wavelength.to(u.angstrom).value:03.0f}"
    new_meta = copy.deepcopy(smap.meta)

    # Extract pointing parameters
    x0 = pointing_table[f"A_{wavelength_str}_X0"][nearest_idx]
    y0 = pointing_table[f"A_{wavelength_str}_Y0"][nearest_idx]
    cdelt = pointing_table[f"A_{wavelength_str}_IMSCALE"][nearest_idx]
    crota2 = pointing_table[f"A_{wavelength_str}_INSTROT"][nearest_idx]+smap.meta.get("SAT_ROT", 0)

    # Update metadata
    for key, value in [
        ("crpix1", x0 + 1), ("crpix2", y0 + 1), ("cdelt1", cdelt),
        ("cdelt2", cdelt), ("crota2", crota2), ("x0_mp", x0), ("y0_mp", y0),
    ]:
        if not np.isnan(value):
            new_meta[key] = value
        else:
            warnings.warn(f"Missing value for {key}. Skipping update.", AiapyUserWarning)

    # Remove existing PCi_j matrix keys
    for key in ["PC1_1", "PC1_2", "PC2_1", "PC2_2"]:
        new_meta.pop(key, None)

    return smap._new_instance(smap.data, new_meta, plot_settings=smap.plot_settings, mask=smap.mask)


# --- 1. Pointing Table Management ---

def fetch_master_pointing(save_dir = "./"):
    """Downloads the master pointing file if not present locally."""
    url="https://aia.lmsal.com/public/master_aia_pointing3h.csv"
    os.makedirs(save_dir,exist_ok=True)
    master_file_path = os.path.join(save_dir ,"master_aia_pointing3h.csv")
    if not os.path.exists(master_file_path):
        print(f"Downloading master pointing table from {url}...")
        tmp_file = download_file(url, cache=True)
        import shutil
        shutil.copy(tmp_file, master_file_path)
    return master_file_path

def write_pointing_table(master_file_path, start_date, end_date, out_path):
    """Filters the master CSV for a specific time range."""
    dt_start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

    pointing_table = Table.read(master_file_path, format='csv')
    # Convert to Time objects for comparison
    t_start_col = Time(pd.to_datetime(pointing_table["T_START"]))
    t_stop_col = Time(pd.to_datetime(pointing_table["T_STOP"]))

    # Buffer of 6 hours to ensure coverage
    mask = (t_start_col >= Time(dt_start - relativedelta(hours=6))) & \
           (t_stop_col <= Time(dt_end + relativedelta(hours=6)))

    rescaled_table = pointing_table[mask]
    rescaled_table.write(out_path, overwrite=True)
    return {"message": f"{out_path} saved", "count": len(rescaled_table)}

# --- 2. Image Processing Logic ---

def cut2full(m):
    """Embeds a cutout map into a full 4096x4096nd-array for processing."""
    new_data = np.zeros((4096, 4096))
    header = m.meta.copy()

    data_cut = m.data
    ny, nx = data_cut.shape

    # Calculate pixel indices based on the metadata added during cutout creation
    # Note: Ensure 'X0_MP' and 'Y0_MP' exist in your header
    x0 = int(header['X0_MP'] - (header['crpix1'] - 1))
    y0 = int(header['Y0_MP'] - (header['crpix2'] - 1))

    header['CRPIX1'] = header['X0_MP'] - 1
    header['CRPIX2'] = header['Y0_MP'] - 1 
    
    new_data[y0:y0+ny, x0:x0+nx] = data_cut
    return sm(new_data, header)

def aia_prep(m, pointing_table):
    """Applies updated pointing and registers (level 1 to level 1.5)."""
    # Assuming update_pointing is imported and functional
    m_updated = update_pointing(m, pointing_table=pointing_table)
    m_registered = register(m_updated, order=0)
    return m_registered


def prep_full(m_full, pointing_table):
    """Full workflow for a full."""

    m_full = fix_observer_location(m_full)
    m_prepped = aia_prep(m_full, pointing_table)
    return m_prepped


def prep_cutout(m, pointing_table):
    """Full workflow for a cutout: Unpad -> Prep -> Recut."""
    # Preserve original FOV coordinates
    bl = m.bottom_left_coord
    tr = m.top_right_coord
    
    # Add a small 5" buffer
    bl_x, bl_y = bl.Tx.value - 5, bl.Ty.value - 5
    tr_x, tr_y = tr.Tx.value + 5, tr.Ty.value + 5

    m_full = cut2full(m)
    m_full = fix_observer_location(m_full)
    m_prepped = aia_prep(m_full, pointing_table)
    
    # Recut using your custom function or sunpy's submap
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    
    submap_bottom_left = SkyCoord(bl_x*u.arcsec, bl_y*u.arcsec, frame=m_prepped.coordinate_frame)
    submap_top_right = SkyCoord(tr_x*u.arcsec, tr_y*u.arcsec, frame=m_prepped.coordinate_frame)
    
    return m_prepped.submap(submap_bottom_left, top_right=submap_top_right)



# Visualisation

import matplotlib.pyplot as plt
from astropy.visualization import ImageNormalize, LinearStretch

def VIS(original_cutout_path, prepped_cutout_path, original_full_path, prepped_full_path):
    from Functions.sunpy_map_cut import cut_one_map_from_another
    from Functions.utilities import get_extent
    from sunpy.map import Map as sm

    # 1. Load Maps
    m_orig_cut = sm(original_cutout_path)
    m_prep_cut = sm(prepped_cutout_path)
    m_orig_full = sm(original_full_path)
    m_prep_full = sm(prepped_full_path)

    # 2. Sync Field of View (preserving raw orientation)
    m_prep_cut_sync = cut_one_map_from_another(m_prep_cut, m_orig_cut)
    m_orig_full_sync = cut_one_map_from_another(m_orig_full, m_orig_cut)
    m_prep_full_sync = cut_one_map_from_another(m_prep_full, m_orig_cut)

    maps = [m_orig_cut, m_prep_cut_sync, m_orig_full_sync, m_prep_full_sync]
    titles = [
        "Original Cutout (Level 1)", 
        "Prepped Cutout (Level 1.5)",
        "Full Disk -> Cutout (Level 1)", 
        "Full Disk Prepped -> Cutout (Level 1.5)"
    ]

    # 3. Setup Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    fig.suptitle(f"AIA Prep Verification | {m_orig_cut.instrument} | {m_orig_cut.wavelength}", fontsize=14)
    
    # Standard normalization for solar features
    norm = ImageNormalize(vmin=40, vmax=350, stretch=LinearStretch())
    axes_flat = axes.flatten()

    for i, (m, ax) in enumerate(zip(maps, axes_flat)):
        # Using extent from your utility to keep spatial context on axes
        im = ax.imshow(m.data, origin="lower", extent=get_extent(m), 
                       norm=norm, cmap=m.cmap)
        
        ax.set_title(titles[i], fontsize=11)
        ax.set_xlabel("Arcsec")
        ax.set_ylabel("Arcsec")

    # Add one shared colorbar
    fig.colorbar(im, ax=axes, shrink=0.8, label='Intensity [DN/s]')

    plt.show()
    return fig


# --- 3. Execution & Visualization ---

if __name__ == "__main__":
    # Setup Data
    # master_path = fetch_master_pointing(save_dir="./master_pointing_dir")
    # write_pointing_table("./master_pointing_dir/pointing_table.csv", '2019-03-01 00:00:00', '2019-11-01 00:00:00', './master_pointing_dir/pointing_table.csv')
    
    
    # pt = Table.read('./master_pointing_dir/pointing_table.csv', format='csv')

    # file_full   = "./aia_full/aia.lev1_euv_12s.2019-03-22T000010Z.171.image_lev1.fits"
    # file_cutout = "./aia_cutout/aia.lev1_euv_12s.2019-03-21T235959Z.171.image.fits"

    # m_cutout = sm(file_cutout)
    # m_full = sm(file_full)

    
    # # Processing
    # m_cutout_prepped = prep_cutout(m_cutout, pt)
    # m_cutout_prepped.save('aia_prep.fits',overwrite=True)

    # m_full_prepped = prep_full(m_full, pt)
    # m_full_prepped.save('aia_prep_full.fits',overwrite=True)

    # Visualization

    file_full   = "./aia_full/aia.lev1_euv_12s.2019-03-22T000010Z.171.image_lev1.fits"
    file_cutout = "./aia_cutout/aia.lev1_euv_12s.2019-03-21T235959Z.171.image.fits"
    file_prepped_cut = 'aia_prep.fits'
    file_prepped_full = 'aia_prep_full.fits'
    VIS(file_cutout,file_prepped_cut,file_full,file_prepped_full)
