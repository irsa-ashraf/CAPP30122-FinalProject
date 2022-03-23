import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import math

from geopy import distance

from amenities_mapper.demographics import import_income, import_demographics
import amenities_mapper.cdp as cdp

def geo_df():
    '''
    Get amenity datasets and convert them to geopandas dataframe.

    Inputs:
        None
    Returns:
        list of geopandas dataframe
    '''
    pd_dfs = cdp.append_pandas()
    rv_lst = []

    for i, df in enumerate(pd_dfs):
        gdf = convert_to_gdf(df)
        rv_lst.append(gdf)

    return rv_lst

def convert_to_gdf(df):
    '''
    Convert pd datafarme to geopandas dataframe. Set CRS for new
    pd datafarme.

    Inputs:
        df: pd dataframe
    Return:
        geopandas dataframe
    '''
    gdf = gpd.GeoDataFrame(df,
                geometry=gpd.points_from_xy(df['lat'], df['lon']))
    gdf = gdf.set_crs('EPSG:26916')
    return gdf

def distance_series(df, point):
    '''
    Calculate the distance between the provided point and each amenity
    in the dataset.

    Inputs:
        point: list of geo-coordinates i.e., [latitude, longtiude]
        df: geopandas dataframe
    Returns:
        pd series
    '''
    lat, long = point
    dist_series = df.apply(lambda x: distance.distance(
                        (x.lat, x.lon),
                        (lat, long)).miles, axis=1)
    return dist_series

def within_distance(point, library, pharmacy, starbucks, murals, walk_dist = 1):
    '''
    Find amenities that are within the specified distance from
    the provided point.

    Inputs:
        point: list of geo-coordinates i.e., [latitude, longtiude]
        library: geopandas dataframe
        pharmacy: geopandas dataframe
        starbucks: geopandas dataframe
        murals: geopandas dataframe
        walking dist (float or int): distance to restrict search
    Returns:
        a tuple of geopandas series
    '''
    lib_dist = distance_series(library, point)
    pharm_dist = distance_series(pharmacy, point)
    sbucks_dist = distance_series(starbucks, point)
    murals_dist = distance_series(murals, point)
    
    lib_dist = lib_dist[lib_dist <= 1]
    pharm_dist = pharm_dist[pharm_dist <= 1]
    sbucks_dist = sbucks_dist[sbucks_dist <= 1]
    murals_dist = murals_dist[murals_dist <= 1]
    
    return lib_dist, pharm_dist, sbucks_dist, murals_dist

def compute_shannon_index(pt, lib, pharm, murals, sbucks):
    '''
    Compute shannon index, which is a measure of the proportion
    of amenities from each category available within a distance.

    Inputs:
        point: list of geo-coordinates i.e., [latitude, longtiude]
        library: geopandas dataframe
        pharmacy: geopandas dataframe
        starbucks: geopandas dataframe
        murals: geopandas dataframe
        walking dist (float or int): distance to restrict search
    Returns:
        shannon index (float)
    '''

    total = lib.shape[0] + pharm.shape[0] + sbucks.shape[0] + murals.shape[0]

    within_dist = within_distance(pt, lib, pharm, sbucks, murals)
    
    score = 0
    
    for amen in within_dist:
        prop = amen.shape[0]/total
        if prop == 0:
            continue
        score += -(prop * math.log(prop))
    if score == 0:
        return None
    return score

def boundary_data():
    '''
    Merge geopandas dataframe containing community area shape info
    with a dataframe that has socio-demographics information

    Inptus: none
    Returns:
        merged geopandas dataframe
    '''
    geojson_file = 'data/Boundaries - Community Areas (current).geojson'
    comm_boundaries = gpd.read_file(geojson_file)
    def cap(st):
        return st.title()
    comm_boundaries['community'] = comm_boundaries.apply(lambda x: cap(x.community), axis = 1)
    comm_boundaries = comm_boundaries.rename(columns = {"community": "neighbor"})
    return comm_boundaries

def choropleth_data():
    '''
    Create dataframes to be used to create choropleth by merging
    geopandas dataframe of community area shapefiles with
    income data and demographics data

    Returns:
        tuple of two geopandas dataframe
    '''
    comm_boundaries = boundary_data()
    income = import_income()
    income = income.loc[:,['neighbor', 'income_per_1000']]
    demo = import_demographics()
    colors = colors_for_choropleth(income, demo)
    demo = demo.loc[:,['neighbor', 'share_BLACK']]
    income_boundaries = pd.merge(comm_boundaries, income, on='neighbor', how='left')
    demo_boundaries = pd.merge(comm_boundaries, demo, on='neighbor', how='left')

    return income_boundaries, demo_boundaries, colors

def colors_for_choropleth(income, demo):
    '''
    Define color settings for choropleths for income data and demographics
    data.

    Input:
        income: geopandas dataframe
        demo: geopandas dataframe
    Returns:
        list of lists where each sublist is a setting for the choropleth
    '''
    rv = []
    rv.append(list(income['income_per_1000'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1])))
    rv.append(['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C'])
    rv.append(list(demo['share_BLACK'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1])))
    rv.append(['#FFD3DE', '#FFBFCF', '#FFACC1', '#FF98B2', '#FF85A3', '#FF7194'])
    return rv