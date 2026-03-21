

def align(image1,image2,im_patch):
    """
    im_patch is the patch of the image taken for cross-correlation\n
    FOV of image2 is greater than image1\n
    image2 will be aligned with image1\n
    """
    from scipy.ndimage import correlate
    import numpy as np


    corr1 = correlate(image1, im_patch)
    y_shift1, x_shift1 = np.unravel_index(np.argmax(corr1,axis=None), corr1.shape)

    corr2 = correlate(image2, im_patch)
    y_shift2, x_shift2 = np.unravel_index(np.argmax(corr2,axis=None), corr2.shape)

    bl1_repr = (y_shift1-im_patch.shape[0]//2,x_shift1-im_patch.shape[1]//2)
    bl2_repr = (y_shift2-im_patch.shape[0]//2,x_shift2-im_patch.shape[1]//2)



    shifted = (bl2_repr[0]-bl1_repr[0],bl2_repr[1]-bl1_repr[1])

    new_image2 = image2[shifted[0]:shifted[0]+image1.shape[0],shifted[1]:shifted[1]+image1.shape[1]]

    return new_image2 , corr1 , corr2



if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    # Creating images

    s = (6,10)
    im_patch = np.zeros(s)
    im_patch = im_patch+50

    image1 = np.zeros((40,40))
    bl1 = (10,12)
    image1[bl1[0]:bl1[0]+s[0],bl1[1]:bl1[1]+s[1]] = im_patch

    im_patch1 = image1[0:30,0:30]

    fig1 = plt.figure()

    ax11 = fig1.add_subplot(1,2,1)
    ax11.imshow(image1,origin='lower')

    ax12 = fig1.add_subplot(1,2,2)
    ax12.imshow(im_patch1,origin='lower')


    image2 = np.zeros((80,80))
    bl2 = (bl1[0]+14,bl1[1]+10)
    image2[bl2[0]:bl2[0]+s[0],bl2[1]:bl2[1]+s[1]] = im_patch

    aligned_image2 ,corr1 , corr2 = align(image1,image2,im_patch1)


    fig = plt.figure()

    ax1 = fig.add_subplot(3,2,1)
    ax1.imshow(image1,origin='lower',aspect='auto')
    ax1.set_title("Image1")

    ax2 = fig.add_subplot(3,2,2)
    ax2.imshow(image2,origin='lower',aspect='auto')
    ax2.set_title("Image2")

    ax3 = fig.add_subplot(3,2,3)
    ax3.imshow(corr1,origin='lower',aspect='auto')

    ax4 = fig.add_subplot(3,2,4)
    ax4.imshow(corr2,origin='lower',aspect='auto')

    ax5 = fig.add_subplot(3,2,5)
    ax5.imshow(image1,origin='lower',aspect='auto')
    ax5.set_title("Original image1")

    ax6 = fig.add_subplot(3,2,6)
    ax6.imshow(aligned_image2,origin='lower',aspect='auto')
    ax6.set_title("aligned image2")


    fig.subplots_adjust(wspace=0,hspace=0)
    plt.show()