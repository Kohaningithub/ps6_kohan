import pandas as pd
import re
from pathlib import Path
import numpy as np

def extract_coordinates(geo_string):
    pattern = r'POINT\(([-\d.]+) ([-\d.]+)\)'
    match = re.search(pattern, str(geo_string))
    if match:
        return float(match.group(2)), float(match.group(1))
    return None, None

def create_top_alerts_map_data(df):
    # Create latitude and longitude columns
    df[['latitude', 'longitude']] = df['geo'].apply(
        lambda x: pd.Series(extract_coordinates(x))
    )
    
    # Fill NaN values
    df['updated_subsubtype'] = df['updated_subsubtype'].fillna("None")
    
    # Bin coordinates
    df['latitude_bin'] = np.round(df['latitude'], decimals=2)
    df['longitude_bin'] = np.round(df['longitude'], decimals=2)
    
    # Aggregate data
    agg_df = df.groupby(
        ['latitude_bin', 'longitude_bin', 'updated_type', 'updated_subtype']
    ).size().reset_index(name='alert_count')
    
    return df,agg_df

def create_hourly_alerts_data(df):
    df['hour'] = pd.to_datetime(df['ts']).dt.strftime('%H:00')
    
    agg_df = df.groupby(
        ['latitude_bin', 'longitude_bin', 'updated_type', 'updated_subtype', 'hour']
    ).size().reset_index(name='alert_count')
    

    app_dir = Path(__file__).parent
    output_path = app_dir / "top_alerts_map_byhour.csv"
    agg_df.to_csv(output_path, index=False)
    
    print(f"\nAggregation level: binned latitude-longitude + alert type + alert subtype + hour")
    print(f"Number of rows in aggregated data: {len(agg_df)}")
    print("\nSample of aggregated data:")
    print(agg_df.head())
    
    return agg_df

if __name__ == "__main__":
    app_dir = Path(__file__).parent
    data_dir = app_dir.parent / "data"
    df_merged = pd.read_csv(data_dir / "processed_waze_data.csv")
    print(f"Loaded {len(df_merged)} rows of data")
    
    processed_df, agg_df = create_top_alerts_map_data(df_merged)
    hourly_agg_df = create_hourly_alerts_data(processed_df)
    
    # Save both datasets
    agg_df.to_csv(app_dir / "top_alerts_map.csv", index=False)
    hourly_agg_df.to_csv(app_dir / "top_alerts_map_byhour.csv", index=False)
    
    print(f"Saved regular aggregation data")
    print(f"Saved hourly aggregation data with {len(hourly_agg_df)} rows")