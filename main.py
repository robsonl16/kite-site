from datetime import datetime
import dataCollection
import windCalculations


#1. Set API parameters 
station_id = '183476'
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 2)
days_per_request = 5
wind_speed_thresholds = [8, 12, 16, 20, 24, 28]
output_file_path = 'C:/PythonTemp/wind_data_2023.csv'

# Gets wind data
wind = dataCollection.fetch_wind_avg_data(station_id=station_id, start_time=start_date, end_time=end_date)
# Calculates time above specified wind speed thresholds
calculation = windCalculations.calculate_time_above_thresholds(wind, "Wind Speed (knots)", "Time", wind_speed_thresholds)
# Plots time above thresholds
windCalculations.plot_time_above_thresholds(calculation)


