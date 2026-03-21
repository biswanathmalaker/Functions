
def px2arcsec(d,hd,px:list,use_sunpy=True):
    import astropy.units as u
    import warnings
    warnings.filterwarnings('ignore')
    from astropy.io.fits.verify import VerifyWarning
    warnings.simplefilter('ignore',category=VerifyWarning)
    import numpy as np
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    from astropy.wcs.utils import wcs_to_celestial_frame


    if use_sunpy:
        import sunpy.map
        import astropy.units as u
        m = sunpy.map.Map((d,hd))
        l = m.pixel_to_world(px[0]*u.pix,px[1]*u.pix)
        return l.Tx.value,l.Ty.value
    else:
        from astropy.wcs import WCS
        wcs = WCS(hd)
        frame = wcs_to_celestial_frame(wcs)
        sky_coords_deg = wcs.wcs_pix2world(px[0],px[1],0)
        sky_coords_arcsec = np.multiply(sky_coords_deg, [u.deg.to(u.arcsec), u.deg.to(u.arcsec)])
        skycoord = SkyCoord(sky_coords_arcsec[0], sky_coords_arcsec[1], unit=(u.arcsec, u.arcsec), frame=frame)
        return skycoord.Tx.value , skycoord.Ty.value



def arcsec2px(d,hd,coord:list,use_sunpy=True):
    '''
    coord = [x,y] in [arcsec,arcsec]
    '''
    
    if use_sunpy:
        import sunpy.map
        import astropy.units as u
        from astropy.coordinates import SkyCoord
        import numpy as np
        m = sunpy.map.Map((d,hd))
        c = SkyCoord(coord[0]*u.arcsec,coord[1]*u.arcsec,frame=m.coordinate_frame)
        l = m.world_to_pixel(c)
        return int(np.rint(l.x.value)),int(np.rint(l.y.value))
    else:
        from astropy.wcs.utils import wcs_to_celestial_frame
        from astropy.wcs import WCS
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        import numpy as np

        wcs = WCS(hd)
        frame = wcs_to_celestial_frame(wcs)
        c = SkyCoord(coord[0]*u.arcsec,coord[1]*u.arcsec,frame=frame)
        l = wcs.world_to_pixel(c)
        # return int(np.rint(l.x.value)),int(np.rint(l.y.value))
        return int(np.rint(l[0])),int(np.rint(l[1]))
 

def cut_data_hd(data,header,bottom_left,top_right):
    from astropy.wcs import WCS

    wcs = WCS(header)
    x0,y0 = arcsec2px(data,header,bottom_left)
    x1,y1 = arcsec2px(data,header,top_right)

    d1 = data[y0:y1,x0:x1]
    wcs1 = wcs[y0:y1,x0:x1]

    header.update(wcs1.to_header())

    return d1 , header

def get_extent(data,hd,use_sunpy = True):
    bl = [0,0]
    tr = [len(data[0]-1),len(data)-1]
    bottom_left = px2arcsec(data,hd,bl,use_sunpy = use_sunpy)
    top_right = px2arcsec(data,hd,tr,use_sunpy = use_sunpy)    

    return [bottom_left[0] , top_right[0],bottom_left[1] , top_right[1]]


    


if __name__=="__main__":
    from sunpy_map_cut import sunpy_map_cut
    from astropy.wcs import WCS
    import sunpy.map
    import astropy.units as u
    import numpy as np
    from astropy.coordinates import SkyCoord
    import matplotlib.pyplot as plt
    import warnings
    warnings.filterwarnings('ignore')
    from astropy.io.fits.verify import VerifyWarning
    warnings.simplefilter('ignore',category=VerifyWarning)
    from simple_plot import simple_plot
    from astropy.time import Time

    file = "./data/cut/aia.lev1_euv_12s.2019-06-30T235959Z.171.image.fits"

    m1 = sunpy.map.Map(file)
    m = sunpy_map_cut(m1,[-200,800],[-50,850])

    d,hd = m1.data , m1.fits_header
    wcs = WCS(hd)

    bottom_left = [-116,801]
    top_right = [-110,806]
    d1,hd1 = cut_data_hd(d,hd,bottom_left,top_right)
    wcs1 = WCS(hd1)

