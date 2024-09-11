# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:39:08 2024

@author: eric kohler aka barzouga
"""

from sgp30 import SGP30
import time
import sys
from smbus2 import SMBus
from bmp280 import BMP280
import smbus

sgp30 = SGP30()

print("SGP30 warming up, please wait...Press Ctrl+C to exit!")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')

bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)
bus = smbus.SMBus(1)

while True:
    print(time.time())
    result = sgp30.get_air_quality()
    print(result)
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    print(f"{temperature:05.2f}*C {pressure:05.2f}hPa")
    config = [0x08, 0x00]
    bus.write_i2c_block_data(0x38, 0xE1, config)
    time.sleep(0.5)
    byt = bus.read_byte(0x38)
    #print(byt&0x68)
    MeasureCmd = [0x33, 0x00]
    bus.write_i2c_block_data(0x38, 0xAC, MeasureCmd)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38,0x00)
    #print(data)
    temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    ctemp = ((temp*200) / 1048576) - 50
    print(u'Temperature: {0:.1f}°C'.format(ctemp))
    tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    #print(tmp)
    ctmp = int(tmp * 100 / 1048576)
    print(u'Humidity: {0}%'.format(ctmp))
    time.sleep(1.0)
    

