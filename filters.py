import streamlit as st

import pandas as pd


@st.cache_data
def load_data():
    return pd.read_csv("data/diabetic_data.csv")


def filter_by_age(df: pd.DataFrame, age_range: tuple):
    """
    Function to filter by age range.
    """
    min_age, max_age = age_range
    
    def is_in_range(age_str):
        lower_bound = int(age_str.strip('[').split('-')[0])
        return min_age <= lower_bound < max_age
    
    return df[df["age"].apply(is_in_range)]


def filter_by_weight(df: pd.DataFrame, weight_range: tuple, include_unknown=True):
    """
    Function to filter by weight range.
    """

    min_weight, max_weight = weight_range
    
    def is_in_range(weight_str):
        if weight_str == '?':
            return include_unknown
        
        if weight_str == '>200':
            return include_unknown
        
        lower_bound = int(weight_str.strip('[').split('-')[0])
        return min_weight <= lower_bound < max_weight
    
    return df[df["weight"].apply(is_in_range)]


# Function to filter by race
def filter_by_race(df: pd.DataFrame, selected_races: list):
    return df[df["race"].isin(selected_races)]


# Function to apply multiple filters at once
def filter_data(df: pd.DataFrame, selected_ages=None, selected_races=None, selected_islands=None):
    filtered = df.copy()

    if selected_ages is not None:
        filtered = filtered[filtered["age"].isin(selected_ages)]
    if selected_races is not None:
        filtered = filtered[filtered["race"].isin(selected_races)]
    if selected_islands is not None:
        filtered = filtered[filtered["island"].isin(selected_islands)]

    return filtered