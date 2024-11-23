import pandas as pd
from pathlib import Path
import altair as alt
from shared import plot_locations_for_hour

def create_three_hour_comparison():
    """Create comparison plots for three different hours"""

    app_dir = Path(__file__).parent
    agg_df = pd.read_csv(app_dir / "top_alerts_map_byhour.csv")
    
    # Create plots for morning, noon, and evening
    morning_plot = plot_locations_for_hour(agg_df, "08:00", "Traffic Jam", "Heavy")
    noon_plot = plot_locations_for_hour(agg_df, "13:00", "Traffic Jam", "Heavy")
    evening_plot = plot_locations_for_hour(agg_df, "18:00", "Traffic Jam", "Heavy")
    
    # Combine plots vertically
    combined_plot = alt.vconcat(
        morning_plot,
        noon_plot,
        evening_plot
    ).resolve_scale(
        size='independent'
    )
    
    # Save the combined plot
    output_path = app_dir / "hourly_traffic_comparison.html"
    combined_plot.save(str(output_path))
    print(f"Saved comparison plot to {output_path}")

if __name__ == "__main__":
    create_three_hour_comparison() 