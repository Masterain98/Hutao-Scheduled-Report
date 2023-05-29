from MysqlConn import MysqlConn
import json
import plotly.express as px
import pandas as pd
import plotly.io as pio
from datetime import datetime
import plotly.graph_objects as go
import os

# MySQL Settings
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
db = MysqlConn(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


def user_per_schedule_bar():
    sql = r"SELECT Data FROM `spiral_abysses_statistics` WHERE Name='Overview';"
    sql_result = db.fetch_all(sql)
    if sql_result is None:
        return None
    else:
        history_stat = []
        for schedule in list(sql_result):
            this_schedule_stat = json.loads(schedule[0])
            history_stat.append({
                "ScheduleId": this_schedule_stat["ScheduleId"],
                "SpiralAbyssTotal": this_schedule_stat["SpiralAbyssTotal"],
                "SpiralAbyssFullStar": this_schedule_stat["SpiralAbyssFullStar"]
            })
    history_stat = history_stat[:6]
    fig = px.bar(history_stat, x="ScheduleId", y=["SpiralAbyssTotal", "SpiralAbyssFullStar"],
                 barmode='group', text_auto=True,
                 labels={"ScheduleId": "Schedule Number",
                         "value": "Total Count"},
                 color_discrete_map={
                     "SpiralAbyssTotal": "darkcyan",
                     "SpiralAbyssFullStar": "cornflowerblue"
                 })
    fig.update_layout(title="Recent Six Schedule Abyss Upload Stat", title_x=0.5)
    pio.write_html(fig, file="output/user_per_schedule_bar.html", auto_open=True, include_plotlyjs="cdn",
                   include_mathjax="cdn")


def uid_layout():
    sql = r"SELECT Uid, UploadTime, Uploader FROM records RIGHT JOIN spiral_abysses ON " \
          r"records.PrimaryId=spiral_abysses.RecordId"
    sql_result = db.fetch_all(sql)

    # Option 1
    # This is a straight forward option, good for single chart but too hard for extensions.
    """
    china_uid_list = [{"UID": int(item[0][:3]), "Time": datetime.fromtimestamp(item[1]), "Uploader": item[2]} for item
                      in list(sql_result) if item[0].startswith(("1", "2"))]
    fig = px.scatter(data_frame=china_uid_list, y="Time", x="UID", color="Uploader", color_discrete_map=uploader_color,
                     labels={
                         "UID": "Starting Number of UID",
                         "Time": "Datetime"
                     })
    
    # For UID Group charts              
    uid_group_count = {}
    for record in china_uid_list:
        this_uid_group = record["UID"]
        if this_uid_group not in uid_group_count.keys():
            uid_group_count[this_uid_group] = 1
        else:
            uid_group_count[this_uid_group] += 1

    fig = go.Figure()
    fig.add_bar(x=list(uid_group_count.keys()), y=list(uid_group_count.values()))
    fig.update_layout()
    fig.show()
    """

    # Option 2
    # Convert SQL result into a dataframe, add charts into trace.
    # Plotly Graph Object (go) is a basic library of Plotly Express (px)

    df = pd.DataFrame(list(sql_result))
    df.rename(columns={0: "UID", 1: "Time", 2: "Uploader"}, inplace=True)
    df["Time"] = [datetime.fromtimestamp(x) for x in df["Time"]]
    df.UID = df.UID.str.slice(stop=3).astype(int)

    df_sh = df[df.Uploader == "Snap Hutao"]
    df_miao = df[df.Uploader == "miao-plugin"]
    df_sh_bm = df[df.Uploader == "Snap Hutao Bookmark"]
    df_dict = {
        "Snap Hutao": df_sh,
        "Snap Hutao Bookmark": df_sh_bm,
        "miao-plugin": df_miao
    }

    uploader_color = {
        "Snap Hutao": "rgb(239,85,59)",
        "Snap Hutao Bookmark": "rgb(0,204,150)",
        "miao-plugin": "rgb(99,110,250)"
    }
    uid_group = [("1", "2"), "5", "6", "7", "8", "9"]
    fig = go.Figure()
    for uid in uid_group:
        for k, v in df_dict.items():
            fig.add_trace(
                go.Scatter(
                    x=v[v.UID.astype(str).str.startswith(uid)]["UID"],
                    y=v[v.UID.astype(str).str.startswith(uid)]["Time"],
                    name=k,
                    mode="markers",
                    marker=dict(color=v[v.UID.astype(str).str.startswith(uid)]["Uploader"].apply(
                        lambda x: uploader_color[x]))
                )
            )

    # Add dropdowns
    button_layer_1_height = 1.08
    fig.update_layout(showlegend=False, title="Uploader UID Information by Time",
                      title_x=0.5)
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{"visible": [True, True, True,
                                           True, True, True,
                                           True, True, True,
                                           True, True, True,
                                           True, True, True,
                                           True, True, True
                                           ]},
                              {"showlegend": False},
                              dict(text="Uploader UID Information by Time (All Regions)")],
                        label="All",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [True, True, True,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False
                                           ]},
                              {"showlegend": True},
                              dict(text="Uploader UID Information by Time (Mainland China)")],
                        label="China",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False,
                                           True, True, True,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False
                                           ]},
                              {"showlegend": True},
                              {"title_text": "Uploader UID Information by Time (bilibili @ Mainland China)"}],
                        label="bilibili",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False,
                                           False, False, False,
                                           True, True, True,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False
                                           ]},
                              {"showlegend": True},
                              {"title_text": "Uploader UID Information by Time (America)"}],
                        label="America",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           True, True, True,
                                           False, False, False,
                                           False, False, False
                                           ]},
                              {"showlegend": True},
                              {"title_text": "Uploader UID Information by Time (Europe)"}],
                        label="EU",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           True, True, True,
                                           False, False, False
                                           ]},
                              {"showlegend": True},
                              {"title_text": "Uploader UID Information by Time (Asia)"}],
                        label="Asia",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           False, False, False,
                                           True, True, True
                                           ]},
                              {"showlegend": True},
                              {"title_text": "Uploader UID Information by Time (Taiwan/Hong Kong/Macau)"}],
                        label="TW/HK/MO",
                        method="update"
                    ),
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top"
            ),
        ]
    )

    pio.write_html(fig, file="output/uploader_info.html", auto_open=True, include_plotlyjs="cdn",
                   include_mathjax="cdn")


if __name__ == "__main__":
    user_per_schedule_bar()
    uid_layout()
