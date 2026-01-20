import altair as alt
import pandas as pd

from globals import primary_color
from utils import color_utils
import re

color_full = primary_color
color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

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
        ).properties(width=150, height=500)
        .add_params(selection)
        .properties(title='Patient count per race')
    )

def get_piechart(df, readmission_type, med_cols, race_selection=None):
    used_cols = med_cols + ["readmitted", "race"]
    df_work = df[used_cols].copy()
    df_work[med_cols] = (
        df_work[med_cols]
        .replace("?", pd.NA)
        .replace({"No": 0, "Up": 1, "Down": 1, "Steady": 1})
    )
    # Keep only patients with any med change
    df_work = df_work[df_work[med_cols].isin([1]).any(axis=1)]

    def label(v):
        if v == "NO":
            return "NO"
        elif v == "<30":
            return "<30"
        else:
            return ">30"

    if readmission_type != "Any":
        df_work["readmitted"].replace(">30", "NO", inplace=True)
    df_work["readmission_label"] = df_work["readmitted"].map(label)

    counts = (
        df_work
        .groupby(["race", "readmission_label"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    if readmission_type != "Any":
        counts = counts[counts["readmission_label"].isin(["NO", "<30"])]

    base = alt.Chart(counts)
    if race_selection is not None:
        base = base.add_params(race_selection).transform_filter(race_selection)



    if readmission_type == "Any":
        color_domain = ["NO", "<30", ">30"]
        color_range = [color_light, color_medium, color_full]
    else:
        color_domain = ["NO", "<30"]
        color_range = [color_light, color_full]

    pie_chart = (
        base
        .mark_arc()
        .encode(
            theta="sum(count):Q",
            color=alt.Color("readmission_label:N",
                            scale=alt.Scale(domain=color_domain, range=color_range)),
            tooltip=[
                alt.Tooltip("readmission_label:N"),
                alt.Tooltip("sum(count):Q", title="Count")
            ],
        )
        .properties(width=250, height=350)
    )
    return pie_chart




import pandas as pd
import re

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
    diag_cat_cols = ["diag_1_cat", "diag_2_cat", "diag_3_cat"]
    diag_cols = ["diag_1", "diag_2", "diag_3"]
    used_cols = diag_cols + ["readmitted", "race"]

    df_work = df[used_cols].copy()
    if readmission_type != "Any":
        df_work["readmitted"].replace(">30", "NO", inplace=True)
    df_work[diag_cols] = df_work[diag_cols].replace("?", pd.NA)
    for col in diag_cols:
        df_work[f"{col}_cat"] = df_work[col].apply(icd9_to_category)

    # Long form, then pre-aggregate by race/readmitted/icd9_category
    df_long = (
        df.melt(
            id_vars=["readmitted", "race"],
            value_vars=diag_cat_cols,
            var_name="diag_position",
            value_name="icd9_category"
        )
        .dropna(subset=["icd9_category"])
    )

    counts = (
        df_long
        .groupby(["race", "readmitted", "icd9_category"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    if readmission_type != "Any":
        counts = counts[counts["readmitted"].isin(["NO", "<30"])]

    base = alt.Chart(counts)
    if race_selection is not None:
        base = base.add_params(race_selection).transform_filter(race_selection)

    # colors omitted for brevity; keep your existing scale setup
    chart = (
        base
        .mark_bar()
        .encode(
            x=alt.X("icd9_category:N", title="Diagnosis category", sort="-y",
                    axis=alt.Axis(labelLimit=500)),
            y=alt.Y("sum(count):Q", title="Proportion of patients", stack="normalize"),
            color=alt.Color("readmitted:N", title="Readmission status",
                            scale=alt.Scale(domain=["NO","<30"] if readmission_type!="Any" else ["NO","<30",">30"],
                                            range=[color_light, color_full] if readmission_type!="Any" else [color_light, color_medium, color_full])),
            tooltip=[
                alt.Tooltip("icd9_category:N", title="Diagnosis category"),
                alt.Tooltip("readmitted:N", title="Readmitted"),
                alt.Tooltip("sum(count):Q", title="Count")
            ]
        )
        .properties(width=600, height=350)
    )
    return chart


def getMosaic(df, readmission_type, med_cols, race_selection=None):
    # Use precomputed diagnosis categories and med_bin columns
    diag_cat_cols = ["diag_1_cat", "diag_2_cat", "diag_3_cat"]
    bin_cols = [f"{c}_bin" for c in med_cols]
    # Map medication statuses to binary indicator
    map_dict = {"No": 0, "Up": 1, "Down": 1, "Steady": 1}
    diag_cols = ["diag_1", "diag_2", "diag_3"]
    used_cols = med_cols + ["race"] + diag_cols
    df_work = df.copy()
    df_work[med_cols] = df_work[med_cols].replace("?", pd.NA).replace(map_dict)

    # Long table: 1 row per diagnosis category occurrence
    df_diag_long = (
        df.melt(
            id_vars=["race"] + bin_cols,
            value_vars=diag_cat_cols,
            var_name="diag_position",
            value_name="diagnosis_category"
        )
        .dropna(subset=["diagnosis_category"])
    )

    # Aggregate: mean usage per med by (race, diagnosis_category)
    agg_means = df_diag_long.groupby(["race", "diagnosis_category"], as_index=False)[bin_cols].mean()
    agg_counts = (
        df_diag_long.groupby(["race", "diagnosis_category"], as_index=False)
        .size().rename(columns={"size": "n"})
    )
    agg = agg_means.merge(agg_counts, on=["race", "diagnosis_category"], how="left")

    # Melt back to long
    agg_long = agg.melt(
        id_vars=["race", "diagnosis_category", "n"],
        value_vars=bin_cols,
        var_name="med_bin",
        value_name="mean_used"
    )
    # Recover nice medication names
    agg_long["medication"] = agg_long["med_bin"].str.replace("_bin$", "", regex=True)

    base = alt.Chart(agg_long)

    heatmap = (
        base
        .mark_rect(cursor='default')
        .encode(
            x=alt.X("diagnosis_category:N", title="Diagnosis category", axis=alt.Axis(labelLimit=500)),
            y=alt.Y("medication:N", title="Medication", axis=alt.Axis(labelLimit=200)),
            color=alt.Color("mean_used:Q", title="Percentage of patients on medication",
                            scale=alt.Scale(scheme="darkred", domain=[0, 1]),
                            legend=alt.Legend(orient="top", titleLimit=500, format=".0%")),
            tooltip=[
                alt.Tooltip("diagnosis_category:N", title="Diagnosis category"),
                alt.Tooltip("medication:N", title="Medication"),
                alt.Tooltip("mean_used:Q", title="Percentage", format=".1%"),
                alt.Tooltip("n:Q", title="Patients")
            ]
        )
        .properties(width=600, height=350)
    )

    if race_selection is not None:
        heatmap = heatmap.transform_filter(race_selection)

    return heatmap