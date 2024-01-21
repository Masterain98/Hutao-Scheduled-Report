from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import matplotlib.colors as mcolors
import numpy as np
import requests
import dash_bootstrap_components as dbc

id_to_name_dict = {v: k for k, v in requests.get("https://api.uigf.org/dict/genshin/chs.json").json().items()}
id_to_name_dict[10000005] = "旅行者"


def make_current_utilization_rate_data() -> pd.DataFrame:
    result = requests.get("https://homa.snapgenshin.com/Statistics/Avatar/UtilizationRate").json().get("data")
    current_schedule = requests.get("https://homa.snapgenshin.com/Statistics/Overview").json() \
        .get("data").get("scheduleId")
    df_list = {}
    for floor in result:
        floor_number = str(floor["Floor"])
        floor_data = [{"item": item["Item"], "Floor %s" % floor_number: item["Rate"],
                       "schedule": current_schedule, "Character": id_to_name_dict[int(item["Item"])]}
                      for item in floor["Ranks"]]
        floor_data = sorted(floor_data, key=lambda x: x["item"], reverse=False)
        for item_data in floor_data:
            if item_data["item"] not in df_list.keys():
                df_list[item_data["item"]] = item_data
            else:
                df_list[item_data["item"]]["Floor %s" % floor_number] = item_data["Floor %s" % floor_number]
    return_df = pd.DataFrame(list(df_list.values()))
    return_df = return_df[["schedule", "Character", "Floor 9", "Floor 10", "Floor 11", "Floor 12"]]
    return return_df


