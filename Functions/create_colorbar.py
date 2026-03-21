from mpl_toolkits.axes_grid1 import make_axes_locatable


def create_colorbar(fig,ax,im,**kwargs):
    """
    kwargs : append_position    : 'top', 'bottom', 'both', 'default', 'none' : string
             title              : title of the cbar
    """

    divider1 = make_axes_locatable(ax)
    # if 'append_position' in kwargs:
    #     cax1 = divider1.append_axes(kwargs['append_position'], size="3%", pad=0.1)
    # else:
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)

    cbar1 = fig.colorbar(im, cax=cax1, orientation='vertical', extend='both')
    # cbar1.set_ticks()
    if 'title' in kwargs:
        cbar1.set_label(kwargs['title'])

    # cbar1.ax.tick_params(labelsize=14)
    # cax1.xaxis.set_ticks_position('right')
    # cax1.xaxis.set_label_position('right')


if __name__=="__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    x = np.random.rand(30,30)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    im = ax.imshow(x,origin="lower")
    create_colorbar(fig,ax,im,title='A (km)')

    plt.show()