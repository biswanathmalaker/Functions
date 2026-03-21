def simple_plot(_2d_data , vmax:float = None , vmin:float = None,wcs=None,\
                origin:str='lower',title:str="write title here",cmap:str="viridis",show_plot = False,save_file:str = None):
    
    import matplotlib.pyplot as plt
    figure = plt.figure()
    ax = figure.add_subplot(1,1,1,projection=wcs)
    ax.set_xlabel("Helioprojective longitude")
    ax.set_xlabel("Helioprojective latitude")
    ax.set_title(title)
    im = ax.imshow(_2d_data,cmap=cmap,vmax=vmax,vmin=vmin,origin=origin)
    plt.colorbar(im)
    if save_file != None:
        show_plot = False
        plt.savefig(save_file)
    
    if show_plot:
        plt.show()



def hist_plot(data,bin_number,ax = None,upper_limit:float=None):
    import numpy as np
    import matplotlib.pyplot as plt

    x = np.array(data)
    x = np.ravel(x)
    if upper_limit!=None:
        x[x>upper_limit] = upper_limit
    ax.hist(x,bin_number)
    plt.show()

if __name__=="__main__":
    file = "./data/cut/aia.lev1_euv_12s.2019-06-30T235959Z.171.image.fits"
    from extract_from_fits import extract_from_fits
    d,hd = extract_from_fits(file)
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    hist_plot(d,100,ax=ax)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1,2,2)
    ax1.set_xlabel("X")
    hist_plot(d,100,ax=ax1)


    plt.show
        
