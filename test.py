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
    time.sleep(2.0)
    Tlist = [5000.0, 4.0, 0.0, 2.0, 1.0] 
    qr_semaphore.acquire()
    qr_proc_to_orch = Tlist
    print("[DEBUG] qr_proc_to_orch = {}" .format(qr_proc_to_orch))
    qr_semaphore.release()

def interface2robot(robot_control_to_orch, robot_semaphore):
    try:
        while True:
            if robot_control_to_orch[4] == 1:
                robot_semaphore.acquire()
                robot_control_to_orch[4] = 0
                local_command = deepcopy(robot_control_to_orch)
                print("[DummyRobot] new command = {}" .format(local_command))
                robot_semaphore.release()
                if local_command[2] != 0.0: 
                    # bot.turn_angle(angle = local_command[2], speed=200)
                    print("[DummyRobot] turning {} degrees" .format(local_command[2]))
                    Sleep(1.6/90 * local_command[2])
                    # bot.drive_direct(0,0)
                    time.sleep(0.1)
                
                print("[DummyRobot] going forward {}" .format(local_command[3]))
                # TODO stop the action if needed
                # time.sleep(local_command[1])
            
            time.sleep(.2)

        
    except KeyboardInterrupt:
        # bot.drive_direct(0, 0)
        print ("kalap")

if __name__ == '__main__':
    try:
        used_commands = []
        manager = mp.Manager()
        # Creating sempahores to use consistent data
        uh_semaphore = manager.BoundedSemaphore(1)
        mqtt_semaphore = manager.BoundedSemaphore(1)
        qr_semaphore = manager.BoundedSemaphore(1)
        robot_semaphore = manager.BoundedSemaphore(1)

        # Creating objects to communicate between processes
        uh_sensor_2_orch = manager.Value('d', 10) 
        uh_sensor_2_orch = 10.0
        orch_2_robot_control = manager.Array('d', []) # ID [float], time [sec], angle [degrees], distance [meter], status [float]
        mqtt_2_orch = manager.Array('d', [])
        qr_proc_2_orch = manager.Array('d', [])

        # Creating processes
        qr_proc = mp.Process(target = dummy_qr_reader, args=(qr_proc_2_orch, qr_semaphore,))
        # robot_control_process = mp.Process(target = interface2robot, args=(orch_2_robot_control, robot_semaphore,))
        # uh_sensor_process = mp.Process(target = uh_sensor, args=(uh_sensor_2_orch, uh_semaphore,))
        # mqtt_process = Process(target = TODO , args=(qr_proc_2_orch, mqtt_semaphore,)) # Work in progress

        # Start the processes
        qr_proc.start()
        # robot_control_process.start()
        # uh_sensor_process.start()
        # mqtt_process.start() 

        # # We need a loop to process the data from the processes and decide what to do
        # while True:
            
        #     uh_semaphore.acquire()
        #     dist_from_uh = deepcopy(uh_sensor_2_orch)
        #     uh_semaphore.release()
        #     if (dist_from_uh < 10):
        #         print ("Stopping the robot! dist = {}" .format(dist_from_uh))
        #         robot_semaphore.acquire()
        #         orch_2_robot_control = [0.0, 0.1, 0.0, 0.0, 1.0] # stop the robot
        #         robot_semaphore.release()

        #     mqtt_semaphore.acquire()
        #     mqtt_code =  deepcopy(mqtt_2_orch) # Note that this will not override the current action
        #     mqtt_semaphore.release()
        #     if(check_id(used_commands, mqtt_code[0])):
        #         used_commands.append(mqtt_code[0])
        #         robot_semaphore.acquire()
        #         orch_2_robot_control = mqtt_code
        #         robot_semaphore.release()
            
        #     qr_semaphore.acquire()
        #     qr_code = deepcopy(orch_2_qr_proc)
        #     qr_semaphore.release()
        #     if(check_id(used_commands, qr_code[0])):
        #         used_commands.append(qr_code[0])
        #         robot_semaphore.acquire()
        #         orch_2_robot_control = qr_code
        #         robot_semaphore.release()

        #     time.sleep(.1)

        qr_proc.join()
        qr_semaphore.acquire()
        print("[DEBUG] qr_proc_to_orch2 = {}" .format(qr_proc_2_orch))
        qr_semaphore.release()
        # robot_control_process.join()
        

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        qr_proc.join()
        # robot_control_process.join()
        # uh_sensor_process.join()
        # mqtt_process.join()