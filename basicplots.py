import altair as alt
import pandas as pd


def get_barchart(race_counts):
    return alt.Chart(race_counts).mark_bar().encode(
        x='race',  # races on x-axis
        y='count',  # counts on y-axis
        tooltip=['race', 'count']  # hover shows race and count
    ).properties(
        title='Number of penguins per race'
    )

def get_piechart(df, readmission_type):


    if readmission_type == "Any":
        count_no = (df['readmitted'] == 'NO').sum()
        count_short = (df['readmitted'] == '<30').sum()
        count_long = (df['readmitted'] == '>30').sum()

        readmit_counts = pd.DataFrame({
            "readmitted": ["No", "<30", ">30"],
            "count": [count_no, count_short, count_long]
        })

        # Create Altair chart

        return (((alt.Chart(readmit_counts).
                mark_arc()).
                encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("readmitted:N", title="Readmission", scale=alt.Scale(domain=["No", "<30", ">30"], range=["orange", "lightblue", "darkblue"])),
            tooltip=["readmitted", "count"]
                )).
        properties(
        width=400,
        height=400,
        title="Readmission distribution"
    ))

    else:
        count_no = (df['readmitted'] == 'NO').sum()
        count_short = (df['readmitted'] == '<30').sum()

        readmit_counts = pd.DataFrame({
            "readmitted": ["No", "<30"],
            "count": [count_no, count_short, ]
        })

        # Create Altair chart

        return (((alt.Chart(readmit_counts).
                  mark_arc()).
        encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("readmitted:N", title="Readmission", scale=alt.Scale(domain=["No", "<30"], range=["orange", "lightblue"])),
            tooltip=["readmitted", "count"]
        )).
        properties(
            width=400,
            height=400,
            title="Readmission distribution"
        ))





    return alt.Chart(df).mark_bar().encode()

