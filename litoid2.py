from functools import cached_property
from pyftdi.ftdi import Ftdi

FTDI_VENDOR_ID = 0x0403
FTDI_PRODUCT_ID = 0x6001
FTDI_URL = 'ftdi:///1'
FTDI_BAUDRATE = 250_000
FTDI_LINE_PROPERTIES = dict(bits=8, stopbit=2, parity='N', break_=False)


class OpenDmxController:
    @cached_property
    def ftdi(self):
        f = Ftdi()
        f.open_from_url(FTDI_URL)
        f.reset()
        f.set_baudrate(FTDI_BAUDRATE)
        f.set_line_property(**FTDI_LINE_PROPERTIES)

    def transmit(self, frame, first):
        # Convert to a bytearray and pad the start of the frame
        # We're transmitting direct DMX data here, so a frame must start at channel 1, but can end early
        data = bytearray(([0] * first) + frame)

        # Write
        self.ftdi.set_break(True)
        self.ftdi.set_break(False)
        self.ftdi.write_data(data)
