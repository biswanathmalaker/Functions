from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib



def add_colorbar(axis,position='right',size='5%',pad=0.1,ticklabel_size=12):
    '''
    cbar1 = plt.colorbar(im4,cax=cax1,)\n
    cax1.set_ylabel("Counts",fontsize=15)\n

    position : {"left", "right", "bottom", "top"}\n
    size : ~mpl_toolkits.axes_grid1.axes_size or float or str , default '5%'\n
    pad = float ; default = 0.1
    '''
    divider = make_axes_locatable(axis)
    cax = divider.append_axes(position=position,size=size,pad=pad)

    return cax


