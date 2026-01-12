import altair as alt


def get_barchart(race_counts):
    return alt.Chart(race_counts).mark_bar().encode(
        x='race',  # races on x-axis
        y='count',  # counts on y-axis
        tooltip=['race', 'count']  # hover shows race and count
    ).properties(
        title='Number of penguins per race'
    )