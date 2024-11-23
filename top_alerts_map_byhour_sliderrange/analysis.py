import pandas as pd
import altair as alt
from pathlib import Path
import json

# Load data
app_dir = Path(__file__).parent
agg_df = pd.read_csv(app_dir / "top_alerts_map_byhour" / "top_alerts_map_byhour.csv")

# Filter for "Jam - Heavy Traffic" and time range 6AM to 9AM
filtered_df = agg_df[
    (agg_df['updated_type'] == "Traffic Jam") &
    (agg_df['updated_subtype'] == "Heavy") &
    (agg_df['hour'].between("06:00", "09:00"))
]

# Aggregate data
top_10_df = (
    filtered_df
    .groupby(['latitude_bin', 'longitude_bin'])
    .agg({'alert_count': 'sum'})
    .reset_index()
    .nlargest(10, 'alert_count')
)

# Load geo data
with open(app_dir.parent / "top_alerts_map" / "chicago-boundaries.geojson") as f:
    chicago_geojson = json.load(f)
geo_data = alt.Data(values=chicago_geojson["features"])

# Base map layer
base_map = alt.Chart(geo_data).mark_geoshape(
    fill='lightgray',
    stroke='white',
    opacity=0.3
).project(
    type='mercator',
    scale=80000,     
    center=[-87.7, 41.85]  
)

# Scatter plot layer
points = alt.Chart(top_10_df).mark_circle().encode(
    longitude='longitude_bin:Q',
    latitude='latitude_bin:Q',
    size=alt.Size('alert_count:Q', scale=alt.Scale(range=[100, 1000])),
    color=alt.value('red'),
    tooltip=['latitude_bin', 'longitude_bin', 'alert_count']
).project(
    type='mercator',
    scale=80000,
    center=[-87.7, 41.85]
)

# Combine layers
plot = (base_map + points).properties(
    title="Top 10 Locations for Heavy Traffic Jam (6AM-9AM)",
    width=800,
    height=700
)

# Display plot
plot.show()
