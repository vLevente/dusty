#!/usr/bin/python

# Custom
import QR_scanner_from_cam
import robot_control
import uh_sensor
import orchestrator
import mqtt_client

import multiprocessing as mp
from copy import deepcopy
import time

if __name__ == '__main__':
    try:
        # Manager provides a way to create data which can be shared between different processes
        manager = mp.Manager()

        # Creating sempahores to use consistent data
        uh_semaphore = manager.BoundedSemaphore(1)
        mqtt_semaphore = manager.BoundedSemaphore(1)
        qr_semaphore = manager.BoundedSemaphore(1)
        robot_semaphore = manager.BoundedSemaphore(1)

        # Creating objects to communicate between processes
        uh_sensor_2_orch = manager.list(range(1))
        uh_sensor_2_orch[0] = 11.0
        orch_2_robot_control = manager.list(range(5)) # ID [float], time [sec], angle [degrees], distance [meter], status [float]
        mqtt_2_orch = manager.list(range(5))
        qr_proc_2_orch = manager.list(range(5))

        # Creating processes
        qr_proc = mp.Process(target = QR_scanner_from_cam.scan_qr, args=(qr_proc_2_orch, qr_semaphore))
        robot_control_process = mp.Process(target = robot_control.interface2robot, args=(orch_2_robot_control, robot_semaphore))
        orch = mp.Process(target = orchestrator.orchme, args=(orch_2_robot_control, uh_sensor_2_orch, mqtt_2_orch, qr_proc_2_orch, robot_semaphore, uh_semaphore, mqtt_semaphore, qr_semaphore))
        uh_sensor_process = mp.Process(target = uh_sensor.uh_sensor, args=(uh_sensor_2_orch, uh_semaphore))
        mqtt_process = Process(target = mqtt_client.mqtt_client , args=(mqtt_2_orch, mqtt_semaphore)) 
        
        # Kill the processes if needed
        qr_proc.daemon=True
        robot_control_process.daemon=True
        orch.daemon=True
        uh_sensor_process.daemon=True
        mqtt_process.daemon=True

        # Start the processes
        qr_proc.start()
        orch.start()
        robot_control_process.start()
        uh_sensor_process.start()
        mqtt_process.start()

        while True:
            time.sleep(5.0)
            

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        print("[INFO] __name__ finished working")
        qr_proc.join()
        orch.join()
        robot_control_process.join()
        uh_sensor_process.join()
        mqtt_process.join()