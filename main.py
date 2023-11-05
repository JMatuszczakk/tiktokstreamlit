import streamlit as st
from tiktokapipy.api import TikTokAPI
import pandas as pd
import time
import os.path
import re
import subprocess

subprocess.run(["playwright", "install"])
subprocess.run(["playwright", "install-deps"])




# Function to get the view count for a given TikTok URL
def getViews(url):
    with TikTokAPI() as api:
        video = api.video(url)
        return video.stats.play_count


st.success("Jeśli nic nie widać, to znaczy, że aplikacja się ładuje.", icon="🚨")
# Create the chart outside the main loop
url = st.text_input('Wpisz url tiktoka')
chart = st.line_chart()
if url != '':
    # Extract the video ID from the TikTok URL
    video_id = re.search(r'(?<=video/)[^/]+', url).group()
    filename = f'{video_id}.xlsx'
    if os.path.isfile(filename):
        # Load existing Excel file
        df = pd.read_excel(filename)
    else:
        # Create a new Excel file if it doesn't exist
        df = pd.DataFrame({'Time': [], 'Number of Views': []})
    while True:
        views = getViews(url)
        # Update the data frame with new view count
        new_data = pd.DataFrame({'Time': [time.strftime('%Y-%m-%d %H:%M:%S')], 'Number of Views': [views]})
        df = pd.concat([df, new_data], ignore_index=True)
        # Update the chart with new data
        chart.line_chart(df['Number of Views'])
        # Save data to Excel file
        with pd.ExcelWriter(filename, mode='w') as writer:
            df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        time.sleep(5)