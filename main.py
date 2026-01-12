import streamlit as st
import pandas as pd
import altair as alt

# Running the Streamlit app
# streamlit run app.py

# Config the settings of the page
st.set_page_config(page_title="Streamlit Tutorial", page_icon="📊", layout="wide")
st.title("🐧 Palmer's Penguins")
st.markdown("Use this Streamlit app to make your own scatterplot about penguins!")


# -------------------------------
# 1) Data loading and cached
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/diabetic_data.csv")


dataframe = load_data()
# st.dataframe(penguins)
import streamlit as st

tab1, tab2 = st.tabs(["Medication Strategy", "Distribution"])

with tab1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
with tab2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)


# -------------------------------
# 2) Sidebar controls
# -------------------------------
st.sidebar.title("Selectors")
selected_ages = st.sidebar.multiselect(
    "age",
    dataframe["age"].unique(),
    default=list(set(dataframe['age']))
)

# -------------------------------
# 3) Scatterplot with brush selection
# -------------------------------
# Create a simple scatterplot with brush selection

# Plot the altair chart on Streamlit app

age_filtered_df = dataframe[dataframe["age"].isin(selected_ages)]


race_counts = age_filtered_df['race'].value_counts().reset_index()
race_counts.columns = ['race', 'count']  # rename columns for Altair
# Create a bar chart
event = alt.Chart(race_counts).mark_bar().encode(
    x='race',         # races on x-axis
    y='count',        # counts on y-axis
    tooltip=['race', 'count']  # hover shows race and count
).properties(
    title='Number of penguins per race'
)
# col2.write(event)

# -------------------------------
# 4) Cross-filter on the bar chart
# -------------------------------
# Filter the dataset after selection
def filtered_table(event):
    selection = event['selection']['brush']

    # 0. Prevent an error if selection object is None or empty.
    if selection == dict():
        return dataframe

    # 1. Create a query string to filter the data
    query = ' & '.join(
        f'{crange[0]} <= `{col}` <= {crange[1]}'
        for col, crange in selection.items())

    df = dataframe.query(query)

    # 2. Filter the penguin data frame from the query
    #df = penguins[penguins['species'].isin(species)].query(query)

    # 3. Add the DataFrame pane that render pandas object
    return df


#filtered = filtered_table(event)

# Add another bar chart with linked selections


st.altair_chart(event)