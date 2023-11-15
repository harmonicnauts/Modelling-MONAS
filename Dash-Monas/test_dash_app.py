# Import the libraries
import json
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_leaflet as dl
import geopandas
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
from dash_extensions.javascript import assign
from xgboost import XGBRegressor
import pickle



# Initiate xgb
model_xgb = XGBRegressor()



# Load dataframes
df_temp = pd.read_csv('../../Data/data_fix_temp.txt') # Temp Dataframe
df_wmoid = pd.read_excel('../../Data/daftar_wmoid.xlsx') # UPT Dataframe
ina_nwp_input = pd.read_csv('../../Data/MONAS-input_nwp_compile.csv') # Feature to predict from INA-NWP

df_wmoid = df_wmoid.rename(columns={'WMOID': 'lokasi'}) # WMOID dataframe preproceses
df_wmoid = df_wmoid[['lokasi', 'Nama UPT']]



# Make merged dataframe for mapping
df_map = df_wmoid.merge(df_temp, on='lokasi')
df_map = df_map[['lokasi', 'Nama UPT', 'LON', 'LAT']].drop_duplicates()



# INA-NWP input preprocess
ina_nwp_input_filtered = ina_nwp_input.drop(columns=['Date', 'LAT', 'LON', 'prec_nwp'])  
ina_nwp_input_filtered = ina_nwp_input_filtered.rename(
    columns={
        'suhu2m(degC)' : 'suhu2m.degC.',
        'dew2m(degC)' : 'dew2m.degC.',
        'rh2m(%)' : 'rh2m...',
        'wspeed(m/s)' : 'wspeed.m.s.',
        'wdir(deg)' : 'wdir.deg.',
        'lcloud(%)' : 'lcloud...',
        'mcloud(%)' : 'mcloud...' ,
        'hcloud(%)' : 'hcloud...',
        'surpre(Pa)' : 'surpre.Pa.' ,
        'clmix(kg/kg)' : 'clmix.kg.kg.' ,
        'wamix(kg/kg)' : 'wamix.kg.kg.' ,
        'outlr(W/m2)' : 'outlr.W.m2.' ,
        'pblh(m)' : 'pblh.m.',
        'lifcl(m)' : 'lifcl.m.' ,
        'cape(j/kg)' : 'cape.j.kg.' ,
        'mdbz' : 'mdbz' ,
        't950(degC)' : 't950.degC.' ,
        'rh950(%)' : 'rh950...',
        'ws950(m/s)' : 'ws950.m.s.' ,
        'wd950(deg)' : 'wd950.deg.' ,
        't800(degC)' : 't800.degC.' ,
        'rh800(%)' : 'rh800...' ,
        'ws800(m/s)' : 'ws800.m.s.',
        'wd800(deg)' : 'wd800.deg.' ,
        't500(degC)' : 't500.degC.' ,
        'rh500(%)' : 'rh500...' ,
        'ws500(m/s)' : 'ws500.m.s.' ,
        'wd500(deg)' : 'wd500.deg.',
})



# Load ML Models
# etr = pickle.load(open('weather_extra_trees_regressor.pkl', 'rb'))
model_xgb.load_model('Temp_xgb_tuned_noShuffle.json')

temp_pred = model_xgb.predict(ina_nwp_input_filtered)



#OUTPUT

df_pred = pd.concat([ina_nwp_input['Date'], ina_nwp_input_filtered[['lokasi', 'suhu2m.degC.']], pd.Series(temp_pred, index = ina_nwp_input_filtered.index)], axis=1)
df_pred.columns = ['Date','lokasi', 'suhu2m.degC.', 'prediction']
df_pred = df_pred.dropna()



# Load script 
colorscale = [
    'rgb(0, 10, 112)',
    'rgb(0, 82, 190)', 
    'rgb(51, 153, 255)', 
    'rgb(153, 235, 255)', 
    'rgb(204, 255, 255)',
    'rgb(255, 255, 204)',
    'rgb(255, 225, 132)',
    'rgb(255, 158, 20)',
    'rgb(245, 25, 25)',
    'rgb(165, 0, 0)',
    'rgb(50, 0, 0)'
    ]
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # js lib used for colors



