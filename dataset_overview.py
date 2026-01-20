import streamlit as st
import pandas as pd
import altair as alt


from filters import load_data_full

st.set_page_config(page_title="Dataset Overview", page_icon="📊", layout="wide")

st.title("Dataset Overview")
st.markdown("""
This section provides an overview of the diabetic dataset used for analysis.
""")

with st.expander("Dataset Source"):
    st.markdown("""    
    **Dataset Name:** Diabetes 130-US Hospitals for Years 1999-2008
    
    **Link:** https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
    
    **Citation:** 
    ```
    Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. N. (2014).
    Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records.
    BioMed Research International, 2014(1), 781670. https://doi.org/10.1155/2014/781670
    ```
    
    **License:** Commons Attribution 4.0 International (CC BY 4.0)
    """)

dataframe, medication_column_names_filtered = load_data_full()

st.subheader("Dataset Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Patient Encounters", f"{len(dataframe):,}", border=True)
with col2:
    st.metric("Number of Features", f"{len(dataframe.columns)}", border=True)
with col3:
    st.metric("Number of Medications", f"{len(medication_column_names_filtered)}", border=True)

st.header("Patient Demographics")

demo_col1, demo_col2 = st.columns(2, width="stretch")

with demo_col1:
    gender_counts = dataframe['gender'].value_counts().reset_index()
    gender_counts.columns = ['gender', 'count']

    select = alt.selection_point(fields=['gender'], name='select')

    gender_chart = alt.Chart(gender_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('gender:N', title='Gender'),
        tooltip=['gender', 'count'],
        opacity=alt.condition(select, alt.value(1), alt.value(0.5))
    ).add_params(
        select
    ).properties(
        title='Gender Distribution (click to filter)',
        height=300
    )
    gender_selection = st.altair_chart(gender_chart, on_select="rerun", key="gender_filter")

    filtered_df = dataframe.copy()
    if gender_selection and gender_selection.selection and 'select' in gender_selection.selection:
        points = gender_selection.selection['select']
        if points:
            selected_genders = [p.get('gender') for p in points if 'gender' in p]
            if selected_genders:
                filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]
                st.info(
                    f"Filtered by Gender: {', '.join(selected_genders)} — Showing {len(filtered_df):,} of {len(dataframe):,} encounters")

with demo_col2:
    age_counts = filtered_df['age'].value_counts().reset_index()
    age_counts.columns = ['age', 'count']
    age_order = ['[0-10)', '[10-20)', '[20-30)', '[30-40)', '[40-50)',
                 '[50-60)', '[60-70)', '[70-80)', '[80-90)', '[90-100)']

    age_chart = alt.Chart(age_counts).mark_bar().encode(
        x=alt.X('age:N', sort=age_order, title='Age Range'),
        y=alt.Y('count:Q', title='Number of Encounters'),
        tooltip=['age', 'count']
    ).properties(
        title='Age Distribution',
        height=300
    )
    st.altair_chart(age_chart)

race_counts = filtered_df['race'].value_counts().reset_index()
race_counts.columns = ['race', 'count']

race_chart = alt.Chart(race_counts).mark_bar().encode(
    x=alt.X('race:N', sort='-y', title='Ethnicity'),
    y=alt.Y('count:Q', title='Number of Encounters'),
    tooltip=['race', 'count']
).properties(
    title='Ethnicity Distribution',
    height=500
)

demo_col1, demo_col2 = st.columns(2)
with demo_col1:
    st.altair_chart(race_chart)

st.header("Clinical Outcomes")

outcome_col1, outcome_col2 = st.columns(2)

with outcome_col1:
    readmit_counts = filtered_df['readmitted'].value_counts().reset_index()
    readmit_counts.columns = ['readmitted', 'count']

    readmit_chart = alt.Chart(readmit_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('readmitted:N', title='Readmission Status',
                        scale=alt.Scale(domain=['NO', '<30', '>30'],
                                        range=['#2ecc71', '#e74c3c', '#f39c12'])),
        tooltip=['readmitted', 'count']
    ).properties(
        title='Readmission Distribution',
        height=300
    )
    st.altair_chart(readmit_chart)

