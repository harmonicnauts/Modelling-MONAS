import streamlit as st
import pandas as pd
import plotly.express as px

# config untuk page MONAS
st.set_page_config(page_title='MONAS Dashboard',
                   layout='wide', initial_sidebar_state='auto')

# with open('../style.css') as f:
#     st.markdown(f'<style> {f.read()} </style>')
#     f.close()

# header halaman dan sidebar
st.sidebar.header('MONAS Dashboard')
st.header('Model Correction of INA-NWP Assimilation (MONAS) Dashboard')

# membaca data
weather = pd.read_csv(
    '.\Modelling\data_fix_temp.txt')
df_wmoid = pd.read_excel('.\Modelling\daftar_wmoid.xlsx')

# mengganti nama kolom WMOID agar dapat dimerge dengan df utama
df_wmoid = df_wmoid.rename(columns={'WMOID': 'lokasi'})
df_wmoid = df_wmoid[['lokasi', 'Nama UPT']]

# weather.set_index('Date')
# weather.index = pd.to_datetime(weather.index)
weather['Date'] = pd.to_datetime(weather['Date'])

# Filter date untuk line chart
col1, col2 = st.sidebar.columns(2)

start_date = (weather['Date']).min()
end_date = (weather['Date']).max()

with col1:
    date1 = st.sidebar.date_input(
        'Start Date', start_date, format='YYYY-MM-DD')
with col2:
    date2 = st.sidebar.date_input('End Date', end_date, format='YYYY-MM-DD')

linechart = pd.DataFrame(
    weather[['Date', 't_obs', 'lokasi']])

linechart_sorted = linechart
linechart_sorted = linechart_sorted.set_index('Date')
linechart_sorted = linechart_sorted.sort_index()

linechart_sorted_merged = linechart_sorted.merge(df_wmoid, on='lokasi')

# config untuk menu multiselect
options = st.sidebar.multiselect(
    'Lokasi Stasiun',
    linechart_sorted_merged.lokasi.unique(),
    linechart_sorted_merged.lokasi.unique()[0])

# st.write(f'{options}')

linechart_sorted_filtered = linechart_sorted[linechart_sorted['lokasi'].isin(
    options)]

st.subheader('Time Series')

# Plotting time series untuk 't_obs'
fig = px.line(linechart_sorted_filtered[date1:date2], y='t_obs', color='lokasi',
              labels={'t_obs': 'Suhu Observasi'}, height=500, width=1000, template='gridon')
st.plotly_chart(fig, use_container_width=True)
