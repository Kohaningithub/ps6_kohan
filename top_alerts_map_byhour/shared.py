import altair as alt
from pathlib import Path
import json

app_dir = Path(__file__).parent
with open(app_dir.parent / "top_alerts_map" / "chicago-boundaries.geojson") as f:
    chicago_geojson = json.load(f)
geo_data = alt.Data(values=chicago_geojson["features"])

def plot_locations_for_hour(agg_df, hour="08:00", alert_type="Traffic Jam", alert_subtype="Heavy"):
    """Plot top 10 locations for a specific hour and alert type"""
    
    top_10_df = (
        agg_df[
            (agg_df['hour'] == hour) & 
            (agg_df['updated_type'] == alert_type) & 
            (agg_df['updated_subtype'] == alert_subtype)
        ]
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
        size=alt.Size('alert_count:Q',
                     scale=alt.Scale(range=[10, 100])),
        color=alt.value('red'),
        tooltip=['latitude_bin', 'longitude_bin', 'alert_count', 'hour']
    ).project(
        type='mercator',
        scale=80000,
        center=[-87.7, 41.85]
    )
    
    # Combine layers
    return (base_map + points).properties(
        title=f"Top 10 Locations for {alert_type} - {alert_subtype} at {hour}",
        width=800,
        height=700
    ) 