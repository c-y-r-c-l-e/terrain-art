output_height = 720
output_width = 1024
source_img_path = "7-65-42.png"
magnify = 2.5

def init_source_img(path):
    normal = loadImage(path)
    image(normal, output_height, output_width)  # Display the img where we don't see it
    loadPixels()
    return normal

def setup():
    size(output_width, output_height)
    background(0)

def draw():
    background(0)
    normal = init_source_img(source_img_path)
    root = int(sqrt(len(normal.pixels)))
    random_green = random(0, 255)
    for i in range(len(normal.pixels)):
        i_elevation_alpha = (normal.pixels[i] >> 24) & 0xFF
        i_normal_red = (normal.pixels[i] >> 16) & 0xFF
        i_normal_green = (normal.pixels[i] >> 8) & 0xFF
        i_normal_blue = normal.pixels[i] & 0xFF
        
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
        stroke(i_elevation_alpha, random_green, 22)   # Use the alpha-encoded elevation for red and a random value (per draw) for green
        strokeWeight(0.5)
        line(X + 50, 
             Y + 50, 
             X_dest + 50, 
             Y_dest + 50)
