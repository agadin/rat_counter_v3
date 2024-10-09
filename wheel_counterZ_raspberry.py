import sys
import os
from gpiozero import Button
from signal import pause
import time
import datetime
import csv
import json
import github
from datetime import datetime

# Add the virtual environment's site-packages to the PYTHONPATH
venv_path = "/home/lakelab/Documents/rat_counter_v3/myvenv/lib/python3.x/site-packages"
sys.path.append(venv_path)

# Set up GPIO
# Sensors 1-4 will be connected to GPIO 05, 06, 13, 19

sensor_names = {
    "D3": "Sensor 1",
    "D4": "Sensor 2",
    "D5": "Sensor 3",
    "D6": "Sensor 4",
    "D7": "Sensor 5",
    "D8": "Sensor 6",
    "D9": "Sensor 7",
    "D41": "Sensor 8"
}

# import secrets
from secrets import secrets
github_repo = secrets['github_repo']

# Replace with your GitHub username and personal access token (PAT)
github_username = secrets['github_username']
github_token = secrets['github_token']

# Initialize variables by reading the hall_effect_sensor_i.txt files
def initialize_hall_sensor_counter(filename):
    try:
        with open(f"/place1/{filename}", "r") as f:
            lines = f.readlines()
            max_count = 0
            for line in lines:
                parts = line.split(",")
                if len(parts) > 1 and "Count" in parts[1]:
                    count = int(parts[1].split(":")[1].strip())
                    if count > max_count:
                        max_count = count
            return max_count
    except FileNotFoundError:
        return 0

# Initialize counters
hall_effect_sensor_1_count = initialize_hall_sensor_counter("hall_effect_sensor_1.txt")
hall_effect_sensor_2_count = initialize_hall_sensor_counter("hall_effect_sensor_2.txt")
hall_effect_sensor_3_count = initialize_hall_sensor_counter("hall_effect_sensor_3.txt")
hall_effect_sensor_4_count = initialize_hall_sensor_counter("hall_effect_sensor_4.txt")

# Define the GPIO pins for the hall sensors
hall_sensor_pins = [5, 6, 13, 19]

# Set up GPIO pins using gpiozero Button
hall_sensors = [Button(pin) for pin in hall_sensor_pins]

def write_to_file(filename, message):
    with open(f"/place1/{filename}", "a") as f:
        f.write(message + "\n")

def update_github_file(filename, message):
    write_to_file(filename, message)
    g = github.Github(github_token)
    repo = g.get_repo(github_repo)
    contents = repo.get_contents(filename)
    repo.update_file(contents.path, f"Updated {filename}", message, contents.sha)

def sensor_callback(sensor_index):
    timestamp = time.time()
    stamp = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    sensor_name = sensor_names.get(f"D{sensor_index+3}", "Unknown Sensor")
    message = f"{stamp}, Sensor {sensor_index+1} ({sensor_name}) triggered"
    print(message)
    write_to_file(f"hall_effect_sensor_{sensor_index+1}.txt", message)
    write_to_file(f"hall_effect_sensor_{sensor_index+1}_temp.txt", message)

def main():
    for i, sensor in enumerate(hall_sensors):
        sensor.when_pressed = lambda i=i: sensor_callback(i)
        sensor.when_released = lambda i=i: sensor_callback(i)

    print("Sensors are set up. Waiting for events...")
    pause()

if __name__ == "__main__":
    main()