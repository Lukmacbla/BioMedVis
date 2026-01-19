import altair as alt
import pandas as pd

from globals import primary_color
from utils import color_utils
import re


def get_barchart(race_counts, selection):
    highlight_color = "black"  # selected bar color
    default_color = "lightgray"   # unselected bar color

    return (
        alt.Chart(race_counts)
        .mark_bar()
        .encode(
            x='race:N',
            y='count:Q',
            color=alt.condition(selection, alt.value(highlight_color), alt.value(default_color)),
            tooltip=['race:N','count:Q']
        ).properties(width=200, height=500)
        .add_params(selection)
        .properties(title='Patient count per race')
    )

def get_piechart(df, readmission_type, med_cols, race_selection=None):
    keep_cols = med_cols+(["race", "encounter_id", "readmitted"])
    df_work = df[keep_cols].copy()
    df_work[med_cols] = df_work[med_cols].replace("?", pd.NA).replace({"No":0,"Up":1,"Down":1,"Steady":1})
    df_work = df_work[df_work[med_cols].isin([1]).any(axis=1)]
    color_full = primary_color
    color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
    color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

    base = alt.Chart(df_work)
    if readmission_type == "Any":
        color_domain = ["NO", "<30", ">30"]
        color_range = [color_light,color_medium, color_full,]
    else:
        color_domain = ["NO", "<30"]
        color_range = [color_light, color_full]

    # Only add selection    if passed
    if race_selection is not None:
        base = base.add_params(race_selection).transform_filter(race_selection)

    pie_chart = (
        base
        .transform_calculate(
            readmission_label="""
                datum.readmitted == 'NO' ? 'NO' :
                datum.readmitted == '<30' ? '<30' :
                '>30'
            """
        )
        # Aggregation happens after filtering, and we keep race column
        .transform_aggregate(
            count='count()',
            groupby=['readmission_label', 'race']
        )
        .mark_arc()
        .encode(
            theta='count:Q',
            color=alt.Color('readmission_label:N',
                            scale=alt.Scale(domain=color_domain, range=color_range)),
            tooltip=['readmission_label:N','count:Q', 'race:N'],

        )
        .properties(width=500,height=500)
    )

    return pie_chart





def icd9_to_category(code: str) -> str:
    """Map an ICD-9(-CM) diagnosis code (001-999, V, E) to a high-level category."""
    if pd.isna(code):
        return "Unknown"

    code_str = str(code).strip().upper()

    # V codes: factors influencing health status / contact with health services
    if code_str.startswith("V"):
        return "Factors influencing health status / contact with health services"

    # E codes: external causes of injury/poisoning
    if code_str.startswith("E"):
        return "External causes of injury and poisoning"

    # Otherwise treat as numeric 001–999
    m = re.match(r"(\d+)", code_str)
    if not m:
        return "Unknown"
    num = int(m.group(1))

    if 1 <= num <= 139:
        return "Infectious and parasitic"
    elif 140 <= num <= 239:
        return "Neoplasms"
    elif 240 <= num <= 279:
        return "Endocrine, nutritional, metabolic, immunity"
    elif 280 <= num <= 289:
        return "Diseases of the blood"
    elif 290 <= num <= 319:
        return "Mental disorders"
    elif 320 <= num <= 389:
        return "Nervous system and sense organs"
    elif 390 <= num <= 459:
        return "Circulatory system"
    elif 460 <= num <= 519:
        return "Respiratory system"
    elif 520 <= num <= 579:
        return "Digestive system"
    elif 580 <= num <= 629:
        return "Genitourinary system"
    elif 630 <= num <= 679:
        return "Pregnancy, childbirth, puerperium"
    elif 680 <= num <= 709:
        return "Skin and subcutaneous tissue"
    elif 710 <= num <= 739:
        return "Musculoskeletal and connective tissue"
    elif 740 <= num <= 759:
        return "Congenital anomalies"
    elif 760 <= num <= 779:
        return "Perinatal conditions"
    elif 780 <= num <= 799:
        return "Symptoms, signs, ill-defined"
    elif 800 <= num <= 999:
        return "Injury and poisoning"
    else:
        return "Unknown"


