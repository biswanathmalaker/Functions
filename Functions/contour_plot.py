def contour_plot(image_1, image_2, levels, ax, extent=None, norm=None, cmap=None, vmax=None, vmin=None, colors=None):
    """
    image_1 --->   Background image.
    image_2 --->   Find contours of this image.
    levels  --->   Levels are a list of values of which contours to be found.
    ax      --->   matplotlib axis.
    extent  --->   Extent of the plot in the form [left, right, bottom, top].
    norm    --->   Normalize the image data.
    cmap    --->   Colormap for mapping the data values to colors.
    vmax    --->   Maximum value for color scaling.
    vmin    --->   Minimum value for color scaling.
    colors  --->   List of colors corresponding to each level.
    """

    from skimage import measure

    if norm is not None:
        vmin = None
        vmax = None

    # Plot the background image
    img = ax.imshow(image_1, origin='lower', aspect='auto', extent=extent, norm=norm, cmap=cmap, vmax=vmax, vmin=vmin)

    # Find contours and plot them with specified colors
    for i, level in enumerate(levels):
        contours = measure.find_contours(image_2, level)
        
        # Set the color for the contour based on the provided colors list
        color = colors[i] if colors and i < len(colors) else 'red'
        
        for j, contour in enumerate(contours):
            linewidth = 2
            label = f'Level {level}'

            if j == 0:
                ax.plot(
                    extent[0] + contour[:, 1] * (extent[1] - extent[0]) / image_2.shape[1],
                    extent[2] + contour[:, 0] * (extent[3] - extent[2]) / image_2.shape[0],
                    linewidth=linewidth,
                    label=label,
                    color=color
                )
            else:
                ax.plot(
                    extent[0] + contour[:, 1] * (extent[1] - extent[0]) / image_2.shape[1],
                    extent[2] + contour[:, 0] * (extent[3] - extent[2]) / image_2.shape[0],
                    linewidth=linewidth,
                    color=color
                )

    return img


if __name__== "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    from skimage import measure


    # Construct some test data
    x, y = np.ogrid[-np.pi:np.pi:100j, -np.pi:np.pi:100j]
    r = np.sin(np.exp(np.sin(x)**3 + np.cos(y)**2))

    # Find contours at a constant value of 0.8
    # contours = measure.find_contours(r, 0.8)

    # Display the image and plot all contours found
    fig, ax = plt.subplots()
    # ax.imshow(r, cmap=plt.cm.gray)

    # for contour in contours:
    #     ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
    im = contour_plot(r,r,[0.8,0.9],ax)
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

