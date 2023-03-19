from functools import cached_property
from pyftdi.ftdi import Ftdi
import numpy as np

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
        return f

    @cached_property
    def _frame(self):
        return bytearray(513)

    @cached_property
    def levels(self):
        frame = np.array(self._frame, dtype='uint8', copy=False)
        return frame[1:]

    def transmit(self):
        # Write
        self.ftdi.set_break(True)
        self.ftdi.set_break(False)
        self.ftdi.write_data(self._frame)

    def close(self):
        self.ftdi.close()


def main():
    od = OpenDmxController()
    od.levels += 255

    while True:
        od.transmit()
        import time
        time.sleep(0.1)

main()
