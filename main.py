from datetime import datetime
import dataCollection


#1. Set API parameters 
station_id = '183476'
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 5)
days_per_request = 5
wind_speed_thresholds = [8, 12, 16, 20, 24, 28]
output_file_path = 'C:/PythonTemp/wind_data_2023.csv'

print(dataCollection.fetch_wind_avg_data(station_id=station_id, start_time=start_date, end_time=end_date))
print(dataCollection.fetch_wind_dir_data(station_id=station_id, start_time=start_date, end_time=end_date))

#This is a comment from Dad
