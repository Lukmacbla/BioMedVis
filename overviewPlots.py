import pandas as pd
import altair as alt


def getOverviewPlots(df, readmission_type):
    meds = [
        'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide',
        'glimepiride', 'acetohexamide', 'glipizide', 'glyburide',
        'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose',
        'miglitol', 'troglitazone', 'tolazamide', 'examide',
        'citoglipton', 'insulin', 'glyburide-metformin',
        'glipizide-metformin', 'glimepiride-pioglitazone',
        'metformin-rosiglitazone', 'metformin-pioglitazone'
    ]
    statuses = ['Up', 'Down', 'No', 'Steady']
    if readmission_type == "Any":
        readmit = df["readmitted"].isin([">30", "<30"]).astype(int)
    else:
        readmit = (df["readmitted"] == "<30").astype(int)

    data = []
    for med in meds:
        for status in statuses:
            count = (df[med] == status).sum()
            count_med_and_readmit = ((df[med] == status) & readmit).sum()
            if (count > 0) & (status != 'No'):
                percent = (count_med_and_readmit / count) * 100
            else:
                percent = 0.0
            data.append({'medication': med, 'status': status, 'count': count, 'percent': percent})
    heatmap_df = pd.DataFrame(data)





    chart = (alt.Chart(heatmap_df).
             mark_circle(size=800).
             encode(
        y=alt.Y('medication:O', title='Medication'),
        x=alt.X('status:O', title='Status', sort=['No', 'Up', 'Steady', 'Down']),
        size=alt.Size('count:Q', scale=alt.Scale(range=[50, 800])),
        color=alt.Color('percent:Q', scale=alt.Scale(scheme='darkred')),
        tooltip=['medication', 'status', 'count']
    ).
             properties(
        title='Medication Status Distribution: Size & Color by Count'
    ).
             interactive()
             )
    return chart