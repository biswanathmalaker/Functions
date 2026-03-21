

def sunpy_map_cut(file:str,lower_left:list,upper_right:list):
    """
    file ---> either data directory or sunpy map.
    return sunpy map
    """
    import sunpy.map
    import astropy.units as u
    from astropy.coordinates import SkyCoord
    import copy

    if getattr(file,"__module__",None)=='sunpy.map.sources.sdo':
        m = file
    else:
        m = sunpy.map.Map(file)


    top_right = SkyCoord(upper_right[0] * u.arcsec, upper_right[1] * u.arcsec, frame=m.coordinate_frame)
    bottom_left = SkyCoord(lower_left[0] * u.arcsec, lower_left[1] * u.arcsec, frame=m.coordinate_frame)
    m_submap = m.submap(bottom_left, top_right=top_right)

    hd = m_submap.fits_header
    if "SLTPX1IX" in hd:
        new_hd = copy.deepcopy(hd)

        # new_hd["SLTPX1IX"] = m_matched_sji.fits_header["SLTPX1IX"]*(m_sji.scale[0].value*60*60/m_aia_171.scale[0].value)
        # m_matched_aia_171 = sm((m1_aia_171_data,m1_aia_171_header))
        print("SLTPX1IX is under construction!")

    return m_submap


def cut_one_map_from_another(map_to_be_cut , templete_map):
    """
    file ---> either data directory or sunpy map.
    return sunpy map
    """
    import sunpy.map
    import astropy.units as u
    from astropy.coordinates import SkyCoord

    lower_left = [templete_map.bottom_left_coord.Tx.value , templete_map.bottom_left_coord.Ty.value]
    upper_right = [templete_map.top_right_coord.Tx.value , templete_map.top_right_coord.Ty.value]

    top_right = SkyCoord(upper_right[0] * u.arcsec, upper_right[1] * u.arcsec, frame=map_to_be_cut.coordinate_frame)
    bottom_left = SkyCoord(lower_left[0] * u.arcsec, lower_left[1] * u.arcsec, frame=map_to_be_cut.coordinate_frame)
    
    m_submap = map_to_be_cut.submap(bottom_left, top_right=top_right)
    return m_submap




if __name__=="__main__":
    file = "./data/cut/aia.lev1_euv_12s.2019-07-01T000023Z.171.image.fits"
    m = sunpy_map_cut(file,[-212.6,817.27],[-64.4,912.5])
