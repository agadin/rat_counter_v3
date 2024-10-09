import streamlit as st
import json
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


#wide
st.set_page_config(page_title="Local Lake Viewer", page_icon="🧊", layout="wide")

#hide top color bar
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)




    
# Function to connect to GitHub and retrieve files
def get_github_files(repo_name, access_key, file_names):
    try:
        g = Github(access_key)
        repo = g.get_repo(repo_name)
        files = {}
        for file_name in file_names:
            try:
                file_content = repo.get_contents(file_name).decoded_content.decode()
                if not file_content.strip():  # Check if the file is empty
                    file_content = (
                        "Date: 10/8/2024 Time: 00:00:33, Count: 0, Pin: D3, Sensor Name: Sensor 1\n"
                        "Date: 10/8/2024 Time: 00:01:33, Count: 0, Pin: D3, Sensor Name: Sensor 1"
                    )
                files[file_name] = file_content
                print(f"Successfully retrieved {file_name}")
            except Exception as e:
                print(f"Error retrieving {file_name}: {e}")

        # Retrieve preferences.json
        preferences_file = 'preferences.json'
        try:
            preferences_content = repo.get_contents(preferences_file).decoded_content.decode()
            preferences = json.loads(preferences_content)
            files[preferences_file] = preferences
            print(f"Successfully retrieved {preferences_file}")
        except Exception as e:
            print(f"Error retrieving {preferences_file}: {e}")

        return files
    except Exception as e:
        print(f"Error connecting to GitHub: {e}")
        return {}

# Function to update preferences.json on GitHub
def update_github_file(repo_name, access_key, file_name, new_content):
    g = Github(access_key)
    repo = g.get_repo(repo_name)
    contents = repo.get_contents(file_name)
    repo.update_file(contents.path, "Update preferences.json", new_content, contents.sha)

# Function to retrieve README from GitHub
def get_github_readme(repo_name, access_key):
    try:
        g = Github(access_key)
        repo = g.get_repo(repo_name)
        readme_content = repo.get_readme().decoded_content.decode()
        return readme_content
    except Exception as e:
        print(f"Error retrieving README: {e}")
        return "Error retrieving README."
    
import plotly.graph_objects as go
import datetime

# Function to parse date and time from your data format
import datetime

import datetime

import datetime


def parse_sensor_data_from_raw(content):
    data = []
    # Split the content into individual lines
    lines = content.strip().split("\n")

    for line in lines:
        # Parse the line
        date_part = line.split("Date: ")[1].split(" Time:")[0].strip()
        time_part = line.split("Time: ")[1].split(",")[0].strip()
        count_part = int(line.split("Count: ")[1].split(",")[0].strip())
        sensor_name_part = line.split("Sensor Name: ")[1].strip()

        # Convert date and time to the desired format
        timestamp = datetime.datetime.strptime(f"{date_part} {time_part}", "%m/%d/%Y %H:%M:%S")
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Store the parsed information
        data.append((formatted_timestamp, count_part, sensor_name_part))

    return data


def clip_to_last_24_hours(filtered_data):
    if not filtered_data:
        return []

    # Find the most recent timestamp
    most_recent_time = datetime.datetime.strptime(filtered_data[-1][0], "%Y-%m-%d %H:%M:%S")

    # Calculate the cutoff time (24 hours before the most recent time)
    cutoff_time = most_recent_time - datetime.timedelta(hours=24)

    # Filter data to include only entries within the last 24 hours
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") >= cutoff_time]

    return clipped_data

# Function to find the first value at the start of the 24-hour period


