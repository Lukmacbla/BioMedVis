import streamlit as st
import pandas as pd
import altair as alt

from filters import load_data_full
from globals import primary_color
from utils import color_utils

color_full = primary_color
color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

st.set_page_config(page_title="Correlations", page_icon="📊", layout="wide")

st.title("Relations of Key Metrics")
st.markdown("""
This section explores correlations between different metrics and their impact on patient readmission rates.
Data on this page includes a random subset of 10,000 records for performance reasons.
""")


# Cached preprocessing function
@st.cache_data(show_spinner="Loading and preprocessing data...")
def load_and_preprocess_data(sample_size=10000):
    dataframe, medication_column_names_filtered = load_data_full()

    if len(dataframe) > sample_size:
        dataframe = dataframe.sample(n=sample_size, random_state=42)

    def age_to_midpoint(age_str):
        if pd.isna(age_str):
            return None
        age_str = str(age_str).strip()
        if age_str.startswith('[') and '-' in age_str:
            parts = age_str.strip('[]()').split('-')
            try:
                lower = int(parts[0])
                upper = int(parts[1])
                return (lower + upper) / 2
            except:
                return None
        return None

    dataframe['age_midpoint'] = dataframe['age'].apply(age_to_midpoint)

    columns_to_keep = [
        'readmitted',
        'time_in_hospital',
        'num_lab_procedures',
        'num_procedures',
        'num_medications',
        'age',
        'gender',
        'age_midpoint'
    ]

    dataframe_filtered = dataframe[columns_to_keep].copy()

    return dataframe_filtered


dataframe = load_and_preprocess_data()

brush = alt.selection_interval(bind='scales', name='brush')

readmission_colors = alt.Scale(
    domain=['NO', '<30', '>30'],
    range=[color_light, color_medium, color_full]
)

st.header("Relations between Metrics and Readmission Rates")
st.caption(
    "Scroll to zoom into the data. Double-click to reset zoom. Point size indicates number of encounters. Color shows readmission rate at that location.")

SCATTER_HEIGHT = 450


def create_scatter_aggregated(data, x_field, y_field, x_title, y_title, title):
    agg_data = data.groupby([x_field, y_field, 'readmitted']).size().reset_index(name='count')

    location_stats = agg_data.groupby([x_field, y_field]).agg({
        'count': 'sum'
    }).reset_index()
    location_stats.rename(columns={'count': 'total_count'}, inplace=True)

    readmit_pivot = agg_data.pivot_table(
        index=[x_field, y_field],
        columns='readmitted',
        values='count',
        fill_value=0
    ).reset_index()

    location_stats = location_stats.merge(readmit_pivot, on=[x_field, y_field])

    if '<30' in location_stats.columns and '>30' in location_stats.columns:
        location_stats['readmission_rate'] = (
                (location_stats['<30'] + location_stats['>30']) / location_stats['total_count'] * 100
        )
    else:
        location_stats['readmission_rate'] = 0

    location_stats['NO_pct'] = (location_stats.get('NO', 0) / location_stats['total_count'] * 100).round(1)
    location_stats['<30_pct'] = (location_stats.get('<30', 0) / location_stats['total_count'] * 100).round(1)
    location_stats['>30_pct'] = (location_stats.get('>30', 0) / location_stats['total_count'] * 100).round(1)

    return alt.Chart(location_stats).mark_circle(opacity=0.8, stroke='white', strokeWidth=0.5).encode(
        x=alt.X(f'{x_field}:Q', title=x_title, scale=alt.Scale(zero=False)),
        y=alt.Y(f'{y_field}:Q', title=y_title, scale=alt.Scale(zero=False)),
        size=alt.Size('total_count:Q',
                      title='Number of Encounters',
                      scale=alt.Scale(range=[30, 1000]),
                      legend=alt.Legend(orient='bottom')),
        color=alt.Color('readmission_rate:Q',
                        title='Readmission Rate (%)',
                        scale=alt.Scale(scheme='redyellowgreen', domain=[60, 0], reverse=False),
                        legend=alt.Legend(orient='right')),
        tooltip=[
            alt.Tooltip(f'{x_field}:Q', title=x_title),
            alt.Tooltip(f'{y_field}:Q', title=y_title),
            alt.Tooltip('total_count:Q', title='Total Encounters', format=','),
            alt.Tooltip('readmission_rate:Q', title='Readmission Rate (%)', format='.1f'),
            alt.Tooltip('NO_pct:Q', title='No Readmit (%)', format='.1f'),
            alt.Tooltip('<30_pct:Q', title='<30 Days (%)', format='.1f'),
            alt.Tooltip('>30_pct:Q', title='>30 Days (%)', format='.1f')
        ]
    ).add_params(
        brush
    ).properties(
        width=350,
        height=SCATTER_HEIGHT,
        title=title
    )


