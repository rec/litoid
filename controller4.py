import time
from pylibftdi import BitBangDevice
from pydmx import DmxController

# Configure FTDI USB-to-serial converter as a bit-bang device
bb_device = BitBangDevice()
bb_device.baudrate = 57600
bb_device.direction = 0xFF  # Set all pins to output

# Initialize DMX controller with the bit-bang device
controller = DmxController(bb_device)

# Set DMX channels to desired values
controller.set_channel(1, 255)  # Set channel 1 to full brightness (255)
controller.set_channel(2, 128)  # Set channel 2 to half brightness (128)
controller.set_channel(3, 0)    # Set channel 3 to off (0)

# Update DMX output
controller.render()

# Wait for a short period of time to allow the lights to update
time.sleep(1)

# Disconnect from DMX controller
controller.close()
bb_device.close()
