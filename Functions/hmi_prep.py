"""
hmi_prep.py
───────────
Python equivalent of IDL's hmi_prep.pro for JSOC HMI cutout data.

Workflow:
    1. Build CRPIX time series from full-disc HMI files  (build_crpix_series)
    2. Load the saved series and create interpolators     (load_crpix_interpolators)
    3. Prep a cutout map                                  (hmi_cutout_prep)

Author  : Biswanath Malaker
Created : 2026
"""

import time
import glob
import numpy as np
import astropy.units as u
from astropy.time import Time
from scipy.interpolate import interp1d
from sunpy.map import Map as sm
from tqdm import tqdm
import os

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  Build CRPIX time series from full-disc HMI files
# ═══════════════════════════════════════════════════════════════════════════════

def build_crpix_series(full_disc_pattern,
                       save_dir='.',
                       sleep_every=30,
                       sleep_seconds=5):
    """
    Rotate each full-disc HMI file by 180° (to match JSOC convention) and
    record CRPIX1, CRPIX2, and observation time.  Results are saved as .npy
    files for later use by load_crpix_interpolators().

    Parameters
    ----------
    full_disc_pattern : str
        Glob pattern for full-disc HMI FITS files,
        e.g. './hmi_files_1d_cad/*.fits'
    save_dir : str
        Directory where T.npy, CRPIX1.npy, CRPIX2.npy are written.
    sleep_every : int
        Pause every N files to avoid memory/thermal issues (default 30).
    sleep_seconds : float
        Duration of each pause in seconds (default 5).

    Returns
    -------
    T, CRPIX1, CRPIX2 : np.ndarray
        Arrays of astropy Times and CRPIX values.
    """
    files = sorted(glob.glob(full_disc_pattern))
    if not files:
        raise FileNotFoundError(f'No files found matching: {full_disc_pattern}')

    T, CRPIX1, CRPIX2 = [], [], []

    for cnt, f in enumerate(tqdm(files, desc='Building CRPIX series')):
        m = sm(f)
        m = m.rotate(angle=180 * u.deg)

        T.append(m.date)
        CRPIX1.append(m.fits_header['CRPIX1'])
        CRPIX2.append(m.fits_header['CRPIX2'])

        if sleep_every and (cnt % sleep_every == 0) and cnt > 0:
            time.sleep(sleep_seconds)

    T      = np.array(T)
    CRPIX1 = np.array(CRPIX1)
    CRPIX2 = np.array(CRPIX2)
    os.makedirs(save_dir,exist_ok = True)
    np.save(f'{save_dir}/T.npy',      T,      allow_pickle=True)
    np.save(f'{save_dir}/CRPIX1.npy', CRPIX1, allow_pickle=True)
    np.save(f'{save_dir}/CRPIX2.npy', CRPIX2, allow_pickle=True)

    print(f'Saved T, CRPIX1, CRPIX2 to {save_dir}/')
    return T, CRPIX1, CRPIX2


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  Load saved series and build interpolators
# ═══════════════════════════════════════════════════════════════════════════════

def load_crpix_interpolators(T=None, CRPIX1=None, CRPIX2=None,
                              load_dir='.', kind='cubic'):
    """
    Build scipy interpolation functions for CRPIX1 and CRPIX2 vs time.

    Parameters
    ----------
    T, CRPIX1, CRPIX2 : np.ndarray, optional
        Pre-loaded arrays. If None, loaded from load_dir/*.npy.
    load_dir : str
        Directory containing T.npy, CRPIX1.npy, CRPIX2.npy.
    kind : str
        Interpolation kind passed to scipy.interpolate.interp1d (default 'cubic').

    Returns
    -------
    f_crpix1, f_crpix2 : callable
        Functions that accept an MJD float and return the interpolated CRPIX value.
    T_mjd, CRPIX1, CRPIX2 : np.ndarray
        Raw arrays (useful for plotting / diagnostics).
    """
    if T is None:
        T      = np.load(f'{load_dir}/T.npy',      allow_pickle=True)
        CRPIX1 = np.load(f'{load_dir}/CRPIX1.npy', allow_pickle=True)
        CRPIX2 = np.load(f'{load_dir}/CRPIX2.npy', allow_pickle=True)

    T_mjd    = np.array([t.mjd for t in T])
    f_crpix1 = interp1d(T_mjd, CRPIX1, kind=kind, bounds_error=True)
    f_crpix2 = interp1d(T_mjd, CRPIX2, kind=kind, bounds_error=True)

    return f_crpix1, f_crpix2, T_mjd, CRPIX1, CRPIX2


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  Core pipeline functions
# ═══════════════════════════════════════════════════════════════════════════════

