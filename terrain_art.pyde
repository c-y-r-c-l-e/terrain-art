# User settings
output_height = 720
output_width = 1024
source_img_path = "7-65-42.png"
magnify = 2.5

# Globals
counter = 0


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


def draw():
    global counter
    global normal
    
    background(0 + counter)
    root = int(sqrt(len(normal.pixels)))
    random_green = random(0, 255)           # Pick a random value for the green channel
    
    for i in range(len(normal.pixels)):
        # Extract values from the png-encoded terrain data
        i_elevation_alpha = (normal.pixels[i] >> 24) & 0xFF
        i_normal_red = (normal.pixels[i] >> 16) & 0xFF
        i_normal_green = (normal.pixels[i] >> 8) & 0xFF
        i_normal_blue = normal.pixels[i] & 0xFF
        
        # Get coordinates from the 1D list of pixels
        X = (i % root) * magnify
        Y = (i // root) * magnify
        
        X_dest = X + magnify * 0.0390625 * (i_normal_red - 128)
        Y_dest = Y + magnify * 0.0390625 * (i_normal_green - 128)
        
        # print(str(i) + "   " + 
        #       str(X) + "   " + 
        #       str(Y) + "   " + 
        #       str(X_dest) + "   " + 
        #       str(Y_dest) + "   " + 
        #       str(hex(normal.pixels[i])) + "   " + 
        #       str(i_elevation_alpha) + "   " +
        #       str(i_normal_red) + "   " +
        #       str(i_normal_green) + "   " +
        #       str(i_normal_blue))
        
        # Draw the lines from C to C_dest
        stroke(i_elevation_alpha, random_green, 22)   # Use the alpha-encoded elevation for red and a random value (per draw) for green
        strokeWeight(0.5)
        line(X + 50, 
             Y + 50, 
             X_dest + 50, 
             Y_dest + 50)
    counter += 1
