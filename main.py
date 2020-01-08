import imageio
import cv2
import os
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from keras.preprocessing.image import img_to_array
import svgwrite

alpha_elevation_mapping = [-11000, -10000, -9000, -8000, -7000, -6000, -5000, -4000, -3000, -2000, -1000,
                           -100, -50, -20, -10, -1, 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220,
                           240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500, 520, 540,
                           560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800, 820, 840, 860,
                           880, 900, 920, 940, 960, 980, 1000, 1020, 1040, 1060, 1080, 1100, 1120, 1140, 1160,
                           1180, 1200, 1220, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380, 1400, 1420, 1440,
                           1460, 1480, 1500, 1520, 1540, 1560, 1580, 1600, 1620, 1640, 1660, 1680, 1700, 1720,
                           1740, 1760, 1780, 1800, 1820, 1840, 1860, 1880, 1900, 1920, 1940, 1960, 1980, 2000,
                           2020, 2040, 2060, 2080, 2100, 2120, 2140, 2160, 2180, 2200, 2220, 2240, 2260, 2280,
                           2300, 2320, 2340, 2360, 2380, 2400, 2420, 2440, 2460, 2480, 2500, 2520, 2540, 2560,
                           2580, 2600, 2620, 2640, 2660, 2680, 2700, 2720, 2740, 2760, 2780, 2800, 2820, 2840,
                           2860, 2880, 2900, 2920, 2940, 2960, 2980, 3000, 3050, 3100, 3150, 3200, 3250, 3300,
                           3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000,
                           4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700,
                           4750, 4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150, 5200, 5250, 5300, 5350, 5400,
                           5450, 5500, 5550, 5600, 5650, 5700, 5750, 5800, 5850, 5900, 5950, 6000, 6100, 6200,
                           6300, 6400, 6500, 6600, 6700, 6800, 6900, 7000, 7100, 7200, 7300, 7400, 7500, 7600,
                           7700, 7800, 7900, 8000, 8100, 8200, 8300, 8400, 8500, 8600, 8700, 8800, 8900]

def display_image_in_actual_size(tensor):
    tensor /= 255
    dpi = plt.rcParams['figure.dpi']
    height, width, depth = np.shape(tensor)

    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # # Cut off dimensions
    # tensor_reduced = tensor[:,:,0]

    # Convert datatype
    tensor = np.float64(tensor)

    # # Shade
    # ls = LightSource(15, 8)
    # tensor = ls.shade_rgb(rgb=tensor[:,:,0:3],
    #                       elevation=tensor[:,:,3],
    #                       blend_mode="hsv",
    #                       vert_exag=5)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(tensor)


def open_img(location, imagePath):
  image = imageio.imread(os.path.join(location, imagePath)).astype(np.float)
  image = img_to_array(image)
  return image


def save_img(img_tensor, name):
    display_image_in_actual_size(img_tensor[:, :, :])   # [HEIGHT, WIDTH, DEPTH]
    out_filepath = 'output/' + name + '.png'
    if not os.path.exists('output'):
        os.makedirs('output')
    print("Saving file...")
    plt.savefig(out_filepath)
    plt.close()
    print('Saved img to    ' + str(out_filepath))


def save_img2(name):
    out_filepath = 'output/' + name + '.png'
    if not os.path.exists('output'):
        os.makedirs('output')
    print("Saving file...")
    plt.savefig(out_filepath)
    plt.close()
    print('Saved img to    ' + str(out_filepath))


def draw_contour_map(tensor):
    dpi = plt.rcParams['figure.dpi']
    height, width = np.shape(tensor)
    figsize = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=figsize)
    fig.add_axes([0, 0, 1, 1])
    # x = y = np.arange(0, 256, 1)
    # X, Y = np.meshgrid(x, y)
    # print("np.shape(X):    " + str(np.shape(X)))
    # print("np.shape(alpha_elevation_mapping):    " + str(np.shape(alpha_elevation_mapping)))
    plt.contour(tensor,
                 Z=tensor,
                 cmap=plt.cm.terrain,
                 levels=alpha_elevation_mapping)
    return tensor

def draw_normals_map(tensor):
    dpi = plt.rcParams['figure.dpi']
    height, width, depth = np.shape(tensor)
    figsize = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=figsize)
    fig.add_axes([0, 0, 1, 1])
    print("np.shape(tensor):    " + str(np.shape(tensor)))
    tensor /= 255
    tensor_directions = np.arctan(tensor[:,:,1] / tensor[:,:,0]) / (2 * math.pi) * 1
    plt.imshow(X=tensor_directions,
               cmap='twilight')
    return tensor


def transform_log(tensor):
    tensor = (np.log2(tensor) - np.log2(128)) * 100
    return tensor


def draw_and_save_svg_lines(tensor, name):
    # Artistic configurations
    spacing = 2
    intensity = 2
    jitter = 0.5
    logtransform = False
    strokecolour = 'rgb(233,116,81)'
    strokewidth = 0.3
    strokeopacity = 0.8

    # Automatic configs
    out_filepath = 'output/' + name + '.svg'
    height, width, depth = np.shape(tensor)
    drawsize = (str(height * spacing) + 'px',
                str(width * spacing) + 'px')

    # Initialise drawing
    d = svgwrite.Drawing(filename=out_filepath,
                         size=drawsize)
    d.add(d.rect(insert=(0, 0),
                 size=drawsize,
                 stroke_width = '0',
                 fill = 'black'))
    normallines = d.add(d.g(id='normallines',
                            stroke=strokecolour,
                            stroke_width=str(strokewidth),
                            stroke_opacity=str(strokeopacity),
                            stroke_linecap='round'))

    # Transform data
    if logtransform:
        tensor = transform_log(tensor)
    else:
        tensor = (tensor - 128)
    tensor = tensor * intensity

    tensor = (jitter * np.random.normal(size=(height, width, depth))) + tensor

    # Draw the lines
    for Y in range(height):
        for X in range(width):
            normallines.add(d.line(start=(X * spacing, Y * spacing),
                                   end=(X * spacing + tensor[X,Y,0],
                                        Y * spacing + tensor[X,Y,1]))) # TODO: base stroke colour/opacity on alpha channel (elevation); don't forget min/max interpolation

    # Save the file
    d.save()


if __name__ == '__main__':
    normal = open_img(".", "5-8-7.png")

    # print("np.shape(normal):    " + str(np.shape(normal)))
    # print("normal[:,:,0:3]:    " + str(normal[:,:,0:3]))     # Dit zouden de "normals" moeten zijn
    # print("normal[:,:,3]:    " + str(normal[:, :, 3]))       # Dit zou de "elevation" moeten zijn

    # print("np.shape(normal[0,0,0:3]):    " + str(normal[0,0,0:3]))

    # draw_contour_map(normal[:,:,3])
    # draw_normals_map(normal[:,:,0:3])

    # save_img2("00018")
    # save_img(normal, "00007")

    draw_and_save_svg_lines(tensor=normal[:,:,0:3],
                            name="00042")