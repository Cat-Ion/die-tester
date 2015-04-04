import serial

port = None

def init(dev, baud):
    global port

    if port == None:
        port = serial.Serial(dev, baud)
        port.readline()

def shake():
    global port
    port.write("1\r\n")
    port.readline()
