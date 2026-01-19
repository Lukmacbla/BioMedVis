import altair as alt
import pandas as pd

from globals import primary_color
from utils import color_utils


def get_barchart(race_counts):
    return alt.Chart(race_counts).mark_bar().encode(
        x='race',  # races on x-axis
        y='count',  # counts on y-axis
        tooltip=['race', 'count']  # hover shows race and count
    ).properties(
        title='Number of patients per race'
    )

def get_piechart(df, readmission_type, med_cols):
    map_dict = {"No": 0, "Up": 1, "Down": 1, "Steady": 1}
    color_full = primary_color
    color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
    color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

    df_work = df.copy()
    df_work[med_cols] = df[med_cols].replace("?", pd.NA)
    df_work[med_cols] = df_work[med_cols].replace(map_dict)

    mask_med_taken = df_work[med_cols].isin([1]).any(axis=1)
    df_work = df_work[mask_med_taken]

    if readmission_type == "Any":
        count_no = (df_work['readmitted'] == 'NO').sum()
        count_short = (df_work['readmitted'] == '<30').sum()
        count_long = (df_work['readmitted'] == '>30').sum()

        readmit_counts = pd.DataFrame({
            "readmitted": ["Never", "<30 days", ">30 days"],
            "count": [count_no, count_short, count_long]
        })

        # Create Altair chart

        def map_readmitted_label(readmitted):
            switch = {
                'No': 'Never',
                '<30': '<30 days',
                '>30': '>30 days'
            }
            return switch.get(readmitted)

        pie_chart = alt.Chart(readmit_counts).mark_arc().encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("readmitted:N", title="Readmission", scale=alt.Scale(domain=["Never", ">30 days", "<30 days"], range=[color_light, color_medium, color_full])),
            tooltip=[alt.Tooltip("readmitted:N", title="Readmission"), alt.Tooltip("count:Q", title="Encounters")]
        ).properties(
            width=400,
            height=400,
            title="Readmission distribution"
        )

        return pie_chart

    else:
        count_no = (df_work['readmitted'] == 'NO').sum()
        count_short = (df_work['readmitted'] == '<30').sum()

        readmit_counts = pd.DataFrame({
            "readmitted": ["No", "<30"],
            "count": [count_no, count_short, ]
        })

        # Create Altair chart

        return (((alt.Chart(readmit_counts).
                  mark_arc()).
        encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("readmitted:N", title="Readmission", scale=alt.Scale(domain=["No", "<30"], range=[color_light, color_full])),
            tooltip=["readmitted", "count"]
        )).
        properties(
            width=400,
            height=400,
            title="Readmission distribution"
        ))


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