def cut2full(m_cut, f_crpix1, f_crpix2):
    """
    Embed an HMI cutout into a 4096×4096 full-disc canvas.

    The interpolated CRPIX values (from the 180°-rotated full-disc series)
    locate disk centre in the canvas; the cutout's own CRPIX values locate
    disk centre within the cutout, so the insertion corner is their difference.

    Parameters
    ----------
    m_cut : sunpy.map.GenericMap
        HMI cutout map from JSOC (level 1.5).
    f_crpix1, f_crpix2 : callable
        Interpolators returned by load_crpix_interpolators().

    Returns
    -------
    m_full : sunpy.map.GenericMap
        Full 4096×4096 map with the cutout embedded and header updated.
    """
    header = m_cut.fits_header.copy()
    data   = m_cut.data
    ny, nx = data.shape

    # Interpolate full-disc disk-centre position at this observation time
    t_obs       = m_cut.date
    crpix1_full = float(f_crpix1(t_obs.mjd))
    crpix2_full = float(f_crpix2(t_obs.mjd))

    # Cutout disk-centre position in its own pixel grid (1-indexed)
    crpix1_cut = header['CRPIX1']
    crpix2_cut = header['CRPIX2']

    # Bottom-left corner of cutout in 0-indexed full-disc pixel coords
    x0 = int(round((crpix1_full - 1) - (crpix1_cut - 1)))
    y0 = int(round((crpix2_full - 1) - (crpix2_cut - 1)))

    # Embed into blank canvas with boundary protection
    canvas = np.zeros((4096, 4096), dtype=data.dtype)
    x0_src = max(0, -x0);  x0_dst = max(0,  x0)
    y0_src = max(0, -y0);  y0_dst = max(0,  y0)
    x1_src = x0_src + min(nx - x0_src, 4096 - x0_dst)
    y1_src = y0_src + min(ny - y0_src, 4096 - y0_dst)
    x1_dst = x0_dst + (x1_src - x0_src)
    y1_dst = y0_dst + (y1_src - y0_src)
    canvas[y0_dst:y1_dst, x0_dst:x1_dst] = data[y0_src:y1_src, x0_src:x1_src]

    # Update header to full-disc coordinate system
    header['NAXIS1'] = 4096
    header['NAXIS2'] = 4096
    header['CRPIX1'] = crpix1_full
    header['CRPIX2'] = crpix2_full

    return sm((canvas, header))


def hmi_prep(m_full):
    """
    Remove the instrument roll angle (CROTA2) from a full-disc HMI map.

    No scaling is applied — CDELT1/2 from the JSOC level 1.5 header is
    already calibrated and Astropy/SunPy WCS handles coordinate conversions
    correctly without resampling to a reference plate scale.

    Parameters
    ----------
    m_full : sunpy.map.GenericMap
        Full-disc HMI map (output of cut2full or a genuine full-disc map).

    Returns
    -------
    m_prepped : sunpy.map.GenericMap
        Map with roll removed and LVL_NUM set to 1.5.
    """
    crota2 = m_full.fits_header['CROTA2']

    if abs(crota2) > 1e-4:
        m_prepped = m_full.rotate(angle=crota2 * u.deg, order=0, missing=0)
    else:
        m_prepped = m_full

    header = m_prepped.fits_header.copy()
    header['LVL_NUM'] = 1.5

    print(m_prepped.data)

    return sm((m_prepped.data, header))


