import serial
from pyftdi.serialext import SerialConverter
from pydmx import DmxController

# Configure serial port for FTDI USB-to-serial converter
serial_port = serial.Serial(
    port='/dev/cu.usbserial-6AYL2V8Z',
    baudrate=57600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1
)

# Create SerialConverter to interface with Enttec DMX USB Pro controller
converter = SerialConverter(serial_port)
controller = DmxController(converter)

# Set DMX channels to desired values
controller.set_channel(1, 255)  # Set channel 1 to full brightness (255)
controller.set_channel(2, 128)  # Set channel 2 to half brightness (128)
controller.set_channel(3, 0)    # Set channel 3 to off (0)

# Update DMX output
controller.render()

# Disconnect from DMX controller
controller.close()
converter.close()
