#!/usr/bin/env python
#-*-coding:utf-8-*-
import time
from pycreate2 import Create2 # Original API
from copy import deepcopy

def interface2robot(orch_2_robot_control, robot_semaphore, interrupt):
    port = "/dev/ttyUSB0"  
    bot = Create2(port)
    bot.start()
    bot.full()

    try:
        while True:
            robot_semaphore.acquire()
            local_command = deepcopy(orch_2_robot_control)
            orch_2_robot_control[4] = 0
            robot_semaphore.release()

            start_time = time.time()
            goal_time = start_time+local_command[1]
            timecomplete = False

            if local_command[4] == 1:
                print("[DEBUG] interface2robot new command = {}" .format(local_command))
                if local_command[2] != 0.0:
                    bot.drive_direct(-100,100)
                    time.sleep(1.6/90 * local_command[2])
                    bot.drive_direct(0,0)
                    time.sleep(0.1)
                # bot.drive_distance(distance = local_command[3], speed=100, stop=True)

                bot.drive_direct(local_command[3], local_command[3])
                while (not interrupt[0] and not timecomplete):
                    if(time.time() >= goal_time):
                        timecomplete = True
                interrupt[0] = False
                bot.drive_direct(0,0)
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("[INFO] interface2robot finished working")
        bot.drive_direct(0, 0)