import dash_leaflet as dl
from . import data_process as dp


def icon_html(icon: str, color: str, bg: str) -> str:
    """ Create standardised icon for Dash Plotly Map """

    return f"""<i class="fa-solid fa-{icon}"
            style="color: {color}; background:{bg};
            border: 2px solid {color}; font-size:1.2em;
            border-radius: 50%; height: 24px; width: 24px;
            display: flex; align-items: center; justify-content: center;"
            ></i>"""


def popup_tooltip(message: str):
    """ Use when I want Tooltip == Popup """
    return [dl.Tooltip(content=message), dl.Popup(content=message)]


def create_layer_grp(input_list: list, name: str):
    """ Simpler way to create LayerGroups """
    return dl.Overlay(dl.LayerGroup(input_list), name=name, checked=True)


def output_table_format(msg: list, varname: str):
    """ Format marker info into result table output """
    msg = "".join([i.replace('div', 'li') for i in msg])
    msg = "<ul>" + msg + "</ul>"
    msg = f"<h4>Nearest {varname}</h4>" + msg
    return msg


def create_location_map_layer(df, search_pt, boundary, icon_fun,
                              icon_color, final_msg, mp, marker_name):
    """ Takes multiple inputs to produce a map layer of certain attributions,
    such as subway or attractions. Output includes a map layer and result
    table that lists the proximity of all selected markers
    """
    tmp = dp.table_select_from_pt(df, search_pt, radius=boundary)
    if tmp.shape[1] != 0:
        stations = dict()
        table_msg = list()
        for i in range(tmp.shape[0]):

            # Set important marker & route info
            pt_info = tmp.loc[i]['loc_info']
            pt_lat = tmp.loc[i]['LATITUDE']
            pt_lon = tmp.loc[i]['LONGITUDE']

            route_list, total_d = dp.create_route(search_pt, (pt_lat, pt_lon))
            tooltip_msg = f"<div>To {pt_info} - <b>{total_d:,.0f}m</b></div>"

            table_msg.append(tooltip_msg)
            mrt_route = dl.Polyline(positions=route_list, interactive=True,
                                    weight=5, color=icon_color)

            mrt_pt = dl.DivMarker(position=(pt_lat, pt_lon),
                                  children=popup_tooltip(tooltip_msg),
                                  iconOptions=icon_fun)

            stations[pt_info] = [mrt_pt, mrt_route]

        # Loop through station map features
        for s in list(stations.keys()):
            tmp = create_layer_grp(stations[s], name=s)
            mp.append(tmp)

        if final_msg:
            final_msg += output_table_format(table_msg, marker_name)
        else:
            final_msg = output_table_format(table_msg, marker_name)

        return mp, final_msg
