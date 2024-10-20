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
