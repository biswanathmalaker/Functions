"""
Author: Vishal Upendran
Contact: uvishal1995@gmail.com

Python script with functions to generate normalization following Dan Seaton's work. 

Changelog:
v1.0: Added code. 
"""

import numpy as np 
from skimage.filters import gaussian
import multiprocessing as mp
import sunpy 

#Need some global variables
distance2 = 0
limb2 = 0

def distfinder(u):
    # Function to find distance from center of the Sun.
    inds = np.where(distance2==u)
    return inds[0],[np.nanmean(limb2[inds])]*len(inds[0])

def disc_filt_variables(data):
    """
        Function to define preliminary variables for Dan Seaton's filter. 
        Inputs:
                data: np.ndarray of shape [M,M], of a single passband AIA image.
        Outputs: 
                mask: np.ndarray of shape [M,M]. 0 for on-disc pixels and 1 for limb. 
                distance: np.ndarray of shape [M,M] indicating distance from center.
    """
    center = np.array([256,256])
    radius = (695700.0/725.0)/(0.6*(4096/data.shape[0])) #very approximate
    print(f"Solar disc radius : {radius}")
    xg = np.arange(0,data.shape[0])
    xgrid,ygrid = np.meshgrid(xg,xg)
    distance = ((xgrid-center[0])**2+(ygrid-center[1])**2).astype(int)

    #disc mask
    mask = np.sign(distance-radius**2)
    mask[mask<0] = 0
    return mask,distance

def Danter(data,mask,distance,**kwargs):
    """
        Filter as applied by Dan Seaton et.al 2021: https://www.nature.com/articles/s41550-021-01427-8
        The code parameters are:
        Parameters: data : np.ndarray of size [M,M].
                          2D array of full disc solar image.
                    mask : np.ndarray of size [M,M].
                          array with 0 on disc, 1 on limb.
                    distance: np.ndarray of size [M,M].
                          array of distances from center of image.
        Optional parameters:
                    pool: bool; default = False
                          True to use multiprocessing, False to use list comprehension.
                    sigma: float; default = 3.0
                          Sigma of the Gaussian blur filter.
                    eps: float; default = 1e-4
                          Constant offset to apodize filter.
                    f_exp: float; default = 0.75
                          Exponent to raise the filter. Must be <=1.
                    scale_exp: float; default = 0.5
                          Exponent to raise the scaled image. Must be <=1.
    
    """
    disc = data*(1-mask)
    limb = data*mask
    data[data<0] = 0.0

    #If you want to check which axis to correctly sum over, check with offlimb. The correct "rows" are axis = 1
    danter_disc = np.sum(disc,axis=1)/np.sum(1-mask,axis=1)
    danter_disc[np.isnan(danter_disc)] = 0.0
    danter_disc = np.repeat(danter_disc.reshape([-1,1]),data.shape[-1],axis=-1)*(1-mask)

    
    #Limb mask
    unique_dist = np.unique(distance)
    global distance2
    distance2 = distance.reshape([-1])
    global limb2
    limb2 = limb.reshape([-1])
    danter_limb = np.zeros_like(limb).reshape([-1])

    pool = kwargs.pop("pool",False)
    assert isinstance(pool,bool)
    if pool:
        pool = mp.Pool()
        inds,vals = zip(*pool.map(distfinder,list(unique_dist)))
        pool.close()
    else:
        inds,vals = zip(*[distfinder(u) for u in list(unique_dist)])
    
    # print(inds , type(inds))
    danter_limb[np.concatenate(inds)] = np.concatenate(vals)


    danter_limb = danter_limb.reshape(list(distance.shape))
    # danter_limb = limb2.reshape(list(distance.shape))

    danter = danter_limb+danter_disc

    #Apply Gaussian blur on the filter
    blur = gaussian(danter,sigma=kwargs.pop("sigma",3))

    #Apodize the filter and exponentiate it
    filt = (blur + kwargs.pop("eps",1e-4))**kwargs.pop("f_exp",0.75)

    
    #Raise the whole image to some power
    out_image = (data/filt)**kwargs.pop("scale_exp",0.5)

    #Renormalize the image, and change type to int.
    out_image = (out_image-np.min(out_image))/np.ptp(out_image)
    out_image = out_image*255

    return out_image

def get_distance_fits(sample):
    """
        Function to get radial annuli for any image
        Inputs:
                sample: FITS header of the image - AXIS1 and AXIS2 are the spatial axes; OR
                        Sunpy.map object - AXIS1 and AXIS2 are the spatial axes;
        Outputs: 
                mask: 2D np.ndarray having 0 for on-disc pixels and 1 for limb. 
                distance: 2D np.ndarray indicating distance from center.
    """
    center = np.array([0.0,0.0])
    radius = 959.63 #In arcsec; very approximate
    # print(f"Solar disc radius : {radius}")
    if isinstance(sample,sunpy.map.GenericMap):
        header = sample.fits_header
        lat_l = sample.bottom_left_coord.Tx.value
        lat_r = sample.top_right_coord.Tx.value
        lon_l = sample.bottom_left_coord.Ty.value
        lon_r = sample.top_right_coord.Ty.value
    else:
        try:
            header = sample
            isinstance(header["NAXIS1"],int) is True 
            lat_r = header['CRVAL1']+header['CDELT1']*header['NAXIS1']/2
            lat_l = header['CRVAL1']-header['CDELT1']*header['NAXIS1']/2
            lon_r = header['CRVAL2']+header['CDELT2']*header['NAXIS2']/2
            lon_l = header['CRVAL2']-header['CDELT2']*header['NAXIS2']/2
        except:
            raise ValueError("FITS header NAXIS1 is not of type int (check if you are actually passing a header first)")
    
    #Get lat and long range in the image
    
    #Full range array.
    latitude = np.linspace(lat_l,lat_r,header['NAXIS1']).reshape([-1,1])
    longitude = np.linspace(lon_l,lon_r,header['NAXIS2']).reshape([1,-1])

    distance = np.sqrt((latitude-center[0])**2+(longitude-center[1])**2).astype(int)

    #disc mask
    mask = np.sign(distance-radius)
    mask[mask<0] = 0
    return mask.T,distance.T





