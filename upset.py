import pandas as pd
import altair as alt

def getUpsetPlot(raw_data):
  med_cols = ['metformin', 'repaglinide', 'glimepiride', 'glipizide', 'insulin']

  df = raw_data.copy()
  for col in med_cols:
      df[col] = df[col].apply(lambda x: 0 if x == 'No' else 1)

  df_active = df[df[med_cols].sum(axis=1) > 0].copy()

  total_counts = df[med_cols].sum().reset_index()
  total_counts.columns = ['medication', 'count']

  intersection_df = df_active.groupby(med_cols).size().reset_index(name='count')

  intersection_df['id'] = intersection_df.index

  matrix_df = pd.melt(intersection_df, id_vars=['id', 'count'], value_vars=med_cols, 
                      var_name='medication', value_name='is_active')
  matrix_df = matrix_df[matrix_df['is_active'] == 1] # Nur Punkte anzeigen, wo Med aktiv ist

  selection = alt.selection_point(fields=['medication'], name="Select", empty='all')

  row_bars = alt.Chart(total_counts).mark_bar().encode(
      y=alt.Y('medication', title="Medication", sort='-x'),
      x=alt.X('count', title="Total Count", scale=alt.Scale(reverse=True)),
      color=alt.condition(selection, alt.value('black'), alt.value('lightgray')),
      opacity=alt.condition(selection, alt.value(1), alt.value(0.6))
  ).add_params(
      selection
  ).properties(
      width=150,
      height=275,
  )

  spacer = alt.Chart(pd.DataFrame({'x': [0]})).mark_text().encode().properties(
      width=150,
      height=100
  )

  row_bars_with_spacer = alt.vconcat(spacer, row_bars, spacing=0)

  # Create a dataset that links each intersection id to its medications
  intersection_with_meds = pd.merge(
      intersection_df[['id', 'count']], 
      matrix_df[['id', 'medication']], 
      on='id'
  )

  print(intersection_with_meds.head())
  intersection_bars_combined = alt.Chart(intersection_with_meds).mark_bar().encode(
      x=alt.X('id:O', axis=None, sort=alt.EncodingSortField(field='count', order='descending')),
      y=alt.Y('count:Q', title=None, aggregate='max'),
      color=alt.value('black'),
      opacity=alt.condition(selection, alt.value(1.0), alt.value(0.2)),
      tooltip=[alt.Tooltip('count:Q', aggregate='max')]
  ).properties(
      width=400,
      height=100
  )

  matrix_dots = alt.Chart(matrix_df).mark_circle(size=100).encode(
      x=alt.X('id:O', axis=None, sort=alt.EncodingSortField(field='count', order='descending')),
      y=alt.Y('medication', title=None, axis=alt.Axis(labels=False, ticks=False), sort=alt.EncodingSortField(field='count', op='sum', order='descending')), # Sortierung angleichen an row_bars wenn möglich
      color=alt.value('black'),
      opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
  ).properties(
      width=400,
      height=275
  )

  matrix_lines = alt.Chart(matrix_df).mark_line(color='lightgray').encode(
      x=alt.X('id:O'), #, sort=alt.EncodingSortField(field='count', order='descending')
      y=alt.Y('medication')
  )

  matrix_plot = alt.layer(matrix_dots, matrix_lines)

  upset_right = alt.vconcat(intersection_bars_combined, matrix_dots, spacing=0)
  final_chart = alt.hconcat(row_bars_with_spacer, upset_right).resolve_legend(
      color="independent"
  )

  return final_chart