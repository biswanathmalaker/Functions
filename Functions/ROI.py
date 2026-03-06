

def rectangle(bl,width,height,theta):

    """
    return ---> Rx,Ry, which are corner points to be plotted
    """
    import numpy as np

    br = [bl[0]+width-1,bl[1]]
    tr = [br[0],br[1]+height-1]
    tl = [tr[0]-width+1,tr[1]]

    rect = zip(bl,br,tr,tl)
    L = list(rect)

    Rx = list(L[0])
    Ry = list(L[1])

    # Rx1 , Rx2 are x and y coordinates of corners.
    Rx1 = Rx.copy()
    Ry1 = Ry.copy()

    # To complete rectangle first corner(bl) included.
    Rx.append(Rx[0])
    Ry.append(Ry[0])

    # generating rotation matrix.
    theta = np.deg2rad(theta)
    R = np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])

    # XY are array of corners to be rotated.
    XY = list(zip(Rx1,Ry1))
    XY = [np.array(l) for l in XY]

    # centre of rotation is translated to bottom left.
    translated_rect = [m-XY[0] for m in XY]

    # Rotation performed.
    translated_rect_p = [np.matmul(R,m) for m in translated_rect]

    # origin translated back to actual origin and XpYp are transformed corners of the rectangles.
    XpYp = [m+XY[0] for m in translated_rect_p]

    # restructuring to give primed version of the corners
    Rxp = [round(l[0]) for l in XpYp]
    Ryp = [round(l[1]) for l in XpYp]
    Rxp.append(Rxp[0])
    Ryp.append(Ryp[0])


    # print(f"XpYp = {XpYp}")

    return Rx,Ry,Rxp,Ryp


def rotation_of_coordinate(coordinate,theta):
    """
    coordinate is either tuple or list of two numbers.
    theta in degrees.
    return ---> rotated coordinate.

    e.g.

    m = rotation_of_coordinate((8,0),45)
    print(m)
    return [6, -6]
    """
    import numpy as np
    a = np.array(coordinate)

    theta = np.deg2rad(theta)
    R = np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
    ap = np.matmul(R,a)
    ap = [round(l) for l in ap]
    return ap



def create_coordinates(width,height):
    """
    return list of coordinates starting from [0,0] of width and height.

    e.g.
    l = create_coordinates(2,3)
    print(l)
    return [[0 0]
            [1 0]
            [0 1]
            [1 1]
            [0 2]
            [1 2]]
    """
    import numpy as np
    m = int(width)
    n = int(height)

    x = np.arange(m)
    y = np.arange(n)

    xx,yy = np.meshgrid(x,y)

    l = list(zip(xx,yy))
    M = [list(zip(k[0],k[1])) for k in l]
    M = np.array(M)
    coordinates = M.reshape((m*n,2))
    return coordinates


def ROI(image,width,height,bottom_left,theta,color = 'red',\
        header=None,vmax = None,vmin = None,single_plot=False):
    
    """
    bl,width,height all in arcsec\n
    sigle_plot = True will return roi,axis\n
    single_plot = False will return only roi
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from astropy.wcs import WCS
    import sunpy.map
    from .coord_pix_conversion import px2arcsec , arcsec2px

    bl_px = arcsec2px(image,header,bottom_left)
    width_px = int(width/header['cdelt1'])
    height_px = int(height/header['cdelt2'])

    l = create_coordinates(width_px,height_px)
    roi = np.zeros((height_px,width_px))
    for j in l:
        k = rotation_of_coordinate(j,theta=theta)
        roi[j[1]][j[0]] = image[k[1]+bl_px[1]][k[0]+bl_px[0]]

    if single_plot:

        m = sunpy.map.Map((image,header))

        x0 = m.bottom_left_coord.Tx.value
        y0 = m.bottom_left_coord.Ty.value
        x1 = m.top_right_coord.Tx.value
        y1 = m.top_right_coord.Ty.value

        Rx,Ry,Rxp,Ryp = rectangle(bl=bottom_left,width=width,height=height,theta=theta)
        fig1 = plt.figure()
        fig1.suptitle("suptitle",fontsize=15,fontweight='medium')
        ax2 = fig1.add_subplot(1,1,1,projection=None)
        ax2.imshow(image,origin = "lower",vmax = vmax , vmin = vmin,extent=[x0,x1,y0,y1])
        ax2.plot(Rxp,Ryp,color=color)
        ax2.set_xlabel("X (arcsec)",fontsize=12,fontweight='medium')
        ax2.set_ylabel("Y (arcsec)",fontsize=12,fontweight='medium')
        
        # fig2 = plt.figure()
        # ax = fig2.add_subplot(1,1,1,)
        # ax.imshow(roi,origin='lower',vmax = vmax,vmin=vmin,
        #           extent=[bottom_left[0],bottom_left[0]+width,bottom_left[1],bottom_left[1]+height])
        # ax.set_xlabel("Width (arcsec)",fontsize=12,fontweight='medium')
        # ax.set_ylabel("Height (arcsec)",fontsize=12,fontweight='medium')

        # plt.show()

    if single_plot:
        return roi , ax2
    else:
        return roi

if __name__=="__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from extract_from_fits import extract_from_fits

    bl = [-160,860]
    width = 50
    height = 100
    theta = 0      # in degrees

    img = np.random.randint(0,50,(100,70))
    file = "./data/cut/aia.lev1_euv_12s.2019-07-01T000011Z.193.image.fits"
    img,hd = extract_from_fits(file)

    roi,ax = ROI(image=img,header=hd,width=width,height=height,bottom_left=bl,theta=theta,\
            single_plot=True,vmax=120,vmin=40)
    ax.set_title("Custom title through axis")
    ax.set_xlabel("Custom X label")
    fig = ax.get_figure()
    fig.suptitle("Custom title through figure")
    plt.show()
    print(roi)



