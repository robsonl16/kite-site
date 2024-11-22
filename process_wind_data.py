from datetime import datetime, timedelta

def process_wind_data(data: dict, units_wind: str ,sunrise: datetime, sunset: datetime) -> dict:
    """
    Process the JSON data for a specific site and calculate metrics within the sunrise-sunset time window.

    Args:
        data (dict): JSON data containing wind and weather metrics.
        sunrise (datetime): Sunrise time for the day.
        sunset (datetime): Sunset time for the day.

    Returns:
        dict: Processed metrics for the day.
    """
    # Initialize processed data
    processed_data = {
        "daylight_hours": (sunset - sunrise).total_seconds() / 3600,
        "air_temp_avg": None,
        "air_temp_low": None,
        "air_temp_high": None,
        "precip_sum": 0,
        "precip_accum_sum": 0,
        "data_frequency": None,
        "units_wind": units_wind,
        #"units_temp": data.get('meta', {}).get('units', {}).get('temp'),
        "wind_threshold_minutes": {threshold: 0 for threshold in wind_speed_thresholds},
        "wind_avg_direction": None,
        "gustiness": [],
        "lulliness": []
    }

    sin_sum, cos_sum, wind_count = 0, 0, 0
    time_gaps = []
    last_time = None
    wind_data = data.get('data', [])
    units_wind = data.get('meta', {}).get('units', {}).get('wind', 'knots')

    for entry in wind_data:
        timestamp = datetime.datetime.utcfromtimestamp(entry['time'] / 1000.0)
        if sunrise <= timestamp <= sunset:
            # Convert wind speeds to knots
            wind_avg = convert_wind_speed_to_knots(entry.get('wind_avg', 0), units_wind)
            wind_gust = convert_wind_speed_to_knots(entry.get('wind_gust', 0), units_wind)
            wind_lull = convert_wind_speed_to_knots(entry.get('wind_lull', 0), units_wind)

            # Track air temperature stats
            air_temp = entry.get('air_temp')
            if air_temp is not None:
                if processed_data["air_temp_low"] is None or air_temp < processed_data["air_temp_low"]:
                    processed_data["air_temp_low"] = air_temp
                if processed_data["air_temp_high"] is None or air_temp > processed_data["air_temp_high"]:
                    processed_data["air_temp_high"] = air_temp
                processed_data["air_temp_avg"] = (processed_data["air_temp_avg"] or 0) + air_temp

            # Track precipitation
            processed_data["precip_sum"] += entry.get('precip', 0)
            processed_data["precip_accum_sum"] += entry.get('precip_accum', 0)

            # Calculate wind threshold metrics
            for threshold in wind_speed_thresholds:
                if wind_avg > threshold:
                    processed_data["wind_threshold_minutes"][threshold] += 1

            # Wind direction calculations
            if wind_avg > 8:  # Only for wind > 8 knots
                wind_dir = entry.get('wind_dir', 0)
                sin_sum += math.sin(math.radians(wind_dir))
                cos_sum += math.cos(math.radians(wind_dir))
                wind_count += 1

                # Gustiness and lulliness
                processed_data["gustiness"].append(wind_gust - wind_avg)
                processed_data["lulliness"].append(wind_avg - wind_lull)

            # Calculate data frequency
            if last_time:
                time_gaps.append((timestamp - last_time).total_seconds() / 60)
            last_time = timestamp

    # Finalize calculations
    if processed_data["air_temp_avg"] is not None:
        processed_data["air_temp_avg"] /= len(wind_data)
    processed_data["data_frequency"] = sum(time_gaps) / len(time_gaps) if time_gaps else None
    if wind_count > 0:
        avg_sin = sin_sum / wind_count
        avg_cos = cos_sum / wind_count
        processed_data["wind_avg_direction"] = math.degrees(math.atan2(avg_sin, avg_cos)) % 360

    # Convert lists of gustiness and lulliness to average metrics
    if processed_data["gustiness"]:
        processed_data["gustiness_avg"] = sum(processed_data["gustiness"]) / len(processed_data["gustiness"])
    if processed_data["lulliness"]:
        processed_data["lulliness_avg"] = sum(processed_data["lulliness"]) / len(processed_data["lulliness"])

    return processed_data


def convert_wind_speed_to_knots(speed: float, units_wind: str) -> float:
    """
    Convert wind speed to knots based on the units.

    Args:
        speed (float): The wind speed to be converted.
        units_wind (str): The current units of the wind speed ('kph', 'mph', or 'knots').

    Returns:
        float: The wind speed converted to knots.
    """
    if units_wind == 'kph':
        return speed * 0.539957  # 1 kilometer per hour = 0.539957 knots
    elif units_wind == 'mph':
        return speed * 0.868976  # 1 mile per hour = 0.868976 knots
    elif units_wind == 'knots':
        return speed  # Already in knots, no conversion needed
    else:
        raise ValueError(f"Unsupported wind speed unit: {units_wind}")
