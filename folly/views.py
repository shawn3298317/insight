from django.shortcuts import render
from django.http import HttpResponse

from pymongo import MongoClient

import pandas as pd
import numpy as np
import folium
import json

import collections
from folium.plugins import HeatMap

def get_colors(N):
    """
    Params :
        N : integer
            Number of colors needed
    Returns :
        colors : list
            List of randomly generated colors
    """
    colors=[]
    for i in range(0,N):
        colors.append('#{:06x}'.format(np.random.randint(0, 256**3)))
    return colors

def draw_clusters_on_map(df,labels,base_latitude,base_longitude):
    """
    Params :
        df : pandas dataframe
            normalized data
        labels : string list
            labels of crimes
        base_latitude : float
                latitude of map center
        base_longitude : float
                longitude of map center
    Returns :
        map : HTML code
            Folium object rendered as html
    """
    map_clusters = folium.Map(location=[base_latitude, base_longitude], zoom_start=11)

    # set color scheme for the clusters
    k=len(labels)
    count=collections.Counter(df['reason'].values)
    total=len(df['reason'].values)
    rainbow=get_colors(k)
    for cluster in range(0,k):
        group = folium.FeatureGroup(name='<span style=\\"color: {0};\\">{1}</span>'.format(rainbow[cluster-1],labels[cluster]+" ("+str(count[cluster]/total)+"%)"))
        for lat, lon,label in zip(df['latitude'], df['longitude'], df['reason']):
            if int(label) == cluster:
                label = folium.Popup('Clustering ' + str(labels[cluster]), parse_html=True)
                folium.CircleMarker(
                    (lat, lon),
                    radius=5,
                    popup=label,
                    color=rainbow[cluster-1],
                    fill=True,
                    fill_color=rainbow[cluster-1],
                    fill_opacity=0.7).add_to(group)
        group.add_to(map_clusters)

    folium.map.LayerControl('topright', collapsed=False).add_to(map_clusters)
    # map_clusters.save(outfile=map_name+".html")
    return map_clusters._repr_html_()

def get_random_dataframe(base_latitude, base_longitude, labels, num_examples, columns):
    """
    Params :
        base_latitude : float
                latitude of map center
        base_longitude : float
                longitude of map center
        labels : string list
            labels of crimes
        num_examples : int
            number of examples to be generated
        columns : string list
            column names of data frame
    Returns :
        df : pandas dataframe
            data
    """
    num_labels=len(labels)
    geo_data=np.random.randint(0,1000,size=(num_examples, 2))/10000
    geo_data[:,0]+=base_latitude
    geo_data[:,1]=base_longitude-geo_data[:,1]

    labels_data=np.random.randint(0,num_labels,size=(num_examples, 1))
    data=np.column_stack((geo_data,labels_data))

    df = pd.DataFrame(data, columns=columns)
    df[columns[len(columns)-1]]=df[columns[len(columns)-1]].astype(int)
    return df

def heat_map(df,base_latitude, base_longitude):
    """
    Params :
        df : pandas dataframe
            data
        base_latitude : float
                latitude of map center
        base_longitude : float
                longitude of map center
    Returns :
    map : HTML code
            Folium object rendered as html
    """
    base_map = folium.Map(location=[base_latitude, base_longitude], zoom_start=11)
    HeatMap(data=df[["latitude", "longitude" , "reason"]].groupby(["latitude", "longitude"]).mean().reset_index().values.tolist(),
    radius=8, max_zoom=13).add_to(base_map)
    return base_map._repr_html_()

def get_datafromdb(data,columns, labels):
    """
    Params :
        data : MongoDB object
                patient data
        columns : string list
            column names of data frame
        labels : string list
            list of crime types
    Returns :
        df : pandas dataframe
            data
    """ 
    mappingdict = {}
    for i,label in enumerate(labels):
        mappingdict.update({label:i})

    df= pd.DataFrame(columns=columns)
    for dat in data:
        if(dat):
            df2=pd.DataFrame(dat,index=[0])
            df2=df2[columns]
            df2['reason']=mappingdict[df2['reason'].values[0]]
            # print(df2)
            df=df.append(df2, ignore_index=True)
    df['reason']=df['reason'].astype(int)
    return df

def driver_code(category,base_latitude,base_longitude, data):
    """
    Params to get : labels, columns, num_examples, df
    testing the folium code
    """
    assert type(base_latitude) is float and type(base_longitude) is float and type(category) is int
    

    labels=np.array(['Drugs','Domestic Violence','Car accidents','Guns'])

    columns=np.array(['latitude','longitude','reason'])
    
    # num_examples=100  
    # df=get_random_dataframe(base_latitude, base_longitude, labels, num_examples, columns)

    df= get_datafromdb(data, columns, labels)
    # print(df.values)
    if(category==0):
        return draw_clusters_on_map(df,labels,base_latitude,base_longitude)
    elif(category==1):
        return heat_map(df,base_latitude, base_longitude)
    pass
def index(request):
    # Boston coordinates
    # base_latitude = 42.3397
    # base_longitude = -71.1352

    category = int(request.GET.get("category")) # 0: cluster_map 1: heat_map
    time_start = request.GET.get("time_st")
    time_end = request.GET.get("time_end")

    center_lat = float(request.GET.get("c_lat"))
    center_long = float(request.GET.get("c_long"))

    client = MongoClient("mongodb+srv://insight:insight@cluster0-ixccp.mongodb.net/test?retryWrites=true&w=majority")
    table = client.hacked.er_patient_data
    data = table.find({})
    # print(data[0]['longitude'])
    return HttpResponse(driver_code(category, center_lat, center_long, data))