def clip_to_last_1_hour(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Calculate the cutoff time (1 hour before the most recent time)
    cutoff_time = most_recent_time - datetime.timedelta(hours=1)
    
    # Filter data to include only entries within the last 1 hour
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") >= cutoff_time]
    
    return clipped_data


def clip_to_previous_24_hours(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Calculate the cutoff times
    end_time = datetime.datetime.strptime(most_recent_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=24)
    start_time = end_time - datetime.timedelta(hours=24)
    
    # Filter data to include only entries within the 24-hour period before the last 24 hours
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if start_time <= datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") < end_time]
    return clipped_data

# Function to clip data to the most recent 7am to 7am period
import datetime

def clip_to_7am_period(filtered_data):
    if not filtered_data:
        return []

    # Find the most recent timestamp and convert it to a datetime object
    most_recent_time = datetime.datetime.strptime(filtered_data[-1][0], "%Y-%m-%d %H:%M:%S")

    # Find the most recent 7am before the most recent timestamp
    most_recent_7am = most_recent_time.replace(hour=7, minute=0, second=0, microsecond=0)
    if most_recent_time.hour < 7:
        most_recent_7am -= datetime.timedelta(days=1)

    # Calculate the cutoff times for the last 7am to 7am period
    cutoff_time_start = most_recent_7am - datetime.timedelta(days=1)
    cutoff_time_end = most_recent_7am

    # Filter data to include only entries within the last 7am to 7am period
    clipped_data = [
        (ts, count, sensor_name)
        for (ts, count, sensor_name) in filtered_data
        if cutoff_time_start <= datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") < cutoff_time_end
    ]
    return clipped_data, cutoff_time_start, cutoff_time_end

# Function to clip data to the 7am to 7am period before the most recent one
import datetime

def clip_to_previous_7am_period(filtered_data):
    if not filtered_data:
        return []

    # Find the most recent timestamp and convert it to a datetime object
    most_recent_time = datetime.datetime.strptime(filtered_data[-1][0], "%Y-%m-%d %H:%M:%S")

    # Find the most recent 7am before the most recent timestamp
    most_recent_7am = most_recent_time.replace(hour=7, minute=0, second=0, microsecond=0)
    if most_recent_time.hour < 7:
        most_recent_7am -= datetime.timedelta(days=1)

    # Calculate the cutoff times for the previous 7am to 7am period
    cutoff_time_start = most_recent_7am - datetime.timedelta(days=2)
    cutoff_time_end = most_recent_7am - datetime.timedelta(days=1)

    # Filter data to include only entries within the previous 7am to 7am period
    clipped_data = [
        (ts, count, sensor_name)
        for (ts, count, sensor_name) in filtered_data
        if cutoff_time_start <= datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") < cutoff_time_end
    ]

    return clipped_data, cutoff_time_start, cutoff_time_end

# Function to calculate counts per 7am to 7am period
def calculate_counts_per_7am_period(filtered_data):
    if not filtered_data:
        return []
    
    counts_per_period = {}
    current_date = filtered_data[0][0].date()
    start_time = datetime.time(7, 0, 0)
    end_time = datetime.time(7, 0, 0)

    current_period_start = datetime.datetime.combine(current_date, start_time)
    current_period_end = datetime.datetime.combine(current_date, end_time)

    total_count = 0
    for timestamp, count, sensor_name in filtered_data:
        if timestamp >= current_period_start and timestamp < current_period_end:
            total_count = count
        elif timestamp >= current_period_end:
            counts_per_period[current_period_start.strftime('%Y-%m-%d %H:%M:%S')] = total_count
            # Move to the next 7am to 7am period
            current_date = timestamp.date()
            current_period_start = datetime.datetime.combine(current_date, start_time)
            current_period_end = datetime.datetime.combine(current_date + datetime.timedelta(days=1), end_time)
            total_count = count
    
    # Add the last period
    counts_per_period[current_period_start.strftime('%Y-%m-%d %H:%M:%S')] = total_count
    
    return counts_per_period

import numpy as np

def calculate_7am_to_7am_ranges(filtered_data):
    if not filtered_data:
        return pd.DataFrame()
    
    # Create a DataFrame from filtered_data
    df = pd.DataFrame(filtered_data, columns=['timestamp', 'count', 'sensor_name'])
    
    # Extract date and time components
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Group by date and calculate start/end timestamps for each 7am to 7am period
    df['7am_period'] = np.where(df['hour'] >= 7, df['date'], df['date'] - pd.Timedelta(days=1))
    df['7am_period_start'] = pd.to_datetime(df['7am_period']) + pd.Timedelta(hours=7)
    df['7am_period_end'] = df['7am_period_start'] + pd.Timedelta(hours=24)
    
    # Group by 7am periods and calculate range of counts
    ranges = df.groupby(['7am_period', 'sensor_name']).agg({
        'count': lambda x: x.max() - x.min()
    }).reset_index()
    
    # Pivot table to have sensors as columns and 7am periods as rows
    pivot_table = pd.pivot_table(ranges, values='count', index='7am_period', columns='sensor_name')
    
    return pivot_table



import pytz

# Function to record timestamp in local time
def record_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to retrieve the last commit date for a file and convert it to Central Time
def get_last_commit_date(repo_name, access_key, file_name):
    try:
        g = Github(access_key)
        repo = g.get_repo(repo_name)
        commits = repo.get_commits(path=file_name)
        if commits:
            last_commit_date = commits[0].commit.committer.date
            last_commit_date = last_commit_date.replace(tzinfo=pytz.utc)  # Ensure datetime is aware of UTC timezone
            central = pytz.timezone('US/Central')
            last_commit_date_central = last_commit_date.astimezone(central)
            return last_commit_date_central
        else:
            return None
    except Exception as e:
        print(f"Error retrieving last commit date for {file_name}: {e}")
        return None

import zipfile
from io import BytesIO

import re

def extract_sensor_names(files):
    sensor_names = {}
    sensor_name_pattern = re.compile(r"Sensor Name: ([\w\s]+)")

    for file_name, file_content in files.items():
        if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
            lines = file_content.splitlines()
            for line in lines:
                match = sensor_name_pattern.search(line)
                if match:
                    sensor_name = match.group(1)
                    sensor_names[file_name] = sensor_name
                    break  # Assuming the sensor name is the same throughout the file

    return sensor_names
# Function to convert .txt files to BytesIO for zip archive
def files_to_bytesio(files):
    zip_data = BytesIO()
    with zipfile.ZipFile(zip_data, mode='w') as z:
        for file_name, content in files.items():
            if file_name.endswith('.txt'):
                z.writestr(file_name, content.encode('utf-8'))  # Encode as bytes if content is a string
    return zip_data.getvalue()

import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import os

#wide
st.set_page_config(page_title="Lake Viewer", page_icon="🧊", layout="wide")

#hide top color bar
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# Function to read local files
def get_local_files(file_names):
    files = {}
    for file_name in file_names:
        try:
            with open(file_name, 'r') as file:
                file_content = file.read()
                if not file_content.strip():  # Check if the file is empty
                    file_content = (
                        "Date: 10/8/2024 Time: 00:00:33, Count: 0, Pin: D3, Sensor Name: Sensor 1\n"
                        "Date: 10/8/2024 Time: 00:01:33, Count: 0, Pin: D3, Sensor Name: Sensor 1"
                    )
                files[file_name] = file_content
                print(f"Successfully read {file_name}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    # Read preferences.json
    preferences_file = 'preferences.json'
    try:
        with open(preferences_file, 'r') as file:
            preferences_content = file.read()
            preferences = json.loads(preferences_content)
            files[preferences_file] = preferences
            print(f"Successfully read {preferences_file}")
    except Exception as e:
        print(f"Error reading {preferences_file}: {e}")

    return files

# Function to parse date and time from your data format
def parse_sensor_data_from_raw(content):
    data = []
    # Split the content into individual lines
    lines = content.strip().split("\n")

    for line in lines:
        # Parse the line
        date_part = line.split("Date: ")[1].split(" Time:")[0].strip()
        time_part = line.split("Time: ")[1].split(",")[0].strip()
        count_part = int(line.split("Count: ")[1].split(",")[0].strip())
        sensor_name_part = line.split("Sensor Name: ")[1].strip()

        # Convert date and time to the desired format
        timestamp = datetime.strptime(f"{date_part} {time_part}", "%m/%d/%Y %H:%M:%S")
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Store the parsed information
        data.append((formatted_timestamp, count_part, sensor_name_part))

    return data

# Main function for Streamlit app
def main():
    selected2 = option_menu(None, ["Settings", "Home", "Wiki"],
                           icons=['gear', 'house', 'wikipedia'],
                           menu_icon="cast", default_index=0, orientation="horizontal")

    if selected2 == "Settings":
        st.header("Settings")

        # Local settings
        st.subheader("Local Settings")
        st.write("Using local .txt files for data.")

        # Counter settings
        st.subheader("Counter Settings")
        is_from_device = True
        try:
            with open('preferences.json') as f:
                preferences = json.load(f)
        except FileNotFoundError:
            st.warning("preferences.json not found. Using default settings.")
            preferences = {
                "time_between_pushes_minutes": 60,
                "sensor_names": {
                    "D3": "Sensor 1",
                    "D4": "Sensor 2",
                    "D5": "Sensor 3",
                    "D6": "Sensor 4",
                    "D7": "Sensor 5",
                    "D8": "Sensor 6",
                    "D9": "Sensor 7",
                    "D41": "Sensor 8"
                },
                "character_lcd": True,
                "uln2003_stepper": False
            }

        # Display settings and indicate if they are from device or GitHub
        st.write("Local Counter Settings (From Device)")

        time_between_pushes = st.number_input("Time Between Pushes (minutes)", value=preferences['time_between_pushes_minutes'])
        sensor_names = preferences['sensor_names']
        for pin, name in sensor_names.items():
            sensor_names[pin] = st.text_input(f"Sensor Name for {pin}", value=name)
        character_lcd = st.checkbox("Character LCD", value=preferences['character_lcd'])
        uln2003_stepper = st.checkbox("ULN2003 Stepper", value=preferences['uln2003_stepper'])
        update_button = st.button("Update Counter Settings")

        if update_button:
            preferences = {
                "time_between_pushes_minutes": time_between_pushes,
                "sensor_names": sensor_names,
                "character_lcd": character_lcd,
                "uln2003_stepper": uln2003_stepper
            }
            with open('preferences.json', 'w') as f:
                json.dump(preferences, f, indent=4)

            st.write("Counter settings updated.")

        # Display last updated time for preferences.json
        if "last_update_time" in st.session_state:
            st.write(f"Last Updated: {st.session_state.last_update_time}")

        # Restore settings
        st.subheader("Restore")
        download_settings = st.download_button("Download Settings File", data=json.dumps(preferences), file_name="settings.json")
        restore_settings = st.file_uploader("Upload Settings File", type="json")

        if restore_settings:
            new_preferences = json.load(restore_settings)
            with open('preferences.json', 'w') as f:
                json.dump(new_preferences, f, indent=4)

            st.write("Settings restored.")

    elif selected2 == "Home":
        # Ensure files have been retrieved or uploaded
        file_names = [f"hall_effect_sensor_{i}.txt" for i in range(1, 9)]
        files = get_local_files(file_names)

        if not files:
            st.error("No files found. Please ensure the .txt files are available locally.")
            return
        
        files = st.session_state.files
        
        
        # Dropdown for selecting time frame        
        
        
        #Second section Metric Setting 
        metric_timeframe = st.selectbox("Select Metric Time Frame", ['Last 24 Hours Available', 'Last 7am to 7am Period'], help='Indicate the tim range for metrics. Note the secondary numbers are change from previous time point.')
        
        if metric_timeframe == 'Last 24 Hours Available':
            # Initialize variables to store total counts
            total_counts_24 = {}
            total_counts_24_prev = {}
            sensor_names_24_out = {}
            
            for i, (file_name, file_content) in enumerate(files.items(), start=1):
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = parse_sensor_data_from_raw(file_content)
                    if filtered_data:
                        # Clip data to the last 24 hours
                        filtered_data_24 = clip_to_last_24_hours(filtered_data)

                        if filtered_data_24:
                            first_count_24 = filtered_data_24[0][1]
                            timestamps_24 = [entry[0] for entry in filtered_data_24]
                            counts_24 = [entry[1] - first_count_24 for entry in filtered_data_24]
                            sensor_names_24 = [entry[2] for entry in filtered_data_24]
                            total_counts_24[f'total_counts_24_hall_{i}'] = max(counts_24)

                            # Convert the first timestamp to a datetime object before calling strftime
                            start_time_24 = datetime.datetime.strptime(timestamps_24[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            end_time_24 = datetime.datetime.strptime(timestamps_24[-1], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            sensor_names_24_out[f'hall_effect_sensor_{i}.txt'] = sensor_names_24[-1]
                        # Clip data to the previous 24 hours
                        filtered_data_prev_24 = clip_to_previous_24_hours(filtered_data)
                        if filtered_data_prev_24:
                            first_count_prev_24 = filtered_data_prev_24[0][1]
                            counts_prev_24 = [entry[1] - first_count_prev_24 for entry in filtered_data_prev_24]
                            total_counts_24_prev[f'total_counts_24_hall_{i}'] = max(counts_prev_24)
                        else:
                            total_counts_24_prev[f'total_counts_24_hall_{i}'] = 0
            
            # Display total counts and deltas in a 4-column by 2-row grid

            sensor_names_24_out = extract_sensor_names(files)
            # Display total counts and deltas in a 4-column by 2-row grid
            cols = st.columns(4)
            for i, (key, value) in enumerate(total_counts_24.items()):
                col = cols[i % 4]
                delta = value - total_counts_24_prev[key]
                file_name = f"hall_effect_sensor_{i+1}.txt"
                sensor_name = sensor_names_24_out.get(file_name, "Unknown Sensor")
                col.metric(f"Total Counts {sensor_name}", value, delta)
                
            
            st.markdown(f"**Date Range for Last 24 Hours**: {start_time_24} to {end_time_24}", help='Time range for data values shown above. Note: Date range may appear to be greater than 24 hours due to how the date increases at midnight, this is normal.')
            
        elif metric_timeframe == 'Last 7am to 7am Period':
            total_counts_7am = {}
            total_counts_7am_prev = {}
            date_ranges_7am = {}
            date_ranges_7am_prev = {}
            sensor_names_7am_out = {}
            
            # Parse data from each .txt file and add to Plotly figure
            for i, (file_name, file_content) in enumerate(files.items(), start=1):
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = parse_sensor_data_from_raw(file_content)
                    if filtered_data:
                        # Clip data to the last 7am to 7am period
                        filtered_data_7am, cutoff_time_start_7am, cutoff_time_end_7am = clip_to_7am_period(filtered_data)
                        print(filtered_data)
                        if filtered_data_7am:
                            first_count_7am = filtered_data_7am[0][1]
                            timestamps_7am = [entry[0] for entry in filtered_data_7am]
                            counts_7am = [entry[1] - first_count_7am for entry in filtered_data_7am]
                            sensor_names_7am = [entry[2] for entry in filtered_data_7am]
                            total_counts_7am[f'total_counts_7am_hall_{i}'] = max(counts_7am)
                            date_ranges_7am[f'total_counts_7am_hall_{i}'] = f"{cutoff_time_start_7am.strftime('%Y-%m-%d %H:%M:%S')} to {cutoff_time_end_7am.strftime('%Y-%m-%d %H:%M:%S')}"
                            print('hello')
                            sensor_names_7am_out[i]=sensor_names_7am[-1]
                        
                        # Clip data to the previous 7am to 7am period
                        filtered_data_prev_7am, cutoff_time_start_prev_7am, cutoff_time_end_prev_7am = clip_to_previous_7am_period(filtered_data)
                        if filtered_data_prev_7am:
                            first_count_prev_7am = filtered_data_prev_7am[0][1]
                            counts_prev_7am = [entry[1] - first_count_prev_7am for entry in filtered_data_prev_7am]
                            total_counts_7am_prev[f'total_counts_7am_hall_{i}'] = max(counts_prev_7am)
                            date_ranges_7am_prev[f'total_counts_7am_hall_{i}'] = f"{cutoff_time_start_prev_7am.strftime('%Y-%m-%d %H:%M:%S')} to {cutoff_time_end_prev_7am.strftime('%Y-%m-%d %H:%M:%S')}"
                        else:
                            total_counts_7am_prev[f'total_counts_7am_hall_{i}'] = 0

            sensor_names_7am_out=extract_sensor_names(files)
            cols = st.columns(4)
            for i, (key, value) in enumerate(total_counts_7am.items()):
                col = cols[i % 4]
                delta = value - total_counts_7am_prev[key]
                sensor_name = sensor_names_7am_out[i+1]
                col.metric(f"Total Counts {sensor_name}", value, delta)
                
            # Display the first date range below the metrics
            first_key = next(iter(date_ranges_7am))
            first_date_range = date_ranges_7am[first_key]
            st.markdown(f"**Date Range for Displayed Data**: {first_date_range}", help='Time range for data values shown above. Note: Date range may appear to be greater than 24 hours due to how the date increases at midnight, this is normal.')
            
            
        graph_1, graph_2 = st.columns(2)
        
        #Second section
        with graph_1:
            # Create figure for Plotly chart
            setting = st.selectbox("Select Time Frame", ['All', 'Last 24 Hours Available', 'Last Hour Avaible'], help='Select the time frame to be displayed in the figure')
    
            fig = go.Figure()
            
            # Parse data based on selected time frame
            if setting == 'All':
                for file_name, file_content in files.items():
                    if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                        filtered_data = parse_sensor_data_from_raw(file_content)
                        
                        if filtered_data:
                            timestamps = [entry[0] for entry in filtered_data]
                            counts = [entry[1] for entry in filtered_data]
                            sensor_names = [entry[2] for entry in filtered_data]
                            
                            # Add trace to Plotly figure with sensor name as label
                            fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
                
                # Customize layout
                fig.update_layout(title='Sensor Data over Time',
                                  xaxis_title='Time',
                                  yaxis_title='Count',
                                  hovermode='x unified')
            
            elif setting == 'Last 24 Hours Available':
                # Parse data from each .txt file and add to Plotly figure
                for file_name, file_content in files.items():
                    if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                        filtered_data = parse_sensor_data_from_raw(file_content)
                        if filtered_data:
                            # Clip data to the last 24 hours
                            filtered_data = clip_to_last_24_hours(filtered_data)
                            first_count = filtered_data[0][1]
                            if filtered_data:
                                timestamps = [entry[0] for entry in filtered_data]
                                counts = [entry[1]-first_count for entry in filtered_data]
                                sensor_names = [entry[2] for entry in filtered_data]
                                
                                # Add trace to Plotly figure with sensor name as label
                                fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
                
                # Customize layout
                fig.update_layout(title='Sensor Data over Time (Last 24 Hours)',
                                  xaxis_title='Time',
                                  yaxis_title='Count',
                                  hovermode='x unified')
            
            elif setting == 'Last Hour Avaible':
                # Parse data from each .txt file and add to Plotly figure
                for file_name, file_content in files.items():
                    if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                        filtered_data = parse_sensor_data_from_raw(file_content)
                        if filtered_data:
                            # Clip data to the last 1 hour
                            filtered_data = clip_to_last_1_hour(filtered_data)
                            first_count = filtered_data[0][1]
                            if filtered_data:
                                timestamps = [entry[0] for entry in filtered_data]
                                counts = [entry[1]-first_count for entry in filtered_data]
                                sensor_names = [entry[2] for entry in filtered_data]
                                
                                # Add trace to Plotly figure with sensor name as label
                                fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
                
                # Customize layout
                fig.update_layout(title='Sensor Data over Time (Last 1 Hour)',
                                  xaxis_title='Time',
                                  yaxis_title='Count',
                                  hovermode='x unified')
            
            # Render Plotly chart
            st.plotly_chart(fig)
            
            with st.expander("Sample Raw .txt data"):
                # Debug: Display file content
                for file_name, content in files.items():
                    if isinstance(content, dict):
                        st.text(f"Content of {file_name}: {content}")  # Display preferences.json content
                    else:
                        st.text(f"Content of {file_name}:\n{content[:500]}...")  # Display first 500 characters for other files

        
       #third section
        with graph_2:
            graph_2_setting = st.selectbox("Select Time Frame", ['7am to 7am'], help='Select the time frame to be displayed in the figure')
            # Initialize DataFrame for display
            ranges_df = pd.DataFrame()
            
            # Process each file for 7am to 7am periods
            for file_name, file_content in files.items():
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = parse_sensor_data_from_raw(file_content)
                    if filtered_data:
                        ranges_data = calculate_7am_to_7am_ranges(filtered_data)
                        ranges_df = pd.concat([ranges_df, ranges_data], axis=1)
            
            # Display the ranges DataFrame using Plotly bar charts
            
            # Create a figure for Plotly bar chart
            fig = go.Figure()
            
            # Add bar traces for each sensor
            for sensor_name in ranges_df.columns:
                fig.add_trace(go.Bar(x=ranges_df.index, y=ranges_df[sensor_name], name=sensor_name))
            
            # Customize layout
            fig.update_layout(
                barmode='group',
                xaxis_tickangle=-45,
                xaxis=dict(title='7am to 7am Period'),
                yaxis=dict(title='Range of Counts'),
                legend=dict(title='Sensor'),
                title='Ranges of Counts per 7am to 7am Periods'
            )
            
            # Display the Plotly figure using st.plotly_chart
            st.plotly_chart(fig)
                        
                
            with st.expander("Raw 7am to 7am data"):
                
                # Calculate counts per 7am to 7am period all
                
    
                # Display the ranges DataFrame
                st.dataframe(ranges_df)
                # Check if refresh button is clicked

        # Button to refresh data
        github_repo_s = st.session_state.get('github_repo')
        github_access_key_s = st.session_state.get('github_access_key')

        with st.expander("Latest Update Times"):
            if github_repo_s and github_access_key_s:
                st.subheader("Last Modified Dates")
                file_names = [f"hall_effect_sensor_{i}.txt" for i in range(1, 9)]
                
                for file_name in file_names:
                    last_modified = get_last_commit_date(github_repo_s, github_access_key_s, file_name)
                    if last_modified:
                        st.write(f"{file_name}: {last_modified}")
                    else:
                        st.write(f"{file_name}: Unable to retrieve last modified date.")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Refresh Data"):
                # Check if GitHub credentials are defined
                
                
                if github_repo_s and github_access_key_s:
                    file_names_s = st.session_state.get('file_names', [])
                    st.write("Refreshing data...")
                    files.update(get_github_files(github_repo_s, github_access_key_s, file_names_s))
                    
                    # Record the timestamp of last refresh
                    timestamp_last_refresh = record_timestamp()
                    st.session_state.timestamp_last_refresh = timestamp_last_refresh
                    
                    # Display confirmation
                    st.write("Data refreshed successfully!")
                
                else:
                    st.error('GitHub repository name or access key is not defined. Please apply settings first.')
            
        
        
        with col2:
            st.download_button(label="Download .txt Files", data=files_to_bytesio(files), file_name="sensor_data.zip")

       

        

        # Display last refreshed timestamp
        if 'timestamp_last_refresh' in st.session_state:
            st.write(f"Last Page Refresh: {st.session_state.timestamp_last_refresh}")
    elif selected2 == "Wiki":
        st.header("README")

        github_access_key_s = st.session_state.get('github_access_key')
        
        if github_access_key_s:
            readme_content = get_github_readme("agadin/Lake_viewer", github_access_key_s)
            st.markdown(readme_content)
        else:
            st.error("GitHub Access Key not defined. Please go to the Settings page and input the key.")


if __name__ == "__main__":
    main()