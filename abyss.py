from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import requests
import dash_bootstrap_components as dbc

id_to_name_dict = {v: k for k, v in requests.get("https://api.uigf.org/dict/genshin/chs.json").json().items()}
id_to_name_dict[10000005] = "旅行者"


def make_current_utilization_rate_data():
    result = requests.get("https://homa.snapgenshin.com/Statistics/Avatar/UtilizationRate").json().get("data")
    current_schedule = requests.get("https://homa.snapgenshin.com/Statistics/Overview").json() \
        .get("data").get("scheduleId")
    df_list = {}
    for floor in result:
        floor_number = str(floor["floor"])
        floor_data = [{"item": item["item"], "Floor %s" % floor_number: item["rate"],
                       "schedule": current_schedule, "text": id_to_name_dict[int(item["item"])]}
                      for item in floor["ranks"]]
        floor_data = sorted(floor_data, key=lambda x: x["item"], reverse=False)
        for item_data in floor_data:
            if item_data["item"] not in df_list.keys():
                df_list[item_data["item"]] = item_data
            else:
                df_list[item_data["item"]]["Floor %s" % floor_number] = item_data["Floor %s" % floor_number]
    return_df = pd.DataFrame(list(df_list.values()))
    return_df = return_df[["schedule", "text", "Floor 9", "Floor 10", "Floor 11", "Floor 12"]]
    return return_df


if __name__ == "__main__":
    # Load data
    df = make_current_utilization_rate_data()

    # Initialize the app
    app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

    # App layout
    app.layout = dbc.Container([
        dbc.Row([
            html.Div(children='Abyss Data', className="text-primary text-center fs-3",
                     style={"font-weight": "bold", "textAlign": "center"})
        ]),
        dbc.Row([
            dcc.RadioItems(options=["Floor 9", "Floor 10", "Floor 11", "Floor 12"],
                           value="Floor 9", id="floor_radio_control", inline=True)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure={}, id="floor_utilization_rate_graph")
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(data=df.to_dict('records'), page_size=15)
            ], width=3)
        ])
    ], fluid=True)


    # Add controls to build the interaction
    @callback(
        Output(component_id="floor_utilization_rate_graph", component_property='figure'),
        Input(component_id="floor_radio_control", component_property='value')
    )
    def update_graph(col_chosen):
        fig = px.histogram(df, x='text', y=col_chosen)
        fig.update_layout(yaxis_tickformat=".0%", xaxis={'categoryorder': 'total descending'})
        return fig


    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)
