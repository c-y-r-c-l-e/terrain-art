# User settings
output_width = 1280
output_height = 800
# source_img_path = "7-65-42.png"    # Netherlands
source_img_path = "6-19-43.png"      # Tierra del Fuego
line_per_frame = False
jitter_start_range = random(2)
jitter_start_speed = random(0.05)
jitter_end_range = random(2)
jitter_end_speed = random(0.05)
swap_rg = True
# keep = 240                            #  0 <= x <= 255
sub_size_range = (100, 150)           #  2 <= a < b <= 254
# update_fraction = 0.99                # TODO: implement fraction/keep trade-off to set itself automatically

# Globals
rel_window = (0.01 * output_width,       #  (left, right, top, bottom)
              0.99 * output_width,
              0.01 * output_height, 
              0.99 * output_height)
x_size = int(random(sub_size_range[0], sub_size_range[1]))


def initialise_img(path):
    global normal
    normal = loadImage(path)
    image(normal, output_height, output_width)  # Displaying the img where we don't see it
    loadPixels()                                #   as loadPixels() won't work without displaying first
    

def setup():
    global normal
    global j
    size(output_width, output_height)
    background(0)
    initialise_img(source_img_path)
    j = 0


def get_random_settings_within_ranges():
    global sub_size_range
    global x_size
    global swap_rg
    global jitter_start_range
    global jitter_start_speed
    global jitter_end_range
    global jitter_end_speed
    
    x_size = int(random(sub_size_range[0], sub_size_range[1]))
    swap_rg = (False, True)[int(round(random(1.01)))]   # PRCQJPX
    jitter_start_range = random(2)
    jitter_start_speed = random(0.05)
    jitter_end_range = random(2)
    jitter_end_speed = random(0.05)
    
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
    global root
    global normal_red
    global normal_green
    global swap_rg
    global x_size
    
    root = int(sqrt(len(normal.pixels)))   
    
    # Select a new random subarray
    y_size = int(0.703125 * x_size)
    subarray_xmin = int(random(0, root - 1))
    subarray_xlim = (subarray_xmin, subarray_xmin + min(256, x_size))             # 0 <= xmin < xmax <= 256
    subarray_ymin = int(random(0, root - 1))
    subarray_ylim = (subarray_ymin, subarray_ymin + min(256, y_size))             # 0 <= ymin < ymax <= 256
    
    subwidth = 1 + subarray_xlim[1] - subarray_xlim[0]
    subheight = 1 + subarray_ylim[1] - subarray_ylim[0]
    
    print("subarray:  " + 
          str(subarray_xlim[0]) + ", " + 
          str(subarray_xlim[1]) + ", " + 
          str(subarray_ylim[0]) + ", " + 
          str(subarray_ylim[1]) + 
          "     sub size:  " + str(subwidth) + " x " + str(subheight))
 
    # Keep only those values from the pixel list that are within the bounds of the subarray
    sub = [p for p in range(len(normal.pixels)) if 
           (p % root) >= subarray_xlim[0] and 
           (p % root) <= subarray_xlim[1] and 
           (p // root) >= subarray_ylim[0] and 
           (p // root) <= subarray_ylim[1]]
    
    # Extract values from the png-encoded terrain data
    sub_len_range = range(len(sub))
    elevations_to_reds = [(normal.pixels[sub[i]] >> 24) & 0xFF for i in sub_len_range]
    normal_red = [((normal.pixels[sub[i]] >> 16) & 0xFF) - 128 for i in sub_len_range]
    normal_green = [((normal.pixels[sub[i]] >> 8) & 0xFF) - 128 for i in sub_len_range]
    normal_blue = [(normal.pixels[sub[i]] & 0xFF) - 128 for i in sub_len_range]
    
    # Calculate colours
    elevations_to_reds = [map(alpha, min(elevations_to_reds), max(elevations_to_reds), 0, 255) for alpha in elevations_to_reds]   # Stretch up the reds
    sub_random_green = random(0, 255)
    sub_random_blue = random(0, 255)
    
    sub_lineweight = 500 / (subwidth + subheight)
    sub_alpha = 50                                      # TODO: animate this
    
    # Get fixed coordinates
    Xs = [sub[i] % root for i in sub_len_range]
    Ys = [sub[i] // root for i in sub_len_range]
    if not swap_rg:
        Xs_dest = [Xs[i] + 0.0390625 * normal_red[i] * (output_width / subwidth) for i in sub_len_range] 
        Ys_dest = [Ys[i] + 0.0390625 * normal_green[i] * (output_height / subheight) for i in sub_len_range]
    else:
        Xs_dest = [Xs[i] + 0.0390625 * normal_green[i] * (output_width / subwidth) for i in sub_len_range] 
        Ys_dest = [Ys[i] + 0.0390625 * normal_red[i] * (output_height / subheight) for i in sub_len_range]       

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
    stroke(red, green, blue, alpha)
    strokeWeight(weight)
    line(from_x, from_y, to_x, to_y)


def calculate_frame_coords(sub, design, j):
    # Get the fraction
    update_fraction = min(1, map(mouseX, 0, output_width * 0.9, 0, 1))
    sub_length = len(sub)
    if update_fraction == 1:
        sub_fraction_length = sub_length
        fractioned_sub = range(sub_length)
    else:
        sub_fraction_length = int(update_fraction * sub_length)
        fractioned_sub = [int(random(a)) for a in [sub_length] * sub_fraction_length]
    
    # Calculate jitter
    noiseSeed(4)
    noiseDetail(1)
    Xs_jitter =  [jitter_start_range * (noise(jitter_start_speed * (j + i)) - 0.5) for i in fractioned_sub]
    noiseSeed(5)
    Ys_jitter = [jitter_start_range * (noise(jitter_start_speed * (j + i)) - 0.5) for i in fractioned_sub]
    noiseSeed(6)
    Xs_dest_jitter = [jitter_end_range * (noise(jitter_end_speed * (j + i)) - 0.5) for i in fractioned_sub]    # TODO: add vector magnitude somehow
    noiseSeed(7)
    Ys_dest_jitter = [jitter_end_range * (noise(jitter_end_speed * (j + i)) - 0.5) for i in fractioned_sub]
    
    # Add noise to absolute coordinates
    Xs_jittered = [design['Xs'][e[1]] + Xs_jitter[e[0]] for e in enumerate(fractioned_sub)]       # e[1] == i    e[0] : range of length of fractioned_sub
    Ys_jittered = [design['Ys'][e[1]] + Ys_jitter[e[0]] for e in enumerate(fractioned_sub)]
    Xs_dest_jittered = [design['Xs_dest'][e[1]] + Xs_dest_jitter[e[0]] for e in enumerate(fractioned_sub)]
    Ys_dest_jittered = [design['Ys_dest'][e[1]] + Ys_dest_jitter[e[0]] for e in enumerate(fractioned_sub)]
    
    # Get absolute window
    abs_window = (min(design['Xs']),       # left
                  max(design['Xs']),       # right
                  min(design['Ys']),       # top
                  max(design['Ys']))       # bottom
    
    # Stretch noisy coordinates out to fill the relative window
    Xs_zoomed = [map(Xs_jittered[h], abs_window[0], abs_window[1], rel_window[0], rel_window[1]) for h in range(sub_fraction_length)]     # h == e[0]
    Ys_zoomed = [map(Ys_jittered[h], abs_window[2], abs_window[3], rel_window[2], rel_window[3]) for h in range(sub_fraction_length)]
    Xs_zoomed_dest = [map(Xs_dest_jittered[h], abs_window[0], abs_window[1], rel_window[0], rel_window[1]) for h in range(sub_fraction_length)]
    Ys_zoomed_dest = [map(Ys_dest_jittered[h], abs_window[2], abs_window[3], rel_window[2], rel_window[3]) for h in range(sub_fraction_length)]
    
    # Collect all the coordinates in a dict
    frame = {"is": fractioned_sub,
             "Xs_zoomed": Xs_zoomed,
             "Ys_zoomed": Ys_zoomed,
             "Xs_zoomed_dest": Xs_zoomed_dest,
             "Ys_zoomed_dest": Ys_zoomed_dest}
    return frame


def draw_all_lines(sub, design, j): 
    # Draw an almost black rectangle over the existing lines
    keep = map(log(mouseY), 0, log(output_height), 0, 255)
    fill(0, 0, 0, 255 - keep)
    rect(-50, -50, output_width + 200, output_height + 200)
    
    # Get the coordinates for this frame
    frame = calculate_frame_coords(sub, design, j)
    
    # Draw the lines
    [draw_single_line(red = design["elevations_to_reds"][e[1]],     # Use the elevation data for red, 
                      green = design["sub_random_green"],           #   random values (per drawing) for green
                      blue = design["sub_random_blue"],             #   and blue
                      alpha = design["sub_alpha"],
                      weight = design["sub_lineweight"],
                      from_x = frame["Xs_zoomed"][e[0]],
                      from_y = frame["Ys_zoomed"][e[0]],
                      to_x = frame["Xs_zoomed_dest"][e[0]],
                      to_y = frame["Ys_zoomed_dest"][e[0]]) for e in enumerate(frame["is"])]
    

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
