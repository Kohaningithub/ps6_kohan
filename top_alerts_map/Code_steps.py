import pandas as pd
import re
from pathlib import Path
import numpy as np
import altair as alt

#a
app_dir = Path(__file__).parent
data_dir = app_dir.parent / "data" 
df_merged = pd.read_csv(data_dir / "processed_waze_data.csv")
print(f"Loaded {len(df_merged)} rows of data")

# Extract coordinates from WKT format
def extract_coordinates(geo_string):
    pattern = r'POINT\(([-\d.]+) ([-\d.]+)\)'
    match = re.search(pattern, str(geo_string))
    if match:
        return float(match.group(2)), float(match.group(1))
    return None, None

# Create latitude and longitude columns
df_merged[['latitude', 'longitude']] = df_merged['geo'].apply(
    lambda x: pd.Series(extract_coordinates(x))
)

# Fill NaN values in updated_subsubtype with "None"
df_merged['updated_subsubtype'] = df_merged['updated_subsubtype'].fillna("None")

# Verify coordinate extraction
print("\nVerifying coordinate extraction:")
print(df_merged[['geo', 'latitude', 'longitude']].head())

# Verify alert type columns
print("\nVerifying alert type columns:")
print(df_merged[['updated_type', 'updated_subtype', 'updated_subsubtype']].head())

# Check for any null values
print("\nChecking for null values in key columns:")
print(df_merged[['latitude', 'longitude', 'updated_type', 'updated_subtype', 'updated_subsubtype']].isnull().sum())


#b
# Bin coordinates (round to 2 decimal places)
df_merged['latitude_bin'] = np.round(df_merged['latitude'], decimals=2)
df_merged['longitude_bin'] = np.round(df_merged['longitude'], decimals=2)

# Group by binned coordinates to find most frequent location
location_counts = df_merged.groupby(['latitude_bin', 'longitude_bin']).size().reset_index(name='count')
most_frequent = location_counts.sort_values('count', ascending=False).head()

print("\nTop 5 most frequent locations (binned):")
print(most_frequent.to_string(index=False))

#Answer for b.latitude_bin:41.88, longitude_bin:-87.65 is the most frequent location.

#c.
def create_top_alerts_map_data(df):
    agg_df = df.groupby(
        ['latitude_bin', 'longitude_bin', 'updated_type', 'updated_subtype']
    ).size().reset_index(name='alert_count')
    
    # Save to CSV
    output_path = Path("/Users/kohanchen/Documents/Fall 2024/student30538/problem_sets/ps6/top_alerts_map/top_alerts_map.csv")
    agg_df.to_csv(output_path, index=False)
    
    print("\nAggregation level: binned latitude-longitude + alert type + alert subtype")
    print(f"Number of rows in aggregated data: {len(agg_df)}")
    
    print("\nSample of aggregated data:")
    print(agg_df.head())
    
    return agg_df

agg_df = create_top_alerts_map_data(df_merged)

#2.
def plot_top_locations(agg_df, alert_type="Traffic Jam", alert_subtype="Heavy"):
    # Filter for specific type and subtype, get top 10
    top_10_df = (
        agg_df[
            (agg_df['updated_type'] == alert_type) & 
            (agg_df['updated_subtype'] == alert_subtype)
        ]
        .nlargest(10, 'alert_count')
    )
    
    # Create scatter plot
    chart = alt.Chart(top_10_df).mark_circle().encode(
        x=alt.X('longitude_bin', 
                title='Longitude',
                # Set domain to cover Chicago area
                scale=alt.Scale(domain=[-87.9, -87.5])),
        y=alt.Y('latitude_bin', 
                title='Latitude',
                scale=alt.Scale(domain=[41.7, 42.0])),
        size=alt.Size('alert_count', 
                     title='Number of Alerts',
                     scale=alt.Scale(range=[100, 1000])),
        tooltip=['latitude_bin', 'longitude_bin', 'alert_count']
    ).properties(
        title=f"Top 10 Locations for {alert_type} - {alert_subtype}",
        width=600,
        height=400
    )
    
    return chart

# Create and display the plot
chart = plot_top_locations(agg_df)
# chart.show()

#C.a
import requests
from pathlib import Path

def download_chicago_boundaries():
    # URL for Chicago Neighborhoods GeoJSON
    url = "https://data.cityofchicago.org/api/geospatial/bbvz-uum9?method=export&format=GeoJSON"
    
    try:
        # Send GET request
        response = requests.get(url)
        response.raise_for_status()  
        
        # Create directory if it doesn't exist
        output_path = Path("/Users/kohanchen/Documents/Fall 2024/student30538/problem_sets/ps6/top_alerts_map/chicago-boundaries.geojson")
        output_path.parent.mkdir(exist_ok=True)
        
        # Save the file
        with open(output_path, "w") as f:
            f.write(response.text)
            
        print(f"Successfully downloaded Chicago boundaries to {output_path}")
        
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

# Download the boundaries
download_chicago_boundaries()

#b
import json
import altair as alt

# MODIFY ACCORDINGLY
file_path = "/Users/kohanchen/Documents/Fall 2024/student30538/problem_sets/ps6/top_alerts_map/chicago-boundaries.geojson"
#----

with open(file_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])

#4
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
        type='mercator',  #
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
        width=800,    # Increased width
        height=700    # Increased height
    )
    
    # Combine layers
    return (base_map + points).properties(
        title=f"Top 10 Locations for {alert_type} - {alert_subtype}"
    )

#5.a
def analyze_combinations(agg_df):
    
    combinations = (
        agg_df
        .groupby(['updated_type', 'updated_subtype'])
        .size()
        .reset_index()
    )
    
    print(f"Total number of type-subtype combinations: {len(combinations)}")
    print("\nAll available combinations:")
    for _, row in combinations.iterrows():
        print(f"- {row['updated_type']} - {row['updated_subtype']}")
    
    return combinations

# Run the analysis
if __name__ == "__main__":
    agg_df = pd.read_csv("/Users/kohanchen/Documents/Fall 2024/student30538/problem_sets/ps6/top_alerts_map/top_alerts_map.csv")
    combinations = analyze_combinations(agg_df)

#5.b
