import imageio
# import cv2
import os
import numpy as np
import math
import pylab as pl
import matplotlib.pyplot as plt
# from matplotlib.colors import LightSource
from skimage import transform
from matplotlib import collections as mc
from keras.preprocessing.image import img_to_array    # TODO: loading Keras/TF just for this function is overkill
import svgwrite
import re
from datetime import datetime
from shutil import copy2
import noise
import python_speech_features as psf
from scipy.io import wavfile
import sys

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
    print("Opening source img   " + location + "/" + imagePath + "   ...")
    image = imageio.imread(os.path.join(location, imagePath)).astype(np.float)
    image = img_to_array(image)
    return image


def open_audio(location, audioPath):
    print("Opening source audio   " + location + "/" + audioPath + "   ...")
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html#scipy.io.wavfile.read
    # WAV format             Min         Max         NumPydtype
    # 32-bit floating-point  -1.0        +1.0        float32
    # 32-bit PCM             -2147483648 +2147483647 int32
    # 16-bit PCM             -32768      +32767      int16
    # 8-bit PCM               0           255        uint8
    audio_samplerate, audio_raw = wavfile.read(filename=os.path.join(location, audioPath))
    audio_length = audio_raw.shape[0] / audio_samplerate

    return audio_raw, audio_length, audio_samplerate


def get_features_from_audio(audio, samplerate, framerate):
    print("Getting MFCCs from audio...")
    mfcc = psf.mfcc(signal=audio,
                    samplerate=audio_samplerate,
                    winlen=2.5 * 1 / framerate,      # The window length is fixed to 2.5 times the step time
                    winstep=1 / framerate,           # The step time is fixed to the framerate for the animation
                    numcep=14,
                    nfft=round(2.5 / framerate * audio_samplerate),
                    winfunc=np.hanning)
    return mfcc



def save_img(img_tensor, name):
    display_image_in_actual_size(img_tensor[:, :, :])   # [HEIGHT, WIDTH, DEPTH]
    out_filepath = 'output/' + name + '.png'
    if not os.path.exists('output'):
        os.makedirs('output')
    print("Saving file...")
    plt.savefig(out_filepath)
    plt.close()
    print('Saved img to   ' + str(out_filepath))


