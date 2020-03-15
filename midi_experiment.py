import rtmidi2
# print(rtmidi2.get_in_ports())
# print(rtmidi2.get_out_ports())

# midi_in = rtmidi2.MidiIn()
# midi_in.open_port(1)

# while True:
#     message, delta_time = midi_in.get_message()  # will block until a message is available
#     if message:
#          print(message, delta_time)

def callback(message, time_stamp):
    print(message, time_stamp)

midi_in = rtmidi2.MidiIn()
midi_in.callback = callback
midi_in.open_port(1)     # TODO: find a better way of selecting the device

print("a")     # This works only in debug mode in PyCharm