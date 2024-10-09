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





#Initialise a strips variable, provide the GPIO Data Pin
#utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)


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

import github
from secrets import secrets
github_repo = secrets['github_repo']

# Replace with your GitHub username and personal access token (PAT)
github_username = secrets['github_username']
github_token = secrets['github_token']

import json

def read_preferences():
    try:
        # Fetch the preferences.json from GitHub
        g = github.Github(github_token)
        repo = g.get_repo(github_repo)
        contents = repo.get_contents('preferences.json')
        preferences = json.loads(contents.decoded_content.decode())
        return preferences
    except github.GithubException as e:
        log_error(f"Error fetching preferences from GitHub: {e}")
        return {}
    except json.JSONDecodeError:
        log_error("Error decoding JSON from preferences.json.")
        return {}
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return {}

preferences = read_preferences()

sensor_names = preferences.get('sensor_names', {
    "1": "Sensor A",
    "2": "Sensor B",
    "3": "Sensor C",
    "4": "Sensor D",
    "5": "Sensor E",
    "6": "Sensor F",
    "7": "Sensor G",
    "8": "Sensor H"
})
time_between_pushes_minutes = preferences.get('time_between_pushes_minutes', 60)
print("Preferences:", preferences)



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


def update_github_file(filename):
    try:
        # Read the content of the file
        with open(filename, 'r') as file:
            file_content = file.read()

        # Initialize GitHub repository
        g = github.Github(github_token)
        repo = g.get_repo(github_repo)

        # Get the file contents from the repository
        contents = repo.get_contents(filename)
        # Update the file on GitHub
        #make the message count the coubnt time and name
        message = f"Count: {globals()[f'hall_effect_sensor_{i}_count']}, Date: {datetime.now().strftime('%m/%d/%Y')}, Time: {datetime.now().strftime('%H:%M:%S')}"

        #upload the txt file to github
        repo.update_file(contents.path, message, file_content, contents.sha, branch="main")

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

debounce_timers = {pin: None for pin in hall_sensor_pins}


# Define the mapping from sensor numbers to colors
sensor_colors = {
    1: (255, 0, 0),    # Red
    2: (255, 165, 0),  # Orange
    3: (255, 255, 0),  # Yellow
    4: (0, 255, 0)     # Green
}





from rpi_lcd import LCD
lcd = LCD()
# Function to update the LCD display
def update_lcd_display():
    try:
        # Read the current counts
        count1 = globals().get('hall_effect_sensor_1_count', 0)
        count2 = globals().get('hall_effect_sensor_2_count', 0)
        count3 = globals().get('hall_effect_sensor_3_count', 0)
        count4 = globals().get('hall_effect_sensor_4_count', 0)

        # Update the LCD display
        lcd.text(f"1:{count1} 2:{count2}", 1)
        lcd.text(f"3:{count3} 4:{count4}", 2)
    except Exception as e:
        log_error(f"Error updating LCD display: {e}")


# Call the update_lcd_display function whenever counts change
def sensor_callback(gpio, level, tick):
    def debounce():
        try:
            timestamp = time.time()
            date_str = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y')
            time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            sensor_number = gpio_to_sensor_number.get(gpio, "Unknown")
            sensor_name = sensor_names.get(f"{sensor_number}", "Unknown Sensor")
            count_var_name = f"hall_effect_sensor_{sensor_number}_count"
            count = globals()[count_var_name] + 1
            globals()[count_var_name] = count
            message = f"Date: {date_str} Time: {time_str}, Count: {count}, Pin: {gpio}, Sensor Name: {sensor_name}"
            print(message)
            write_to_file(f"hall_effect_sensor_{sensor_number}.txt", message)
            write_to_file(f"hall_effect_sensor_{sensor_number}_temp.txt", message)


            # Update the LCD display
            update_lcd_display()
        except Exception as e:
            log_error(f"Error in sensor callback for GPIO {gpio}: {e}")

    if level == pigpio.LOW:  # Sensor detected
        if debounce_timers[gpio] is not None:
            debounce_timers[gpio].cancel()
        debounce_timers[gpio] = threading.Timer(0.25, debounce)
        debounce_timers[gpio].start()

# Register the callback for rising and falling edges
for pin in hall_sensor_pins:
    pi.callback(pin, pigpio.EITHER_EDGE, sensor_callback)

print("Sensors are set up. Waiting for events...")

# Initialize the last push time
last_push_time = time.monotonic()
time_between_pushes_minutes = preferences.get('time_between_pushes_minutes', 60)
print(f"time_between_pushes_minutes: {time_between_pushes_minutes}")
def reload_preferences(signum, frame):
    global preferences, sensor_names, time_between_pushes_minutes
    try:
        preferences = read_preferences()
        sensor_names = preferences.get('sensor_names', {
            "1": "Sensor A",
            "2": "Sensor B",
            "3": "Sensor C",
            "4": "Sensor D",
            "5": "Sensor E",
            "6": "Sensor F",
            "7": "Sensor G",
            "8": "Sensor H"
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
            try:
                last_push_time = current_time
                for i in range(1, 5):
                   filename = f"hall_effect_sensor_{i}.txt"
                   #make commit message include count name date/time
                   message = f"Count: {globals()[f'hall_effect_sensor_{i}_count']}, Date: {datetime.now().strftime('%m/%d/%Y')}, Time: {datetime.now().strftime('%H:%M:%S')}"
                   print(f"Uploading {filename} to GitHub with message: {message}")
                   update_github_file(filename)
                time.sleep(60)  # Wait a minute to avoid multiple pushes within the same minute
            except Exception as e:
                log_error(f"Unexpected error uploading to github: {e}")
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("Exiting...")
except Exception as e:
    log_error(f"Unexpected error: {e}")
finally:
    pi.stop()  # Clean up pigpio