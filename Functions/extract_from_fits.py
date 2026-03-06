def extract_from_fits(file):
    """
    return data,header
    """
    from astropy.io import fits
    import numpy as np
    import warnings
    warnings.filterwarnings("ignore")

    hdul = fits.open(file)
    if type(hdul[0].data).__module__ == 'numpy':
        data = hdul[0].data
        header = hdul[0].header
    else:
        data = hdul[1].data
        header = hdul[1].header

    return data,header


if __name__=="__main__":
    data, header = extract_from_fits("./2019-07-01T02:59:21.35.fits")
    # print(data)