# Min and Max temp for point colors
vmin = 0
vmax = 35
colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=vmin, max=vmax, unit='°C')

BMKG_LOGO = "https://cdn.bmkg.go.id/Web/Logo-BMKG-new.png"



# Function for adding some properties to all the points in Leaflet Map
on_each_feature = assign(
    """function(feature, layer, context){
        if(feature.properties.lokasi){
            layer.bindTooltip(`${feature['properties']['Nama UPT']} \nKode:${feature['properties']['lokasi']} \n Koord : (${feature['properties']['LAT']},${feature['properties']['LON']})`)
        }
    }
    """)



# Function for assignng circlemarkers to each point
point_to_layer = assign(
    """
    function(feature, latlng, context){
        const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
        const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
        circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop
        return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
    }
    """)




# Make dataframe for showing min, max, avg temperature
grouped = df_pred.groupby('lokasi')['prediction'].agg(['max', 'mean', 'min']).astype('float64').round(1)
data_table_lokasi = df_wmoid.merge(grouped, left_on='lokasi', right_index=True)
data_table_lokasi = data_table_lokasi.rename(columns={'mean': 'average', 'max': 'max', 'min': 'min'})



# Make geopandas geometry for coordinates
geometry = geopandas.points_from_xy(df_map.LON, df_map.LAT)
upt_gpd = geopandas.GeoDataFrame(df_map, geometry=geometry)
upt_gpd = pd.merge(upt_gpd, data_table_lokasi[['lokasi', 'average']], on='lokasi')
upt_gpd = upt_gpd.reset_index(drop=True)

geojson = json.loads(upt_gpd.to_json())
geobuf = dlx.geojson_to_geobuf(geojson)
upt = dl.GeoJSON(
    data=geobuf,
    id='geojson',
    format='geobuf',
    zoomToBounds=True,  # when true, zooms to bounds when data changes
    pointToLayer=point_to_layer,  # how to draw points
    onEachFeature=on_each_feature,  # add (custom) tooltip
    hideout=dict(
        colorProp='average', 
        circleOptions=dict(
            fillOpacity=1, 
            stroke=False, 
            radius=5),
            min=vmin, 
            max=vmax, 
            colorscale=colorscale)
)
print('upt_gpd\n', upt_gpd)



# Sort the data by Date
# ina_nwp_input_sorted = ina_nwp_input_filtered.copy()
# ina_nwp_input_sorted = ina_nwp_input_sorted.sort_values(by='Date')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Begin
app = Dash(__name__, external_scripts=[chroma],  external_stylesheets=external_stylesheets, prevent_initial_callbacks=True)

