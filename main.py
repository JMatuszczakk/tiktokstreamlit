import streamlit as st
from tiktokapipy.api import TikTokAPI
import pandas as pd
import time
import os.path
import re
import subprocess

subprocess.run(["playwright", "install"])

# Function to get the view count and like count for a given TikTok URL
def getStats(url):
    with TikTokAPI() as api:
        video = api.video(url)
        return video.stats.play_count, video.stats.digg_count

st.warning("Jeśli nic nie widać, to znaczy, że aplikacja się ładuje.", icon="🚨")
st.warning("Żeby działało trzeba wkleić czysty link taki jak ten: https://www.tiktok.com/@codzienieciekawostka/video/7298018042145983777", icon="🔥")

# Create the chart and current views/likes count outside the main loop
url = st.text_input('Wpisz url tiktoka')
chart = st.line_chart()
current_stats = st.empty()

if url != '':
    # Extract the video ID from the TikTok URL
    video_id = re.search(r'(?<=video/)[^/]+', url).group()
    filename = f'{video_id}.xlsx'
    if os.path.isfile(filename):
        # Load existing Excel file
        df = pd.read_excel(filename)
    else:
        # Create a new Excel file if it doesn't exist
        df = pd.DataFrame({'Time': [], 'Number of Views': [], 'Number of Likes': []})
    while True:
        try:
            views, likes = getStats(url)
        except:
            pass
        # Update the data frame with new view count and like count
        new_data = pd.DataFrame({'Time': [time.strftime('%Y-%m-%d %H:%M:%S')], 'Number of Views': [views], 'Number of Likes': [likes]})
        df = pd.concat([df, new_data], ignore_index=True)
        # Update the chart with new data
        chart.line_chart(df['Number of Views'])
        # Update the current views/likes count
        current_stats.success(f"👀 Obecna ilość wyświetleń: {views}\n 👍 Ilość lików: {likes}")
        # Save data to Excel file
        with pd.ExcelWriter(filename, mode='w') as writer:
            df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        time.sleep(5)