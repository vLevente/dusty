#!/usr/bin/python

import multiprocessing as mp
import QR_scanner_from_cam
import robot_control
import uh_sensor
# import mqtt_client
from copy import deepcopy
import time

if __name__ == '__main__':
    try:
        # Creating objects to communicate between processes
        uh_sensor_2_orch = mp.Value('d') 
        uh_sensor_2_orch.value = 10
        orch_2_robot_control = mp.Array('d', 5) # ID [float], time [msec], angle [degrees], distance [meter], status [float]
        mqtt_2_orch = mp.Array('d', 5)
        qr_proc_2_orch = mp.Array('d', 5)

        # Creating processes
        qr_proc = Process(target = scan_qr, args=(qr_proc_2_orch,))
        robot_control_process = Process(target = interface2robot, args=(orch_2_robot_control,))
        uh_sensor_process = mp.Process(target = uh_sensor, args=(uh_sensor_2_orch,))
        # mqtt_process = Process(target = TODO , args=(qr_proc_2_orch,)) # Work in progress

        # Start the processes
        qr_proc.start()
        robot_control_process.start()
        uh_sensor_process.start()
        # mqtt_process.start() 

        # We need a loop to process the data from the processes and decide what to do
        while True:
            current_command_id

            dist_from_uh = uh_sensor_2_orch.value
            if (dist_from_uh < 10):
                print ("Stopping the robot! dist = {}" .format(dist_from_uh))
                orch_2_robot_control.Array = [0.0 0.1, 0.0, 0.0, 1.0] # stop the robot

            qr_code = deepcopy(orch_2_qr_proc.Array)
            if(current_command_id is not qr_code[0])
                orch_2_robot_control.Array = qr_code

            mqtt_code =  deepcopy(mqtt_2_orch.Array) # Note that this will not override the current action
            if(current_command_id is not mqtt_code[0])
                orch_2_robot_control.Array = mqtt_code

            time.sleep(.1)
  

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        qr_proc.join()
        robot_control_process.join()
        uh_sensor_process.join()
        # mqtt_process.join()