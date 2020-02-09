# User settings
output_width = 1024
output_height = 720
# source_img_path = "7-65-42.png"    # Netherlands
source_img_path = "6-19-43.png"    # Tierra del Fuego
line_per_frame = False
jitter_start_range = 1
jitter_start_speed = 0.02
jitter_end_range = 1
jitter_end_speed = 0.02
swap_rg = True
keep = 220          #  0 <= x <= 255

# Globals
i = 0
j = 0
window = (0.01 * output_width,       #  (left, right, top, bottom)
          0.99 * output_width,
          0.01 * output_height, 
          0.99 * output_height)


def initialise_img(path):
    global normal
    normal = loadImage(path)
    image(normal, output_height, output_width)  # Displaying the img where we don't see it
    loadPixels()                                #   as loadPixels() won't work without displaying first
    

def setup():
    global normal
    size(output_width, output_height)
    background(0)
    initialise_img(source_img_path)
    restart_drawing()


def restart_drawing():
    global normal
    global sub
    global subwidth
    global subheight
    global root
    global elevation_alpha
    global normal_red
    global normal_green
    global random_green
    global random_blue
    global Xs
    global Ys
    global Xs_dest
    global Ys_dest
    global swap_rg

    background(0)
    
    root = int(sqrt(len(normal.pixels)))   
    
    # Select a new random subarray
    x_size = int(random(10, 30))
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
          str(subarray_ylim[1]))
    print("sub size:  " + str(subwidth) + " x " + str(subheight))
 
    # Keep only those values from the pixel list that are within the bounds of the subarray
    sub = [p for p in range(len(normal.pixels)) if 
           (p % root) >= subarray_xlim[0] and 
           (p % root) <= subarray_xlim[1] and 
           (p // root) >= subarray_ylim[0] and 
           (p // root) <= subarray_ylim[1]]
    
    # Extract values from the png-encoded terrain data
    elevation_alpha = [(normal.pixels[sub[i]] >> 24) & 0xFF for i in range(len(sub))]
    normal_red = [((normal.pixels[sub[i]] >> 16) & 0xFF) - 128 for i in range(len(sub))]
    normal_green = [((normal.pixels[sub[i]] >> 8) & 0xFF) - 128 for i in range(len(sub))]
    normal_blue = [(normal.pixels[sub[i]] & 0xFF) - 128 for i in range(len(sub))]
    
    # Calculate colours
    elevation_alpha = [map(alpha, min(elevation_alpha), max(elevation_alpha), 0, 255) for alpha in elevation_alpha]   # Stretch up the reds
    random_green = random(0, 255)
    random_blue = random(0, 255)
    
    Xs = [sub[i] % root for i in range(len(sub))]
    Ys = [sub[i] // root for i in range(len(sub))]
    if not swap_rg:
        Xs_dest = [Xs[i] + 0.0390625 * normal_red[i] * (output_width / subwidth) for i in range(len(sub))] 
        Ys_dest = [Ys[i] + 0.0390625 * normal_green[i] * (output_height / subheight) for i in range(len(sub))]
    else:
        Xs_dest = [Xs[i] + 0.0390625 * normal_green[i] * (output_width / subwidth) for i in range(len(sub))] 
        Ys_dest = [Ys[i] + 0.0390625 * normal_red[i] * (output_height / subheight) for i in range(len(sub))]        


def draw_line():
    global normal  # TODO: sort out these globals
    global i
    global j
    global sub
    global subwidth
    global subheight
    global root
    global subarray_xlim
    global subarray_ylim
    global elevation_alpha
    global normal_red
    global normal_green
    global random_green
    global random_blue
    global Xs
    global Ys
    global Xs_dest
    global Ys_dest
    global window
    global jitter_start_range
    global jitter_start_speed
    global jitter_end_range
    global jitter_end_speed
    global line_per_frame
    
    # Calculate jitter
    noiseSeed(4)
    noiseDetail(4, 0.5)
    X_jitter = (jitter_start_range * noise(jitter_start_speed * j))
    noiseSeed(5)
    Y_jitter = (jitter_start_range * noise(jitter_start_speed * j))
    X_dest_jitter = (jitter_end_range * noise(jitter_end_speed * j))  # TODO: add vector magnitude somehow
    noiseSeed(6)
    Y_dest_jitter = (jitter_end_range * noise(jitter_end_speed * j))
    
    # Get absolute coordinates
    X = Xs[i] + X_jitter
    Y = Ys[i] + Y_jitter
    X_dest = Xs_dest[i] + X_dest_jitter
    Y_dest = Ys_dest[i] + Y_dest_jitter
    
    # Calculate coordinates for subarray stretched out to entire canvas
    X_zoomed = map(X, min(Xs), max(Xs), window[0], window[1])
    Y_zoomed = map(Y, min(Ys), max(Ys), window[2], window[3])
    X_zoomed_dest = map(X_dest, min(Xs), max(Xs), window[0], window[1])
    Y_zoomed_dest = map(Y_dest, min(Ys), max(Ys), window[2], window[3])
    
    # print("   i: " + str(i) + 
    #       "   sub[i]: " + str(sub[i]) + 
    #       "   len(sub): " + str(len(sub)) +
    #       "   X: " + str(X) + 
    #       "   Y: " + str(Y) + 
    #       "   X_dest: " + str(int(X_dest)) + 
    #       "   Y_dest: " + str(int(Y_dest)) + 
    #       "   X_zoomed: " + str(round(X_zoomed, 1)) + 
    #       "   Y_zoomed: " + str(round(Y_zoomed, 1)) + 
    #       "   X_zoomed_dest: " + str(round(X_zoomed_dest, 1)) + 
    #       "   Y_zoomed_dest: " + str(round(Y_zoomed_dest, 1)) + 
    #       "   elevation_alpha[i]: " + str(elevation_alpha[i])
    #       )
    
    # Draw the lines from C to C_dest
    stroke(elevation_alpha[i],                 # Use the alpha-encoded elevation for red, 
           random_green,                       #   random values (per square) for green
           random_blue,                        #   and blue,
           (50 + line_per_frame * 100))        #   and high opacity when drawing single lines or low opacity when drawing all at once
    strokeWeight(500 / (subwidth + subheight))
    line(X_zoomed, Y_zoomed, X_zoomed_dest, Y_zoomed_dest)
    
    # Update counters
    i = (i + 1) % len(sub)


def set_new_subarray():
    return None

def draw_all_lines(sub):
    global i
    global keep
    fill(0, 0, 0, 255 - keep)
    rect(-50, -50, output_width + 200, output_height + 200)
    [draw_line() for i in range(len(sub))]


def draw():
    global i
    global j
    global sub
    print("i: " + str(i) + "   j: " + str(j))
    
    if line_per_frame:
        if i == 0:
            restart_drawing()
        draw_line()
    else:
        if j == 0:
            restart_drawing()
        draw_all_lines(sub)
        j = (j + 1) % 240