def recut(m_prepped, m_cut):
    """
    Re-cut the prepped full-disc map to the FOV of the original cutout.

    Parameters
    ----------
    m_prepped : sunpy.map.GenericMap — prepped full-disc map
    m_cut     : sunpy.map.GenericMap — original cutout (defines the FOV)

    Returns
    -------
    sunpy.map.GenericMap
    """
    return m_prepped.submap(m_cut.bottom_left_coord,
                            top_right=m_cut.top_right_coord)


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  Top-level convenience function
# ═══════════════════════════════════════════════════════════════════════════════

def hmi_cutout_prep(m_cut, f_crpix1, f_crpix2, recut_fov=True, save_full=False):
    """
    Complete HMI cutout prep pipeline:
        cutout  →  full-disc  →  prep  →  (optional) re-cut

    Parameters
    ----------
    m_cut           : sunpy.map.GenericMap
        HMI cutout map from JSOC.
    f_crpix1, f_crpix2 : callable
        CRPIX interpolators from load_crpix_interpolators().
    recut_fov       : bool
        If True (default), re-cut to the original cutout FOV after prepping.
    save_full       : str or False
        If a filepath string, save the intermediate full-disc map to that path.

    Returns
    -------
    sunpy.map.GenericMap — prepped map
    """
    m_full    = cut2full(m_cut, f_crpix1, f_crpix2)

    if save_full:
        m_full.save(save_full, overwrite=True)

    m_prepped = hmi_prep(m_full)

    if recut_fov:
        m_prepped = recut(m_prepped, m_cut)

    return m_prepped


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  Diagnostic plot
# ═══════════════════════════════════════════════════════════════════════════════

