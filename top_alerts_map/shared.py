import altair as alt
from map_data import load_geo_data
import json

# Load geo data once
geo_data = load_geo_data()

def plot_top_locations_with_map(agg_df, alert_type="Traffic Jam", alert_subtype="Heavy"):
    # Filter for top 10 locations
    top_10_df = (
        agg_df[
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
        tooltip=['latitude_bin', 'longitude_bin', 'alert_count']
    ).project(  
        type='mercator',
        scale=80000,
        center=[-87.7, 41.85]
    ).properties(
        width=800,
        height=700
    )
    
    # Combine layers
    return (base_map + points).properties(
        title=f"Top 10 Locations for {alert_type} - {alert_subtype}"
    ) 