with outcome_col2:
    time_counts = filtered_df['time_in_hospital'].value_counts().reset_index()
    time_counts.columns = ['days', 'count']

    time_chart = alt.Chart(time_counts).mark_bar().encode(
        x=alt.X('days:O', title='Days in Hospital'),
        y=alt.Y('count:Q', title='Number of Encounters'),
        tooltip=['days', 'count']
    ).properties(
        title='Length of Hospital Stay',
        height=300
    )
    st.altair_chart(time_chart)

st.header("Healthcare Utilization")

util_col1, util_col2, util_col3 = st.columns(3)

with util_col1:
    # Number of Lab Procedures - precompute bins
    lab_bins = pd.cut(filtered_df['num_lab_procedures'], bins=20)
    lab_counts = lab_bins.value_counts().sort_index().reset_index()
    lab_counts.columns = ['bin', 'count']
    lab_counts['bin_mid'] = lab_counts['bin'].apply(lambda x: x.mid)

    lab_hist = alt.Chart(lab_counts).mark_bar().encode(
        x=alt.X('bin_mid:Q', title='Lab Procedures'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=[alt.Tooltip('bin_mid:Q', title='Lab Procedures', format='.1f'), 'count']
    ).properties(
        title='Lab Procedures Distribution',
        height=250
    )
    st.altair_chart(lab_hist)

with util_col2:
    med_bins = pd.cut(filtered_df['num_medications'], bins=20)
    med_counts = med_bins.value_counts().sort_index().reset_index()
    med_counts.columns = ['bin', 'count']
    med_counts['bin_mid'] = med_counts['bin'].apply(lambda x: x.mid)

    med_hist = alt.Chart(med_counts).mark_bar().encode(
        x=alt.X('bin_mid:Q', title='Medications'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=[alt.Tooltip('bin_mid:Q', title='Medications', format='.1f'), 'count']
    ).properties(
        title='Medications per Encounter',
        height=250
    )
    st.altair_chart(med_hist)

with util_col3:
    diag_counts = filtered_df['number_diagnoses'].value_counts().reset_index()
    diag_counts.columns = ['diagnoses', 'count']

    diag_chart = alt.Chart(diag_counts).mark_bar().encode(
        x=alt.X('diagnoses:O', title='Number of Diagnoses'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=['diagnoses', 'count']
    ).properties(
        title='Diagnoses per Encounter',
        height=250
    )
    st.altair_chart(diag_chart)

st.header("Prior Healthcare Visits")

visit_col1, visit_col2, visit_col3 = st.columns(3)

with visit_col1:
    outpatient_counts = filtered_df['number_outpatient'].clip(upper=10).value_counts().reset_index()
    outpatient_counts.columns = ['visits', 'count']

    outpatient_chart = alt.Chart(outpatient_counts).mark_bar().encode(
        x=alt.X('visits:O', title='Outpatient Visits'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=['visits', 'count']
    ).properties(
        title='Prior Outpatient Visits',
        height=250
    )
    st.altair_chart(outpatient_chart)

with visit_col2:
    emergency_counts = filtered_df['number_emergency'].clip(upper=10).value_counts().reset_index()
    emergency_counts.columns = ['visits', 'count']

    emergency_chart = alt.Chart(emergency_counts).mark_bar().encode(
        x=alt.X('visits:O', title='Emergency Visits'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=['visits', 'count']
    ).properties(
        title='Prior Emergency Visits',
        height=250
    )
    st.altair_chart(emergency_chart)

with visit_col3:
    inpatient_counts = filtered_df['number_inpatient'].clip(upper=10).value_counts().reset_index()
    inpatient_counts.columns = ['visits', 'count']

    inpatient_chart = alt.Chart(inpatient_counts).mark_bar().encode(
        x=alt.X('visits:O', title='Inpatient Visits'),
        y=alt.Y('count:Q', title='Encounters'),
        tooltip=['visits', 'count']
    ).properties(
        title='Prior Inpatient Visits',
        height=250
    )
    st.altair_chart(inpatient_chart)
