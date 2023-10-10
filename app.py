import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='MONAS Dashboard',
                   layout='wide', initial_sidebar_state='collapsed')

# with open('../style.css') as f:
#     st.markdown(f'<style> {f.read()} </style>')
#     f.close()

st.sidebar.header('MONAS Dashboard')

weather = pd.read_csv(
    'C:/Users/nasut/OneDrive/Documents/Kuliah/Semester 7/PKKM/BMKG/Project/Data/data_fix_temp.txt')

# weather.set_index('Date')
# weather.index = pd.to_datetime(weather.index)
weather['Date'] = pd.to_datetime(weather['Date'])

# Filter date untuk line chart
col1, col2 = st.columns(2)

start_date = (weather['Date']).min()
end_date = (weather['Date']).max()

with col1:
    date1 = st.date_input('Start Date', start_date, format='YYYY-MM-DD')
with col2:
    date2 = st.date_input('End Date', end_date, format='YYYY-MM-DD')


st.subheader('Time Series')

linechart = pd.DataFrame(
     weather[['Date','t_obs', 'lokasi']])

linechart_sorted = linechart
linechart_sorted = linechart_sorted.set_index('Date')
linechart_sorted = linechart_sorted.sort_index()
linechart_sorted_filtered = linechart_sorted[linechart_sorted['lokasi'] == 97260]


fig = px.line(linechart_sorted_filtered[date1:date2], y='t_obs',
              labels={'t_obs': 'Suhu Observasi'}, height=500, width=1000, template='gridon')
st.plotly_chart(fig, use_container_width=True)
