import streamlit as st

import pandas as pd


# Example: load your data here or pass it in
@st.cache_data
def load_data():
    return pd.read_csv("data/diabetic_data.csv")

# Function to filter by age
def filter_by_age(df: pd.DataFrame, selected_ages: list):
    return df[df["age"].isin(selected_ages)]


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