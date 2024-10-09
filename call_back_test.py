import RPi.GPIO as GPIO
import time

# Configure GPIO
HALL_SENSOR_PIN = 17  # Change this to the correct GPIO pin

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set up the pin for input with a pull-down resistor
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Callback function
def hall_effect_callback(channel):
    if GPIO.input(HALL_SENSOR_PIN):
        print("Magnetic field detected!")
    else:
        print("Magnetic field lost!")

# Add event detection for the Hall effect sensor
try:
    GPIO.add_event_detect(HALL_SENSOR_PIN, GPIO.BOTH, callback=hall_effect_callback, bouncetime=200)
except RuntimeError as e:
    print(f"Failed to add edge detection: {e}")

# Main loop
try:
    print("Monitoring Hall effect sensor. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
