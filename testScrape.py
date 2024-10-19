from bs4 import BeautifulSoup
import requests
import shutil
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from datetime import datetime
import pandas as pd


#1. Set API parameters 
station_id = '183476'
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 5)
days_per_request = 5
wind_speed_thresholds = [8, 12, 16, 20, 24, 28]
output_file_path = 'C:/PythonTemp/wind_data_2023.csv'

 # 2. Function to collect data for a specific time period 
def fetch_wind_data(station_id, start_time, end_time):
    params = {  'spot_id': station_id,
                'time_start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'time_end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'units_wind': 'mph',
                'fields': 'wind,wind_gust,wind_dir',
                'wf_token': api_token,
                'type': 'dataonly',
                'format': 'json' }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else: 
        print(f"Error fetching data: {response.status_code}")
        return None

data = fetch_wind_data(183476, start_date, end_date)
wind_data = data['wind_avg_data']
df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed"])
df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
plt.plot(df["Time"], df["Wind Speed"])
plt.xlabel("Time")
plt.ylabel("Wind Speed")
plt.grid(True)
plt.show()
print(data)
# html_doc = """
# <html><head><title>The Dormouse's story</title></head>
# <body>
# <p class="title"><b>The Dormouse's story</b></p>

# <p class="story">Once upon a time there were three little sisters; and their names were
# <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
# <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
# <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
# and they lived at the bottom of a well.</p>

# <p class="story">...</p>
# """

# # Fetch the website
# html_page = requests.get('https://stackoverflow.com/questions/20180543/how-do-i-check-the-versions-of-python-modules')
# if html_page.status_code != 200:
#     print(f"Failed to retrieve webpage. Status code: {html_page.status_code}")
# else:
#     soup = BeautifulSoup(html_page.content, 'html.parser')

#     # Find the first image
#     images = soup.findAll('img')
#     if images:
#         example = images[0]
#         url_base = "https://webscraper.io"
#         url_ext = example.attrs['src']
#         full_url = url_ext
#         print(f"Image URL: {full_url}")

#         # Request the image
#         r = requests.get(full_url, stream=True)
#         if r.status_code == 200:
#             img_path = r"C:\Users\robso_jdkjtyb\OneDrive\Documents\GitHub\Scraping\img.jpg"
#             os.makedirs(os.path.dirname(img_path), exist_ok=True)
#             with open(img_path, 'wb') as f:
#                 r.raw.decode_content = True
#                 shutil.copyfileobj(r.raw, f)

#             # Display the image
#             img = mpimg.imread(img_path)
#             imgplot = plt.imshow(img)
#             plt.show()
#         else:
#             print(f"Failed to retrieve image. Status code: {r.status_code}")
#     else:
#         print("No images found on the page.")


# # html_page = requests.get('https://webscraper.io/test-sites/tables')
# # soup = BeautifulSoup(html_page.content, 'html.parser')
# # # print(soup)
# # # warning = soup.find('div', class_="alert alert-warning")
# # # book_container = warning.nextSibling.nextSibling
# # images = soup.findAll('img')
# # example = images[0]
# # url_base = "https://webscraper.io" #Original website
# # url_ext = example.attrs['src'] #The extension you pulled earlier

# # full_url = url_base + url_ext #Combining first 2 variables to create a complete URL

# # r = requests.get(full_url, stream=True) #Get request on full_url
# # print(r.raw)
# # if r.status_code == 200:                     #200 status code = OK
# #    with open(r"C:\Users\robso_jdkjtyb\OneDrive\Documents\GitHub\Scraping\img.jpg", 'wb') as f: 
# #       r.raw.decode_content = True
# #       shutil.copyfileobj(r.raw, f)
# # img = mpimg.imread(r"C:\Users\robso_jdkjtyb\OneDrive\Documents\GitHub\Scraping\img.jpg")
# # imgplot = plt.imshow(img)
# # plt.show()
# # with open("C:\\Users\\robso_jdkjtyb\\Downloads\\sample2.html") as fp:
# #     soup = BeautifulSoup(fp, "html.parser")
# # soup = BeautifulSoup(page, 'html.parser')
# # print(type(soup.find_all()))