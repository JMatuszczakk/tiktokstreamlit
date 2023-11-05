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
current_stats = st.empty()
progress_bar = st.progress(0)
st.text_input("Podaj nazwe tiktoka jeśli chesz")

if url != '':
    video_id = re.search(r'(?<=video/)[^/]+', url).group()
    filename = f'{video_id}.xlsx'
    if os.path.isfile(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame({'Time': [], 'Number of Views': [], 'Number of Likes': []})

    while True:
        views, likes = getStats(url)

        new_data = pd.DataFrame({'Time': [time.strftime('%Y-%m-%d %H:%M:%S')], 'Number of Views': [views], 'Number of Likes': [likes]})
        df = pd.concat([df, new_data], ignore_index=True)
        chart.line_chart(df['Number of Views'])
        current_stats.info(f"👀 Obecna ilość wyświetleń: {views}\n 👍 Ilość lików: {likes}")
        if len(df) >= 2 and views > 0 and df['Number of Views'].iloc[-2] == 0:
            st.balloons()
            st.toast("Film ruszył!", icon="🎉")
        with pd.ExcelWriter(filename, mode='w') as writer:
            df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1)
        for i in range(100, 0, -1):
            time.sleep(0.05)
            progress_bar.progress(i - 1)