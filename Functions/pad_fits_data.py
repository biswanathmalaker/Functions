def pad_fits_data(data,hd,pad):
    """
    return padded data ,header
    """
    from astropy.wcs import WCS
    wcs = WCS(hd)

    data = data[pad:len(data[0])-pad,pad:len(data)-pad]
    wcs = wcs[pad:len(data[0])-pad,pad:len(data)-pad]
    hd.update(wcs.to_header())

    return data , hd