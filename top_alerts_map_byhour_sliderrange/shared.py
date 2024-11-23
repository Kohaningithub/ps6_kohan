import altair as alt
import json
from pathlib import Path

app_dir = Path(__file__).parent
with open(app_dir.parent / "top_alerts_map" / "chicago-boundaries.geojson") as f:
    chicago_geojson = json.load(f)
geo_data = alt.Data(values=chicago_geojson["features"])

def plot_locations_for_hour_range(agg_df, start_hour, end_hour, alert_type, alert_subtype):
    """Plot top 10 locations for a specific hour range and alert type"""
    
    # Filter for specific hour range and type
    filtered_df = agg_df[
        (agg_df['hour'].between(f"{start_hour:02d}:00", f"{end_hour:02d}:00")) &
        (agg_df['updated_type'] == alert_type) &
        (agg_df['updated_subtype'] == alert_subtype)
    ]

    # Aggregate data
    top_10_df = (
        filtered_df
        .groupby(['latitude_bin', 'longitude_bin'])
        .agg({'alert_count': 'sum'})
        .reset_index()
        .nlargest(10, 'alert_count')
    )
    
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
        size=alt.Size('alert_count:Q', scale=alt.Scale(range=[10, 100])),
        color=alt.value('red'),
        tooltip=['latitude_bin', 'longitude_bin', 'alert_count']
    ).project(
        type='mercator',
        scale=80000,
        center=[-87.7, 41.85]
    )

    if start_hour == end_hour:
        time_label = f"{start_hour}:00"
    else:
        time_label = f"{start_hour}:00-{end_hour}:00"
    
    # Combine layers
    return (base_map + points).properties(
        title=f"Top 10 Locations for {alert_type} - {alert_subtype} ({time_label})",
        width=800,
        height=700
    )