app.layout = html.Div([
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                [dbc.Row(
                    [
                        dbc.Col(html.Img(src=BMKG_LOGO, height="55px")),
                        dbc.Col(dbc.NavbarBrand(className="ms-2")),
                        
                    ],
                    align="center",
                    className="g-0 d-flex flex-column align-items-center justify m-2",
                ),
                html.H1(children='MONAS Dashboard'),
                ],
                href="#",
                style={
                    "textDecoration": "none",
                    "display" : "flex",
                    "align-content": "center",
                    "justify-content" : "left",
                    "flex-direction" : "row",
                    },
            ),
        ]
    ),
    html.Div([  # Wrap the map and header in a div for layout
    dl.Map(
    [dl.TileLayer(), 
    upt,
    colorbar,
    ],
    center=[-2.058210136999589, 116.78386542384145],
    zoom=5,
    markerZoomAnimation = True,
    style={
        'height': '90vh', 
        'width' : '60vw'
        }
        ),
    html.Div([
    html.Div([
    html.Div([ # Div for map, metric, and graph
        dcc.RangeSlider(
            id='temp-metric',
            min=0,
            max=40,
            value=[0,0],
            step=None,
            vertical=True,
            tooltip={
                "placement": "left", 
                "always_visible": True
                },
            disabled=True,
        ),
        dcc.Graph(
            id='graph_per_loc', 
            style={
                'display' : 'relative',
                'top' : '0px',
                'left' : '100%',
            }),
    ], 
    style={
        'display': 'grid', 
        'grid-column': 'auto auto',
        'grid-auto-flow': 'column'
    }),



    html.Div([# Div for other details such as comparison graph, data tables, and other metrics 
        dcc.Dropdown(
                options=[{'label': loc, 
                        'value': loc} for loc in df_temp['lokasi'].unique()],
                value=[96001],
                id='dropdown-selection',
                multi=True,
            ),
        html.Div([ 
            dcc.Graph(id='graph-content', 
            style={
                'display': 'flex', 
                'align-items': 'center',
                'justify-content': 'center',
            }),
            dash_table.DataTable(
                data=data_table_lokasi.to_dict('records'), 
                page_size=10),
            ], style={
                'display': 'grid', 
                'grid-column': 'auto auto',
                'grid-auto-flow': 'row'
                })        
        ], style= {
            'display': 'grid', 
            'grid-column': 'auto auto',
            'grid-auto-flow': 'row'
        }),

    ], 
    style={
        'display': 'grid', 
        'grid-column': 'auto auto',
        'grid-auto-flow': 'row'
        }
        ),  # Display elements side by side
    ]),
    ], style={
        'display' : 'grid',
        'grid-column': 'auto auto',
        'grid-auto-flow': 'column'
    }),
])



# Callback function for changing line graph based on 'lokasi'.
@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # lokasi_length = len(value)
    dff = df_pred[df_pred['lokasi'].isin(value)][['Date', 'prediction', 'lokasi']]
    print(value)
    print(df_pred)
    print(dff)
    print(data_table_lokasi)
    return px.line(dff, x='Date', y='prediction', title='Temperature Prediction', color='lokasi', markers=True, line_shape='spline')



# Callback function for changing 
@callback(
        Output("temp-metric", "value"),
        Output("graph_per_loc", "figure"), 
        Input("geojson", "clickData"),
        prevent_initial_call=True
        )
def upt_click(feature):
    print(feature)    
    if feature is not None:
        wmoid_lokasi = data_table_lokasi['lokasi']
        prop_lokasi = feature['properties']['lokasi']
        nama_upt = data_table_lokasi[wmoid_lokasi == prop_lokasi]['Nama UPT'].values[0]

        features_to_display = ['Date', 'suhu2m.degC.', 'prediction', 'lokasi']

        dff_one_loc = df_pred[df_pred['lokasi'] == prop_lokasi][features_to_display]
        
        figure = px.line(dff_one_loc, x='Date', y='prediction', title=f'Temperatures in UPT {nama_upt} (UTF)', color='lokasi', markers=True, line_shape='spline')

        figure.add_scatter(x=dff_one_loc['Date'], y=dff_one_loc['suhu2m.degC.'], mode='lines', name='Output suhu 2m INA-NWP')
        figure.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        min_temp = data_table_lokasi[wmoid_lokasi == prop_lokasi]['min'].iloc[0]
        avg_temp = data_table_lokasi[wmoid_lokasi == prop_lokasi]['average'].iloc[0]
        max_temp = data_table_lokasi[wmoid_lokasi == prop_lokasi]['max'].iloc[0]

        slider_value = [min_temp, max_temp]

        return slider_value, figure
    else:
        figure =  px.line(dff_one_loc, y='prediction', title=f'Temperatures in UPT x', color='lokasi', markers=True, line_shape='spline')
        dff_one_loc = df_pred[df_pred['lokasi'] == 96001][['prediction', 'lokasi']]
        return figure



if __name__ == '__main__':
    app.run_server(debug=True)
