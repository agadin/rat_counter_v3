import RPi.GPIO as GPIO
import threading
import time

# Configure GPIO
HALL_SENSOR_PIN = 17  # GPIO pin number

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Callback function
def hall_effect_callback(channel):
    if GPIO.input(HALL_SENSOR_PIN):
        print("Magnetic field detected!")
    else:
        print("Magnetic field lost!")

# Thread function to monitor the Hall effect sensor
def monitor_sensor():
    GPIO.add_event_detect(HALL_SENSOR_PIN, GPIO.BOTH, callback=hall_effect_callback, bouncetime=200)
    while True:
        time.sleep(1)  # Keep the thread alive

# Start the monitoring in a separate thread
sensor_thread = threading.Thread(target=monitor_sensor)
sensor_thread.daemon = True  # Daemonize thread to exit when the main program exits
sensor_thread.start()

try:
    print("Monitoring Hall effect sensor in a separate thread. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the main program running

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
