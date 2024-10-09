import pigpio
import time

# GPIO pin number
HALL_SENSOR_PIN = 5

# Callback function to handle state changes
def hall_effect_callback(gpio, level, tick):
    if level == pigpio.HIGH:
        print("Magnetic field detected!")  # Triggered when the magnetic field is detected
    else:
        print("Magnetic field lost!")  # Triggered when the magnetic field is no longer detected

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    exit()

# Set up GPIO pin for input
pi.set_mode(HALL_SENSOR_PIN, pigpio.INPUT)
pi.set_pull_up_down(HALL_SENSOR_PIN, pigpio.PUD_DOWN)  # Set pull-down resistor

# Register the callback for rising and falling edges
pi.callback(HALL_SENSOR_PIN, pigpio.EITHER_EDGE, hall_effect_callback)

try:
    print("Monitoring Hall effect sensor using interrupts. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the program running

except KeyboardInterrupt:
    print("Exiting...")
finally:
    pi.stop()  # Clean up pigpio
