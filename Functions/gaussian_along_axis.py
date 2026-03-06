def gaussian_along_axis(image,sigma):
    """
    return image with gaussian filtered along a particular column
    """
    from scipy.ndimage import gaussian_filter1d
    import copy
    import numpy as np
    z = np.zeros_like(image.T)
    for i,r in enumerate(image.T):
        z[i] = gaussian_filter1d(r,sigma=sigma)
    
    return z.T

if __name__=="__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    z = np.random.randint(1,400,(400,1)).reshape((20,20))
    z1 = gaussian_along_axis(z,1)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1,)
    ax1.imshow(z,origin="lower")

    ax2 = fig.add_subplot(1,2,2,)
    ax2.imshow(z1,origin="lower")

    plt.show()



