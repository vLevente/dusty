#!/usr/bin/python

import multiprocessing as mp
# import QR_scanner_from_cam
# import robot_control
# import uh_sensor
# import mqtt_client
from copy import deepcopy
import time


def check_id(list_of_ids, new_id):
    for x in list_of_ids:
        if x == new_id:
            return False
    return True

def dummy_qr_reader(qr_proc_2_orch, qr_semaphore):
    try:
        time.sleep(2.0)
        Tlist = [5000.0, 4.0, 0.0, 2.0, 1.0]
        qr_proc_2_orch[0] = Tlist[0]
        while True:
            qr_semaphore.acquire()
            qr_proc_2_orch[0] += 1
            qr_proc_2_orch[1] = Tlist[1]
            qr_proc_2_orch[2] = Tlist[2]
            qr_proc_2_orch[3] = Tlist[3]
            qr_proc_2_orch[4] = Tlist[4]
            qr_semaphore.release()
            time.sleep(2.0)
    
    except KeyboardInterrupt:
            print("Oh shit happened dummy_qr_reader")

def interface2robot(orch_2_robot_control, robot_semaphore):
    try:
        while True:
            robot_semaphore.acquire()
            local_command = deepcopy(orch_2_robot_control)
            orch_2_robot_control[4] = 0
            robot_semaphore.release()
            if local_command[4] == 1:
                print("[DummyRobot] new command = {}" .format(local_command))
                if local_command[2] != 0.0:
                    print("[DummyRobot] turning {} degrees" .format(local_command[2]))
                    Sleep(1.6/90 * local_command[2])
                    time.sleep(0.1)
                print("[DummyRobot] going forward {}" .format(local_command[3]))
            time.sleep(1.0)

    except KeyboardInterrupt:
        print ("Oh shit happened interface2robot")
        
def orchme(orch_2_robot_control, uh_sensor_2_orch, mqtt_2_orch, qr_proc_2_orch, robot_semaphore, uh_semaphore, mqtt_semaphore, qr_semaphore):
    try:
        mqtt_code = [0.0, 0.1, 0.0, 0.0, 1.0]
        dist_from_uh = [0.0, 0.1, 0.0, 0.0, 1.0]
        qr_code = [0.0, 0.1, 0.0, 0.0, 1.0]
        used_commands = []
        time.sleep(2.0)

        while True:
            uh_semaphore.acquire()
            dist_from_uh = deepcopy(uh_sensor_2_orch)
            uh_semaphore.release()
            if (dist_from_uh[0] < 10):
                print ("orchme Stopping the robot! dist = {}" .format(dist_from_uh[0]))
                robot_semaphore.acquire()
                orch_2_robot_control[0] = 0.0
                orch_2_robot_control[1] = 0.1
                orch_2_robot_control[2] = 0.0
                orch_2_robot_control[3] = 0.0
                orch_2_robot_control[4] = 1.0
                robot_semaphore.release()
            
            mqtt_semaphore.acquire()
            mqtt_code =  deepcopy(mqtt_2_orch) # Note that this will not override the current action
            mqtt_semaphore.release()
            if(check_id(used_commands, mqtt_code[0])):
                print ("orchme New mqtt_code! mqtt_code = {}" .format(mqtt_code))
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
                print ("orchme New qr_code! qr_code = {}" .format(qr_code))
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
        print ("Oh shit happened orchme")


if __name__ == '__main__':
    try:
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
        qr_proc = mp.Process(target = dummy_qr_reader, args=(qr_proc_2_orch, qr_semaphore))
        robot_control_process = mp.Process(target = interface2robot, args=(orch_2_robot_control, robot_semaphore))
        orch = mp.Process(target = orchme, args=(orch_2_robot_control, uh_sensor_2_orch, mqtt_2_orch, qr_proc_2_orch, robot_semaphore, uh_semaphore, mqtt_semaphore, qr_semaphore))
        # uh_sensor_process = mp.Process(target = uh_sensor, args=(uh_sensor_2_orch, uh_semaphore,))
        # mqtt_process = Process(target = TODO , args=(qr_proc_2_orch, mqtt_semaphore,)) # Work in progress
        
        # Kill the processes if needed
        qr_proc.daemon=True
        robot_control_process.daemon=True
        orch.daemon=True
        # uh_sensor_process.daemon=True
        # mqtt_process.daemon=True

        # Start the processes
        qr_proc.start()
        orch.start()
        robot_control_process.start()
        # uh_sensor_process.start()
        # mqtt_process.start()

        while True:
            time.sleep(1.0)
            

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        print("Oh shit happened __name__")
        qr_proc.join()
        orch.join()
        robot_control_process.join()
        # uh_sensor_process.join()
        # mqtt_process.join()
