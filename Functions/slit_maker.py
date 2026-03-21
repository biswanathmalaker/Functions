import numpy as np
from skimage import measure
from skimage.draw import polygon2mask
from Functions.contour_plot import contour_plot
from sunpy.map import Map as sm
from Functions.utilities import get_extent
import matplotlib.pyplot as plt
from Functions.sunpy_map_cut import sunpy_map_cut
import astropy.units as u
from astropy.coordinates import SkyCoord



def get_rectangle(bl,dx,dy,theta=25,rotation_point=None):
    """
    Provides rectangles that is making an angle of theta degree (default) with respect to bottom left (bl or rotation_point) in clockwise direction from vertical axis.
    """
    import copy
    import numpy as np
    R0 = np.array([
        [bl[1],bl[0]],
        [bl[1]+dy,bl[0]],
        [bl[1]+dy,bl[0]+dx],
        [bl[1],bl[0]+dx],
        [bl[1],bl[0]]
    ])       # unrotated rectangle wrt origin
    
    if rotation_point!=None:
        R0_1  = R0-np.array(rotation_point)[::-1]
    else:
        R0_1  = R0-np.array(bl)[::-1]

    
    M_theta = np.array([
        [np.cos(np.deg2rad(theta)),-np.sin(np.deg2rad(theta))],
        [+np.sin(np.deg2rad(theta)),np.cos(np.deg2rad(theta))]
    ])  # clockwise rotation matrix
    
    R1_1 = np.zeros_like(R0_1,dtype=np.float64) # Rotated rectangle wrt rotation point or bl.    
    for i in range(R0_1.shape[0]):
        R1_1[i] = M_theta@R0_1[i][::-1][::-1]
        
    if rotation_point!=None:
        R1_1  = R1_1+np.array(rotation_point)[::-1]
    else:
        R1_1  = R1_1+np.array(bl)[::-1]     
        
    return R1_1   





