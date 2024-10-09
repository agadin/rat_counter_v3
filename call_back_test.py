import RPi.GPIO as GPIO
import time

# Configure GPIO
HALL_SENSOR_PIN = 17  # Use the GPIO pin connected to the Hall effect sensor

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Use a pull-down resistor

# Callback function to be called when the Hall effect sensor detects a magnetic field
def hall_effect_callback(channel):
    if GPIO.input(HALL_SENSOR_PIN):
        print("Magnetic field detected!")
    else:
        print("Magnetic field lost!")

# Add event detection for the Hall effect sensor
GPIO.add_event_detect(HALL_SENSOR_PIN, GPIO.BOTH, callback=hall_effect_callback, bouncetime=200)

try:
    print("Monitoring Hall effect sensor. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
