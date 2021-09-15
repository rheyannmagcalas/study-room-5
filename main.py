import datetime
import folium
import geopandas as gpd
import geopy
import haversine as hs
import joblib
import networkx as nx
import osmnx as ox
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import time

from branca.element import Figure
from folium.features import DivIcon
from geopandas import GeoDataFrame
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from haversine import Unit
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Butuan Tourism",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown(
    """
    <style>
    .main {
        background-color:  #042a53 !important;
        color: white !important;
    }
    
    .css-hby737 {
        background-color:  #23446c !important;
        color: white !important;
    }
    
    .css-1v0mbdj {
        margin-left: 25%;
    }
        
    
    
    .css-1ubkpyc {
        background-color: #23446c !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)



image = Image.open('butuan-logo.png')
st.sidebar.image(image, caption='', width=120)
st.sidebar.markdown('<h1 style="margin-left:15%; margin-bottom: 10%; color:white">2021 Sparta Butuan City Hackathon</h1>', unsafe_allow_html=True)


data = pd.read_csv('Places - View Point.csv')
data = data[data['Type'].isin(['View Point', 'Picnic Site/Park', 'Historical', 'Hiking', 'Park',
                                  'Museum', 'Park/Social Activities', 'Falls', 'Garden, Zoo',
                                  'Church', 'Garden', 'Relic Site', 'River', 'Distillery', 'Farm',
                                  'Forest', 'Water Park'])]

topic_type = st.sidebar.selectbox(
    'Topics',
    ("Tourism", "Safe Space Underprivileged", "Child Vulnerability"))
    

def get_distance(loc1, loc2):
    orig = ox.get_nearest_node(G, loc1)
    dest = ox.get_nearest_node(G, loc2)

    route2 = nx.shortest_path(G, orig, dest, weight='travel_time')
    route2_time = int(sum(ox.utils_graph.get_route_edge_attributes(G, route2, 'travel_time')))
    
    return route2_time

if topic_type == 'Tourism':
    data = pd.read_csv('Places - View Point.csv')
    data = data.dropna(subset=['Lat'])
    genre = st.sidebar.radio("", ('Introduction', 'Map', 'Recommender Engine'))
    
    
    if genre == 'Introduction':
        st.markdown('<h1 style="margin-bottom: 2%; color:white">Introduction</h1>', unsafe_allow_html=True)
        st.markdown('<h3>Upholding tourism in the midst of pandemic using data and technology</h3>', unsafe_allow_html=True)
    elif genre == 'Map':
        st.markdown('<h1 style="margin-bottom: 2%; color:white">Tourism Map</h1>', unsafe_allow_html=True)
        selected_options = st.multiselect("Options:",['View Point', 'Picnic Site/Park', 'Historical', 'Hiking', 'Park',
                                  'Museum', 'Park/Social Activities', 'Falls', 'Garden, Zoo',
                                  'Church', 'Garden', 'Relic Site', 'River', 'Distillery', 'Farm',
                                  'Forest', 'Water Park', 'Restaurant'],
                                            ['View Point', 'Picnic Site/Park', 'Historical', 'Hiking', 'Park',
                                  'Museum', 'Park/Social Activities', 'Falls', 'Garden, Zoo',
                                  'Church', 'Garden', 'Relic Site', 'River', 'Distillery', 'Farm',
                                  'Forest', 'Water Park', 'Restaurant'])
        
        if st.button('Search'):
            current_location = (8.936796, 125.521337)
            fig=Figure(height=550,width=750)
            m = folium.Map(location=[current_location[0], current_location[1]],
                                 zoom_start = 11,
                                 tiles='cartodbpositron')

            details = pd.DataFrame()
            ctr = 0
            for _data in data[data['Type'].isin(selected_options)].iterrows():
                ctr +=1
                if _data[1]['Lat'] is not None  and _data[1]['Lon'] is not None:
                    color = 'blue'
                    tag = 'Tourist'
                    if _data[1]['Type'] == 'Restaurant':
                        color= 'orange'
                        tag = 'Restaurant'

                    folium.Marker([_data[1]['Lat'], _data[1]['Lon']],
                                      icon=folium.Icon(color=color, icon='home', prefix='fa'),
                                        tooltip='{}-{}'.format(tag, _data[1]['Name'])
                                     ).add_to(m)


            folium_static(m, width=900)
        
    else:
        source_address = st.selectbox('Current Source', data[data['Type'].isin(['Hotel', 'Lodge', 'Guest House'])]['Name'].unique())
        
        selected_options = st.multiselect("Options:",['View Point', 'Picnic Site/Park', 'Historical', 'Hiking', 'Park',
                                  'Museum', 'Park/Social Activities', 'Falls', 'Garden, Zoo',
                                  'Church', 'Garden', 'Relic Site', 'River', 'Distillery', 'Farm',
                                  'Forest', 'Water Park', 'Restaurant'],
                                            ['View Point', 'Picnic Site/Park', 'Historical', 'Hiking', 'Park',
                                  'Museum', 'Park/Social Activities', 'Falls', 'Garden, Zoo',
                                  'Church', 'Garden', 'Relic Site', 'River', 'Distillery', 'Farm',
                                  'Forest', 'Water Park', 'Restaurant'])
        if st.button('Search'):
            G = joblib.load('overall_graph_driving.sav')
            
            current_location = (data[data['Name']==source_address]['Lat'].iloc[0], data[data['Name']==source_address]['Lon'].iloc[0])
            
            fig=Figure(height=550,width=750)
            m2 = folium.Map(location=[current_location[0], current_location[1]], zoom_start = 14, tiles='cartodbpositron')

            folium.Marker(current_location,
                          icon=folium.plugins.BeautifyIcon(border_color='red',
                                       text_color='red',
                                       number=0,
                                       icon_shape='marker'),
              tooltip='Your Current Location'
            ).add_to(m2)
            
            details = data[data['Type'].isin(selected_options)]
            
            details['current_distance'] = details.apply(lambda x: get_distance(current_location, (x['Lat'], x['Lon'])), axis=1)
            top_10 = details.sort_values('current_distance', ascending=True).head(10)
            
            ctr = 0
            details = pd.DataFrame()
            for _top_10 in top_10.iterrows():
                ctr +=1
                if _top_10[1]['Lat'] is not None  and _top_10[1]['Lon'] is not None:
                    orig = ox.get_nearest_node(G, current_location)
                    dest = ox.get_nearest_node(G, (_top_10[1]['Lat'], _top_10[1]['Lon']))

                    route2 = nx.shortest_path(G, orig, dest, weight='travel_time')
                    route2_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route2, 'length')))
                    route2_time = int(sum(ox.utils_graph.get_route_edge_attributes(G, route2, 'travel_time')))

                    d = {
                         'name':  _top_10[1]['Name'], 'Type ':  _top_10[1]['Type'],
                         'Length': [route2_length], 'Time': [route2_time]
                        }

                    df = pd.DataFrame(data=d)

                    details = pd.concat([details, df])

                    coords_1 = [] 
                    coords_1.append(current_location)
                    for i in route2:
                        point = G.nodes[i]
                        coords_1.append([point['y'], point['x']])

                color = '#5499c7'
                if _top_10[1]['Type'] == 'Restaurant':
                    color= '#d4ac0d'

                coords_1.append([_top_10[1]['Lat'], _top_10[1]['Lon']])

                current_path = nx.shortest_path_length(G, orig, dest, 'travel_time')

                folium.Marker([_top_10[1]['Lat'], _top_10[1]['Lon']],
                                  icon=folium.plugins.BeautifyIcon(border_color=color,
                                               text_color=color,
                                               number=ctr,
                                               icon_shape='marker'),
                                    tooltip=_top_10[1]['Name']
                                 ).add_to(m2)

                folium.PolyLine(coords_1, popup='<b>Path of Vehicle_1</b>',
                                         tooltip='Vehicle_1',
                                         color='#52be80',
                                         weight=2).add_to(m2)


            fig.add_child(m2)
            folium_static(m2, width=900)
            
            details['Length'] = details['Length']/1000
            details['Time'] = details['Time']/60
            details = details.rename(columns={'Length': 'Length (kilometers)', 'Time': 'Time (minutes)'})
            st.write(details.reset_index())
    
elif topic_type == 'Safe Space Underprivileged':
    genre = st.sidebar.radio("", ('Introduction', 'EDA', 'Clustering'))
    if genre == 'Introduction':
        st.markdown('<h1 style="margin-bottom: 2%; color:white">Introduction</h1>', unsafe_allow_html=True)
    elif genre == 'EDA':
        st.markdown('<h1 style="margin-bottom: 2%; color:white">Safe Space Underprivileged Exploratory Data Analysis</h1>', unsafe_allow_html=True)
        gdf = joblib.load('safe-space-gdf.shp')
        gdf = gdf.rename(columns={ 'LAND AREA-SQM': 'LAND_AREA_SQM', 
                                   'POVERTY INCIDENCE LEVEL': 'POVERTY_INCIDENCE_LEVEL',
                                   'DROUGHT SCORE': 'DROUGHT_SCORE', 'FLOODING  % ': 'FLOODING', 
                                   'SEA LEVEL %': 'SEA_LEVEL', 'LANDSLIDE %': 'LANDSLIDE',
                                   'LIQUE-FACTION  %':'LIQUE_FACTION'
                                 })
        
        safe_space_features = st.selectbox('Features', ['POPULATION', 'POVERTY INCIDENCE LEVEL', 
                                                        'DROUGHT SCORE', 'FLOODING  % ', 'SEA LEVEL %', 'LANDSLIDE %', 
                                                        'LIQUE-FACTION  %'])
        
        m = folium.Map(location=[8.946492, 125.544239], zoom_start=10.5, tiles='CartoDB positron')
        
        feature = ''
        row_feature = ''
        if safe_space_features == 'POPULATION':
            feature = 'POPULATION'
        elif safe_space_features == 'POVERTY INCIDENCE LEVEL':
            feature = 'POVERTY_INCIDENCE_LEVEL'
        elif safe_space_features == 'DROUGHT SCORE':
            feature = 'DROUGHT_SCORE'
        elif safe_space_features == 'FLOODING  % ':
            feature = 'FLOODING'
        elif safe_space_features == 'SEA LEVEL %':
            feature = 'SEA_LEVEL'
        elif safe_space_features == 'LANDSLIDE %':
            feature = 'LANDSLIDE'
        elif safe_space_features == 'LIQUE-FACTION  %':
            feature = 'LIQUE_FACTION'
        
        
        for row in gdf.itertuples():
            if safe_space_features == 'POPULATION':
                row_feature = row.POPULATION
            elif safe_space_features == 'POVERTY INCIDENCE LEVEL':
                row_feature = row.POVERTY_INCIDENCE_LEVEL
            elif safe_space_features == 'DROUGHT SCORE':
                row_feature = row.DROUGHT_SCORE
            elif safe_space_features == 'FLOODING  % ':
                row_feature = row.FLOODING
            elif safe_space_features == 'SEA LEVEL %':
                row_feature = row.SEA_LEVEL
            elif safe_space_features == 'LANDSLIDE %':
                row_feature = row.LANDSLIDE
            elif safe_space_features == 'LIQUE-FACTION  %':
                row_feature = row.LIQUE_FACTION
            
            folium.Marker(location=[row.LAT,row.LON], popup='BRGY:{}, {}:{}'.format(
                row.BARANGAY, safe_space_features, row_feature)).add_to(m)
            
        
        folium.Choropleth(
            geo_data=gdf,
            data=gdf,
            columns=['BARANGAY', feature],
            key_on="feature.properties.BARANGAY",
            fill_color='YlGnBu',
            fill_opacity=1,
            line_opacity=0.2,
            legend_name=feature,
            smooth_factor=0,
            Highlight= True,
            line_color = "#0000",
            name = feature,
            show=False,
            overlay=True,
            nan_fill_color = "White"
        ).add_to(m)
        
        folium_static(m, width=900)
    
elif topic_type == 'Child Vulnerability':
    genre = st.sidebar.radio("", ('Introduction', 'Map', 'Recommender Engine'))
    
    