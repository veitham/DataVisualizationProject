import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil
import pydeck as pdk

def count_rows(rows): 
    return len(rows)

def getDate(month_and_year):
    months = ['january','february','march','april','may','june','july','august','september','october','november','december']
    i = 0
    m = ''
    # getting the year
    l = len(month_and_year)
    year = month_and_year[l-4:l]

    #substring the written month from the month_and_year
    while(month_and_year[i] != ' '):
        m = m + month_and_year[i]
        i+=1
   
    # getting the index of that month
    if m in months:
        j=1
        for e in months:
            if(e == m): 
                month = j
            j+=1
    else:
        print('error')
    
    if(len(str(month)) == 2):
        return (str(year) + '-' + str(month))
    else:
        return (str(year) + '-0' + str(month))

st.write('Matthieu Andreani DS3')
st.title('My Trips')

#import data
path = 'map_data.csv'
map_data = pd.read_csv(path)

#slider widget to select the date range of the data
start_date, end_date = st.select_slider(
    'Select the date range:',
    options=[
        'october 2018','november 2018','december 2018', #2018
        'january 2019','february 2019','march 2019','april 2019','may 2019','june 2019','july 2019','august 2019','september 2019','october 2019','november 2019','december 2019', #2019
        'january 2020','february 2020','march 2020','april 2020','may 2020','june 2020','july 2020','august 2020','september 2020','october 2020','november 2020','december 2020', #2020
        'january 2021','february 2021','march 2021','april 2021','may 2021','june 2021','july 2021','august 2021','september 2021' #2021
    ],
    value=('october 2018', 'september 2021')
    )

#select greater than the start date and smaller than the end date
sd = getDate(start_date)+'-01'
ed = getDate(end_date)+'-31'
mask = (map_data['start_date'] >= sd) & (map_data['start_date'] <= ed)
selected_map_data = map_data.loc[mask]

#Dataframe
h = 'Date : '+ start_date+ ' to '+ end_date
st.header(h)
st.subheader('Selected data:')

st.dataframe(selected_map_data)
st.write('Size:',selected_map_data.shape[0],'rows and ',selected_map_data.shape[1],'columns')

#Frequency by Day of month
st.subheader('Frequency by Day of month')

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.hist(selected_map_data['start_dom'],bins = 30, rwidth=0.8, range=(0.5,30.5),color = "#f76363")
plt.xticks(range(1, 31))
plt.xlabel('Date of the month')
plt.ylabel('Frequency')
st.pyplot(fig1)

#Frequency by Day of month
st.subheader('Frequency by Hour')

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.hist(selected_map_data['start_hour'],bins = 24, rwidth=0.8, range=(0.5,24.5),color='#73adff')
plt.xticks(range(0, 25))
plt.xlabel('Hour of the day')
plt.ylabel('Frequency')
st.pyplot(fig2)

#Frequency by Day of Week
st.subheader('Frequency by Day of the Week')

fig3, ax3 = plt.subplots(figsize = (10,5))
ax3.hist(selected_map_data['start_weekday'], bins = 7, rwidth = 0.8, range = (-.5, 6.5),color='#6dff6b')
plt.xlabel('Day of the week')
plt.ylabel('Frequency')
plt.xticks(np.arange(7), 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split())
st.pyplot(fig3)

#Heatmap of the day of the week in comparison to the hour
st.subheader('Heatmap of the day of the week in comparison to the hour')
weekday_by_hour = selected_map_data.groupby(['start_weekday', 'start_hour']).apply(count_rows).unstack()

fig4, ax4 = plt.subplots(figsize = (10,5))
sns.heatmap(weekday_by_hour, linewidths = .5)
#Annoted heatmap
ax4.set_yticklabels(('Mon Tue Wed Thu Fri Sat Sun').split(), rotation='horizontal')
plt.xlabel('Hour')
plt.ylabel('Day of the week')
st.pyplot(fig4)

#Frequency by Place
st.subheader('Frequency by Place')

places = selected_map_data.groupby(['name']).apply(count_rows)
places = places.sort_values(ascending=False)
places = places.to_frame()

#percentage of the visited places
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(places.index[0], str(ceil((places[0][0]/selected_map_data.shape[0])*100))+'%')
col2.metric(places.index[1], str(ceil((places[0][1]/selected_map_data.shape[0])*100))+'%')
col3.metric(places.index[2], str(ceil((places[0][2]/selected_map_data.shape[0])*100))+'%')
col4.metric(places.index[3], str(ceil((places[0][3]/selected_map_data.shape[0])*100))+'%')
col5.metric(places.index[4], str(ceil((places[0][4]/selected_map_data.shape[0])*100))+'%')



#Maps
#select the gps data
gps_data = pd.DataFrame()
gps_data['lat'] = selected_map_data['lat']
gps_data['lon'] = selected_map_data['lon']

#2D Map
st.subheader('2D Map')
st.map(gps_data)

#3D Map
st.subheader('3D Map')

#select size of hexs
st.write('Select the size of the hexagon bins:')
size = st.slider('bin size', 1,1000,500)

layer = pdk.Layer(
    'HexagonLayer',
    gps_data,
    get_position=['lon', 'lat'],
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    elevation_range=[100, 2000],
    extruded=True,
    coverage=1,
    radius=size)

view_state = pdk.ViewState(
    longitude=2.3845,
    latitude=48.8463,
    zoom=6,
    min_zoom=0,
    max_zoom=15,
    pitch=40.5,
    bearing=-27.36)

r = pdk.Deck(layers=[layer], initial_view_state=view_state)
st.pydeck_chart(r)