if __name__ == "__main__":
    df = make_current_utilization_rate_data()

    app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

    # Main app layout
    app.layout = html.Div([
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.NavbarBrand(
                                    html.A([
                                        html.Img(
                                            src='/assets/masterain.webp',
                                            height="30px", width="30px"),
                                        " Spiral Abyss Live Report"
                                    ], href="#", style={'color': 'white', 'text-decoration': 'none'}),
                                    className="navbar-brand"
                                )
                            ),
                            dbc.Col(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(dbc.NavLink("Home", href="/", style={'color': 'white'})),
                                        dbc.NavItem(
                                            dbc.NavLink("Snap Hutao", href="https://hut.ao", style={'color': 'white'})),
                                        dbc.NavItem(
                                            dbc.NavLink("Pizza Helper for Genshin",
                                                        href="https://apps.apple.com/pw/app/pizza-helper-for-genshin/id1635319193",
                                                        style={'color': 'white'})),
                                        # New item
                                    ],
                                    className="ml-auto flex-nowrap mt-3 mt-md-0", navbar=True
                                ),
                                width="auto"
                            ),
                        ],
                        align="center",
                        className="no-gutters",
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            html.A([
                                html.Img(
                                    src='/assets/github-mark.svg',
                                    height="30px", width="30px")
                            ], href="https://github.com/Masterain98")
                        ),
                        className="ml-auto"
                    ),
                ]
            ),
            color="primary",
            dark=True,
        ),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Floor to Display Data", className="mb-2"),
                        dbc.CardBody([
                            dbc.RadioItems(options=[{"label": "Floor 9", "value": "Floor 9"},
                                                    {"label": "Floor 10", "value": "Floor 10"},
                                                    {"label": "Floor 11", "value": "Floor 11"},
                                                    {"label": "Floor 12", "value": "Floor 12"}],
                                           value="Floor 9", id="floor_radio_control", inline=True,
                                           className="mb-2"),
                        ])
                    ], className="mb-3"),
                ], width=12),
            ]),
            dcc.Store(id='num_bins_store', storage_type='session'),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Character Usage Data Diagram"),
                        dbc.CardBody([
                            dcc.Graph(figure={}, id="floor_utilization_rate_graph"),
                            html.Label("Set number of character display",
                                       style={'fontSize': 18, 'marginBottom': '10px'}),
                            dcc.Slider(
                                id='num_bins_slider',
                                min=1,
                                max=50,
                                step=5,
                                value=15,
                            ),
                        ])
                    ], className="mb-3"),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Data Table"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='data_table',
                                data=df.to_dict('records'),
                                page_size=15,
                                sort_action='native',
                                sort_mode='single',
                                columns=[
                                    {"name": "Character", "id": "Character", "type": "text"},
                                    {"name": "Floor 9", "id": "Floor 9", "type": "numeric",
                                     "format": {"specifier": ".2%"}},
                                    {"name": "Floor 10", "id": "Floor 10", "type": "numeric",
                                     "format": {"specifier": ".2%"}},
                                    {"name": "Floor 11", "id": "Floor 11", "type": "numeric",
                                     "format": {"specifier": ".2%"}},
                                    {"name": "Floor 12", "id": "Floor 12", "type": "numeric",
                                     "format": {"specifier": ".2%"}}
                                ],
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold'
                                },
                                style_cell={
                                    'backgroundColor': 'rgb(255, 255, 255)',
                                    'color': 'black',
                                    'border': '1px solid grey'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ]
                            )

                        ])
                    ], className="mb-3"),
                ], width=6)
            ])
        ], fluid=True),

        dbc.Card([
            dbc.CardHeader("Uploader Info"),
            dbc.CardBody([
                html.Iframe(src='assets/output/uploader_info.html', width='90%', height='900')
            ])
        ], className="mb-3"),

        html.Div([
            html.Span([
                "© 2023 ",
                html.A("Masterain", href="https://github.com/Masterain98", style={'color': 'inherit'}),
                "; Data provided by Hutao API"
            ])
        ], id='mail-footer', style={
            'font-family': 'Roboto-Regular, Helvetica, Arial, sans-serif',
            'width': '100%',
            'display': 'flex',
            'flex-direction': 'column',
            'text-align': 'center',
            'font-size': '11px',
            'color': 'rgb(0 0 0 / 0.54)',
            'line-height': '18px',
        }),
    ])


    # Add controls to build the interaction
    @callback(
        Output(component_id="floor_utilization_rate_graph", component_property='figure'),
        [Input(component_id="floor_radio_control", component_property='value'),
         Input('num_bins_store', 'data')]
    )
    def update_graph(col_chosen: str, num_bins: int):
        # Limit the dataframe to the top num_bins characters
        limited_df = df.nlargest(num_bins, col_chosen)

        # Convert RGB colors to HSV
        gold_rgb = np.array([252, 163, 38]) / 255
        blue_rgb = np.array([89, 200, 228]) / 255
        gold_hsv = mcolors.rgb_to_hsv(gold_rgb)
        blue_hsv = mcolors.rgb_to_hsv(blue_rgb)

        # Create a color array with HSV values
        if num_bins > 1:
            colors_hsv = [(gold_hsv[0] + i / (num_bins - 1) * (blue_hsv[0] - gold_hsv[0]),
                           gold_hsv[1] + i / (num_bins - 1) * (blue_hsv[1] - gold_hsv[1]),
                           gold_hsv[2] + i / (num_bins - 1) * (blue_hsv[2] - gold_hsv[2])) for i in range(num_bins)]
        else:
            colors_hsv = [gold_hsv]

        # Convert HSV colors back to RGB
        colors = ['rgb' + str(tuple(int(j * 255) for j in mcolors.hsv_to_rgb(i))) for i in colors_hsv]

        text_values = [f'{val:.2%}' for val in limited_df[col_chosen]]

        fig = go.Figure(data=[go.Bar(
            x=limited_df['Character'],
            y=limited_df[col_chosen],
            marker_color=colors,  # use the color array here
            marker_line_color='rgb(8,48,107)',  # set the marker line color to dark blue
            marker_line_width=1.5,  # set the marker line width to 1.5
            text=text_values,  # set the text to the y-values
            textposition='outside'  # position the text to be outside the bars
        )])

        fig.update_layout(
            yaxis_tickformat=".0%",
            xaxis={'categoryorder': 'total descending'}
        )

        return fig


    @callback(
        Output('data_table', 'sort_by'),
        Input('floor_radio_control', 'value')
    )
    def update_sorting(floor_value: str):
        return [{'column_id': floor_value, 'direction': 'desc'}]


    @callback(
        Output('num_bins_store', 'data'),
        [Input('num_bins_slider', 'value')]
    )
    def update_num_bins(value):
        return value


    if __name__ == '__main__':
        app.run_server(debug=True)
