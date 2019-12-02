cat: main: No such file or directory
pi@raspberrypi:~/dusty$ cat main.PY
cat: main.PY: No such file or directory
pi@raspberrypi:~/dusty$ cat main.py
#!/usr/bin/python

# Custom
import QR_scanner_from_cam
import robot_control
import uh_sensor
import orchestrator
# import mqtt_client

import multiprocessing as mp
from copy import deepcopy
import time
from re import findall
import paho.mqtt.client as mqtt

# -------------------------------------------------------------------------
def init_robot_client(cname, cleansession):
    # Define MQTT client instance
    client = mqtt.Client(cname, cleansession)
    # Bind callbacks to callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_log = on_log
    # Define and set custom flags for iiot UE application
    client.commandArrived = False
    client.commandArray = [0.0, 0.0, 0.0, 0.0, 0.0] # This is a correct list
    return client

def on_message_robot(mosq, obj, msg):
    # This callback runs when a message arrives to /robot/cotrol #
    print(">>> Robot control message arrived to topic: " + msg.topic + " (QoS: " + str(msg.qos) + "), Payload:" + str(msg.payload))

    if msg.topic == "/robot/control":
        receivedString = str(msg.payload.decode("utf-8"))

        # Convert the received string to 5 floats
        Tlist = [0, 0, 0, 0, 0]
        Tlist = findall(r"[-+]?\d*\.\d+|\d+", str(receivedString))
        x=0
        while x < len(Tlist):
            Tlist[x] = float(Tlist[x])
            x+=1
        print("[DEBUG] Tlist = {}" .format(Tlist))
        
        # Set the commandArrived
        mqttc.commandArrived = True
        # Fill the commandArray
        mqttc.commandArray = deepcopy(Tlist)
        print("[DEBUG] client.commandArray = {}" .format(mqttc.commandArray))

def on_connect(mqttc, obj, flags, rc):
    print("Return code: " + str(rc))

def on_message(mosq, obj, msg):
    # This callback will be called for messages that we receive that do not
    # match any patterns defined in topic specific callbacks
    print(">>> General message arrived: " + msg.topic + " (QoS: " + str(msg.qos) + ") " + str(msg.payload))

def on_publish(mqttc, obj, mid):
    print("Publish message ID: " + str(mid))
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed to: " + str(mid) + " , QoS" + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print("Log: " + string)

def mqtt_client(mqtt_2_orch, mqtt_semaphore):
    # Init iiot client instance
    # mqttc = init_robot_client("Raspberry028", True)
    print (mqttc)

    # Add message callbacks that will only trigger on a specific subscription match.
    mqttc.message_callback_add("/robot/control/#", on_message_robot)

    # TODO: IP address of the Rpi
    # connect(host, port, keepalive[s])
    mqttc.connect("152.66.244.201", 1883, 60)

    # Start the loop thread - runs in the background asynchronously until mqttc.loop_stop() is called!
    # mqttc.loop_start()

    # Subscribe to topics
    mqttc.subscribe("/robot/control/#", 0)

    try:
        while True:
            # If a controll message arrives to /robot/control topic
            # on_message_control() callback function handle it
            mqttc.loop()

            if not mqttc.commandArrived:
                print("No command message received over mqtt")
                
            if mqttc.commandArrived:
                # take the semaphore, and write the command to the Array
                mqtt_semaphore.acquire()
                print("[DEBUG] client.commandArray = {}" .format(mqttc.commandArray))
                mqtt_2_orch[0] = mqttc.commandArray[0]
                mqtt_2_orch[1] = mqttc.commandArray[1]
                mqtt_2_orch[2] = mqttc.commandArray[2]
                mqtt_2_orch[3] = mqttc.commandArray[3]
                mqtt_2_orch[4] = mqttc.commandArray[4]
                print("[DEBUG] New mqtt_2_orch= {}" .format(mqtt_2_orch))
                mqttc.commandArrived = False
                mqtt_semaphore.release()
            
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("[INFO] mqtt_client finished working")

# Init iiot client instance - MUST BE GLOBAL!!
mqttc = init_robot_client("Raspberry028", True)

# -------------------------------------------------------------------------

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
        mqtt_process = mp.Process(target = mqtt_client , args=(mqtt_2_orch, mqtt_semaphore)) 
        
        # Kill the processes if needed
        # qr_proc.daemon=True
        robot_control_process.daemon=True
        orch.daemon=True
        uh_sensor_process.daemon=True
        mqtt_process.daemon=True

        # Start the processes
        # qr_proc.start()
        orch.start()
        robot_control_process.start()
        uh_sensor_process.start()
        mqtt_process.start()

        while True:
            time.sleep(5.0)
            

    except KeyboardInterrupt:
        # Wait to finish the processes (which normally does not happen)
        print("[INFO] __name__ finished working")
        # qr_proc.join()
        orch.join()
        robot_control_process.join()
        uh_sensor_process.join()
        mqtt_process.join()