def plot_crpix(T_mjd, CRPIX1, CRPIX2, f_crpix1, f_crpix2, query_time=None,
               save_path='crpix_vs_time.png'):
    """
    Plot CRPIX1 and CRPIX2 vs time with the cubic spline and an optional
    query point marked.

    Parameters
    ----------
    T_mjd, CRPIX1, CRPIX2 : np.ndarray  — raw series from load_crpix_interpolators
    f_crpix1, f_crpix2    : callable     — interpolators
    query_time            : str or None
        ISO time string to mark on the plot, e.g. '2019-03-22T00:00:45'.
    save_path             : str
        Output PNG path (default 'crpix_vs_time.png').
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    T_dt      = Time(T_mjd, format='mjd', scale='tai').to_datetime()
    T_fine    = np.linspace(T_mjd.min(), T_mjd.max(), 2000)
    T_dt_fine = Time(T_fine, format='mjd', scale='tai').to_datetime()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle('HMI Full-Disc CRPIX1 & CRPIX2 vs Time', fontsize=13)

    for ax, data, fine_fn, color, label in [
        (ax1, CRPIX1, f_crpix1, 'steelblue',  'CRPIX1'),
        (ax2, CRPIX2, f_crpix2, 'darkorange', 'CRPIX2'),
    ]:
        ax.plot(T_dt,      data,            'o', ms=4,  color=color, label='Full-disc data')
        ax.plot(T_dt_fine, fine_fn(T_fine), '-', lw=1.5, color=color, alpha=0.7, label='Cubic spline')
        ax.set_ylabel(f'{label} (pixel)', fontsize=11)
        ax.grid(True, alpha=0.3)

        if query_time is not None:
            t_q  = Time(query_time, format='isot', scale='tai')
            v_q  = float(fine_fn(t_q.mjd))
            dt_q = t_q.to_datetime()
            ax.axvline(dt_q, color='red', lw=1.2, ls='--')
            ax.axhline(v_q,  color='red', lw=0.8, ls=':')
            ax.plot(dt_q, v_q, '*', ms=12, color='red',
                    label=f'Interp {label} = {v_q:.3f}')
            print(f'{label} at {query_time}: {v_q:.4f}')

        ax.legend(fontsize=9, loc='best')

    ax2.set_xlabel('Date', fontsize=11)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f'Plot saved to {save_path}')




# ═══════════════════════════════════════════════════════════════════════════════
# Visualise
# ═══════════════════════════════════════════════════════════════════════════════


def open_hmi_written_by_idl(filepath):
    from astropy.io import fits
    from sunpy.map import Map as sm
    hduls = fits.open(filepath)
    data = hduls[0].data
    header = hduls[0].header
    header['CUNIT1'] = 'arcsec'
    header['CUNIT2'] = 'arcsec'

    return sm((data,header))


def VIS(original_cut_file,prepped_cut_from_python_file,prepped_file_from_idl,original_full_file):

    import matplotlib.pyplot as plt
    from Functions.sunpy_map_cut import sunpy_map_cut , cut_one_map_from_another
    from Functions.utilities import get_extent
    from sunpy.map import Map as sm
    

    fig1234 = plt.figure()
    ax1 = fig1234.add_subplot(2,2,1)
    ax2 = fig1234.add_subplot(2,2,2)
    ax3 = fig1234.add_subplot(2,2,3)
    ax4 = fig1234.add_subplot(2,2,4)

    m_cut = sm(original_cut_file)
    m_cut_prepped_python = sm(prepped_cut_from_python_file)
    m_prepped_idl = open_hmi_written_by_idl(prepped_file_from_idl)
    m_prepped_idl_cut = cut_one_map_from_another(m_prepped_idl,m_cut)
    m_full_original = sm(original_full_file)


    ax1.imshow(m_cut.data,
            origin="lower", extent=get_extent(m_cut),
            vmin=-50, vmax=+50)
    ax1.set_title('Original cutout')

    ax2.imshow(m_cut_prepped_python.data,
            origin="lower", extent=get_extent(m_cut_prepped_python),
            vmin=-50, vmax=+50)
    ax2.set_title('Prepped (Python)')

    ax3.imshow(m_prepped_idl_cut.data,
            origin="lower", extent=get_extent(m_prepped_idl_cut),
            vmin=-50, vmax=+50)
    ax3.set_title('Prepped (IDL)')

    ax4.imshow(m_full_original.data,
            origin="lower", extent=get_extent(m_full_original),
            vmin=-50, vmax=+50)
    ax4.set_title('Original full-disc')

    plt.tight_layout()
    plt.show()



# ═══════════════════════════════════════════════════════════════════════════════
# Example usage
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    # ── One-time: build CRPIX series from full-disc files ─────────────────────
    # build_crpix_series('./hmi_files_1d_cad/*.fits', save_dir='./CRPIX_VALS')

    # ── Every run: load interpolators ─────────────────────────────────────────
    # f_crpix1, f_crpix2, T_mjd, CRPIX1, CRPIX2 = load_crpix_interpolators(load_dir='./CRPIX_VALS')

    # # ── Diagnostic plot ────────────────────────────────────────────────────────
    # plot_crpix(T_mjd, CRPIX1, CRPIX2, f_crpix1, f_crpix2,
    #            query_time='2019-03-22T00:00:45',save_path="crpix_vs_time1.png")
    
    # # ── Prep a cutout ──────────────────────────────────────────────────────────
    # m_cut = sm('./hmi_cutout/hmi.m_45s.20190322_000045_TAI.2.magnetogram.fits')
    # m_out = hmi_cutout_prep(m_cut, f_crpix1, f_crpix2,
    #                         recut_fov=True, save_full='cut_full_prepped_python.fits')
    # m_out.save('cut_full_prepped_cut_python.fits', overwrite=True)
    # print('Done.')


    # # ── Visualise Correctly ──────────────────────────────────────────────────────────

    # original_cut_file = './hmi_cutout/hmi.m_45s.20190322_000045_TAI.2.magnetogram.fits'
    # prepped_cut_from_python_file = 'cut_full_prepped_cut_python.fits'
    # prepped_file_from_idl = 'hmi_prepped_full_idl.fits'
    # original_full_file = './hmi_full/hmi.m_45s.20190322_000045_TAI.2.magnetogram.fits'

    # VIS(original_cut_file,prepped_cut_from_python_file,prepped_file_from_idl,original_full_file)

    pass
