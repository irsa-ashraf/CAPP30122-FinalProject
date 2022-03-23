'''
Import demographic and socioeconomic data from csv
    and convert to Pandas Dataframe.

'''

import pandas as pd

def import_demographics():
    '''
    Import data on racial and population data from csv file
        and save as pandas dataframe.
    Imports:
        - none
    Returns:
        - dem_percents (pandas dataframe): a dataframe with
            neighborhood name, total population, white,
            Black, Asian, other and columns for
            the share of each racial
            category relative to the whole
    '''

    demographics = pd.read_csv("data/Census2020SupplementCCA.csv")
    demographics = demographics.iloc[:,[1,2,6,7,8,9]]

    racial_columns = ["WHITE","BLACK","ASIAN","OTHER"]
    replace_values = {"The Loop" : "Loop", "O'Hare": "Ohare", "McKinley Park" : "Mckinley Park"}

    dem_percents = demographics.copy()

    for column in racial_columns:
        dem_percents["share" + "_" + column] = dem_percents[column]/dem_percents["TOT_POP"]

    dem_percents = dem_percents.rename(columns = {"GEOG": "neighbor"})
    dem_percents = dem_percents.replace({"neighbor" : replace_values})

    return dem_percents


def import_income():
    '''
    Import data on income (socioeconomic status)
         data from csv file
        and save as pandas dataframe.
    Imports:
        - none
    Returns:
        - income (pandas dataframe): a dataframe with
            neighborhood name, per capita income, hardship
            index, and income per capita per 1000 dollars
    '''
    income = pd.read_csv("data/income.csv")
    income = income.iloc[:-1 , :]
    income = income[["COMMUNITY AREA NAME", "PER CAPITA INCOME ", "HARDSHIP INDEX"]]

    replace_values = {"Montclaire" : "Montclare", "Humboldt park" : "Humboldt Park", \
        "McKinley Park" : "Mckinley Park", "Washington Height" : "Washington Heights"}

    income = income.rename(columns = {"PER CAPITA INCOME ": "PER CAPITA INCOME"})
    income["income_per_1000"] = income["PER CAPITA INCOME"]/1000
    income = income.rename(columns = {"COMMUNITY AREA NAME": "neighbor"})
    income = income.replace({"neighbor" : replace_values})

    return income


def combine_dataframes():
    '''
    Combine two pandas dataframes (one for
        demographics and one for socioeconomic
        data) into tuple of the
        dataframes.
    Inputs:
        - none
    Returns:
        - dem_stats (tuple): tuple of demographics and
            income dataframes
    '''
    demographics = import_demographics()
    income = import_income()
    dem_stats = (demographics, income)
    return dem_stats
