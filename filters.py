import streamlit as st
import pandas as pd

from utils import icd9_to_category


@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv("data/diabetic_data_smol.csv")

    medication_column_names = df.columns[24 - 17:47 - 17].tolist()
    # medication_column_names = df.columns[24:47].tolist()
    medication_column_names_filtered = [
        c for c in medication_column_names
        if (df[c] != "No").sum() > 100
    ]
    return df, medication_column_names_filtered


@st.cache_data(show_spinner=False)
def load_data_full():
    df = pd.read_csv("data/diabetic_data.csv")

    medication_column_names = df.columns[24 - 17:47 - 17].tolist()
    medication_column_names_filtered = [
        c for c in medication_column_names
        if (df[c] != "No").sum() > 100
    ]
    return df, medication_column_names_filtered


@st.cache_data(show_spinner=False)
def prepare_df(df: pd.DataFrame, med_cols_all=None) -> pd.DataFrame:
    df = df.copy()

    df["age_lb"] = df["age"].str.extract(r"(\d+)").astype("int16")

    # Weight lower bound: "?", ">200" -> NaN or 200
    w = df["weight"].replace({"?": pd.NA, ">200": "200"})
    df["weight_lb"] = pd.to_numeric(w.str.extract(r"(\d+)")[0], errors="coerce").astype("float32")

    diag_cols = ["diag_1", "diag_2", "diag_3"]
    df[diag_cols] = df[diag_cols].replace("?", pd.NA)
    for col in diag_cols:
        df[f"{col}_cat"] = df[col].apply(icd9_to_category)

    if med_cols_all:
        df[med_cols_all] = df[med_cols_all].replace("?", pd.NA)
        for c in med_cols_all:
            df[f"{c}_bin"] = (df[c].isin(["Up", "Down", "Steady"])).astype("int8")

    for col in ["readmitted", "race"]:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def filter_by_age(df: pd.DataFrame, age_range: tuple):
    min_age, max_age = age_range

    def is_in_range(age_str):
        lower_bound = int(age_str.strip('[').split('-')[0])
        return min_age <= lower_bound < max_age

    return df[df["age"].apply(is_in_range)]


def filter_by_weight(df: pd.DataFrame, weight_range: tuple, include_unknown=True):
    min_weight, max_weight = weight_range

    def is_in_range(weight_str):
        if weight_str == '?':
            return include_unknown

        if weight_str == '>200':
            return include_unknown

        lower_bound = int(weight_str.strip('[').split('-')[0])
        return min_weight <= lower_bound < max_weight

    return df[df["weight"].apply(is_in_range)]


def filter_by_race(df: pd.DataFrame, selected_races: list):
    return df[df["race"].isin(selected_races)]


def filter_by_readmission(df: pd.DataFrame, selectedType):
    if selectedType == "Any":
        print("using any")
        return df
    print("using selected type: " + selectedType)
    # return df[df["readmitted"].isin(["<30", "NO"])]
    return df[df["readmitted"].replace(">30", "NO", inplace=True)]


def filter_all(df, age_range, weight_range, include_unknown_weight=True, readmission_type="Any"):
    min_age, max_age = age_range
    min_w, max_w = weight_range

    mask_age = (df["age_lb"] >= min_age) & (df["age_lb"] < max_age)

    if include_unknown_weight:
        mask_weight = df["weight_lb"].isna() | (
                (df["weight_lb"] >= min_w) & (df["weight_lb"] < max_w)
        )
    else:
        mask_weight = df["weight_lb"].notna() & (
                (df["weight_lb"] >= min_w) & (df["weight_lb"] < max_w)
        )
    if readmission_type == "Any":
        mask_readm = pd.Series(True, index=df.index)
    else:
        # mask_readm = df["readmitted"].isin(["NO", "<30"])
        df["readmitted"].replace(">30", "NO", inplace=True)
        mask_readm = df["readmitted"].isin(["NO", "<30"])

    mask = mask_age & mask_weight & mask_readm
    return df.loc[mask]
