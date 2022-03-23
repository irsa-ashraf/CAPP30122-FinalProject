"""
Importing and filtering data on Chicago's
    libraries, pharmacies,
    and murals for use in our software.

"""
import json
from matplotlib.style import library
from sodapy import Socrata
import pandas as pd
import amenities_mapper.starbucks as starbucks


API_KEY = "9Qto0x2IrJoK0BwbM4NSKwpkr"

class DataPortalCollector:

    def __init__(self):
        '''
        Constructor for class.
        Attributes:
            - client: Socrata object that creates
                a connection to the API
        '''

        self.client = Socrata("data.cityofchicago.org", API_KEY)


    def get_libraries(self):
        '''
        Pull the the data on libraries located in
            Chicago from Chicago Open Data Portal
            and save as a pandas dataframe
        Inputs:
            - none
        Returns:
            -  library_df: (pandas dataframe) a
                dataframe with name,
                latitude, longitude, and address of
                all libraries in Chicago
        '''

        results = self.client.get("x8fc-8rcq")
        library_df = pd.DataFrame.from_dict(results)

        return library_df


    def get_pharmacies(self):
        '''
        Pull the data on pharmacies located in Chicago from
            Chicago Open Data Portal
            and save as a pandas dataframe
        Inputs:
            - none
        Returns:
            - pharmacy_df: (pandas dataframe) a dataframe with name,
                latitude, longitude, address, and open/closed status of all
                pharmacies in Chicago
        '''

        results = self.client.get("2et2-5aw3")
        pharmacy_df = pd.DataFrame.from_dict(results)

        return pharmacy_df


    def get_murals(self):
        '''
        Pull the data on murals located in Chicago
            from Chicago Open Data Portal
            and save as a pandas dataframe
        Inputs:
            - none
        Returns:
            - murals_df: (pandas dataframe) a dataframe with name, address,
                latitude and longitude of all murals in Chicago
        '''

        results = self.client.get("we8h-apcf")
        murals_df = pd.DataFrame.from_dict(results)

        return murals_df


def clean_libraries(dpc_class):
    '''
    Gets the library dataframe from the DataPortalCollector class,
        gets latitude and longitude from location, cleans dataframe
            and changes column names.

    Inputs:
        - dpc_class (object): a DataPortalCollector class object
    Returns:
        - library dataframe
    '''

    libs = dpc_class.get_libraries()

    filter_data = libs[["name_", "address", "location"]]

    # split location column up
    split_location_col = \
        [filter_data, pd.DataFrame(filter_data["location"].tolist()).iloc[:, :3]]
    split_location = \
        pd.concat(split_location_col, axis=1).drop(['location', "human_address"], axis=1)

    # change column name
    split_location = \
        split_location.rename(columns \
        = {"name_": "tooltip", "latitude": "lat", "longitude": "lon"})
    split_location["type"] = "library"
    split_location["color"] = "blue"
    split_location["tooltip"] = \
        split_location.apply(lambda x: x.tooltip + ' ({})'.format(x.type), axis= 1)

    return split_location


def clean_pharmacies(dpc_class):
    '''
    Gets the pharmacy dataframe from
        the DataPortalCollector class,
        cleans dataframe and changes column names.

    Inputs:
        - dpc_class (object): a DataPortalCollector class object
    Returns:
        - pharmacies dataframe
    '''

    pharms = dpc_class.get_pharmacies()

    filter_data = pharms[["pharmacy_name", "address", "geocoded_column", "status"]]

    # split location column up into lat/lon
    split_location = pd.concat([filter_data, \
        filter_data["geocoded_column"].apply(pd.Series)], axis=1)
    split_location = split_location[["pharmacy_name", "address", "status", "coordinates"]]
    split_location_list = pd.concat([split_location, \
        split_location["coordinates"].apply(pd.Series)], axis=1)

    # fix coordinate column names
    split_location_list = \
        split_location_list.rename(columns = {0: "longitude", 1: "latitude"})
    condensed = \
        split_location_list[["pharmacy_name", "address", "latitude", "longitude", "status"]]

    # clean status column
    pharms_clean = condensed.copy()
    mask1 = (pharms_clean.status == "Open") | (split_location.status == "OPEN")
    mask2 = pharms_clean.status == "CLOSED"
    mask3 = pharms_clean.status == "Permanently closed"
    column = "status"
    pharms_clean.loc[mask1, column] = "open"
    pharms_clean.loc[mask2, column] = "closed"
    pharms_clean.loc[mask3, column] = "permanently closed"

    # change column name
    pharmacy_data = pharms_clean.rename(columns = \
        {"pharmacy_name": "tooltip", "latitude": "lat", "longitude": "lon"})
    pharmacy_data["type"] = "pharmacy"
    pharmacy_data["color"] = "red"
    pharmacy_data["tooltip"] = \
        pharmacy_data.apply(lambda x: x.tooltip + ' ({})'.format(x.type), axis= 1)

    pharmacy_data.dropna(inplace = True)

    return pharmacy_data


def clean_murals(dpc_class):
    '''
    Gets the murals dataframe from
        the DataPortalCollector class,
        cleans dataframe and changes column names

    Inputs:
        - dpc_class (object): a DataPortalCollector class object
    Returns:
        - murals dataframe
    '''

    murals_df = dpc_class.get_murals()

    murals_df = murals_df[["artwork_title", "street_address", "latitude", "longitude"]]
    murals_df.rename(columns = \
        {"artwork_title":"tooltip", "street_address":"address", \
        "latitude": "lat", "longitude": "lon"},\
         inplace = True)
    murals_df["type"] = "mural"
    murals_df["color"] = "violet"
    murals_df.dropna(inplace = True)
    murals_df["tooltip"] = \
        murals_df.apply(lambda x: x.tooltip + ' ({})'.format(x.type), axis= 1)

    return murals_df


def append_pandas():
    '''
    Instantiates a DataPortalCollector object,
        and runs the above functions
        to clean and return dataframes

    Inputs:
        -none

    Returns:
        - Tuple: tuple containing the three dataframes for
            libraries, pharmacies and murals
    '''
    dpc = DataPortalCollector()

    library_data = clean_libraries(dpc)
    pharmacy_data = clean_pharmacies(dpc)
    murals_data = clean_murals(dpc)

    return (library_data, pharmacy_data, murals_data)

def get_data_dicts():
    '''
    Converts each dataframe to a list of dictionaries

    Inputs:
        - none

    Returns:
        - four lists of dictionaries, for our four dataframes
            (libraries, pharmacies, murals, Starbucks)
    '''

    lib, pharm, mur = append_pandas()

    lib_dict = lib.to_dict('records')
    pharm_dict = pharm.to_dict('records')
    mur_dict = mur.to_dict('records')
    starbucks_dict = starbucks.go()

    return lib_dict, pharm_dict, mur_dict, starbucks_dict
