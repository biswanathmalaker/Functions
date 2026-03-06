def write_average_fit(F:list,file_name,fix_plate_scale=False,fix_exptime=True):
    """
    create average of the fits files inside F and write to file_name.
    """
    import numpy as np
    from astropy.io import fits
    from scipy.ndimage import zoom
    import os
    from .extract_from_fits import extract_from_fits
    # for i,file in enumerate(F):

    # hduls_0 = fits.open(files[0],ignore_missing_simple=True)
    data_0 ,hd = extract_from_fits(F[0])

    if fix_plate_scale:
        z0 = hd["cdelt1"]/0.6
        data_0 = zoom(data_0,z0)

    data = np.zeros_like(data_0)

    if os.path.isfile(file_name):
        print(f"{file_name} exists")
    else:
        cnt = 0
        for f in F:
            try:
                data1,hd1 = extract_from_fits(f)

                if fix_plate_scale:
                    cdelt1 = hd1['cdelt1']
                    z = cdelt1/0.6
                    data1 = zoom(data1,z)

                if fix_exptime:
                    exp_time = hd1['exptime']
                    data1 = data1/exp_time

                data = data +data1
                cnt+=1
            except Exception as error:
                print(error)
        av_data = data/cnt
        av_data[av_data<0] = 0
        av_data = av_data.astype(np.float32)

        if fix_exptime:
            hd['exptime'] = 1.0
        
        if fix_plate_scale:
            hd['cdelt1'] = 0.6
            hd['cdelt2'] = 0.6
            
        hdu = fits.PrimaryHDU(data=av_data,header=hd)
        hdul = fits.HDUList([hdu])
        hdul.verify('ignore')
        hdul.writeto(file_name,output_verify='ignore')
