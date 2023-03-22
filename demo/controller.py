import time
import pyenttec as dmx

con = dmx.DMXConnection('/dev/cu.usbserial-6AYL2V8Z')
con.dmx_frame[0] = con.dmx_frame[1] = con.dmx_frame[2] = 1 * 100
con.render()
time.sleep(3)

con.dmx_frame[0] = con.dmx_frame[1] = con.dmx_frame[2] = 0 * 100
con.render()
time.sleep(0.1)
