from p5 import *
import rtmidi2

# User settings
output_width = 800
output_height = 600

# midi-influenced globals
midi_from_x = 0
midi_from_y = 0
midi_to_x = 1
midi_to_y = 1
midi_stroke_weight = 1
midi_red = 0
midi_green = 0
midi_blue = 0

def midi_callback(message, time_stamp):
    global midi_from_x
    global midi_from_y
    global midi_to_x
    global midi_to_y
    global midi_stroke_weight
    global midi_red
    global midi_green
    global midi_blue
    if message[0] == 176 and message[1] == 20:
        midi_from_x = remap(message[2], (0, 127), (0, output_width))
    if message[0] == 176 and message[1] == 21:
        midi_from_y = remap(message[2], (0, 127), (0, output_height))
    if message[0] == 176 and message[1] == 22:
        midi_to_x = remap(message[2], (0, 127), (0, output_width))
    if message[0] == 176 and message[1] == 23:
        midi_to_y = remap(message[2], (0, 127), (0, output_height))
    if message[0] == 176 and message[1] == 24:
        midi_stroke_weight = remap(message[2], (0, 127), (0, 800))
    if message[0] == 176 and message[1] == 25:
        midi_red = remap(message[2], (0, 127), (0, 255))
    if message[0] == 176 and message[1] == 26:
        midi_green = remap(message[2], (0, 127), (0, 255))
    if message[0] == 176 and message[1] == 27:
        midi_blue = remap(message[2], (0, 127), (0, 255))
    print("message:  " + str(message) + "   message[0]:  " + str(message[0]))

midi_in = rtmidi2.MidiIn()
midi_in.callback = midi_callback
midi_in.open_port(1)  # TODO: find a better way of selecting the device


def setup():
    size(output_width, output_height)
    color_mode("RGB")
    background(12)


def draw():
    background(34)
    stroke(r=midi_red, g=midi_green, b=midi_blue)
    stroke_weight(midi_stroke_weight)
    if not (midi_from_x, midi_from_y) == (midi_to_x, midi_to_y):
        line((midi_from_x, midi_from_y), (midi_to_x, midi_to_y))


if __name__ == "__main__":
    run()