def save_img2(name):   # TODO: sort these two functions out
    out_filepath = name + '.png'
    if not os.path.exists('output'):
        os.makedirs('output')
    print("Saving img to   " + out_filepath + " ...")
    plt.savefig(out_filepath)
    plt.close()
    print("Saved.")


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
    spacing = 3
    intensity = 5.5
    jitter = 0
    logtransform = False
    # strokecolour = 'rgb(233,116,81)'
    strokewidth = 0.1 * 3.142
    strokeopacity = 0.95

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
                            # stroke=strokecolour,
                            stroke_width=str(strokewidth),
                            stroke_opacity=str(strokeopacity),
                            stroke_linecap='round'))

    # Transform data
    if logtransform:
        tensor = transform_log(tensor)
    else:
        tensor = (tensor - 128)
    tensor = tensor * intensity

    elevation_scaled = (tensor[:,:,3] - np.min(tensor[:,:,3])) * (255 / (np.max(tensor[:,:,3]) - np.min(tensor[:,:,3])))

    # Draw the lines
    for Y in range(height):
        for X in range(width):
            normallines.add(d.line(start=(X * spacing + (jitter * np.random.normal()),
                                          Y * spacing + (jitter * np.random.normal())),
                                   end=(X * spacing + (jitter * np.random.normal()) + tensor[X,Y,1],
                                        Y * spacing + (jitter * np.random.normal()) + tensor[X,Y,0]),
                                   stroke='rgb(' + str(256 - int(round(elevation_scaled[X,Y]))) + ',86,153)'))

    # Save the file
    print("Saving to " + out_filepath + " ...")
    d.save()
    print("Saved.")

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def draw_png_lines(tensor,
                   strokewidth,
                   intensity,
                   jitter,
                   strokeopacity,
                   terrain_overrides_colour_channel,
                   red=128,
                   green=128,
                   blue=128):
    # Artistic configurations
    magnification = 1
    spacing = 2           # Spacing between plotted lines

    apply_blurscaling = True     # Same as kronscaling, but with gaussian blur. If True, set intensity to something big
    blurscale = 2

    apply_kronscaling = False    # Every (source-)pixel becomes a block of $kronscale by $kronscale pixels
    kronscale = 1

    # intensity = 20  # 5.5     #  ≈ Length of the lines
    # jitter = 2                #  Apply some randomness to all coordinates
    logtransform = False
    backgroundcolour = 'black'
    # strokecolour = 'darkgreen'
    # strokewidth = 2.4  # 1
    # strokeopacity = 0.2

    # Automatic configs
    if apply_blurscaling:
        tensor = transform.pyramid_expand(image=tensor,
                                          upscale=blurscale,
                                          multichannel=True)
    if apply_kronscaling:
        tensor = np.kron(tensor, np.ones((kronscale, kronscale, 1)))  # Apply kronscale before determining imgsize etc
    height, width, depth = np.shape(tensor)
    dpi = plt.rcParams['figure.dpi']
    plt.rcParams['figure.facecolor'] = backgroundcolour
    plt.rcParams['axes.facecolor'] = backgroundcolour
    figsize = magnification * (width / float(dpi)), \
              magnification * (height / float(dpi))

    # Initialise drawing
    print("Generating drawing...")
    fig, ax = pl.subplots(figsize=figsize)

    # Transform data
    if logtransform:
        tensor = transform_log(tensor)
    else:
        tensor = (tensor - 128)
    tensor = np.rot90(m=tensor, k=3) * intensity
    elevation_scaled = (tensor[:,:,3] - np.min(tensor[:,:,3])) * (255 / (np.max(tensor[:,:,3]) - np.min(tensor[:,:,3])))

    # Prepare the line collection
    tensorlines = []
    strokecolour_variation = []
    for X in range(height):
        for Y in range(width):
            tensorlines.append([(X * spacing + (jitter * np.random.normal()),
                                 Y * spacing + (jitter * np.random.normal())),
                                (X * spacing + (jitter * np.random.normal()) + tensor[X, Y, 1],
                                 Y * spacing + (jitter * np.random.normal()) + tensor[X, Y, 0])])
            try:
                strokecolour_variation.append(256 - int(round(elevation_scaled[X, Y])))
            except ValueError:
                strokecolour_variation.append(0)

    # the _terrain channel is determined by the terrain elevation
    # the remaining two channels are determined through the parent function (=perlin or base)
    if terrain_overrides_colour_channel == 'red':     # TODO: find a way to play more flexibly with colours
        strokecolours = [(red_terrain / 256,
                          green,
                          blue) for red_terrain in strokecolour_variation]
    elif terrain_overrides_colour_channel == 'green':
        strokecolours = [(red,
                          green_terrain / 256,
                          blue) for green_terrain in strokecolour_variation]
    elif terrain_overrides_colour_channel == 'blue':
        strokecolours = [(red,
                          green,
                          blue_terrain / 256) for blue_terrain in strokecolour_variation]
    lc = mc.LineCollection(tensorlines,
                           colors=strokecolours,
                           linewidths=strokewidth,
                           alpha=strokeopacity)

    # Draw the lines
    ax.add_collection(lc)  # This draws the actual lines
    ax.autoscale()
    ax.axes.get_yaxis().set_visible(False)
    ax.axes.get_xaxis().set_visible(False)


def get_next_name_in_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    dirfiles = os.listdir(path=dir)
    numbered_dirfiles = [re.split(pattern='\.', string=f)[0] for f in dirfiles if
                         re.search(pattern=r'\d\d\d\d\d(\.png|\.svg|$)', string=f)]
    if not numbered_dirfiles:
        next_filenumber = 0
    else:
        next_filenumber = max([int(x) for x in numbered_dirfiles]) + 1
    next_filenumber = '{:05d}'.format(next_filenumber)
    return next_filenumber


def save_source(name):
    """This just copies the python script (the one you are reading now) so I know which settings I used to generate a
    particular img.

    example123.png  will correspond to  example123.txt"""
    out_filepath = 'output/' + name + '.txt'
    if not os.path.exists('output'):
        os.makedirs('output')
    print("Saving txt to   " + out_filepath + " ...")
    copy2(src="main.py",
          dst=out_filepath)
    print("Saved.")


