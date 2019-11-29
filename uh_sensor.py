# Import required Python libraries
import time
import RPi.GPIO as GPIO
import multiprocessing
# from copy import deepcopy

def uh_sensor(uh_sensor_2_orch, uh_semaphore):
    # Use BCM GPIO references
    # instead of physical pin numbers
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Define GPIO to use on Pi
    GPIO_TRIGGER = 20
    GPIO_ECHO    = 21

    # Set pins as output and input
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
    GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER, False)
    # Allow module to settle
    time.sleep(0.5)

    try:
        while True:
            # Send 10us pulse to trigger
            GPIO.output(GPIO_TRIGGER, True)
            time.sleep(0.00001) 
            GPIO.output(GPIO_TRIGGER, False)
            start = time.time()

            while GPIO.input(GPIO_ECHO)==0:
                start = time.time()

            while GPIO.input(GPIO_ECHO)==1:
                stop = time.time()

            # Calculate pulse length
            elapsed = stop-start

            # Distance pulse travelled in that time is time
            # multiplied by the speed of sound (cm/s)
            distancet = elapsed * 34300

            # That was the distance there and back so halve the value
            distance = distancet / 2
            
            uh_semaphore.acquire()
            uh_sensor_2_orch[0] = distance
            uh_semaphore.release()

            time.sleep(.5) 
            
    except KeyboardInterrupt:
        GPIO.cleanup() # Reset GPIO settings

