from p5 import *
import numpy as np
from PIL import Image

import cProfile


# User settings
output_width = 1280
output_height = 800
# source_img_path = "7-65-42.png"    # Netherlands
source_img_path = "6-19-43.png"      # Tierra del Fuego
line_per_frame = False
jitteriness = 0.1
swap_rg = False
# keep = 240                            #  0 <= x <= 255
sub_size_range = (30, 31)           #  2 <= a < b <= 254
# update_fraction = 0.99                # TODO: implement fraction/keep trade-off to set itself automatically

# Globals
rel_window = (0.01 * output_width,       #  (left, right, top, bottom)
              0.99 * output_width,
              0.01 * output_height, 
              0.99 * output_height)
x_size = int(random_uniform(sub_size_range[0], sub_size_range[1]))
rng = np.random.default_rng()


def initialise_img(path):
    img = Image.open(path)
    array = np.array(img)
    return array
    

def setup():
    global normal
    global j
    global design
    global sub
    size(output_width, output_height)
    color_mode("RGB")
    background(0)
    normal = initialise_img(source_img_path)
    design, sub = restart_drawing()
    j = 0
    print("NOTE: quitting on j == 100")


# def generate_perlin_noise_2d(shape, res, k):    # Adapted rom https://github.com/pvigier/perlin-numpy
#     def f(t):
#         return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3
#
#     delta = (res[0] / shape[0], res[1] / shape[1])
#     d = (shape[0] // res[0], shape[1] // res[1])
#     grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) + k
#     grid %= 1
#     # print(str(grid))
#     # Gradients
#     angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
#     gradients = np.dstack((np.cos(angles), np.sin(angles)))
#     g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
#     g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
#     g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
#     g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
#     # Ramps
#     n00 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * g00, 2)
#     n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
#     n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
#     n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
#     # Interpolation
#     t = f(grid)
#     n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
#     n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
#     result = np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)
#     return result


def get_random_settings_within_ranges():
    global sub_size_range
    global x_size
    global swap_rg
    global jitteriness
    
    x_size = int(rng.integers(sub_size_range[0], sub_size_range[1]))
    swap_rg = bool(rng.binomial(1, .5))
    jitteriness = rng.uniform(low=max(0, jitteriness-1),
                              high=jitteriness+1)

    print("x_size:  " + str(x_size))
    # print("swap_rg:  " + str(swap_rg))
    print("jitter:  s: " + str(round(jitteriness, 1)))


def restart_drawing():
    global normal
    global sub_size_range
    global normal_red
    global normal_green
    global swap_rg
    global x_size
    
    # Select a new random subarray
    y_size = int(0.703125 * x_size)
    x_start = int(rng.integers(256 - x_size))
    y_start = int(rng.integers(256 - y_size))
    sub = normal[x_start:(x_start + x_size), y_start:(y_start + y_size), :]

    # print("x_start:   " + str(x_start) +
    #       "\nx end:     " + str(x_start + x_size) +
    #       "\ny_start:   " + str(y_start) +
    #       "\ny_end:     " + str(y_start + y_size))
    
    subwidth = sub.shape[0]
    subheight = sub.shape[1]
    
    # Extract values from the png-encoded terrain data
    elevations_to_reds = sub[:,:,3]
    normal_red = sub[:,:,0] - 128
    normal_green = sub[:,:,1] - 128
    # normal_blue = sub[:,:,2]
    
    # Calculate colours
    elevations_to_reds = (elevations_to_reds - np.min(elevations_to_reds)) * \
                         (255 / (np.max(elevations_to_reds) - np.min(elevations_to_reds) + 1))   # Stretch up the reds
    elevations_to_reds = elevations_to_reds.astype('int')
    sub_random_green = int(rng.integers(0, 255))
    sub_random_blue = int(rng.integers(0, 255))
    
    sub_lineweight = 500 / (subwidth + subheight)
    sub_alpha = 50                                      # TODO: animate these properties
    
    # Get fixed coordinates
    Xs, Ys = np.meshgrid(np.arange(subheight), np.arange(subwidth))
    if not swap_rg:
        Xs_dest = Xs + 0.00390625 * normal_red
        Ys_dest = Ys + 0.00390625 * normal_green
    else:
        Xs_dest = Xs + 0.00390625 * normal_green
        Ys_dest = Ys + 0.00390625 * normal_red

    # Collect all the artistic properties in a dict
    sub_design = {"elevations_to_reds": elevations_to_reds, 
                  "sub_random_green": sub_random_green, 
                  "sub_random_blue": sub_random_blue, 
                  "sub_alpha": sub_alpha, 
                  "sub_lineweight": sub_lineweight, 
                  "Xs": Xs,
                  "Ys": Ys,
                  "Xs_dest": Xs_dest,
                  "Ys_dest": Ys_dest}
    return sub_design, sub


def draw_single_line(red, green, blue, alpha, weight, from_x, from_y, to_x, to_y):
    red = int(red)
    stroke(r = red, g = green, b = blue, a = alpha)
    stroke_weight(weight)
    # print("from: " + str((from_x, from_y)) + "\n  to: " + str((to_x, to_y)))
    line((from_x, from_y), (to_x, to_y))