col1, col2 = st.columns(2)

with col1:
    chart1 = create_scatter_aggregated(
        dataframe,
        'num_medications',
        'time_in_hospital',
        'Number of Medications',
        'Days in Hospital',
        'Medication Count vs Hospital Stay'
    )
    st.altair_chart(chart1, use_container_width=True)

with col2:
    chart2 = create_scatter_aggregated(
        dataframe,
        'num_lab_procedures',
        'num_medications',
        'Number of Lab Procedures',
        'Number of Medications',
        'Lab Procedures vs Medications'
    )
    st.altair_chart(chart2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    chart3 = create_scatter_aggregated(
        dataframe,
        'num_procedures',
        'num_medications',
        'Number of Procedures (non-lab)',
        'Number of Medications',
        'Procedures vs Medications'
    )
    st.altair_chart(chart3, use_container_width=True)

with col4:
    age_df = dataframe[dataframe['age_midpoint'].notna()]
    chart4 = create_scatter_aggregated(
        age_df,
        'age_midpoint',
        'num_medications',
        'Age (years)',
        'Number of Medications',
        'Age vs Medication Count'
    )
    st.altair_chart(chart4, use_container_width=True)

st.header("Correlations Summary")

correlations = pd.DataFrame({
    'Correlation': [
        dataframe[['num_medications', 'time_in_hospital']].corr().iloc[0, 1],
        dataframe[['num_lab_procedures', 'num_medications']].corr().iloc[0, 1],
        dataframe[['num_procedures', 'num_medications']].corr().iloc[0, 1],
        dataframe[dataframe['age_midpoint'].notna()][['age_midpoint', 'num_medications']].corr().iloc[0, 1]
    ]
}, index=[
    'Medication Count ↔ Hospital Stay',
    'Lab Procedures ↔ Medications',
    'Procedures ↔ Medications',
    'Age ↔ Medications'
])

col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    st.subheader("Correlation Coefficients")
    st.dataframe(
        correlations.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1).format('{:.3f}'),
        use_container_width=True
    )
    st.caption("Pearson correlation coefficients.")

with col_stat2:
    st.subheader("Key Insights")

    strongest_idx = correlations['Correlation'].abs().idxmax()
    strongest_val = correlations.loc[strongest_idx, 'Correlation']

    st.metric(
        "Strongest Correlation",
        f"{strongest_val:.3f}",
        border=True,
    )

    med_by_readmit = dataframe.groupby('readmitted')['num_medications'].mean()

st.header("Readmission Rate by Medication Count")

dataframe['med_count_bin'] = pd.cut(
    dataframe['num_medications'],
    bins=[0, 5, 10, 15, 20, 100],
    labels=['0-5', '6-10', '11-15', '16-20', '20+']
)

readmit_by_med_bin = dataframe.groupby(['med_count_bin', 'readmitted']).size().reset_index(name='count')

stacked_bar = alt.Chart(readmit_by_med_bin).mark_bar().encode(
    x=alt.X('med_count_bin:N', title='Number of Medications'),
    y=alt.Y('count:Q', title='Number of Encounters', stack='normalize'),
    color=alt.Color('readmitted:N', title='Readmission Status', scale=readmission_colors),
    tooltip=[
        alt.Tooltip('med_count_bin:N', title='Medication Range'),
        alt.Tooltip('readmitted:N', title='Readmission'),
        alt.Tooltip('count:Q', title='Encounters')
    ]
).properties(
    width=600,
    height=300,
    title='Readmission Rate Distribution by Medication Count'
)

st.altair_chart(stacked_bar, use_container_width=True)
