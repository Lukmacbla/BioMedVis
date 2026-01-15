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
             mark_circle().
             encode(
        y=alt.Y('medication:O', title='Medication', axis=alt.Axis(labelLimit=200)),
        x=alt.X('status:O', title='Status', sort=['No', 'Up', 'Steady', 'Down']),
        #size=alt.Size('count:Q', scale=alt.Scale(range=[50, 800])),
        size=alt.condition(alt.datum.count > 1, alt.Size('count:Q', scale=alt.Scale(type='sqrt', range=[150, 900])), alt.value(0)), # TODO: decide whether linear or sqrt looks better
        #size=alt.condition(alt.datum.count > 1, alt.Size('count:Q', scale=alt.Scale(type='linear', range=[150, 900])), alt.value(0)),
        color=alt.Color('percent:Q', title='Readmission rate (%)', scale=alt.Scale(scheme='darkred', reverse=True, domain=[0, 100])),
        #color=alt.condition(alt.datum.status == 'No',alt.value('lightblue'),alt.Color('percent:Q', scale=alt.Scale(scheme='darkred', reverse=True, domain=[0, 100]), title='Readmission rate (%)')),
        tooltip=['medication', 'status', 'count', 'percent:N']
    ).
             properties(
        title='Medication Status Distribution: Size & Color by Count'
    ).
             interactive()
             )
    return chart