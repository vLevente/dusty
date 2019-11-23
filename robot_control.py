#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import time
from pycreate2 import Create2 # Original API
from copy import deepcopy

def interface2robot(robot_control_to_orch):
    port = "/dev/ttyUSB0"  
    bot = Create2(port)
    bot.start()
    bot.full()

    try:
        while True:
            if robot_control_to_orch.Array[4] == 1:
                robot_control_to_orch.Array[4] = 0
                local_command = deepcopy(robot_control_to_orch.Array)
                if local_command[2] is not 0.0: 
                    bot.turn_angle(angle = local_command[2], speed=200)
                    time.sleep(1)
                bot.drive_distance(distance = local_command[3], speed=300, stop=True)
                #TODO stop the action if needed
                time.sleep(local_command[1])
            
            time.sleep(.2)

        
    except KeyboardInterrupt:
        bot.drive_direct(0, 0)
