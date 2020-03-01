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

    # TODO: only calculate this for the coordinates in fraction

    # Calculate jitter
    noise_seed(27)
    X_jitter = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Xs'].flat]).reshape(design['Xs'].shape)
    noise_seed(28)
    Y_jitter = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Ys'].flat]).reshape(design['Xs'].shape)
    noise_seed(29)
    X_jitter_dest = np.array([jitteriness * (noise(0.05 * (j + n)) - 0.5) for n in design['Xs_dest'].flat]).reshape(design['Xs'].shape)
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
    frame = {"fsub": sub,
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
    f_height, f_width, _ = np.shape(frame['fsub'])
    f_hv = f_height*f_width

    # Get the fraction
    update_fraction = int(min(1, remap(mouse_x, (0, output_width * 1.1), (0, 1))) * f_hv)
    fraction = rng.choice(f_hv, size=update_fraction, replace=False)

    # Draw the lines
    [draw_single_line (red=design['elevations_to_reds'][hv // f_width, hv % f_width],
                       green=design['sub_random_green'],
                       blue=design['sub_random_blue'],
                       alpha=design['sub_alpha'],
                       weight=design['sub_lineweight'],
                       from_x=frame['Xs_zoomed'][hv // f_width, hv % f_width],
                       from_y=frame['Ys_zoomed'][hv // f_width, hv % f_width],
                       to_x=frame['Xs_zoomed_dest'][hv // f_width, hv % f_width],
                       to_y=frame['Ys_zoomed_dest'][hv // f_width, hv % f_width])
     for hv in fraction]


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