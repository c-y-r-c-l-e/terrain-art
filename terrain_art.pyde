# User settings
output_width = 1024
output_height = 720
source_img_path = "7-65-42.png"
subarray_xlim = (205, 225)            # 0 <= xmin < xmax <= 256
subarray_ylim = (85, 105)             # 0 <= ymin < ymax <= 256
line_per_frame = False
jitter_start = 0.1
jitter_stop = 0.2
swap_rg = True

# Globals
i = 0
j = 0
window = (0.05 * output_width,       #  (left, right, top, bottom)
          0.95 * output_width,
          0.05 * output_height, 
          0.95 * output_height)


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
    x_size = int(random(2, 40))
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


def draw_lines():
    global normal  # TODO: sort out these globals
    global i
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
    global jitter_start
    global jitter_stop
    # Get absolute coordinates
    X = Xs[i] + (jitter_start * randomGaussian())
    Y = Ys[i] + (jitter_start * randomGaussian())
    X_dest = Xs_dest[i] + (jitter_stop * randomGaussian())
    Y_dest = Ys_dest[i] + (jitter_stop * randomGaussian())
    
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
    stroke(elevation_alpha[i], random_green, random_blue, 20)   # Use the alpha-encoded elevation for red and random values (per square) for green and blue
    strokeWeight(500 / (subwidth + subheight))
    line(X_zoomed, Y_zoomed, X_zoomed_dest, Y_zoomed_dest)
    
    # Update counters
    i = (i + 1) % len(sub)


def set_new_subarray():
    return None

def draw_all_lines(sub):
    global i
    [draw_lines() for i in range(len(sub))]


def draw():
    global i
    global j
    global sub
    print("i: " + str(i) + "   j: " + str(j))
    
    if line_per_frame:
        if i == 0:
            restart_drawing()
        draw_lines()
    else:
        if j == 0:
            restart_drawing()
        draw_all_lines(sub)
        j = (j + 1) % 24
