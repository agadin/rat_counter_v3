import RPi.GPIO as GPIO
import time

# Set the GPIO pin number
HALL_SENSOR_PIN = 17  # Change to the correct GPIO pin

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        state = GPIO.input(HALL_SENSOR_PIN)
        if state:
            print("Magnetic field detected!")
        else:
            print("Magnetic field lost!")
        time.sleep(1)  # Sleep for 1 second
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
