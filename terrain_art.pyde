def setup():
    size(200,200)
    background(0)

def draw():
    tensor = [[14, 84, 94, 68, 76, 56, 22, 40, 96, 03],
              [90, 31, 58, 40, 01, 55, 72, 20, 77, 83],
              [30, 53, 32, 72, 74, 65, 29, 93, 69, 26],
              [16, 35, 88, 58, 74, 10, 85, 62, 93, 01],
              [98, 79, 19, 12, 53, 42, 78, 52, 64, 72],
              [82, 76, 51, 54, 16, 51, 99, 13, 78, 15],
              [49, 72, 63, 38, 47, 93, 28, 94, 64, 48],
              [48, 68, 37, 90, 21, 13, 04, 25, 73, 66],
              [78, 06, 32, 33, 91, 01, 81, 68, 83, 02],
              [80, 95, 99, 64, 23, 82, 35, 40, 40, 58]]
    for X in range(10):
        for Y in range(10):
            stroke(128)
            line(10 * X + 50, 
                 10 * Y + 50, 
                 X + tensor[X][Y] + 50, 
                 Y + tensor[X][Y] + 50)
