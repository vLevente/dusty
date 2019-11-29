import context  # Ensures paho is in PYTHONPATH
import time
from re import findall
import paho.mqtt.client as mqtt

def on_message_control(mosq, obj, msg):
    # This callback will only be called for messages arrived to /robot/cotrol #

    print(">>> Robot control message arrived: " + msg.topic + " (QoS: " + str(msg.qos) + ") " + str(msg.payload))

    if msg.topic == "/robot/cotrol":
        receivedString = str(msg.payload.decode("utf-8"))
        # Convert the received string to 5 floats
        Tlist = findall(r"[-+]?\d*\.\d+|\d+", str(receivedString))
        x=0
        while x < len(Tlist):
            Tlist[x] = float(Tlist[x])
            x+=1
        print("[DEBUG] Tlist = {}" .format(Tlist))
        
        # Set the commandFlag
        client.commandFlag = True
        # Fill the commandArray
        client.commandArray = Tlist

def on_connect(mqttc, obj, flags, rc):
    print("Return code: " + str(rc))


def on_message(mosq, obj, msg):
    # This callback will be called for messages that we receive that do not
    # match any patterns defined in topic specific callbacks
    print(">>> General message arrived: " + msg.topic + " (QoS: " + str(msg.qos) + ") " + str(msg.payload))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed to: " + str(mid) + " , QoS" + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print("Log: " + string)

def mqtt_client(mqtt_2_orch, mqtt_semaphore):
    # Init MQTT client
    client = mqtt.Client("Raspberry_Robot", True)
    # Bind callbacks to callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_log
    # Define Array for callback function to pass the Array
    client.commandFlag = False
    #client.commandArray = [0.0 0.0 0.0 0.0 0.0] OG
    client.commandArray = [0.0, 0.0, 0.0, 0.0, 0.0] # This is a correct list

    client.message_callback_add("/robot/cotrol#", on_message_control)

    # TODO: IP address of the Rpi
    # connect(host, port, keepalive[s]) 
    client.connect("192.168.1.167", 1883, 60)

    # Subscribe to relevant topic
    client.subscribe("/robot/cotrol", 0)

    # Let's loop here forever, waiting for incoming control commands
    try:
        while True:
            # If a controll message arrives to /robot/control topic
            # on_message_control() callback function handle it
            client.loop()

            if client.commandFlag:
                print("No command message received yet")
                
            if client.commandFlag:
                # take the semaphore, and write the command to the Array
                mqtt_semaphore.acquire()
                mqtt_2_orch[0] = client.commandArray[0]
                mqtt_2_orch[1] = client.commandArray[1]
                mqtt_2_orch[2] = client.commandArray[2]
                mqtt_2_orch[3] = client.commandArray[3]
                mqtt_2_orch[4] = client.commandArray[4]
                print("[DEBUG] New mqtt message mqtt_2_orch = {}" .format(mqtt_2_orch))
                client.commandFlag = False
                mqtt_semaphore.release()
    
    except KeyboardInterrupt:
        print("[INFO] mqtt_client finished working")