def draw_and_save_bulk_png_lines(tensor, name, anim_base):
    # Artistic configurations  # TODO: refactor colours
    number_of_frames = 70
    strokewidth = 0.5
    intensity = 10
    jitter = 2
    strokeopacity = 0.75
    terrain_influences_channel = 'red'
    use_perlin = False
    use_base = True

    # Set mappings between MFCC features and artistic configs
    mfcc_intensity = 0
    mfcc_strokewdith = 1
    mfcc_strokeopacity = 2
    mfcc_red = 3                # TODO: implement long-term features
    mfcc_green = 4
    mfcc_blue = 12
    mfcc_jitter = 6


    if use_perlin and use_base:
        sys.exit("Error: choose either use_perlin or use_base but not both")  # TODO: make a prettier error handler for this


    if use_perlin:
        # Set up some perlin noise motions for the time dimension
        motion = {0: np.zeros(number_of_frames),
                  1: np.zeros(number_of_frames),
                  2: np.zeros(number_of_frames)}
        motion[0] = [1 + noise.pnoise1(f/number_of_frames, octaves=1) for f in range(number_of_frames)]
        motion[1] = [1 + noise.pnoise1(f/number_of_frames, octaves=2) for f in range(number_of_frames)]
        motion[2] = [1 + noise.pnoise1(f/number_of_frames, octaves=8, persistence=1.2) for f in range(number_of_frames)]

        print("Start building animation in   " + name + "   ...")
        for frame in range(number_of_frames):
            draw_png_lines(tensor,
                           strokewidth=strokewidth * motion[1][frame],
                           intensity=intensity * motion[0][frame],
                           jitter=jitter * motion[2][frame],
                           strokeopacity=strokeopacity + 0.1 * motion[1][frame])
            framename = get_next_name_in_folder(name)
            save_img2(name + "/" + framename)
            clean()

    if use_base:
        # Scale the MFCC features to fitting ranges (ie. 0<=x<=1 for colours)
        # print("np.shape(anim_base):                                 " + str(np.shape(anim_base)))
        # print("np.shape(np.transpose(anim_base)):                   " + str(np.shape(np.transpose(anim_base))))
        # print("np.shape(np.transpose(anim_base)[mfcc_intensity]):   " + str(np.shape(np.transpose(anim_base)[mfcc_intensity])))
        bases = np.transpose(anim_base)
        intensities = 2 * intensity * (bases[mfcc_intensity] - np.min(bases[mfcc_intensity]))/np.ptp(bases[mfcc_intensity])
        strokewidths = np.clip(2 * strokewidth * (bases[mfcc_strokewdith] - np.min(bases[mfcc_strokewdith]))/np.ptp(bases[mfcc_strokewdith]), a_min=0.01, a_max=10)
        strokeopacities = np.clip(strokeopacity * (bases[mfcc_strokeopacity] - np.min(bases[mfcc_strokeopacity]))/np.ptp(bases[mfcc_strokeopacity]), a_min=0, a_max=1)
        reds = (bases[mfcc_red] - np.min(bases[mfcc_red]))/np.ptp(bases[mfcc_red])
        greens = (bases[mfcc_green] - np.min(bases[mfcc_green]))/np.ptp(bases[mfcc_green])
        blues = (bases[mfcc_blue] - np.min(bases[mfcc_blue]))/np.ptp(bases[mfcc_blue])
        jitters = 2 * jitter * (bases[mfcc_jitter] - np.min(bases[mfcc_jitter]))/np.ptp(bases[mfcc_jitter])


        print("Start building animation in   " + name + "   ...")
        for frame in range(len(anim_base)):
            draw_png_lines(tensor,
                           intensity=intensities[frame],
                           strokewidth=strokewidths[frame],
                           strokeopacity=strokeopacities[frame],
                           red=reds[frame],
                           green=greens[frame],
                           blue=blues[frame],
                           terrain_overrides_colour_channel=terrain_influences_channel,
                           jitter=jitters[frame])
            framename = get_next_name_in_folder(name)
            save_img2(name + "/" + framename)
            clean()


def clean():
    plt.close('all')

def mirror_animation(name):
    # TODO: write mirror function
    return


if __name__ == '__main__':
    startTime = datetime.now()

    # Config     # TODO: move this to somewhere smart
    anim_framerate = 24

    normal = open_img(".", "7-65-42.png")
    audio, audio_length, audio_samplerate = open_audio(".", "musicsample.wav")
    audio_features = get_features_from_audio(audio, audio_samplerate, anim_framerate)

    # print("np.shape(audio_features):                            " + str(np.shape(audio_features)))

    filename = get_next_name_in_folder("./output")
    draw_and_save_bulk_png_lines(tensor=normal[:,:,:],
                                 name="./output/" + filename,
                                 anim_base=audio_features)
    save_source(name=filename)

    # mirror_animation(name="./output/" + filename)

    print("This took " + str(datetime.now() - startTime))