def AIA_PLOT(file_path ,processed = False , vmax=None , vmin=None , sigma=2  , eps=1e-4,f_exp =0.75,scale_exp = 0.5):
    """
    file_path --> fits file path \n
    """

    from astropy.io import fits
    import sunpy.map
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    from astropy.wcs import WCS
    import sunpy.map
    import os
    import warnings
    warnings.filterwarnings('ignore')

    hdu_data_index = 0

    hdul = fits.open(file_path)
    data1 = hdul[hdu_data_index].data
    obs_date = hdul[hdu_data_index].header['DATE-OBS']
    wvl = hdul[hdu_data_index].header['wavelnth']


    if processed:
        aiamap = sunpy.map.Map(file_path)
        mask,distance = get_distance_fits(aiamap)
        out_image= Danter(aiamap.data,mask,distance , pool=True , sigma=sigma  , eps=eps,f_exp =f_exp,scale_exp = scale_exp)
    else:
        pass
    
    
    wcs = WCS(hdul[hdu_data_index].header)
    wcs = wcs
    data1[data1<1] = 1
    f = plt.figure(figsize=(14,10))
    ax  =f.add_subplot(projection = wcs)
    out_image[out_image<1]  = 1
    if processed:
        im = ax.imshow(out_image , cmap = 'binary_r' , vmax =vmax , vmin = vmin)
    else:
        im = ax.imshow(np.log(data1) , cmap = 'Greys_r',vmax = vmax,vmin=vmin )

    # plt.colorbar(im)
    # ax2 = plt.hist(out_image.ravel(), bins=400, range=(0.0, 200.0), fc='k', ec='r')


    plt.title(obs_date+'\n'+str(wvl))
    plt.xlabel("Helioprojective longitude")
    plt.ylabel("Helioprojective latitude")
    # name = '/home/biswanath/testdir/images/sigma{:03d}.png'.format(sigma)
    # name = '/home/biswanath/testdir/images/scale_exp{:03f}.png'.format(scale_exp)
    # name = "/home/biswanath/testdir/12s/Images/non_normalized/" + file_path[42:61] + ".png"
    name = "/home/biswanath/project1/images/" + file_path[19:39] + ".png"


    plt.savefig(name)
    # print(out_image.std())


    # plt.show()














if __name__=="__main__":
    
    def AIA_PLOT(file_path ,processed = False , vmax=None , vmin=None , sigma=2  , eps=1e-4,f_exp =0.75,scale_exp = 0.5):
        """
        file_path --> fits file path \n
        """

        from astropy.io import fits
        import sunpy.map
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib
        from astropy.wcs import WCS
        import sunpy.map
        import os
        import warnings
        # warnings.filterwarnings('ignore')

        hdu_data_index = 0

        hdul = fits.open(file_path)
        data1 = hdul[hdu_data_index].data
        obs_date = hdul[hdu_data_index].header['DATE-OBS']


        if processed:
            aiamap = sunpy.map.Map(file_path)
            mask,distance = get_distance_fits(aiamap)
            out_image= Danter(aiamap.data,mask,distance , pool=True , sigma=sigma  , eps=eps,f_exp =f_exp,scale_exp = scale_exp)
        else:
            pass
        
        
        wcs = WCS(hdul[hdu_data_index].header)
        wcs = wcs
        data1[data1<1] = 1
        f = plt.figure(figsize=(14,10))
        ax  =f.add_subplot(projection = wcs)
        if processed:
            im = ax.imshow(out_image , cmap = 'binary_r')
        else:
            im = ax.imshow(np.log(data1) , cmap = 'Greys_r',vmax = vmax,vmin=vmin )

        plt.colorbar(im)
        # ax2 = plt.hist(out_image.ravel(), bins=400, range=(0.0, 200.0), fc='k', ec='r')


        plt.title(obs_date+" , sigma = {} , eps = {} , f_exp = {}, \nscale_exp = {}".format(sigma , eps , f_exp , scale_exp))
        plt.xlabel("Helioprojective longitude")
        plt.ylabel("Helioprojective latitude")
        # name = '/home/biswanath/testdir/images/sigma{:03d}.png'.format(sigma)
        # name = '/home/biswanath/testdir/images/scale_exp{:03f}.png'.format(scale_exp)

        # plt.savefig(name)
        # print(out_image.std())


        plt.show()



    file_path = 'cut_image.fits'
    file_path = '/home/biswanath/testdir/AIA193_original/2019_07_01_00_00_04.fits'
    file_path = '/home/biswanath/testdir/AIA193_original/2019_07_01_10_15_04.fits'
    file_path = './deconvolution/decon_1.fits'
    # file_path = "/home/biswanath/testdir/deconvolution/aia_lev1_193a_2019_01_01t00_00_16_84z_image_lev1.fits"


    AIA_PLOT(file_path=file_path , processed=True , sigma=1  , eps=1e-4,f_exp =0.5,scale_exp = 0.58)
