import pandas as pd


def getOverviewPlots(df):
    row_labels = df[['metformin', 'repaglinide']].agg('_'.join, axis=1)
    column_labels = df[['no', 'steady', 'up', 'down']].agg('_'.join, axis=1)
    heatmap_df = pd.crosstab(row_labels, column_labels, aggfunc='count')
    return alt