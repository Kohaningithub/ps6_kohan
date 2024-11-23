from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
from shared import plot_locations_for_hour_range

agg_df = pd.read_csv("/Users/kohanchen/Documents/Fall 2024/student30538/problem_sets/ps6/top_alerts_map_byhour/top_alerts_map_byhour.csv")

combinations = (
    agg_df
    .groupby(['updated_type', 'updated_subtype'])
    .size()
    .reset_index()
    .apply(lambda x: f"{x['updated_type']} - {x['updated_subtype']}", axis=1)
    .sort_values()
    .tolist()
)

app_ui = ui.page_fluid(
    ui.h2("Top Alert Locations in Chicago by Hour"),
    ui.page_sidebar(
        ui.sidebar(
            ui.input_select(
                "alert_combo",
                "Select Alert Type and Subtype",
                choices=combinations,
                selected="Traffic Jam - Heavy"
            ),
            ui.input_switch(
                "switch_button",
                "Toggle to switch to range of hours"
            ),
            ui.output_ui("hour_input"),
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
    
    @output
    @render.ui
    def hour_input():
        if input.switch_button():
            return ui.input_slider(
                "hour_range",
                "Select Hour Range",
                min=0,
                max=23,
                value=(6, 9),
                step=1,
                ticks=True
            )
        else:
            return ui.input_slider(
                "single_hour",
                "Select Hour",
                min=0,
                max=23,
                value=8,
                step=1,
                ticks=True
            )
    
    @output
    @render.ui
    def map_plot():
        alert_type, alert_subtype = get_selected_types()
        if input.switch_button():
            start_hour, end_hour = input.hour_range()
            chart = plot_locations_for_hour_range(agg_df, start_hour, end_hour, alert_type, alert_subtype)
        else:
            hour = input.single_hour()
            chart = plot_locations_for_hour_range(agg_df, hour, hour, alert_type, alert_subtype)
        return ui.HTML(chart.to_html())

app = App(app_ui, server)
