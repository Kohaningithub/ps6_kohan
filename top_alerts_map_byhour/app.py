from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
from shared import plot_locations_for_hour

# Load data
app_dir = Path(__file__).parent
agg_df = pd.read_csv(app_dir / "top_alerts_map_byhour.csv")

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

HOUR_MARKS = {
    8: "08:00",
    13: "13:00",
    18: "18:00"
}

app_ui = ui.page_fluid(
    ui.h2("Top Alert Locations in Chicago by Hour"),
    ui.page_sidebar(
        ui.sidebar(
            ui.input_select(
                "alert_combo",
                "Select Alert Type and Subtype",
                choices=combinations
            ),
            ui.input_slider(
                "hour",
                "Select Hour",
                min=8,
                max=18,
                value=8,
                step=5,  
                ticks=True
            ),
            width="300px"
        ),
        ui.output_ui("map_plot")
    )
)

def server(input, output, session):
    @reactive.Calc
    def get_selected_types():
        alert_type, alert_subtype = input.alert_combo().split(" - ")
        return alert_type, alert_subtype
    
    @reactive.Calc
    def get_nearest_hour():
        hour_value = input.hour()
        if hour_value <= 10:
            return 8
        elif hour_value <= 15:
            return 13
        else:
            return 18
        
    @output
    @render.ui
    @reactive.event(input.alert_combo, input.hour)
    def map_plot():
        alert_type, alert_subtype = get_selected_types()
        hour = HOUR_MARKS[get_nearest_hour()]  
        chart = plot_locations_for_hour(agg_df, hour, alert_type, alert_subtype)
        return ui.HTML(chart.to_html())

app = App(app_ui, server)