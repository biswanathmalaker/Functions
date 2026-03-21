def write_fits1(data,header,file_path,fix_exposure_time = True):
    """
    write fits file to the path , file_path.
    """
    if fix_exposure_time:
        data = data/header['exptime']
        header['exptime'] = 1.0
    
    
    from astropy.io import fits
    hdu = fits.PrimaryHDU(data=data,header=header)
    hdul = fits.HDUList([hdu])
    hdul.verify('ignore')
    hdul.writeto(file_path,output_verify='ignore',overwrite=True)
