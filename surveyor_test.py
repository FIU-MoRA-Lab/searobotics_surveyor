import sys
import time
import pandas as pd
import cv2

# import surveyor_library
import surveyor_library.surveyor_helper as hlp
from surveyor_library import Surveyor


boat = Surveyor()
SPEED = 9
DELAY = 1.5
print(boat.exo2.exo2_params)

with boat:
    while True:
        
        ret, frame = boat.get_image()
        print(boat.get_data())
        # print(frame)
        if ret:
            cv2.imshow('Video Stream', frame)
            cv2.waitKey(1)
        # time.sleep(0.01)
    
    cv2.destroyAllWindows()

    
