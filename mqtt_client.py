import context  # Ensures paho is in PYTHONPATH
import time
import paho.mqtt.client as mqtt


def init_iiot_client(cname, cleansession):
    # Define MQTT client instance
    client = mqtt.Client(cname, cleansession)
    # Bind callbacks to callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    # client.on_log = on_log
    # Define and set custom flags for iiot UE application
    client.getConfigArrived = False
    client.apnSelectionArrived = False
    client.startWorkingArrived = False
    client.connected_flag = False
    client.disconnect_flag = False
    return client


def on_message_iot(mosq, obj, msg):
    # This callback will only be called for messages with topics that match
    # /iiot/device/Huawei01/iot/#

    print(">>> IoT message arrived: " + msg.topic + " (QoS: " + str(msg.qos) + ") " + str(msg.payload))

    if str(msg.payload.decode("utf-8")) == "getConfig" and msg.topic == "/iiot/device/Huawei01/iot":
        mqttc.getConfigArrived = True

    if str(msg.payload.decode("utf-8")) == "startWorking" and msg.topic == "/iiot/device/Huawei01/iot":
        mqttc.startWorkingArrived = True


def on_message_3gpp(mosq, obj, msg):
    # This callback will only be called for messages with topics that match
    # /iiot/device/216012087073947/3gpp/#

    print(">>> 3GPP message arrived: " + msg.topic + " (QoS: " + str(msg.qos) + ") " + str(msg.payload))

    if str(msg.payload.decode("utf-8")) == "apnSelection" and msg.topic == "/iiot/device/216012087073947/3gpp":
        # TODO: also have to pass the new APN name to the main thread!!
        mqttc.apnSelectionArrived = True


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


# Init iiot client instance
mqttc = init_iiot_client("Raspberry028", True)

# Add message callbacks that will only trigger on a specific subscription match.
mqttc.message_callback_add("/iiot/device/Huawei01/iot/#", on_message_iot)
mqttc.message_callback_add("/iiot/device/216012087073947/3gpp/#", on_message_3gpp)

######################################################################################
# TODO: Connect to 5G (with Huawei e3372 LTE stick)
# - in final application this will be the only internet connection of the Raspberry Pi,
#       so it is necessary to bring up MQTT connection
# - but in the development phase I need the local wireless connection too, for SSH
#       and as a side effect, this connection can be used to bring up MQTT connection!
######################################################################################

# TODO: change this to 172.16.7.14
mqttc.connect("192.168.0.153", 1883, 60)

# Start the loop thread - runs in the background asynchronously until mqttc.loop_stop() is called!
mqttc.loop_start()

# Subscribe to topics
mqttc.subscribe("/iiot/device/Huawei01/iot/#", 0)
mqttc.subscribe("/iiot/device/216012087073947/3gpp/#", 0)
mqttc.subscribe("/iiot", 0)

# Publish 5G attached message and wait until completed!
info_init = mqttc.publish("/iiot/device/216012087073947/3gpp/attach", "ATTACHED", qos=0)
time.sleep(3)  # Give 3sec time to the loop thread to complete the action
info_init.wait_for_publish()

# Publish getConfiguration message for myself - ( DELETE THIS LATER!! )
# info_getconf = mqttc.publish("/iiot/device/Huawei01/iot", "getConfig", qos=0)
# time.sleep(3)  # Give 3sec time to the loop thread to complete the action
# info_getconf.wait_for_publish()

while not mqttc.getConfigArrived:
    print("getConfig message not arrived yet")
    time.sleep(5)

if mqttc.getConfigArrived:
    info_conf = mqttc.publish("/iiot/device/Huawei01/iot", "Device configuration - JSON", qos=0)
    info_conf.wait_for_publish()

# Publish new APN selection message for myself - ( DELETE THIS LATER!! )
# info_apn = mqttc.publish("/iiot/device/216012087073947/3gpp", "apnSelection", qos=0)
# time.sleep(3)  # Give 3sec time to the loop thread to complete the action
# info_apn.wait_for_publish()

while not mqttc.apnSelectionArrived:
    print("apnSelection message not received yet")
    time.sleep(5)

if mqttc.apnSelectionArrived:
    info_detach = mqttc.publish("/iiot/device/216012087073947/3gpp/detach", "Detach old APN - JSON", qos=0)
    info_detach.wait_for_publish()
    time.sleep(10)
    ################################################################################################
    #
    # TODO: detach old APN, and attach new APN via AT commands - this should be in the main thread!!
    #
    ################################################################################################
    info_attach = mqttc.publish("/iiot/device/216012087073947/3gpp/attach", "Attach new APN - JSON", qos=0)
    info_attach.wait_for_publish()

# Publish startWorking myself - ( DELETE THIS LATER!! )
# info_apn = mqttc.publish("/iiot/device/Huawei01/iot", "startWorking", qos=0)
# time.sleep(3)  # Give 3sec time to the loop thread to complete the action
# info_apn.wait_for_publish()

while not mqttc.startWorkingArrived:
    print("startWorking message not received yet")
    time.sleep(5)

if mqttc.startWorkingArrived:
    info_start = mqttc.publish("/iiot/device/Huawei01/iot", "Start working OK - JSON", qos=0)
    info_start.wait_for_publish()

while True:
    # TODO: looping the IoT process controller application
    # TODO: permanently check the MQTT and 5G connection - if lost, repeat the whole connection establishment

    time.sleep(10)
    print("Working...")
