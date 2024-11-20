import pandas as pd
from datetime import timedelta

# File paths
main_csv = r"C:\Kite_site\SUN\merged_output_241119.csv"
station_details_csv = r"C:\weather_station_data\All Weather Station Details 241118.csv"
timezone_offsets_csv = r"C:\weather_station_data\timezone_offsets_2025.csv"

# Step 1: Read only the first 2000 rows from the main CSV
print("Reading the first 2000 rows of the main CSV file...")
main_data = pd.read_csv(main_csv, nrows=2000)

# Ensure the "Date" column is in datetime format and add the "Week" column
print("Adding 'Week' column based on ISO week...")
main_data['Date'] = pd.to_datetime(main_data['Date'], errors='coerce')
main_data['Week'] = main_data['Date'].dt.isocalendar().week

# Step 2: Merge TimeZone_LongName from the station details file
print("Reading the weather station details file and merging 'TimeZone_LongName'...")
station_details = pd.read_csv(station_details_csv)
main_data = main_data.merge(
    station_details[['Station_Id', 'TimeZone_LongName']],
    on='Station_Id',
    how='left'
)

# Step 3: Read timezone_offsets and merge GMT Offset
print("Reading the timezone offsets file...")
timezone_offsets = pd.read_csv(timezone_offsets_csv)

# Ensure the 'Date' columns in both dataframes are in datetime format
print("Converting 'Date' columns to datetime format...")
main_data['Date'] = pd.to_datetime(main_data['Date'], errors='coerce')
timezone_offsets['Date'] = pd.to_datetime(timezone_offsets['Date'], errors='coerce')

# Merge GMT Offset
print("Merging 'GMT Offset'...")
main_data = main_data.merge(
    timezone_offsets[['Date', 'Time Zone', 'GMT Offset (Hours)']],
    left_on=['Date', 'TimeZone_LongName'],
    right_on=['Date', 'Time Zone'],
    how='left'
)
main_data.rename(columns={'GMT Offset (Hours)': 'GMT_Offset'}, inplace=True)

# Step 4: Correct Dawn, Dusk, Sunrise, Sunset to local times
print("Adjusting Dawn, Sunrise, Sunset, and Dusk to local times...")
time_columns = ['Dawn', 'Sunrise', 'Sunset', 'Dusk']

for col in time_columns:
    # Convert the column to timedelta for time adjustments
    def parse_time(value):
        if pd.isna(value):
            return timedelta(0)  # Return zero timedelta for NaN values
        try:
            # Parse the string value into hours, minutes, and seconds
            parts = str(value).split(':')
            return timedelta(
                hours=int(parts[0]),
                minutes=int(parts[1]),
                seconds=float(parts[2]) if len(parts) > 2 else 0
            )
        except Exception as e:
            print(f"Error parsing time for column '{col}': {value}")
            return timedelta(0)

    # Apply the parsing function to each value in the column
    main_data[col] = main_data[col].apply(parse_time)
    
    # Adjust by GMT offset
    main_data[col] = main_data[col] + main_data['GMT_Offset'].apply(lambda x: timedelta(hours=x) if not pd.isna(x) else timedelta(0))


# Save the intermediate file
intermediate_output = r"C:\Kite_site\SUN\intermediate_output.csv"
print(f"Saving the intermediate file to: {intermediate_output}...")
main_data.to_csv(intermediate_output, index=False)

# Step 5: Pivot the data by Station_Id and Week to get averages
print("Pivoting the data by Station_Id and Week to calculate averages...")
pivot_data = main_data.groupby(['Station_Id', 'Week'])[time_columns].mean().reset_index()

# Save the final output
final_output = r"C:\Kite_site\SUN\final_output.csv"
print(f"Saving the final pivoted data to: {final_output}...")
pivot_data.to_csv(final_output, index=False)

print("Processing complete!")
