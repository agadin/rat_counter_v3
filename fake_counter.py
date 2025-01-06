import time

# Define the file path
file_path = "sensor_data.txt"

# Starting timestamp components
year = 2025
month = 1
day = 5
hour = 18
minute = 49
second = 15


# Define a function to increment the time
def increment_time(year, month, day, hour, minute, second):
    second += 1  # Increment seconds
    if second >= 60:
        second = 0
        minute += 1
    if minute >= 60:
        minute = 0
        hour += 1
    if hour >= 24:
        hour = 0
        day += 1
    # Simplified: Assume all months have 30 days (adjust if needed)
    if day > 30:
        day = 1
        month += 1
    if month > 12:
        month = 1
        year += 1
    return year, month, day, hour, minute, second


# Open the file in write mode
with open(file_path, "w") as file:
    # Simulate 99,999 data entries
    for i in range(1, 100000):
        # Format: 2025,1,5,18,49,15,1,Sensor 1,Pin D3
        timestamp = f"{year},{month},{day},{hour},{minute},{second},{i},Sensor 1,Pin D3"

        # Write the entry to the file
        file.write(timestamp + "\n")

        # Increment time for the next entry
        year, month, day, hour, minute, second = increment_time(year, month, day, hour, minute, second)

print(f"Successfully wrote 99,999 entries to {file_path}")
