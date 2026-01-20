import tempfile

import streamlit as st
import pandas as pd
import altair as alt

from basicplots import get_barchart, get_piechart, getStackedBarChart, getMosaic
from cluster import render_graph, build_graph
from filters import load_data, prepare_df, filter_all
from upset import getUpsetPlot
from overviewPlots import getOverviewPlots


# Running the Streamlit app
# streamlit run app.py

def main():
    st.set_page_config(page_title="Diabetic Medication Analysis Dashboard", page_icon="📊", layout="wide")
    st.title("Diabetic Medication Analysis Dashboard")
    st.markdown("Analyze medication strategies and their impact on clinical readmission rates.")

    dataframe, medication_column_names_filtered = load_data()
    df_prep = prepare_df(dataframe, med_cols_all=medication_column_names_filtered)

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
    readmission_type = st.sidebar.radio(
        "Readmission definition",
        ["Any", "<30 days only"]
    )

    filtered_df = filter_all(
        df_prep,
        age_range=age_range,
        weight_range=weight_range,
        include_unknown_weight=include_unknown_weight,
        readmission_type=readmission_type
    )

    race_counts = filtered_df['race'].value_counts().reset_index()
    race_counts.columns = ['race', 'count']  # rename columns for Altair

    race_selection = alt.selection_point(fields=['race'], toggle=True)

    cluster_container = st.sidebar.container(border=True)
    with cluster_container:
        st.header("Medication Clusters")
    min_cooccurrence = cluster_container.slider(
        "Minimum co-occurrence",
        min_value=10,
        max_value=500,
        value=50,
        step=10
    )

    size_mode = cluster_container.radio(
        "Node size represents",
        ["Medication frequency", "Readmission risk"]
    )

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

        with col3:
            st.metric("Number of Features", f"{len(dataframe.columns)}", border=True,
                      help="Some features from the original dataset were removed during preprocessing.")
        with col4:
            st.metric("Selected Medications", f"{len(selected_medications)}", border=True,
                      help="Medications with low occurrence were excluded.")

        race_count = get_barchart(race_counts, race_selection)

        col1, col2 = st.columns(2)
        # overview plot
        tab1, tab2 = col1.tabs(["Medication Strategy", "Medication Distribution"])

        with tab1:
            st.header("Medication Strategy")
            st.altair_chart(getOverviewPlots(filtered_df, readmission_type, selected_medications))
        with tab2:
            st.header("Medication Distribution")
            if selected_medications.__len__() > 6:
                st.warning("There are too many medications selected. Please select a maximum of 6 medications.")
            else:
                upset_plot = getUpsetPlot(filtered_df, selected_medications)

                st.altair_chart(upset_plot)

        stacked_bar_chart = getStackedBarChart(filtered_df, readmission_type, race_selection=race_selection)

        @st.cache_data(show_spinner=True, max_entries=8)
        def cached_build_graph(df, min_cooccurrence, readmission_type, selected_meds):
            G = build_graph(df, min_cooccurrence, readmission_type, selected_meds)
            return G

        with col2:
            st.header("Medication Clusters")
            if st.toggle("Show clusters", value=False):
                with st.spinner("Building cluster graph..."):
                    G = cached_build_graph(filtered_df, min_cooccurrence, readmission_type, selected_medications)
                    net = render_graph(G, size_mode)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                        net.save_graph(tmp.name)
                        st.components.v1.html(open(tmp.name).read(), height=800)

        race_count = race_count + alt.Chart(pd.DataFrame({'dummy': [0]})).mark_point(opacity=0)
        pie_chart = get_piechart(filtered_df, readmission_type, selected_medications, race_selection=race_selection)

        if (selected_medications.__len__() > 1):
            st.altair_chart((race_count | pie_chart | getMosaic(filtered_df, readmission_type, selected_medications,
                                                                race_selection=race_selection)).resolve_scale(
                color='independent'), use_container_width=True)
        else:
            st.altair_chart((race_count | pie_chart | stacked_bar_chart).resolve_scale(color='shared'),
                            use_container_width=True)

    render_main_view()


pages = {
    "Navigation": [
        st.Page("dataset_overview.py", title="Dataset Overview"),
        st.Page(main, title="Medication Analysis"),
        st.Page("correlations.py", title="Relations of Key Metrics"),
    ]
}

pg = st.navigation(pages)
pg.run()
