import altair as alt
import pandas as pd

from globals import primary_color
from utils import color_utils, icd9_to_category

color_full = primary_color
color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
color_light = color_utils.desaturate(primary_color, 0.05, 1.0)


def get_barchart(race_counts, selection):
    highlight_color = "black"
    default_color = "lightgray"

    return (
        alt.Chart(race_counts)
        .mark_bar()
        .encode(
            x='race:N',
            y='count:Q',
            color=alt.condition(selection, alt.value(highlight_color), alt.value(default_color)),
            tooltip=['race:N', 'count:Q']
        ).properties(width=150, height=500)
        .add_params(selection)
        .properties(title='Patient count per race')
    )


def get_piechart(df, readmission_type, med_cols, race_selection=None):
    df_work = df.copy()
    df_work[med_cols] = df_work[med_cols].replace("?", pd.NA).replace({"No": 0, "Up": 1, "Down": 1, "Steady": 1})
    df_work = df_work[df_work[med_cols].isin([1]).any(axis=1)]
    color_full = primary_color
    color_medium = color_utils.desaturate(primary_color, 0.4, 1.0)
    color_light = color_utils.desaturate(primary_color, 0.05, 1.0)

    base = alt.Chart(df_work)
    if readmission_type == "Any":
        color_domain = ["NO", "<30", ">30"]
        color_range = [color_light, color_medium, color_full, ]
    else:
        color_domain = ["NO", "<30"]
        color_range = [color_light, color_full]

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
        .transform_aggregate(
            count='count()',
            groupby=['readmission_label', 'race']
        )
        .mark_arc()
        .encode(
            theta='count:Q',
            color=alt.Color('readmission_label:N',
                            scale=alt.Scale(domain=color_domain, range=color_range)),
            tooltip=['readmission_label:N', 'count:Q'],

        )
        .properties(width=500, height=500)
    )
    return pie_chart


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

    chart = (
        base
        .mark_bar()
        .encode(
            x=alt.X("icd9_category:N", title="Diagnosis category", sort="-y",
                    axis=alt.Axis(labelLimit=500)),
            y=alt.Y("sum(count):Q", title="Proportion of patients", stack="normalize"),
            color=alt.Color("readmitted:N", title="Readmission status",
                            scale=alt.Scale(domain=["NO", "<30"] if readmission_type != "Any" else ["NO", "<30", ">30"],
                                            range=[color_light, color_full] if readmission_type != "Any" else [
                                                color_light, color_medium, color_full])),
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
    diag_cat_cols = ["diag_1_cat", "diag_2_cat", "diag_3_cat"]
    bin_cols = [f"{c}_bin" for c in med_cols]

    map_dict = {"No": 0, "Up": 1, "Down": 1, "Steady": 1}
    diag_cols = ["diag_1", "diag_2", "diag_3"]
    used_cols = med_cols + ["race"] + diag_cols
    df_work = df.copy()
    df_work[med_cols] = df_work[med_cols].replace("?", pd.NA).replace(map_dict)

    df_diag_long = (
        df.melt(
            id_vars=["race"] + bin_cols,
            value_vars=diag_cat_cols,
            var_name="diag_position",
            value_name="diagnosis_category"
        )
        .dropna(subset=["diagnosis_category"])
    )

    agg_means = df_diag_long.groupby(["race", "diagnosis_category"], as_index=False)[bin_cols].mean()
    agg_counts = (
        df_diag_long.groupby(["race", "diagnosis_category"], as_index=False)
        .size().rename(columns={"size": "n"})
    )
    agg = agg_means.merge(agg_counts, on=["race", "diagnosis_category"], how="left")

    agg_long = agg.melt(
        id_vars=["race", "diagnosis_category", "n"],
        value_vars=bin_cols,
        var_name="med_bin",
        value_name="mean_used"
    )

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
