import requests
from pathlib import Path
import json
import altair as alt

def download_chicago_boundaries():
    url = "https://data.cityofchicago.org/api/geospatial/bbvz-uum9?method=export&format=GeoJSON"
    app_dir = Path(__file__).parent
    output_path = app_dir / "chicago-boundaries.geojson"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, "w") as f:
            f.write(response.text)
        print(f"Successfully downloaded Chicago boundaries")
        
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def load_geo_data():
    app_dir = Path(__file__).parent
    file_path = app_dir / "chicago-boundaries.geojson"
    
    with open(file_path) as f:
        chicago_geojson = json.load(f)
    
    return alt.Data(values=chicago_geojson["features"])

if __name__ == "__main__":
    download_chicago_boundaries() 