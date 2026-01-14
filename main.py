import streamlit as st
import pandas as pd
import altair as alt

from basicplots import get_barchart
from filters import load_data, filter_by_age
from upset import getUpsetPlot

# Running the Streamlit app
# streamlit run app.py

# Config the settings of the page
st.set_page_config(page_title="Streamlit Tutorial", page_icon="📊", layout="wide")
st.title("🐧 Palmer's Penguins")
st.markdown("Use this Streamlit app to make your own scatterplot about penguins!")


# -------------------------------
# 1) Data loading and cached
# -------------------------------



dataframe = load_data()
# st.dataframe(penguins)


# -------------------------------
# 2) Sidebar controls
# -------------------------------
st.sidebar.title("Selectors")
selected_ages = st.sidebar.multiselect(
    "age",
    dataframe["age"].unique(),
    default=list(set(dataframe['age']))
)

# -------------------------------
# 3) Scatterplot with brush selection
# -------------------------------
# Create a simple scatterplot with brush selection

# Plot the altair chart on Streamlit app

age_filtered_df = filter_by_age(dataframe, selected_ages)


race_counts = age_filtered_df['race'].value_counts().reset_index()
race_counts.columns = ['race', 'count']  # rename columns for Altair

tab1, tab2 = st.tabs(["Medication Strategy", "Distribution"])

with tab1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
with tab2:
    st.header("Medication Distribution")

    upset_plot = getUpsetPlot(age_filtered_df)

    # event = st.altair_chart(upset_plot, use_container_width=False, on_select="rerun")
    event = st.altair_chart(upset_plot)
    

# -------------------------------
# 4) Cross-filter on the bar chart
# -------------------------------
# Filter the dataset after selection
def filtered_table(event):
    selection = event['selection']['brush']

    # 0. Prevent an error if selection object is None or empty.
    if selection == dict():
        return dataframe

    # 1. Create a query string to filter the data
    query = ' & '.join(
        f'{crange[0]} <= `{col}` <= {crange[1]}'
        for col, crange in selection.items())

    df = dataframe.query(query)

    # 2. Filter the penguin data frame from the query
    #df = penguins[penguins['species'].isin(species)].query(query)

    # 3. Add the DataFrame pane that render pandas object
    return df


#filtered = filtered_table(event)

# Add graphs
race_count = get_barchart(race_counts)

st.altair_chart(race_count)