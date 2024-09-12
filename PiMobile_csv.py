# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:48:04 2024

@author: eric kohler aka barzouga
"""

import os
import time
import csv
from sgp30 import SGP30
import sys
from smbus2 import SMBus
from bmp280 import BMP280
import smbus


today = time.strftime("%Y-%m-%d")

data_dir = '../data_PiMobile'

today_dir = os.path.join(data_dir, today)

if not os.path.exists(data_dir):
    #print(f"Le répertoire '{data_dir}' n'existe pas. Création...")
    os.makedirs(data_dir)
#else:
    #print(f"Le répertoire '{data_dir}' existe déjà.")

if not os.path.exists(today_dir):
    #print(f"Le répertoire '{today_dir}' n'existe pas. Création...")
    os.makedirs(today_dir)
#else:
    #print(f"Le répertoire '{today_dir}' existe déjà.")


csv_file = os.path.join(today_dir, today+".csv")

sgp30 = SGP30()

#print("SGP30 warming up, please wait...Press Ctrl+C to exit!")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')

bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)
bus = smbus.SMBus(1)
config = [0x08, 0x00]
#plt.text(0.5, 0.5, 'T P CO2 COV HR T', horizontalalignment='center',verticalalignment='center')
while True:
    #plt.close()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    #plt.text(0.1, 0.7, time.time())#•, horizontalalignment='center',verticalalignment='center')
    result = sgp30.get_air_quality()
    #print(result)
    #plt.text(0.1, 0.6, result)
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    #print(f"{temperature:05.2f}*C {pressure:05.2f}hPa")
    #plt.text(0.1, 0.5, f"{temperature:05.2f}*C {pressure:05.2f}hPa")#•, horizontalalignment='center',verticalalignment='center')
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
    #print(u'Temperature: {0:.1f}°C'.format(ctemp))
    #plt.text(0.1, 0.4, u'Temperature: {0:.1f}°C'.format(ctemp))#•, horizontalalignment='center',verticalalignment='center')
    tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    #print(tmp)
    ctmp = int(tmp * 100 / 1048576)
    #plt.text(0.1, 0.4, u'Humidity: {0}%'.format(ctmp))
    #print(u'Humidity: {0}%'.format(ctmp))
    
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow([timestamp, str(result) + f"{temperature:05.2f}*C {pressure:05.2f}hPa" + u'Temperature: {0:.1f}°C'.format(ctemp) + u'Humidity: {0}%'.format(ctmp)])
    
    #print(f"Données enregistrées : {timestamp}, {result}")
    
    time.sleep(1.0)
    