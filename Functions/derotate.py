

def de_rotate(file , ref_coordinate , initial_time , end_time , plot_point = False,model = 'howard'):
    """
    file is here to get coordinate frame. and plotting purpose and nowhere it has role.
    coodinate   --->    tuple (x,y) in arcsecs ; reference coordinate.
    time        --->    int or float in sec; +ve for future time coordinate to rotate
     , -ve for past time coodinate to rotate.
    plot_point  --->    default : False , If true will plot points on the map provided in file.
    return      --->    tuple ; (x,y) rotated in arcsec
    """

    import matplotlib.pyplot as plt
    import numpy as np

    import astropy.units as u
    from astropy.coordinates import SkyCoord

    import sunpy.map
    from sunpy.coordinates import RotatedSunFrame

    import datetime

    initial_time = datetime.datetime.strptime(initial_time,"%Y-%m-%dT%H:%M:%S.%f")
    end_time = datetime.datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S.%f")


    time = end_time-initial_time
    time = time.total_seconds()
    aiamap = sunpy.map.Map(file)
    point = SkyCoord(ref_coordinate[0]*u.arcsec, ref_coordinate[1]*u.arcsec, frame=aiamap.coordinate_frame)
    # print(point.observer)
    durations = np.array([time])*u.s
    # print(point.frame)
    diffrot_point = RotatedSunFrame(base=point, duration=durations , rotation_model=model)

    transformed_diffrot_point = diffrot_point.transform_to(aiamap.coordinate_frame)

    if plot_point:
        ax = plt.subplot(projection=aiamap)
        aiamap.plot(clip_interval=(1., 99.95)*u.percent)

        ax.plot_coord(point, 'ro', fillstyle='none', label='Original')
        ax.plot_coord(transformed_diffrot_point, 'bo', fillstyle='none',
                    label='Rotated')
        plt.legend()

        plt.show()

    return transformed_diffrot_point.Tx.value[0] , transformed_diffrot_point.Ty.value[0]