def getStackedBarChart(df, readmission_type, race_selection=None):
    # Prep long data that retains 'race' for filtering
    diag_cols = ["diag_1", "diag_2", "diag_3"]

    keep_cols = diag_cols + ["encounter_id", "readmitted", "race"]

    df_work = df.copy()
    df_work[diag_cols] = df_work[diag_cols].replace("?", pd.NA)
    for col in diag_cols:
        df_work[f"{col}_cat"] = df_work[col].apply(icd9_to_category)

    df_long = (
        df_work
        .melt(
            id_vars=["readmitted", "race"],
            value_vars=["diag_1_cat", "diag_2_cat", "diag_3_cat"],
            var_name="diag_position",
            value_name="icd9_category"
        )
        .dropna(subset=["icd9_category"])
    )

    base = alt.Chart(df_long)
    if race_selection is not None:
        base = base.add_params(race_selection).transform_filter(race_selection)
    print(race_selection)
    color_full = primary_color
    color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
    color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

    # Choose color domain and range
    if readmission_type == "Any":
        color_domain = ["NO", "<30", ">30"]
        color_range = [color_light,color_medium, color_full,]
    else:
        color_domain = ["NO", "<30"]
        color_range = [color_light, color_full]

    chart = (
        base
        .mark_bar()
        .encode(
            x=alt.X("icd9_category:N", title="Diagnosis category", sort="-y",
                    axis=alt.Axis(labelLimit=500)),
            # Aggregate in Altair so proportions update when the selection filters
            y=alt.Y("count():Q", title="Proportion of patients", stack="normalize"),
            color=alt.Color("readmitted:N", title="Readmission status",
                            scale=alt.Scale(domain=color_domain, range=color_range)),
            tooltip=[
                alt.Tooltip("icd9_category:N", title="Diagnosis category"),
                alt.Tooltip("readmitted:N", title="Readmitted"),
                alt.Tooltip("count():Q", title="Count")
            ]
        )
        .properties(width=1000, height=500)
    )
    return chart


def getMosaic(df, readmission_type, med_cols, race_selection=None):
    # Map medication statuses to binary "used" indicator
    map_dict = {"No": 0, "Up": 1, "Down": 1, "Steady": 1}

    df_work = df.copy()
    df_work[med_cols] = df_work[med_cols].replace("?", pd.NA).replace(map_dict)

    diag_cols = ["diag_1", "diag_2", "diag_3"]
    df_work[diag_cols] = df_work[diag_cols].replace("?", pd.NA)

    # Derive diagnosis categories
    for col in diag_cols:
        df_work[f"{col}_cat"] = df_work[col].apply(icd9_to_category)

    # Long table that retains 'race' so we can filter by selection
    df_long = (
        df_work
        .melt(
            id_vars=med_cols + ["race"],  # keep race for filtering
            value_vars=["diag_1_cat", "diag_2_cat", "diag_3_cat"],
            var_name="diag_position",
            value_name="diagnosis_category"
        )
        .dropna(subset=["diagnosis_category"])
    )

    # Second melt: turn medication columns into a single 'medication' column with values in 'used'
    df_heat_long = (
        df_long
        .melt(
            id_vars=["diagnosis_category", "race"],
            value_vars=med_cols,
            var_name="medication",
            value_name="used"
        )
        .dropna(subset=["used"])
    )

    # Build chart; filter by race before aggregation, aggregate in Altair
    base = alt.Chart(df_heat_long)
    if race_selection is not None:
        base = base.add_params(race_selection).transform_filter(race_selection)

    heatmap = (
        base
        .mark_rect()
        .encode(
            x=alt.X("diagnosis_category:N", title="Diagnosis category",
                    axis=alt.Axis(labelLimit=500)),
            y=alt.Y("medication:N", title="Medication",
                    axis=alt.Axis(labelLimit=200)),
            # mean(used) ∈ [0,1]; format as percentage in legend and tooltip
            color=alt.Color(
                "mean(used):Q",
                title="Percentage of patients on medication",
                scale=alt.Scale(scheme="darkred", domain=[0, 1]),
                legend=alt.Legend(orient="top", titleLimit=500, format=".0%")
            ),
            tooltip=[
                alt.Tooltip("diagnosis_category:N", title="Diagnosis category"),
                alt.Tooltip("medication:N", title="Medication"),
                alt.Tooltip("mean(used):Q", title="Percentage", format=".1%")
            ]
        )
        .properties(width=1000, height=500)
    )

    return heatmap
