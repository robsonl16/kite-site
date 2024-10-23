import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

def summarize_wind_data(wind_data):
    """
    Summarizes wind data by calculating mean, max, and min wind speeds
    
    Parameters: 
        wind_data (list): List of dictionaries containing wind speed data
    
    Returns: 
        summary (dict): Dictionary with 'mean', 'max', and 'min' wind speeds
    """
    df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed"])
    df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
    
    mean_speed = df["Wind Speed"].mean()
    max_speed = df["Wind Speed"].max()
    min_speed = df["Wind Speed"].min()
    
    summary = {
        "mean_speed": mean_speed,
        "max_speed": max_speed,
        "min_speed": min_speed
    }
    return summary



def calculate_time_intervals(df: pd.DataFrame, timestamp_col: str) -> pd.Series:
    """
    Calculate the time intervals between consecutive wind data readings.
    
    df: DataFrame containing wind data with a timestamp column of pandas Timestamp objects.
    timestamp_col: Name of the column containing the timestamps (in Timestamp format).
    
    Returns: pandas Series of time intervals between readings (in seconds).
    """
    # Calculate the time difference between consecutive timestamps
    time_intervals = df[timestamp_col].diff().dt.total_seconds()

    return time_intervals



def calculate_time_above_thresholds(df: pd.DataFrame, wind_speed_col: str, timestamp_col: str, thresholds: list) -> dict:
    """
    Calculate the total time the wind speed is above specific thresholds.
    
    df: DataFrame containing wind data with wind speed and timestamp columns.
    wind_speed_col: Name of the column containing the wind speeds.
    timestamp_col: Name of the column containing the timestamps (in Timestamp format).
    thresholds: List of speed thresholds in knots.
    
    Returns: A dictionary mapping each threshold to total time in seconds.
    """
    # Ensure there are at least two timestamps to calculate intervals
    if len(df) < 2:
        raise ValueError("DataFrame must contain at least two timestamps to calculate time intervals.")
    
    # Calculate the consistent time interval between readings
    time_interval = (df[timestamp_col].iloc[1] - df[timestamp_col].iloc[0]).total_seconds()
    
    # Initialize a dictionary to store total time above each threshold
    time_above = {threshold: 0 for threshold in thresholds}
    
    # Loop through each threshold and calculate the time wind speed is above it
    for threshold in thresholds:
        # Count the number of readings where the wind speed is above the threshold
        readings_above_threshold = df[df[wind_speed_col] > threshold].shape[0]
        
        # Calculate the total time above the threshold
        time_above[threshold] = readings_above_threshold * time_interval
    
    return time_above


def seconds_to_hms(seconds: float) -> str:
    """
    Convert seconds to a formatted string of hours, minutes, and seconds.
    
    seconds: Total time in seconds.
    
    Returns: Formatted string in the format "HH:MM:SS".
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"


import matplotlib.pyplot as plt

def plot_time_above_thresholds(time_above: dict):
    """
    Plot the total time above each wind speed threshold in a bar graph.
    
    time_above: Dictionary mapping each threshold to total time in seconds.
    """
    # Convert total time from seconds to H:M:S
    thresholds = list(time_above.keys())
    times_in_hms = [seconds_to_hms(time) for time in time_above.values()]

    # Convert times to total seconds for bar heights
    total_times = list(time_above.values())

    # Create bar graph
    plt.figure(figsize=(10, 6))
    bars = plt.bar(thresholds, total_times, color='skyblue')
    
    # Set labels and title
    plt.xlabel('Wind Speed Threshold (knots)')
    plt.ylabel('Total Time Above Threshold (seconds)')
    plt.title('Total Time Above Wind Speed Thresholds')
    
    # Add the time in H:M:S format on top of the bars
    for i, bar in enumerate(bars):
        height = bar.get_height()  # Get the height of the bar
        plt.text(bar.get_x() + bar.get_width() / 2, height, times_in_hms[i], ha='center', va='bottom')

    plt.xticks(thresholds)
    plt.grid(axis='y')
    plt.show()





