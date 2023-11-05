import streamlit as st
from tiktokapipy.api import TikTokAPI
import pandas as pd
import time
import os.path
import re
import subprocess

subprocess.run(["playwright", "install"])

def getStats(url):
    with TikTokAPI() as api:
        video = api.video(url)
        return video.stats.play_count, video.stats.digg_count

st.warning("Jeśli nic nie widać, to znaczy, że aplikacja się ładuje.", icon="🚨")
st.success("Żeby działało trzeba wkleić czysty link taki jak ten: https://www.tiktok.com/@codzienieciekawostka/video/7298018042145983777", icon="🔥")

url = st.text_input('Wpisz url tiktoka')
chart = st.line_chart()
col1, col2, col3 = st.columns(3)
likes_metric = col1.metric("👍", "0")
views_metric = col2.metric("👀", "0")

progress_bar = st.progress(0)
st.text_input("Podaj nazwe tiktoka jeśli chesz")

from datetime import datetime, timedelta


if url != '':
    video_id = re.search(r'(?<=video/)[^/]+', url).group()
    filename = f'{video_id}.xlsx'
    if os.path.isfile(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame({'Time': [], 'Number of Views': [], 'Number of Likes': []})

    last_two_minutes = []
    while True:
        views, likes = getStats(url)

        new_data = pd.DataFrame({'Time': [time.strftime('%Y-%m-%d %H:%M:%S')], 'Number of Views': [views], 'Number of Likes': [likes]})
        df = pd.concat([df, new_data], ignore_index=True)
        chart.area_chart({'Number of Views': df['Number of Views'], 'Number of Likes (*10)': df['Number of Likes'] * 10})

        # Add current views and timestamp to last_two_minutes
        last_two_minutes.append((views, datetime.now()))

        # Remove views and timestamps that are older than two minutes
        last_two_minutes = [(v, t) for v, t in last_two_minutes if datetime.now() - t < timedelta(minutes=2)]


        if len(df) >= 2 and views > 0 and df['Number of Views'].iloc[-2] == 0:
            st.balloons()
            st.toast("Film ruszył!", icon="🎉")
        
        # Display metrics for likes, views, and view rate in three columns
        
        likes_metric.metric("👍", f"{likes:,}")
        views_metric.metric("👀", f"{views:,}")

        try:
            view_rate = views - df['Number of Views'].iloc[-10]
        except:
            view_rate = 0
        col3.metric("View Rate", f"{view_rate:,}")

        with pd.ExcelWriter(filename, mode='w') as writer:
            df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1)
        for i in range(100, 0, -1):
            time.sleep(0.05)
            progress_bar.progress(i - 1)