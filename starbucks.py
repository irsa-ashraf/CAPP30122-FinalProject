import requests
import pandas as pd
import json
import amenities_mapper.map_util as mu

API = "BcNrdvBLg1ZFWdTWKfTBxmu48ehAXPGM"

def go():
    '''
    Returns a list of dictionaries with geographic information about a Starbucks location.
    Inputs: None
    Outputs: list of dictionaries
    '''

    zips = ['60290', '60601', '60602', '60603', '60604', '60605', '60606',
            '60607', '60608', '60610', '60611', '60614', '60615', '60618',
            '60619', '60622', '60623', '60624', '60628', '60609', '60612',
            '60613', '60616', '60617', '60620', '60621', '60625', '60626',
            '60629', '60630', '60632', '60636', '60637', '60631', '60633',
            '60634', '60635', '60638', '60641', '60642', '60643', '60646',
            '60652', '60653', '60656', '60660', '60661', '60664', '60639',
            '60640', '60644', '60645', '60649', '60651', '60654', '60655',
            '60657', '60659', '60666', '60668', '60673', '60677', '60669',
            '60670', '60674', '60675', '60678', '60680', '60681', '60682',
            '60686', '60687', '60688', '60689', '60694', '60695', '60697',
            '60699', '60684', '60685', '60690', '60691', '60693', '60696',
            '60701', '60707', '60018', '60647', '60627']

    cafe_dicts = get_long_lat(zips)
    return cafe_dicts

def starbucks_df():
    '''
    Convert list of dictionaries of starbucks to a geopandas dataframe.

    Inputs: None
    Returns:
        geopandas dataframe
    '''
    cafe_dicts = go()
    sbucks = pd.DataFrame(cafe_dicts)
    sbucks = mu.convert_to_gdf(sbucks)
    return sbucks

def get_long_lat(zips):
    '''
    Takes a list of ZIP codes and makes an API request. Returns geographical
        info for each Starbucks within that ZIP code.
    Inputs:
        list of ZIP codes
    Returns:
        dictionary of Starbucks
    '''

    seen = set()
    cafe_dicts = []
    for zipcode in zips:
        url = gen_url(zipcode)
        req = requests.get(url)
        data_json = json.loads(req.text)
        if data_json:
            for cafe in data_json:
                if (cafe['lat'], cafe['lon']) not in seen:
                    one_cafe = {}
                    one_cafe['tooltip'] = format_location(cafe['display_name'])
                    one_cafe['lat'] = cafe['lat']
                    one_cafe['lon'] = cafe['lon']
                    one_cafe['color'] = 'green'
                    cafe_dicts.append(one_cafe)
                    seen.add((cafe['lat'], cafe['lon']))
    return cafe_dicts


def gen_url(zipcode):
    '''
    Formats a URL to create an API request.
    Inputs:
        zipcode (string)
    Returns:
        URL (string)
    '''
    return (f"http://open.mapquestapi.com/nominatim/v1/search.php?key={API}&format" +
                f"=json&q=starbucks+chicago+{zipcode}+[cafe]&addressdetails=1&limit=10")


def format_location(display_name):
    '''
    Formats the name of a Starbucks location.
    Inputs:
        display_name (string)
    Returns:
        formatted name (string)
    '''

    split = display_name.split(',')
    if any(char.isdigit() for char in split[1]):
        name = split[2].strip()
        idx = 2
    else:
        name = split[1].strip()
        idx = 1
    return name + ',' + split[idx + 1] + ', (Starbucks)'
