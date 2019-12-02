#!/usr/bin/python

import multiprocessing as mp
from copy import deepcopy
import time


def check_id(list_of_ids, new_id):
    for x in list_of_ids:
        if x == new_id:
            return False
    return True


def orchme(orch_2_robot_control, uh_sensor_2_orch, mqtt_2_orch, qr_proc_2_orch, robot_semaphore, uh_semaphore, mqtt_semaphore, qr_semaphore):
    try:
        # HACK we need a valid initial value
        mqtt_code = [999.0, 0.1, 0.0, 0.0, 1.0] 
        dist_from_uh = [999.0, 0.1, 0.0, 0.0, 1.0]
        qr_code = [999.0, 0.1, 0.0, 0.0, 1.0]
        used_commands = []
        interrupt[0] = False

        time.sleep(2.0)

        while True:
            uh_semaphore.acquire()
            dist_from_uh = deepcopy(uh_sensor_2_orch)
            uh_semaphore.release()
            if (dist_from_uh[0] < 10):
                print ("Stopping the robot! dist = {}" .format(dist_from_uh[0]))
                robot_semaphore.acquire()
                orch_2_robot_control[0] = 0.0
                orch_2_robot_control[1] = 0.1
                orch_2_robot_control[2] = 0.0
                orch_2_robot_control[3] = 0.0
                orch_2_robot_control[4] = 1.0
                interrupt[0] = True
                robot_semaphore.release()
            
            mqtt_semaphore.acquire()
            mqtt_code =  deepcopy(mqtt_2_orch) # Note that this will not override the current action
            mqtt_semaphore.release()
            if(check_id(used_commands, mqtt_code[0])):
                print ("New mqtt_code! mqtt_code = {}" .format(mqtt_code))
                used_commands.append(mqtt_code[0])
                robot_semaphore.acquire()
                orch_2_robot_control[0] = mqtt_code[0]
                orch_2_robot_control[1] = mqtt_code[1]
                orch_2_robot_control[2] = mqtt_code[2]
                orch_2_robot_control[3] = mqtt_code[3]
                orch_2_robot_control[4] = mqtt_code[4]
                robot_semaphore.release()
            
            qr_semaphore.acquire()
            qr_code = deepcopy(qr_proc_2_orch)
            qr_semaphore.release()
            if(check_id(used_commands, qr_code[0])):
                print ("New qr_code! qr_code = {}" .format(qr_code))
                used_commands.append(qr_code[0])
                robot_semaphore.acquire()
                orch_2_robot_control[0] = qr_code[0]
                orch_2_robot_control[1] = qr_code[1]
                orch_2_robot_control[2] = qr_code[2]
                orch_2_robot_control[3] = qr_code[3]
                orch_2_robot_control[4] = qr_code[4]
                robot_semaphore.release()
            time.sleep(2.2)

    except KeyboardInterrupt:
        print ("[INFO] orchme finished working")