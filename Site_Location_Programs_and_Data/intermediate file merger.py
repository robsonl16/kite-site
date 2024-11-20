import os
import pandas as pd

# Folder containing intermediate CSV files
input_folder = r'c:\Kite_site\SUN'
output_file = os.path.join(input_folder, 'merged_output_241119.csv')

# List to hold DataFrame objects for all CSV files
dataframes = []

# Iterate through files in the folder
for filename in os.listdir(input_folder):
    if filename.startswith('intermediate_missed_241119') and filename.endswith('.csv'):
        file_path = os.path.join(input_folder, filename)
        print(f"Processing file: {filename}")
        # Read the CSV file into a DataFrame and append to the list
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dataframes, ignore_index=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv(output_file, index=False)

print(f"Merged file saved as: {output_file}")
