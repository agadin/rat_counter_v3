import RPi.GPIO as GPIO
import time

# Configure GPIO
HALL_SENSOR_PIN = 17  # GPIO pin number

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin as input with pull-down resistor


# Callback function to handle Hall effect sensor state changes
def hall_effect_callback(channel):
    if GPIO.input(HALL_SENSOR_PIN):
        print("Magnetic field detected!")  # Triggered when the magnetic field is detected
    else:
        print("Magnetic field lost!")  # Triggered when the magnetic field is no longer detected


# Add event detection for the Hall effect sensor
try:
    GPIO.add_event_detect(HALL_SENSOR_PIN, GPIO.BOTH, callback=hall_effect_callback, bouncetime=200)
    print("Monitoring Hall effect sensor. Press Ctrl+C to exit.")

    # Keep the script running to listen for events
    while True:
        time.sleep(1)  # Wait indefinitely

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