def getStackedBarChart(df, readmission_type):
    color_full = primary_color
    color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
    color_light = color_utils.desaturate(primary_color, 0.05, 1.0)
    diag_cols = ["diag_1", "diag_2", "diag_3"]

    df_work = df.copy()
    df_work[diag_cols] = df[diag_cols].replace("?", pd.NA)

    for col in diag_cols:
        df_work[f"{col}_cat"] = df_work[col].apply(icd9_to_category)

    diag_cols = ["diag_1_cat", "diag_2_cat", "diag_3_cat"]
    df_long = (
        df_work
        .melt(
            id_vars=["readmitted"],  # keep readmission status
            value_vars=diag_cols,
            var_name="diag_position",
            value_name="icd9_category"
        )
        .dropna(subset=["icd9_category"])  # ensure no missing diagnosis
    )

    # 2) Count patients per (diagnosis category, readmitted)
    group_counts = (
        df_long
        .groupby(["icd9_category", "readmitted"])
        .size()
        .reset_index(name="count")
    )

    # 3) Compute percentage within each diagnosis category
    group_counts["pct"] = (
        group_counts
        .groupby("icd9_category")["count"]
        .transform(lambda x: x / x.sum())
    )

    if (readmission_type == "Any"):
        chart = (
            alt.Chart(group_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "icd9_category:N",
                    title="Diagnosis category",
                    sort="-y",  # optional: control order
                    axis=alt.Axis(labelLimit=500)
                ),
                y=alt.Y(
                    "sum(pct):Q",
                    title="Proportion of patients",
                    stack="normalize",  # ensures full bar height = 1
                ),
                color=alt.Color(
                    "readmitted:N",
                    title="Readmission status",
                    scale=alt.Scale(domain=["NO", ">30", "<30"], range=[color_light, color_medium, color_full])
                ),
                tooltip=[
                    alt.Tooltip("icd9_category:N", title="Diagnosis category"),
                    alt.Tooltip("readmitted:N", title="Readmitted"),
                    alt.Tooltip("pct:Q", title="Proportion", format=".1%"),
                    alt.Tooltip("count:Q", title="Count")
                ]
            )
            .properties(width=600, height=1000)
        )
    else:
        chart = (
            alt.Chart(group_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "icd9_category:N",
                    title="Diagnosis category",
                    sort="-y",  # optional: control order
                    axis=alt.Axis(labelLimit=500)
                ),
                y=alt.Y(
                    "sum(pct):Q",
                    title="Proportion of patients",
                    stack="normalize",  # ensures full bar height = 1
                ),
                color=alt.Color(
                    "readmitted:N",
                    title="Readmission status",
                    scale=alt.Scale(domain=["NO", "<30"], range=[color_light, color_full])
                ),
                tooltip=[
                    alt.Tooltip("icd9_category:N", title="Diagnosis category"),
                    alt.Tooltip("readmitted:N", title="Readmitted"),
                    alt.Tooltip("pct:Q", title="Proportion", format=".1%")
                ]
            )
            .properties(width=600, height=1000)
        )

    return chart


def getMosaic(df, readmission_type, med_cols):
    map_dict = {"No": 0, "Up": 1, "Down": 1, "Steady": 1}
    df_work = df.copy()
    df_work[med_cols] = df[med_cols].replace("?", pd.NA)
    df_work[med_cols] = df_work[med_cols].replace(map_dict)

    diag_cols = ["diag_1", "diag_2", "diag_3"]
    df_work[diag_cols] = df[diag_cols].replace("?", pd.NA)

    for col in diag_cols:
        df_work[f"{col}_cat"] = df_work[col].apply(icd9_to_category)

    diag_cols = ["diag_1_cat", "diag_2_cat", "diag_3_cat"]
    df_long = (
        df_work
        .melt(
            id_vars=med_cols,
            value_vars=diag_cols,
            var_name="diag_position",
            value_name="diagnosis_category"
        )
        .dropna(subset=["diagnosis_category"])
    )

    heatmap_data = (
        df_long
        .melt(
            id_vars=["diagnosis_category"],
            value_vars=med_cols,
            var_name="medication",
            value_name="used"
        )
        .groupby(["diagnosis_category", "medication"], as_index=False)["used"]
        .mean()
        .rename(columns={"used": "proportion"})
    )
    heatmap_data["percentage"] = heatmap_data["proportion"] * 100

    heatmap = (
        alt.Chart(heatmap_data)
        .mark_rect()
        .encode(
            x=alt.X("diagnosis_category:N", title="Diagnosis category", axis=alt.Axis(labelLimit=500)),
            y=alt.Y("medication:N", title="Medication", axis=alt.Axis(labelLimit=200)),
            color=alt.Color(
                "percentage:Q",
                title="Percentage of patients on medication",
                scale=alt.Scale(scheme="darkred", domain=[0, 100]),
                legend=alt.Legend(orient="top", titleLimit=500)
            ),
            tooltip=[
                alt.Tooltip("diagnosis_category:N", title="Diagnosis category"),
                alt.Tooltip("medication:N", title="Medication"),
                alt.Tooltip("percentage:Q", title="Percentage")
            ]
        )
        .properties()
    )

    return heatmap
