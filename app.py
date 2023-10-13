import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import geopandas

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
    'C:/Users/nasut/OneDrive/Documents/Kuliah/Semester 7/PKKM/BMKG/Project/Data/data_fix_temp.txt')
df_wmoid = pd.read_excel('C:/Users/nasut/OneDrive/Documents/Kuliah/Semester 7/PKKM/BMKG/Project/MONAS-Dashboard/Modelling/daftar_wmoid.xlsx')

# mengganti nama kolom WMOID agar dapat dimerge dengan df utama
df_wmoid = df_wmoid.rename(columns={'WMOID': 'lokasi'})
df_wmoid = df_wmoid[['lokasi', 'Nama UPT']]

# Coming soon (Code untuk plotting titik stasiun pada peta)
new_df_unique_coord = df_wmoid.merge(weather, on='lokasi')
new_df_unique_coord = new_df_unique_coord[['lokasi','Nama UPT', 'LON', 'LAT']].drop_duplicates()

geometry = geopandas.points_from_xy(new_df_unique_coord.LON, new_df_unique_coord.LAT)
geo_df = geopandas.GeoDataFrame(
    new_df_unique_coord, geometry=geometry
)
geo_df = geo_df.reset_index(drop=True)
geo_df.head()


weather['Date'] = pd.to_datetime(weather['Date'])

# Filter date untuk line chart
col11, col12 = st.sidebar.columns(2)

start_date = (weather['Date']).tail(3).iloc[0]
end_date = (weather['Date']).max()

with col11:
    date1 = st.sidebar.date_input(
        'Start Date', start_date, format='YYYY-MM-DD')
with col12:
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


col21,col22 = st.columns(2)

# Plotting time series untuk 't_obs'
fig = px.line(linechart_sorted_filtered[date1:date2], y='t_obs', color='lokasi',
              labels={'t_obs': 'Suhu Observasi'},  template='gridon')

with col21:
    st.subheader('Temperatur')
    st.plotly_chart(fig, use_container_width=True)


center = (-7.471424, 110.319866)

m = folium.Map(location=center, zoom_start=10)
geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]

i = 0
for coordinates in geo_df_list:
  m.add_child(
        folium.Marker(
            location=coordinates,
            popup="WMOID: "
            + str(geo_df['lokasi'][i])
            + "<br>"
            + "Nama UPT: "
            + str(geo_df['Nama UPT'][i])
            + "<br>"
            + "Coordinates: "
            + str(geo_df_list[i]),
          
        )
    )
  i = i + 1

st_folium(m,width=1000)