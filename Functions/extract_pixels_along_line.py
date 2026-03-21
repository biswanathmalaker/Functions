

def extract_pixels_along_line(data,alpha,beta,theta,length):
    """
    length is length when theta = 0 degrees toward +ve x
    alpha,beta initial position,
    theta is rotation clockwise
    """
    import numpy as np
    import matplotlib.pyplot as plt

    theta = np.deg2rad(theta)

    sinth = np.sin(theta)
    costh = np.cos(theta)

    coords = np.arange(length)
    zeros = np.zeros_like(coords)
    coords = np.vstack((coords,zeros))

    R = np.array([[costh,sinth],[-sinth,costh]])    # rotation matrix clockwise.

    coords_p = np.array([np.rint(np.matmul(R,coord)) for coord in coords.T],dtype = np.int32)
    coords_p = np.unique(coords_p,axis = 0)
    Xp = coords_p[:,0]+alpha
    Yp = coords_p[:,1]+beta

    x = [Xp[0],Xp[-1]]
    y = [Yp[0],Yp[-1]]

    coords_p = np.vstack((Xp,Yp)).T
    V = np.zeros(len(coords_p))

    for i,cp in enumerate(coords_p):
        V[i] = data[cp[1]][cp[0]]

    return x,y,V

if __name__=="__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    data = np.random.randint(0,20,(60,40))
    alpha ,beta = 10,20
    theta = 35  # in degrees
    length = 8 

    Xp,Yp,V = extract_pixels_along_line(data,alpha,beta,theta,length)
    x = [Xp[0],Xp[-1]]
    y = [Yp[0],Yp[-1]]

    plt.imshow(data,origin='lower')
    plt.plot(x,y,'-r')
    plt.show()
