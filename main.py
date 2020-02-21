from p5 import *
import numpy as np
from PIL import Image

# User settings
output_width = 1280
output_height = 800
# source_img_path = "7-65-42.png"    # Netherlands
source_img_path = "6-19-43.png"      # Tierra del Fuego
line_per_frame = False
jitter_start_range = random_uniform(2)
jitter_start_speed = random_uniform(0.05)
jitter_end_range = random_uniform(2)
jitter_end_speed = random_uniform(0.05)
swap_rg = False
# keep = 240                            #  0 <= x <= 255
sub_size_range = (100, 101)           #  2 <= a < b <= 254
# update_fraction = 0.99                # TODO: implement fraction/keep trade-off to set itself automatically

# Globals
rel_window = (0.01 * output_width,       #  (left, right, top, bottom)
              0.99 * output_width,
              0.01 * output_height, 
              0.99 * output_height)
x_size = int(random_uniform(sub_size_range[0], sub_size_range[1]))


def initialise_img(path):
    img = Image.open(path)
    array = np.array(img)
    return array
    

def setup():
    global normal
    global j
    size(output_width, output_height)
    color_mode("RGB")
    background(0)
    normal = initialise_img(source_img_path)
    j = 0


def generate_perlin_noise_2d(shape, res):    # From https://github.com/pvigier/perlin-numpy (it's not a pkg yet)
    def f(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


def get_random_settings_within_ranges():
    global sub_size_range
    global x_size
    global swap_rg
    global jitter_start_range
    global jitter_start_speed
    global jitter_end_range
    global jitter_end_speed
    
    x_size = int(random_uniform(sub_size_range[0], sub_size_range[1]))
    swap_rg = (False, True)[int(round(random_uniform(1.01)))]   # PRCQJPX
    jitter_start_range = random_uniform(2)
    jitter_start_speed = random_uniform(0.05)
    jitter_end_range = random_uniform(2)
    jitter_end_speed = random_uniform(0.05)
    
    print("x_size:  " + str(x_size))
    print("swap_rg:  " + str(swap_rg))
    print("jitter:  s: " + 
          str(round(jitter_start_range, 1)) + "___" + 
          str(round(jitter_start_speed, 2)) + "   & e: " + 
          str(round(jitter_end_range, 1)) + "___" + 
          str(round(jitter_end_speed, 2)))


def restart_drawing():
    global normal
    global sub_size_range
    global normal_red
    global normal_green
    global swap_rg
    global x_size
    
    # Select a new random subarray
    y_size = int(0.703125 * x_size)
    x_start = int(random_uniform(256 - x_size))
    y_start = int(random_uniform(256 - y_size))
    sub = normal[x_start:(x_start + x_size), y_start:(y_start + y_size), :]
    
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
    sub_random_green = int(random_uniform(0, 255))
    sub_random_blue = int(random_uniform(0, 255))
    
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
    # Get the fraction
    update_fraction = min(1, remap(mouse_x, (0, output_width * 0.9), (0, 1)))
    # sub_length = len(sub)
    if update_fraction == 1:
        # sub_fraction_length = sub_length
        fractioned_sub = sub
    else:
        # sub_fraction_length = int(update_fraction * sub_length)
        # fractioned_sub = [int(random_uniform(a)) for a in [sub_length] * sub_fraction_length]
        fractioned_sub = sub  # TODO: repair this with numpy
    
    # Calculate jitter
    # noise_seed(4)
    # noise_detail(1)
    # Xs_jitter =  [jitter_start_range * (noise(jitter_start_speed * (j + i)) - 0.5) for i in fractioned_sub]
    #
    # noise_seed(5)
    # Ys_jitter = [jitter_start_range * (noise(jitter_start_speed * (j + i)) - 0.5) for i in fractioned_sub]
    # noise_seed(6)
    # Xs_dest_jitter = [jitter_end_range * (noise(jitter_end_speed * (j + i)) - 0.5) for i in fractioned_sub]
    # noise_seed(7)
    # Ys_dest_jitter = [jitter_end_range * (noise(jitter_end_speed * (j + i)) - 0.5) for i in fractioned_sub]
    # np.random.seed(8)
    subwidth = sub.shape[0]
    subheight = sub.shape[1]
    jitter = 0  # generate_perlin_noise_2d((subwidth, subheight), (1, 1))     # TODO: fix this   # TODO: incorporate j and waviness in this
    np.random.seed(9)
    jitter_dest = 0  # generate_perlin_noise_2d((subwidth, subheight), (1, 1))     # TODO: add vector magnitude somehow
    
    # Add noise to absolute coordinates
    Xs_jittered = design['Xs'] + jitter
    Ys_jittered = design['Ys'] + jitter
    Xs_dest_jittered = design['Xs_dest'] + jitter_dest
    Ys_dest_jittered = design['Ys_dest'] + jitter_dest
    
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
    f_height, f_width, f_depth = np.shape(frame['fsub'])
    for v in range(f_height):
        for h in range(f_width):
            draw_single_line(red=design['elevations_to_reds'][v, h],
                             green=design['sub_random_green'],
                             blue=design['sub_random_blue'],
                             alpha=design['sub_alpha'],
                             weight=design['sub_lineweight'],
                             from_x=frame['Xs_zoomed'][v, h],
                             from_y=frame['Ys_zoomed'][v, h],
                             to_x=frame['Xs_zoomed_dest'][v, h],
                             to_y=frame['Ys_zoomed_dest'][v, h])    # TODO: find a smarter/faster way than double for-loop


def mousePressed():
    global j
    get_random_settings_within_ranges()
    j = 0
    

def draw():
    global j
    global sub
    global design
    
    if j == 0:
        design, sub = restart_drawing()
    draw_all_lines(sub, design, j)
    j += 1


if __name__ == "__main__":
    run()