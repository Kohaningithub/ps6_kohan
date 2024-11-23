from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
from shared import plot_top_locations_with_map

# Use relative path
app_dir = Path(__file__).parent
agg_df = pd.read_csv(app_dir / "top_alerts_map.csv")

# Get unique combinations for dropdown
combinations = (
    agg_df
    .groupby(['updated_type', 'updated_subtype'])
    .size()
    .reset_index()
    .apply(lambda x: f"{x['updated_type']} - {x['updated_subtype']}", axis=1)
    .sort_values()
    .tolist()
)

# UI
app_ui = ui.page_fluid(
    ui.h2("Top Alert Locations in Chicago"),
    ui.page_sidebar(
        ui.sidebar(
            ui.input_select(
                "alert_combo",
                "Select Alert Type and Subtype",
                choices=combinations
            ),
        ),
        ui.output_ui("map_plot")
    )
)

def server(input, output, session):
    @reactive.Calc
    def get_selected_types():
        alert_type, alert_subtype = input.alert_combo().split(" - ")
        return alert_type, alert_subtype
    
    @output
    @render.ui
    def map_plot():
        alert_type, alert_subtype = get_selected_types()
        chart = plot_top_locations_with_map(agg_df, alert_type, alert_subtype)
        return ui.HTML(chart.to_html())

app = App(app_ui, server) 