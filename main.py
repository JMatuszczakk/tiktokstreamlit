import streamlit as st
from tiktokapipy.api import TikTokAPI
import pandas as pd
import time
import os.path
import re
import subprocess
from sklearn.linear_model import LinearRegression
import numpy as np

subprocess.run(["playwright", "install"])
subprocess.run(["pip3", "install", "scikit-learn"])

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

    last_ten_seconds = []
    while True:
        views, likes = getStats(url)

        new_data = pd.DataFrame({'Time': [time.strftime('%Y-%m-%d %H:%M:%S')], 'Number of Views': [views], 'Number of Likes': [likes]})
        df = pd.concat([df, new_data], ignore_index=True)
        chart.area_chart({'Number of Views': df['Number of Views'], 'Number of Likes (*10)': df['Number of Likes'] * 10})

        # Add current views and timestamp to last_ten_seconds
        last_ten_seconds.append((views, datetime.now()))

        # Remove views and timestamps that are older than ten seconds
        last_ten_seconds = [(v, t) for v, t in last_ten_seconds if datetime.now() - t < timedelta(seconds=10)]

        if len(df) >= 2 and views > 0 and df['Number of Views'].iloc[-2] == 0:
            st.balloons()
            st.toast("Film ruszył!", icon="🎉")
        
        # Display metrics for likes, views, and view rate in three columns
        
        likes_metric.metric("👍", f"{likes:,}")
        views_metric.metric("👀", f"{views:,}")

        try:
            view_rate = (views - last_ten_seconds[0][0]) / (datetime.now() - last_ten_seconds[0][1]).total_seconds()
        except:
            view_rate = 0

        # Perform linear regression on the data
        X = np.array(df['Number of Likes']).reshape(-1, 1)
        y = np.array(df['Number of Views']).reshape(-1, 1)
        model = LinearRegression().fit(X, y)
        predicted_views = model.predict([[likes]])[0][0]

        st.write(f"Predicted future view count: {predicted_views:.0f}")

        with pd.ExcelWriter(filename, mode='w') as writer:
            df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1)
        for i in range(100, 0, -1):
            time.sleep(0.05)
            progress_bar.progress(i - 1)