def calculate_frame_coords(sub, design, j):
    global jitteriness
    # Get the fraction
    update_fraction = min(1, remap(mouse_x, (0, output_width * 0.9), (0, 1)))
    # sub_length = len(sub)
    if update_fraction == 1:
        # sub_fraction_length = sub_length
        fractioned_sub = sub
    else:
        # sub_fraction_length = int(update_fraction * sub_length)
        # fractioned_sub = [int(rng.integers(a)) for a in [sub_length] * sub_fraction_length]
        fractioned_sub = sub  # TODO: repair this with numpy
    
    # Calculate jitter
    # subwidth = sub.shape[0]
    # subheight = sub.shape[1]
    # np.random.seed(27)
    # X_jitter = generate_perlin_noise_2d((subwidth, subheight), (1, 1), k=0.005*j) - .5
    noise_seed(27)
    X_jitter = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Xs'].flat]).reshape(design['Xs'].shape)
    # np.random.seed(28)
    # Y_jitter = generate_perlin_noise_2d((subwidth, subheight), (1, 1), k=0.005*j) - .5
    noise_seed(28)
    Y_jitter = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Ys'].flat]).reshape(design['Xs'].shape)
    # np.random.seed(29)
    # X_jitter_dest = generate_perlin_noise_2d((subwidth, subheight), (1, 1), k=0.005*j) - .5    # TODO: add vector magnitude somehow
    noise_seed(29)
    X_jitter_dest = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Xs_dest'].flat]).reshape(design['Xs'].shape)
    # np.random.seed(30)
    # Y_jitter_dest = generate_perlin_noise_2d((subwidth, subheight), (1, 1), k=0.005*j) - .5
    noise_seed(30)
    Y_jitter_dest = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Ys_dest'].flat]).reshape(design['Xs'].shape)
    
    # Add noise to absolute coordinates
    Xs_jittered = design['Xs'] + X_jitter
    Ys_jittered = design['Ys'] + Y_jitter
    Xs_dest_jittered = design['Xs_dest'] + X_jitter_dest
    Ys_dest_jittered = design['Ys_dest'] + Y_jitter_dest
    
    # Get absolute window
    abs_window = (np.min(design['Xs']),       # left
                  np.max(design['Xs']),       # right
                  np.min(design['Ys']),       # top
                  np.max(design['Ys']))       # bottom
    
    # Stretch noisy coordinates out to fill the relative window
    Xs_zoomed = (Xs_jittered - abs_window[0]) * (rel_window[1] / (abs_window[1] - abs_window[0]))
    Ys_zoomed = (Ys_jittered - abs_window[2]) * (rel_window[3] / (abs_window[3] - abs_window[2]))
    Xs_zoomed_dest = (Xs_dest_jittered - abs_window[0]) * (rel_window[1] / (abs_window[1] - abs_window[0]))
    Ys_zoomed_dest = (Ys_dest_jittered - abs_window[2]) * (rel_window[3] / (abs_window[3] - abs_window[2])) + 1      # TODO: A line from a coordinate to the exact same coordinate causes a crash; adding 1 pixel to y2 prevents this most of the time but it could still go wrong

    # Collect all the coordinates in a dict
    frame = {"fsub": fractioned_sub,
             "Xs_zoomed": Xs_zoomed,
             "Ys_zoomed": Ys_zoomed,
             "Xs_zoomed_dest": Xs_zoomed_dest,
             "Ys_zoomed_dest": Ys_zoomed_dest}
    return frame


def draw_all_lines(sub, design, j): 
    # Draw an almost black rectangle over the existing lines
    keep = remap(mouse_y, (0, output_height), (0, 255))
    backgroundcol = Color(0, 0, 0, 255 - keep)
    fill(backgroundcol)
    rect((-50, -50), output_width + 200, output_height + 200)

    # Get the coordinates for this frame
    frame = calculate_frame_coords(sub, design, j)

    # Draw the lines
    f_height, f_width, _ = np.shape(frame['fsub'])
    [[draw_single_line(red=design['elevations_to_reds'][v, h],
                       green=design['sub_random_green'],
                       blue=design['sub_random_blue'],
                       alpha=design['sub_alpha'],
                       weight=design['sub_lineweight'],
                       from_x=frame['Xs_zoomed'][v, h],
                       from_y=frame['Ys_zoomed'][v, h],
                       to_x=frame['Xs_zoomed_dest'][v, h],
                       to_y=frame['Ys_zoomed_dest'][v, h])
      for h in range(f_width)]
     for v in range(f_height)]    # TODO: find a smarter/faster way than double list comp


def mouse_pressed():
    global j
    global sub
    global design
    get_random_settings_within_ranges()
    design, sub = restart_drawing()
    j = 0
    

def draw():
    global j
    global sub
    global design

    draw_all_lines(sub, design, j)
    j += 1

    fill(Color(255, 255, 255, 200))
    text(str(round(frame_rate)) + " fps",
         (10, 10))

    # print(str(j))
    if j == 100:
        quit()


if __name__ == "__main__":
    # cProfile.run('run()', sort='time')
    run()