def split_rectangle(rectangle,n):
    """
    rectangle must be rectangle and if be provided like :\n
        [
            point A0,
            point An,
            point Dn,
            point D0,
            point A0,
        ]
        
        then the division will be along the lines joining A0-An (similar as D0-Dn) starting from A0 to An
    
    NOTE : rectangle is similar like contour of skimage.measure.find_contours();
    RETURN : list of n number of rectangles equally divided.
    """
    A0 = rectangle[0]
    An = rectangle[1]

    D0 = rectangle[3]
    Dn = rectangle[2]


    K = np.array([i/n for i in range(1,n+1)])
    A_middle = []
    D_middle = []

    for k in K:
        Ai = (1-k)*A0+k*An
        Di = (1-k)*D0+k*Dn

        A_middle.append(Ai)
        A_middle.append(Ai)
        
        D_middle.append(Di)
        D_middle.append(Di)
        
    A_middle = np.array(A_middle)
    D_middle = np.array(D_middle)

    A = np.concatenate(([A0],A_middle))[:-1]
    D = np.concatenate(([D0],D_middle))[:-1]

    R0 = np.hstack((A,D))
    R1 = R0.reshape((n,R0.size//n))
    R2 = np.hstack((R1,R1[:,0:2]))
    R = R2.reshape((n,5,2))
    R[:,[2,3]] = R[:,[3,2]]

    return R



def get_rectangle_on_map(m,X,Y,DX,DY,angle,n=None,rotation_point = None,return_DN = True):
    '''
    m                       : sunpy map (prepped as 0.6 pixel scale has been used)
    X(float:arcsec)         : x coordinate of bottom left.
    Y(float:arcsec)         : y coordinate of the bottom left.
    DX(float:arcsec)        : width of the rectangles.
    DY(float:arcsec)        : height of the rectangles.
    angle(float:degree)     : Angle of rotation in clockwise direction.
    n                       : split the rectangle along dy into n equal parts.
    rotation_point          : None(default)/'mid'(middle of DX).
    return_DN               : If True , return DN values for RECTANGLE ( + rectangles)

    if n!=None:
        if return_DN:
            return RECTANGLE , RECTANGLE_world , rectangles , rectangles_world , data_RECTANGLE , data_rectangles
        else:
            return RECTANGLE , RECTANGLE_world , rectangles , rectangles_world 
    else:
        if return_DN:
            return RECTANGLE , RECTANGLE_world , data_RECTANGLE
        else:
            return RECTANGLE , RECTANGLE_world

    NOTE :  rectangles , rectangles_world , data_rectangles are starting from the side where rotation is taking place(base).\n
    '''

    bl_world = SkyCoord(X*u.arcsec,Y*u.arcsec,frame=m.coordinate_frame)
    px = m.world_to_pixel(bl_world)
    x = int(np.rint(px.x.value))
    y = int(np.rint(px.y.value))


    dx = int(np.rint(DX/0.6))
    dy = int(np.rint(DY/0.6))
    rotator = None
    if rotation_point == 'mid':
        rotator = [x+dx/2,y]
        # print("ROTATOR")
    # print(rotator)
    RECTANGLE = get_rectangle([x,y],dx,dy,angle,rotation_point=rotator)
    RECTANGLE_world = m.pixel_to_world(RECTANGLE[:,1]*u.pix,RECTANGLE[:,0]*u.pix)

    if n!=None:
        rectangles = split_rectangle(RECTANGLE,n)
        rectangles_world = []
        for rectangle in rectangles:
            rectangle_world = m.pixel_to_world(rectangle[:,1]*u.pix,rectangle[:,0]*u.pix)
            rectangle_world = np.vstack((rectangle_world.Ty.value,rectangle_world.Tx.value)).T
            rectangles_world.append(rectangle_world)
        rectangles_world = np.array(rectangles_world)

    data_RECTANGLE = None
    data_rectangles = None
    if return_DN:
        mask_REXCTANGLE = polygon2mask(m.data.shape,RECTANGLE)
        data_RECTANGLE = m.data[mask_REXCTANGLE]
    
        data_rectangles = []
        if n!=None:
            for rectangle in rectangles:
                mask_rectangle = polygon2mask(m.data.shape,rectangle)
                data_rectangle = m.data[mask_rectangle]
                data_rectangles.append(data_rectangle)

    if n!=None:
        if return_DN:
            return RECTANGLE , RECTANGLE_world , rectangles , rectangles_world , data_RECTANGLE , data_rectangles
        else:
            return RECTANGLE , RECTANGLE_world , rectangles , rectangles_world 
    else:
        if return_DN:
            return RECTANGLE , RECTANGLE_world , data_RECTANGLE
        else:
            return RECTANGLE , RECTANGLE_world

        


if __name__ == "__main__":
    file = "./DATA_TEST/2016-03-19T14:55:30.000000.fits"
    file = "./data/full/aia.lev1_euv_12s.2019-07-01T000010Z.171.image_lev1.fits"

    m = sm(file)
    m = sunpy_map_cut(m,[0,300],[25,450])
    # contours = measure.find_contours(m.data,level=400)

    X,Y = [10,360]
    DX = 2  # arcsec
    DY = 10
    angle = 45

    RECTANGLE , RECTANGLE_world , rectangles , rectangles_world , data_RECTANGLE , data_rectangles = get_rectangle_on_map(m,X,Y,DX,DY,angle,n=5,rotation_point=None)
    # RECTANGLE , RECTANGLE_world , rectangles , rectangles_world  = get_rectangle_on_map(m,X,Y,DX,DY,angle,5,None,return_DN=False)
    # RECTANGLE , RECTANGLE_world , data_RECTANGLE1 = get_rectangle_on_map(m,X,Y,DX,DY,angle,None,None)
    # RECTANGLE , RECTANGLE_world  = get_rectangle_on_map(m,X,Y,DX,DY,angle,None,None,return_DN=False)

    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    ax1= fig.add_subplot(1,2,2)


    im = ax.imshow(m.data,origin="lower")

    im1 = ax1.imshow(m.data,origin="lower",extent=get_extent(m))

    cont_plot = ax.plot(RECTANGLE[:,1],RECTANGLE[:,0],linewidth=8)
    for rectangle in rectangles:
        ax.plot(rectangle[:,1],rectangle[:,0])

    ax1.plot(RECTANGLE_world.Tx.value,RECTANGLE_world.Ty.value,linewidth=8)
    for rectangle_world in rectangles_world:
        ax1.plot(rectangle_world[:,1],rectangle_world[:,0])

    plt.show()
