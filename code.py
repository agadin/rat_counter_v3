#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 16:20:17 2024

@author: alexandergadin
"""
import time
import board
import digitalio
import adafruit_sdcard
import storage
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi as esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_ds3231
import neopixel
import adafruit_requests
import adafruit_binascii
import socketpool
import wifi
import ssl
import os
from secrets import secrets
import json

from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface



try:
    import adafruit_motor.stepper as stepper
    from adafruit_motor import motor
except ImportError:
    stepper = None
    motor = None

# GitHub repository information
github_repo = secrets['github_repo']


# Replace with your GitHub username and personal access token (PAT)
github_username = secrets['github_username']
github_token = secrets['github_token']
# Setup RTC
i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Setup SD card

# check SD mount
if not 'sd' in os.listdir('/'):
    try:
        os.mkdir('/sd')
    except OSError as err:
        if err.errno == 30:
            print("/sd mount point folder does not exist, either create this folder")
            print("from the host computer or configure CIRCUITPY for read/write by")
            print("modifying the boot.py file, inserting the following:")
            print('\nimport storage\nstorage.remount("/",False)')
        else:
            print(str(err))

spi = board.SPI()
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Setup Hall sensors
# Hall 1
hall_sensor_1_pin = digitalio.DigitalInOut(board.D3)  # Change to your Hall sensor pin
hall_sensor_1_pin.direction = digitalio.Direction.INPUT
hall_sensor_1_pin.pull = digitalio.Pull.UP

# Hall 2
hall_sensor_2_pin = digitalio.DigitalInOut(board.D4)  # Change to your second Hall
hall_sensor_2_pin.direction = digitalio.Direction.INPUT
hall_sensor_2_pin.pull = digitalio.Pull.UP

# Hall 3
hall_sensor_3_pin = digitalio.DigitalInOut(board.D5)  # Change to your second Hall
hall_sensor_3_pin.direction = digitalio.Direction.INPUT
hall_sensor_3_pin.pull = digitalio.Pull.UP

# Hall 4
hall_sensor_4_pin = digitalio.DigitalInOut(board.D6)  # Change to your Hall
hall_sensor_4_pin.direction = digitalio.Direction.INPUT
hall_sensor_4_pin.pull = digitalio.Pull.UP

# Hall 5
hall_sensor_5_pin = digitalio.DigitalInOut(board.D7)  # Change to your second Hall
hall_sensor_5_pin.direction = digitalio.Direction.INPUT
hall_sensor_5_pin.pull = digitalio.Pull.UP

# Hall 6
hall_sensor_6_pin = digitalio.DigitalInOut(board.D8)  # Change to your second Hall
hall_sensor_6_pin.direction = digitalio.Direction.INPUT
hall_sensor_6_pin.pull = digitalio.Pull.UP

# Hall 7
hall_sensor_7_pin = digitalio.DigitalInOut(board.D9)  # Change to your second Hall
hall_sensor_7_pin.direction = digitalio.Direction.INPUT
hall_sensor_7_pin.pull = digitalio.Pull.UP

# Hall 8
hall_sensor_8_pin = digitalio.DigitalInOut(board.D41)  # Change to your second Hall
hall_sensor_8_pin.direction = digitalio.Direction.INPUT
hall_sensor_8_pin.pull = digitalio.Pull.UP

# Setup NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True, pixel_order=neopixel.GRB)

# Create a session for making requests

pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

def get_rtc_time():
    RTC = rtc.datetime
    return "Date: {}/{}/{} Time: {:02}:{:02}:{:02}".format(
        RTC.tm_mon, RTC.tm_mday, RTC.tm_year, RTC.tm_hour, RTC.tm_min, RTC.tm_sec
    )


def write_to_file(filename, message):
    with open(f"/sd/{filename}", "a") as f:
        f.write(message + "\n")

# load settings file
def update_preferences():
    global time_between_pushes_minutes, sensor_names, lcd_enabled, lcd

    try:
        # Fetch preferences.json from GitHub
        response = requests.get(f"https://raw.githubusercontent.com/{github_repo}/main/preferences.json")
        print("Response:", response.status_code)
        print("Response Content:", response.text)
        if response.status_code == 200:
            preferences = json.loads(response.text)
            # Save preferences.json to SD card for future use
            with open("/sd/preferences.json", "w") as pref_file:
                pref_file.write(response.text)
                print('Settings Updated')
        else:
            print(f"Failed to fetch preferences.json: {response.status_code}")
    except Exception as e:
        print(f"Error updating preferences: {e}")

    try:
        with open("/sd/preferences.json", "r") as pref_file:
            preferences = json.load(pref_file)
            time_between_pushes_minutes = preferences.get("time_between_pushes_minutes", 60)
            sensor_names = preferences.get("sensor_names", {})
            lcd_enabled = preferences.get("character_lcd", False)  # Corrected from false to False
    except FileNotFoundError:
        # If preferences.json doesn't exist on SD card, initialize with defaults
        print('No File Found')
        time_between_pushes_minutes = 60
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
        lcd_enabled= false
    if lcd_enabled:
        try:
            print("initialising i2c and looking for address")
            i2c.try_lock()
            address = i2c.scan()[0]
            print(f"found address of i2c '{address}'")
            i2c.unlock()
            lcd = LCD(I2CPCF8574Interface(i2c, address), num_rows=2, num_cols=16)
            print("debug: lcd initialised")
        except Exception as e:
            print("Error initializing LCD:", e)

update_preferences()# Load preferences from SD card if available


def push_to_github(filename):
    global requests
    # Read file content
    with open(f"/sd/{filename}", "r") as f:
        content = f.read()
    #start
    github_file_path = filename
    github_api_url = f"https://api.github.com/repos/{secrets['github_repo']}/contents/{github_file_path}"
    file_content_base64=adafruit_binascii.b2a_base64(content.encode("utf-8"))[:-1].decode("utf-8")
    # HTTP headers for GitHub API request
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Body of the request (in JSON format)
    data = {
        "message": "my commit message",
        "committer": {
            "name": "again",
            "email": "a.gadin@wustl.edu"
        },
        "content": file_content_base64,
    }
    # HTTP headers for GitHub API requests
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    # Step 1: Get the current SHA of the file
    try:
        response = requests.get(github_api_url, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            current_sha = file_info["sha"]
        else:
            print("Error getting file info:", response.status_code, response.text)
            raise SystemExit
    except Exception as e:
        print("Error retrieving file SHA:", e)
        raise SystemExit

    # Step 2: Upload the new content with the SHA of the existing file
    data = {
        "message": "my commit message",
        "committer": {
            "name": secrets['committer_name'],
            "email": secrets['committer_email']
        },
        "content": file_content_base64,
        "sha": current_sha
    }

    try:
        response = requests.put(github_api_url, headers=headers, json=data)
        print("Response:", response.status_code)
        print("Response Content:", response.text)
    except Exception as e:
        print("Error uploading file to GitHub:", e)
def flash_led(color):
    # Flash the NeoPixel LED
    pixel[0] = color  # Set to given color
    time.sleep(0.5)
    pixel[0] = (0, 0, 0)  # Turn off
    time.sleep(0.5)

def set_rtc_from_ntp():
    # Connect to Wi-Fi
    global requests

    # Get current time from NTP server
    response = requests.get("http://worldtimeapi.org/api/timezone/America/Chicago")
    if response.status_code == 200:
        data = response.json()
        datetime_str = data["datetime"][:19]  # Get the datetime string in the format "YYYY-MM-DDTHH:MM:SS"

        # Manually parse the date and time from the string
        year = int(datetime_str[0:4])
        month = int(datetime_str[5:7])
        day = int(datetime_str[8:10])
        hour = int(datetime_str[11:13])
        minute = int(datetime_str[14:16])
        second = int(datetime_str[17:19])

        # Create a struct_time object
        utc_time = time.struct_time((year, month, day, hour, minute, second, 0, 0, -1))

        # Update RTC
        rtc.datetime = utc_time
        print("RTC time updated from NTP")
        print(utc_time)
    else:
        print("Failed to get time from NTP server")


def initialize_hall_sensor_counter(filename):
    try:
        with open(f"/sd/{filename}", "r") as f:
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


last_push_time = time.monotonic()

# Update RTC from NTP at startup
set_rtc_from_ntp()

# Initialize hall sensor counters
hall_sensor_1_counter = initialize_hall_sensor_counter("hall_effect_sensor_1.txt")
print(f"Hall sensor 1 counter initialized to {hall_sensor_1_counter}")

hall_sensor_2_counter = initialize_hall_sensor_counter("hall_effect_sensor_2.txt")
print(f"Hall sensor 2 counter initialized to {hall_sensor_2_counter}")

hall_sensor_3_counter = initialize_hall_sensor_counter("hall_effect_sensor_3.txt")
print(f"Hall sensor 3 counter initialized to {hall_sensor_3_counter}")

hall_sensor_4_counter = initialize_hall_sensor_counter("hall_effect_sensor_4.txt")
print(f"Hall sensor 4 counter initialized to {hall_sensor_4_counter}")

hall_sensor_5_counter = initialize_hall_sensor_counter("hall_effect_sensor_5.txt")
print(f"Hall sensor 5 counter initialized to {hall_sensor_5_counter}")

hall_sensor_6_counter = initialize_hall_sensor_counter("hall_effect_sensor_6.txt")
print(f"Hall sensor 6 counter initialized to {hall_sensor_6_counter}")

hall_sensor_7_counter = initialize_hall_sensor_counter("hall_effect_sensor_7.txt")
print(f"Hall sensor 7 counter initialized to {hall_sensor_7_counter}")

hall_sensor_8_counter = initialize_hall_sensor_counter("hall_effect_sensor_8.txt")
print(f"Hall sensor 8 counter initialized to {hall_sensor_8_counter}")

cycle_counter=0
previous_hall_counts = {}
hall_1 = True
hall_2 = True
hall_3 = True
hall_4 = True
hall_5 = True
hall_6 = True
hall_7 = True
hall_8 = True
while True:
    try:
        if not hall_sensor_1_pin.value:
            hall_sensor_1_counter += 1
            sensor_name = sensor_names.get("D3", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_1_counter}, Pin: D3, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_1.txt", message)
            write_to_file("hall_effect_sensor_1_temp.txt", message)
            flash_led((150, 0, 0))  # Red for sensor 1
            print(message)  # Debug print
            hall_1 = False

        if not hall_sensor_2_pin.value:
            hall_sensor_2_counter += 1
            sensor_name = sensor_names.get("D4", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_2_counter}, Pin: D4, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_2.txt", message)
            write_to_file("hall_effect_sensor_2_temp.txt", message)
            flash_led((255, 165, 0))  # Green for sensor 2
            print(message)  # Debug print
            hall_2 = False

        if not hall_sensor_3_pin.value:
            hall_sensor_3_counter += 1
            sensor_name = sensor_names.get("D5", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_3_counter}, Pin: D5, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_3.txt", message)
            write_to_file("hall_effect_sensor_3_temp.txt", message)
            flash_led((255, 255, 0))  # Yellow for sensor 3
            print(message)  # Debug print
            hall_3 = False

        if not hall_sensor_4_pin.value:
            hall_sensor_4_counter += 1
            sensor_name = sensor_names.get("D6", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_4_counter}, Pin: D6, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_4.txt", message)
            write_to_file("hall_effect_sensor_4_temp.txt", message)
            flash_led((0, 255, 0))  # Green for sensor 4
            print(message)  # Debug print
            hall_4 = False

        if not hall_sensor_5_pin.value:
            hall_sensor_5_counter += 1
            sensor_name = sensor_names.get("D7", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_5_counter}, Pin: D7, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_5.txt", message)
            write_to_file("hall_effect_sensor_5_temp.txt", message)
            flash_led((0, 255, 255))  # Cyan for sensor 5
            print(message)  # Debug print
            hall_5 = False

        if not hall_sensor_6_pin.value:
            hall_sensor_6_counter += 1
            sensor_name = sensor_names.get("D8", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_6_counter}, Pin: D8, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_6.txt", message)
            write_to_file("hall_effect_sensor_6_temp.txt", message)
            flash_led((0, 0, 255))  # Blue for sensor 6
            print(message)  # Debug print
            hall_6= False

        if not hall_sensor_7_pin.value:
            hall_sensor_7_counter += 1
            sensor_name = sensor_names.get("D9", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_7_counter}, Pin: D9, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_7.txt", message)
            write_to_file("hall_effect_sensor_7_temp.txt", message)
            flash_led((255, 0, 255))  # Magenta for sensor 7
            print(message)  # Debug print
            hall_7= False

        if not hall_sensor_8_pin.value:
            hall_sensor_8_counter += 1
            sensor_name = sensor_names.get("D41", "Unknown Sensor")
            message = f"{get_rtc_time()}, Count: {hall_sensor_8_counter}, Pin: D41, Sensor Name: {sensor_name}"
            write_to_file("hall_effect_sensor_8.txt", message)
            write_to_file("hall_effect_sensor_8_temp.txt", message)
            flash_led((128, 0, 128))  # Purple for sensor 8
            print(message)  # Debug print
            hall_8 = False
        if lcd_enabled:
            hall_counts = {
                "A": hall_sensor_1_counter,
                "B": hall_sensor_2_counter,
                "C": hall_sensor_3_counter,
                "D": hall_sensor_4_counter,
                "E": hall_sensor_5_counter,
                "F": hall_sensor_6_counter,
                "G": hall_sensor_7_counter,
                "H": hall_sensor_8_counter,
            }

            # Update display only every 50 cycles or if hall_counts changed
            if hall_counts != previous_hall_counts and all(count < 10 for count in hall_counts.values()):
                previous_hall_counts = hall_counts.copy()
                message = ""
                for label, count in hall_counts.items():
                    message += f"{label}:{count} "
                lcd.clear()
                lcd.print(message)
            elif cycle_counter % 50 == 0 or hall_counts != previous_hall_counts:
                previous_hall_counts = hall_counts.copy()
                # Split hall_counts into two halves
                items = list(hall_counts.items())
                first_half = items[:len(items)//2]
                second_half = items[len(items)//2:]
                # Alternate display every 50 cycles
                if (cycle_counter // 50) % 2 == 0:
                    message = ""
                    for label, count in first_half:
                        message += f"{label}:{count} "
                    lcd.clear()
                    lcd.print(message)
                else:
                    message = ""
                    for label, count in second_half:
                        message += f"{label}:{count} "
                    lcd.clear()
                    lcd.print(message)

        # Check if it's time to push the files to GitHub
        current_time = time.monotonic()
        if current_time - last_push_time >= time_between_pushes_minutes * 60:
            for i in range(1, 9):
                filename = f"hall_effect_sensor_{i}_temp.txt"
                push_to_github(filename)
                try:
                    with open(f"/sd/{filename}", "w") as f:
                        pass  # Opening the file in 'w' mode clears its contents
                    print(f"{filename} has been cleared.")
                except Exception as e:
                    print(f"Error clearing {filename}: {e}")
            update_preferences()
            last_push_time = current_time
        cycle_counter += 1

        #pin off
        if hall_sensor_1_pin.value:
            hall_1 = True
        if hall_sensor_2_pin.value:
            hall_2 = True
        if hall_sensor_3_pin.value:
            hall_3 = True
        if hall_sensor_4_pin.value:
            hall_4 = True
        if hall_sensor_5_pin.value:
            hall_5 = True
        if hall_sensor_6_pin.value:
            hall_6 = True
        if hall_sensor_7_pin.value:
            hall_7 = True
        if hall_sensor_8_pin.value:
            hall_8 = True

    except Exception as e:
        print("An error occurred: ", e)

    time.sleep(0.05)  # Check sensors every second
