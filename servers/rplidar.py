'''
On construction, basis for future developments
'''

import os
from math import cos, sin, pi, floor
import pygame
import time
from adafruit_rplidar import RPLidar
# Set up pygame and the display
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
in_x, in_y = 500 , 500
lcd = pygame.display.set_mode((in_x,in_y))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
PORT_NAMEs = '/dev/bus/usb/001/011'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

#pylint: disable=redefined-outer-name,global-statement
def process_data(data):
    global max_distance
    lcd.fill((0,0,0))
    for angle in range(360):
        distance = data[angle]
        if distance > 0 and distance < 9500:                  # ignore initially ungathered data points
            
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            
            point = (int(in_x/2 + x/5), int(in_y/2 + y/5))
            print(point)
            lcd.set_at(point, pygame.Color(255, 255, 255))
    pygame.display.update()


scan_data = [0]*360

try:
    for scan in lidar.iter_scans():
        scan_data = [0]*360
        for (qual, angle, distance) in scan:
            
            scan_data[min([359, floor(angle)])] = distance
        process_data(scan_data)
        print(qual,sum(scan_data)/360)
        

except KeyboardInterrupt:
    print('Stoping.')
lidar.stop()
lidar.disconnect()
