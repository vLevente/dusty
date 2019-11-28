#!/usr/bin/python

import multiprocessing as mp
import QR_scanner_from_cam
import robot_control
import uh_sensor
import mqtt_client
from copy import deepcopy
import time


def check_id(list_of_ids, new_id):
    for x in list_of_ids:
        if x == new_id:
            return False
    return True


if __name__ == '__main__':
    try:
        used_commands = []
        # Creating sempahores to use consistent data
        uh_semaphore = mp.BoundedSemaphore(1)
        mqtt_semaphore = mp.BoundedSemaphore(1)
        qr_semaphore = mp.BoundedSemaphore(1)
        robot_semaphore = mp.BoundedSemaphore(1)

        # Creating objects to communicate between processes
        uh_sensor_2_orch = mp.Value('d') 
        uh_sensor_2_orch.value = 10
        orch_2_robot_control = mp.Array('d', 5) # ID [float], time [sec], angle [degrees], distance [meter], status [float]
        mqtt_2_orch = mp.Array('d', 5)
        qr_proc_2_orch = mp.Array('d', 5)

        # Creating processes
        qr_proc = mp.Process(target = scan_qr, args=(qr_proc_2_orch, qr_semaphore,))
        robot_control_process = mp.Process(target = interface2robot, args=(orch_2_robot_control, robot_semaphore,))
        uh_sensor_process = mp.Process(target = uh_sensor, args=(uh_sensor_2_orch, uh_semaphore,))
        mqtt_process = Process(target = TODO , args=(qr_proc_2_orch, mqtt_semaphore,)) # Work in progress

        # Start the processes
        qr_proc.start()
        robot_control_process.start()
        uh_sensor_process.start()
        mqtt_process.start() 

        # We need a loop to process the data from the processes and decide what to do
        while True:
            
            uh_semaphore.acquire()
            dist_from_uh = deepcopy(uh_sensor_2_orch.value)
            uh_semaphore.release()
            if (dist_from_uh < 10):
                print ("Stopping the robot! dist = {}" .format(dist_from_uh))
                robot_semaphore.acquire()
                orch_2_robot_control.Array = [0.0, 0.1, 0.0, 0.0, 1.0] # stop the robot
                robot_semaphore.release()

            mqtt_semaphore.acquire()
            mqtt_code =  deepcopy(mqtt_2_orch.Array) # Note that this will not override the current action
            mqtt_semaphore.release()
            if(check_id(used_commands, mqtt_code[0])):
                used_commands.append(mqtt_code[0])
                robot_semaphore.acquire()
                orch_2_robot_control.Array = mqtt_code
                robot_semaphore.release()
            
            qr_semaphore.acquire()
            qr_code = deepcopy(orch_2_qr_proc.Array)
            qr_semaphore.release()
            if(check_id(used_commands, qr_code[0])):
                used_commands.append(qr_code[0])
                robot_semaphore.acquire()
                orch_2_robot_control.Array = qr_code
                robot_semaphore.release()

            time.sleep(.1)
  

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        qr_proc.join()
        robot_control_process.join()
        uh_sensor_process.join()
        mqtt_process.join()