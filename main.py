import tempfile

from pyvis.network import Network
import streamlit as st
import pandas as pd
import altair as alt

import matplotlib.pyplot as plt
from basicplots import get_barchart, get_piechart
from cluster import render_graph, build_graph
from filters import load_data, filter_by_age
from upset import getUpsetPlot
from overviewPlots import getOverviewPlots

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
filtered_df = age_filtered_df # variable which is totally filtered # TODO: combine all filters in this variable
race_counts.columns = ['race', 'count']  # rename columns for Altair



min_cooccurrence = st.sidebar.slider(
    "Minimum co-occurrence",
    min_value=10,
    max_value=500,
    value=50,
    step=10
)
readmission_type = st.sidebar.radio(
    "Readmission definition",
    ["Any", "<30 days only"]
)
size_mode = st.sidebar.radio(
    "Node size represents",
    ["Medication frequency", "Readmission risk"]
)








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






# overview plot
tab1, tab2 = st.tabs(["Medication Strategy", "Medication Distribution"])

with tab1:
    st.header("Medication Strategy")
    st.altair_chart(getOverviewPlots(filtered_df, readmission_type))
with tab2:
    st.header("Medication Distribution")

    upset_plot = getUpsetPlot(age_filtered_df)

    # event = st.altair_chart(upset_plot, use_container_width=False, on_select="rerun")
    event = st.altair_chart(upset_plot)
# medication chart



col1, col2 = st.columns(2)

with col1:
    st.header("Graph 1")
    fig1, ax1 = plt.subplots()
    st.altair_chart(get_piechart(filtered_df, readmission_type))
    ax1.plot([1, 2, 3], [4, 5, 6])
    st.pyplot(fig1)
    st.altair_chart(race_count)

with col2:
    G = build_graph(min_cooccurrence, readmission_type)

    net = render_graph(G, size_mode)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)

        st.header("Graph 2")
        fig2, ax2 = plt.subplots()
        ax2.bar([1, 2, 3], [6, 4, 5])
        st.components.v1.html(open(tmp.name).read(), height=800)
        st.pyplot(fig2)


# Basic plots
