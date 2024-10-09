import logging
import sys
import os
import pigpio
import time
import datetime
import csv
import json
import github
import signal
import threading
from datetime import datetime


# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

def log_error(message):
    logging.error(message)

import os

# Set the current working directory
os.chdir('/home/lakelab/Documents/rat_counter_v3')

# Verify the current working directory
print("Current working directory:", os.getcwd())

# Add the virtual environment's site-packages to the PYTHONPATH


# Set up GPIO
# Sensors 1-4 will be connected to GPIO 05, 06, 13, 19

def read_preferences():
    file_path = 'preferences.json'
    try:
        with open(file_path, 'r') as file:
            preferences = json.load(file)
            return preferences
    except FileNotFoundError:
        log_error(f"Preferences file {file_path} not found.")
        return {}
    except json.JSONDecodeError:
        log_error(f"Error decoding JSON from {file_path}.")
        return {}

preferences = read_preferences()

sensor_names = preferences.get('sensor_names', {
    "D3": "Sensor 1",
    "D4": "Sensor 2",
    "D5": "Sensor 3",
    "D6": "Sensor 4",
    "D7": "Sensor 5",
    "D8": "Sensor 6",
    "D9": "Sensor 7",
    "D41": "Sensor 8"
})
print("Sensor names:", sensor_names)

from secrets import secrets
github_repo = secrets['github_repo']

# Replace with your GitHub username and personal access token (PAT)
github_username = secrets['github_username']
github_token = secrets['github_token']

# Initialize variables by reading the hall_effect_sensor_i.txt files
def initialize_hall_sensor_counter(filename):
    try:
        with open(f"{filename}", "r") as f:
            lines = f.readlines()
            max_count = 0
            for line in lines:
                parts = line.split(",")
                if len(parts) > 1 and "Count" in parts[1]:
                    count = int(parts[1].split(":")[1].strip())
                    if count > max_count:
                        max_count = count
            print(f"Initialized {filename} with count: {max_count}")
            return max_count
    except FileNotFoundError:
        log_error(f"File {filename} not found.")
        return 0

# Initialize counters
hall_effect_sensor_1_count = initialize_hall_sensor_counter("hall_effect_sensor_1.txt")
hall_effect_sensor_2_count = initialize_hall_sensor_counter("hall_effect_sensor_2.txt")
hall_effect_sensor_3_count = initialize_hall_sensor_counter("hall_effect_sensor_3.txt")
hall_effect_sensor_4_count = initialize_hall_sensor_counter("hall_effect_sensor_4.txt")

# Define the GPIO pins for the hall sensors
hall_sensor_pins = [5, 6, 13, 19]

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    log_error("Failed to connect to pigpio.")
    exit()

# Set up GPIO pins for input
for pin in hall_sensor_pins:
    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_DOWN)  # Set pull-down resistor

def write_to_file(filename, message):
    try:
        with open(f"{filename}", "a") as f:
            f.write(message + "\n")
    except Exception as e:
        log_error(f"Error writing to {filename}: {e}")

def update_github_file(filename, message):
    write_to_file(filename, message)
    try:
        g = github.Github(github_token)
        repo = g.get_repo(github_repo)
        contents = repo.get_contents(filename)
        repo.update_file(contents.path, f"Updated {filename}", message, contents.sha)
        print(f"Updated GitHub file {filename}")
    except Exception as e:
        log_error(f"Error updating GitHub file {filename}: {e}")

# Define the mapping from GPIO pins to sensor numbers
gpio_to_sensor_number = {
    5: 1,
    6: 2,
    13: 3,
    19: 4
}

def sensor_callback(gpio, level, tick):
    try:
        if level == pigpio.LOW:  # Sensor detected
            timestamp = time.time()
            date_str = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y')
            time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            sensor_number = gpio_to_sensor_number.get(gpio, "Unknown")
            sensor_name = sensor_names.get(f"D{gpio}", "Unknown Sensor")
            count_var_name = f"hall_effect_sensor_{sensor_number}_count"
            count = globals()[count_var_name] + 1
            globals()[count_var_name] = count
            message = f"Date: {date_str} Time: {time_str}, Count: {count}, Pin: D{gpio}, Sensor Name: {sensor_name}"
            print(message)
            write_to_file(f"hall_effect_sensor_{sensor_number}.txt", message)
            write_to_file(f"hall_effect_sensor_{sensor_number}_temp.txt", message)
    except Exception as e:
        log_error(f"Error in sensor callback for GPIO {gpio}: {e}")

# Register the callback for rising and falling edges
for pin in hall_sensor_pins:
    pi.callback(pin, pigpio.EITHER_EDGE, sensor_callback)

print("Sensors are set up. Waiting for events...")

# Initialize the last push time
last_push_time = time.monotonic()
time_between_pushes_minutes = preferences.get('time_between_pushes_minutes', 60)

def reload_preferences(signum, frame):
    global preferences, sensor_names, time_between_pushes_minutes
    try:
        preferences = read_preferences()
        sensor_names = preferences.get('sensor_names', {
            "D3": "Sensor 1",
            "D4": "Sensor 2",
            "D5": "Sensor 3",
            "D6": "Sensor 4",
            "D7": "Sensor 5",
            "D8": "Sensor 6",
            "D9": "Sensor 7",
            "D41": "Sensor 8"
        })
        time_between_pushes_minutes = preferences.get('time_between_pushes_minutes', 10)
        print("Preferences reloaded")
    except Exception as e:
        log_error(f"Error reloading preferences: {e}")

# Set up signal handler for SIGHUP
signal.signal(signal.SIGHUP, reload_preferences)

def health_check():
    try:
        health_status = {
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_status": {f"D{pin}": pi.read(pin) for pin in hall_sensor_pins},
            "last_push_time": last_push_time,
            "time_between_pushes_minutes": time_between_pushes_minutes
        }
        with open("health_check.log", "a") as f:
            f.write(json.dumps(health_status) + "\n")
        print("Health check completed")
    except Exception as e:
        log_error(f"Error during health check: {e}")

def schedule_health_check(interval):
    while True:
        health_check()
        time.sleep(interval)

# Start the health check thread
health_check_interval = preferences.get('health_check_interval', 600)  # Default to 10 minutes
health_check_thread = threading.Thread(target=schedule_health_check, args=(health_check_interval,))
health_check_thread.daemon = True
health_check_thread.start()

try:
    while True:
        current_time = time.monotonic()
        if current_time - last_push_time >= time_between_pushes_minutes * 60:
            last_push_time = current_time
            for i in range(1, 9):
                filename = f"hall_effect_sensor_{i}.txt"
                update_github_file(filename)
            time.sleep(60)  # Wait a minute to avoid multiple pushes within the same minute
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("Exiting...")
except Exception as e:
    log_error(f"Unexpected error: {e}")
finally:
    pi.stop()  # Clean up pigpio