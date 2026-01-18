import tempfile

from pyvis.network import Network
import streamlit as st
import pandas as pd
import altair as alt

import matplotlib.pyplot as plt
from basicplots import get_barchart, get_piechart, getStackedBarChart, getMosaic
from cluster import render_graph, build_graph
from filters import load_data, filter_by_age, filter_by_weight
from upset import getUpsetPlot
from overviewPlots import getOverviewPlots

# Running the Streamlit app
# streamlit run app.py

# Config the settings of the page
st.set_page_config(page_title="Diabetic Medication Analysis Dashboard", page_icon="📊", layout="wide")
st.title("Diabetic Medication Analysis Dashboard")
st.markdown("Analyze medication strategies and their impact on clinical readmission rates.")


# -------------------------------
# 1) Data loading and caching
# -------------------------------

dataframe, medication_column_names_filtered = load_data()


# -------------------------------
# 2) Sidebar controls
# -------------------------------
st.sidebar.title("Filter Options")

st.sidebar.subheader("Patient Demographics")
age_container = st.sidebar.container(border=True)
age_range = age_container.slider(
    "Patient Age",
    min_value=0,
    max_value=100,
    value=(0, 100),
    step=10
)

weight_container = st.sidebar.container(border=True)

weight_range = weight_container.slider(
    "Patient Weight",
    min_value=0,
    max_value=200,
    value=(0, 200),
    step=25
)
include_unknown_weight = weight_container.checkbox("Include unknown", value=True)

age_filtered_df = filter_by_age(dataframe, age_range)
weight_filtered_df = filter_by_weight(age_filtered_df, weight_range, include_unknown_weight)
race_counts = weight_filtered_df['race'].value_counts().reset_index()
filtered_df = weight_filtered_df # variable which is totally filtered # TODO: combine all filters in this variable
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
# 3) Main Graph Views
# -------------------------------
def render_main_view():
    col_left, col_right = st.columns(2)
    with col_left:
        selected_medications = st.multiselect(
            "Select Medications",
            list(medication_column_names_filtered),
            default=['insulin', 'metformin', 'glipizide', 'glyburide', 'rosiglitazone']
        )

    if medication_column_names_filtered.__len__() == 0:
        st.warning("No medications available with more than 100 patients. Please adjust the medication selection.")
        st.stop()
        return
    
    if selected_medications.__len__() == 0:
        st.warning("No medications selected. Please select at least one medication.")
        st.stop()
        return
    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Encounters", f"{filtered_df.shape[0]}", border=True)

    total_readmission_rate = (filtered_df['readmitted'] != 'NO').mean() * 100

    col2.metric("Overall Readmission Rate", f"{total_readmission_rate:.2f}%", border=True)
        
    race_count = get_barchart(race_counts)

    # overview plot
    tab1, tab2 = st.tabs(["Medication Strategy", "Medication Distribution"])

    with tab1:
        st.header("Medication Strategy")
        st.altair_chart(getOverviewPlots(filtered_df, readmission_type, selected_medications))
    with tab2:
        st.header("Medication Distribution")

        upset_plot = getUpsetPlot(age_filtered_df, selected_medications)

        # event = st.altair_chart(upset_plot, use_container_width=False, on_select="rerun")
        event = st.altair_chart(upset_plot)
    # medication chart



    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        st.altair_chart(get_piechart(filtered_df, readmission_type)) # TODO medication filter ?
        st.altair_chart(race_count)


    with col2:
        G = build_graph(filtered_df, min_cooccurrence, readmission_type, selected_medications)

        net = render_graph(G, size_mode)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)

            st.components.v1.html(open(tmp.name).read(), height=800)
        if (selected_medications.__len__() > 1):
            st.altair_chart(getMosaic(filtered_df, readmission_type, selected_medications))
        else:
            st.altair_chart(getStackedBarChart(filtered_df, readmission_type))

render_main_view()
