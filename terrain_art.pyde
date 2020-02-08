# User settings
output_height = 720
output_width = 1024
source_img_path = "7-65-42.png"
magnify = 2.5
subarray_xlim = (95, 105)            # 0 <= xmin < xmax <= 256
subarray_ylim = (85, 95)           # 0 <= ymin < ymax <= 256

# Globals
counter = 0
i = 0


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


def restart_drawing():
    global normal
    global sub
    global subwidth
    global subheight
    global root
    background(0)
    subwidth = subarray_xlim[1] - subarray_xlim[0]
    subheight = subarray_ylim[1] - subarray_ylim[0]
    root = int(sqrt(len(normal.pixels)))    
    sub = [p for p in range(len(normal.pixels)) if 
           (p % root) >= subarray_xlim[0] and 
           (p % root) < subarray_xlim[1] and 
           (p // root) >= subarray_ylim[0] and 
           (p // root) < subarray_ylim[1]]


def draw():
    global counter
    global normal
    global i
    global sub
    global subwidth
    global subheight
    global root
    global subarray_xlim
    global subarray_ylim
    
    if counter == 0:
        restart_drawing()

    random_green = random(0, 255)           # Pick a random value for the green channel
    
    # Extract values from the png-encoded terrain data
    i_elevation_alpha = (normal.pixels[sub[i]] >> 24) & 0xFF
    i_normal_red = (normal.pixels[sub[i]] >> 16) & 0xFF
    i_normal_green = (normal.pixels[sub[i]] >> 8) & 0xFF
    i_normal_blue = normal.pixels[sub[i]] & 0xFF
    
    # Get coordinates from the 1D list of pixels
    X = (sub[i] % root) * magnify
    Y = (sub[i] // root) * magnify
    
    X_dest = X + magnify * 0.0390625 * (i_normal_red - 128)
    Y_dest = Y + magnify * 0.0390625 * (i_normal_green - 128)
    
    # Draw the lines from C to C_dest
    stroke(i_elevation_alpha, random_green, 22)   # Use the alpha-encoded elevation for red and a random value (per draw) for green
    strokeWeight(0.5)
    line(X + 50, 
         Y + 50, 
         X_dest + 50, 
         Y_dest + 50)
    
    # Update counters
    i = (i + 1) % len(sub)
    counter = (counter + 1) % (subwidth * subheight) 
