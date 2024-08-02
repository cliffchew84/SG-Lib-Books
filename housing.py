from dash import Dash, html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
from utils import data_process as dp
import plotly.graph_objects as go
from datetime import datetime
import dash_ag_grid as dag
import pandas as pd
import numpy as np
import warnings
import requests
import json
warnings.simplefilter(action="ignore", category=FutureWarning)

# Simple parameter to trigger mongoDB instead of using local storage
api_calls = True
if api_calls:
    current_mth = datetime.now().date().strftime("%Y-%m")
    total_periods = [str(i)[:7] for i in pd.date_range(
        "2024-01-01", current_mth + "-01", freq='MS').tolist()]
    recent_periods = total_periods[-6:]

    df_cols = ['month', 'town', 'flat_type', 'block', 'street_name',
               'storey_range', 'floor_area_sqm', 'remaining_lease',
               'resale_price']
    param_fields = ",".join(df_cols)
    base_url = "https://data.gov.sg/api/action/datastore_search?resource_id="
    ext_url = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
    full_url = base_url + ext_url

    recent_df = pd.DataFrame()
    for period in recent_periods:
        params = {
            "fields": param_fields,
            "filters": json.dumps({'month': period}),
            "limit": 10000
        }
        response = requests.get(full_url, params=params)
        mth_df = pd.DataFrame(response.json().get("result").get("records"))
        recent_df = pd.concat([recent_df, mth_df], axis=0)

    # Data Processing
    df = recent_df.copy()
    df.columns = ['month', 'town', 'flat', 'block', 'street_name',
                  'storey_range', 'area_sqm', 'lease_mths', 'price']

    df = dp.process_df_lease_left(df)
    df = dp.process_df_flat(df)

    df['storey_range'] = [i.replace(' TO ', '-') for i in df['storey_range']]
    df['area_sqm'] = df['area_sqm'].astype(np.float16)
    df['price'] = df['price'].astype(np.float32)

    df = df[df['month'] >= '2024-01']
    df['area_sq_ft'] = [round(i, 2) for i in df['area_sqm'] * 10.7639]
    df['price_sq_m'] = [round(i, 2) for i in df['price'] / df['area_sqm']]
    df['price_sq_ft'] = [round(i, 2) for i in df['price'] / df['area_sq_ft']]

    df['lease_mths'] = [i.replace("years", 'yrs') for i in df['lease_mths']]
    df['lease_mths'] = [i.replace("months", 'mths') for i in df['lease_mths']]

    df = df[['month', 'town', 'flat', 'block', 'street_name', 'storey_range',
             'lease_mths', 'area_sqm', 'area_sq_ft', 'price_sq_m',
             'price_sq_ft', 'price']]

    print("Completed data extraction from data.gov.sg")

else:
    # Load data through MongoDB, but I am mindful of storage and costs
    df = pd.read_csv("data/local_df.csv")
    df.rename(columns={'area': 'area_sqm'}, inplace=True)
    df = df[df['month'] >= '2024-01']
    df['area_sq_ft'] = [round(i, 2) for i in df['area_sqm'] * 10.7639]

    df['price_sq_m'] = [round(i, 2) for i in df['price'] / df['area_sqm']]
    df['price_sq_ft'] = [round(i, 2) for i in df['price'] / df['area_sq_ft']]

    df = df[['month', 'town', 'flat', 'block', 'street_name', 'storey_range',
             'lease_mths', 'area_sqm', 'area_sq_ft', 'price_sq_m',
             'price_sq_ft', 'price']]

# Initalise App
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix="/housing/",
)

towns = df.town.unique().tolist()
towns.sort()
towns = ["All",] + towns

flat_type_grps = df["flat"].unique().tolist()
flat_type_grps.sort()

# Data processing for visualisations
# May wanna use polar for lazy evaluation

df["count"] = 1

period = "month"
period_grps = df[period].unique().tolist()
price_max, price_min = df["price"].max(), df["price"].min()
area_max, area_min = df["area_sqm"].max(), df["area_sqm"].min()
legend = dict(orientation="h", yanchor="bottom", y=-0.26, xanchor="right", x=1)
chart_width, chart_height = 500, 450
table_cols = ['month', 'town', 'flat', 'block', 'street_name', 'storey_range',
              'lease_mths', 'area_sqm', 'area_sq_ft', 'price_sq_m',
              'price_sq_ft', 'price']


def df_filter(month, town, flat, area_type, max_area, min_area, price_type,
              max_price, min_price, min_lease, max_lease, street_name,
              data_json):
    """Standardised filtering of df for visualisations"""
    fdf = pd.read_json(data_json, orient="split")

    if street_name:
        fdf = fdf[fdf.street_name.str.contains(street_name, case=False)]

    current_mth = datetime.now().date().strftime("%Y-%m")
    selected_mths = [str(i)[:7] for i in pd.date_range(
        "2024-01-01", current_mth + "-01", freq='MS').tolist()]
    selected_mths = selected_mths[-int(month):]

    fdf = fdf[fdf.month.isin(selected_mths)]
    fdf = fdf[fdf.flat.isin(flat)]
    fdf['lease_yrs'] = [int(i.split("y")[0]) for i in fdf['lease_mths']]
    if min_lease:
        fdf = fdf[fdf.lease_yrs <= int(min_lease)]

    if max_lease:
        fdf = fdf[fdf.lease_yrs >= int(max_lease)]

    if area_type == "Sq M":
        area_type = "area"
    else:
        area_type = "area_sq_ft"

    if price_type == "Price":
        price_type = "price"
    else:
        price_type = "price_sq_ft"

    if town != "All":
        fdf = fdf[fdf.town == town]

    if max_price:
        fdf = fdf[fdf[price_type] <= max_price]

    if min_price:
        fdf = fdf[fdf[price_type] >= min_price]

    if max_area:
        fdf = fdf[fdf[area_type] <= max_area]

    if min_area:
        fdf = fdf[fdf[area_type] >= min_area]

    return fdf


app.layout = html.Div([
    html.Div(
        id="data-store",
        style={"display": "none"},
        children=df.to_json(date_format="iso", orient="split"),
    ),
    html.H2(
        children="These are Homes, Truly",
        style={"textAlign": "left", "padding-top": "10px",
               "padding-right": "10px", "padding-left": "10px",
               "color": "#555"},
    ),
    dcc.Markdown(
        """
        Explore Singapore's most recent past public housing transactions
        effortlessly with our site! Updated daily with data from data.gov.sg
        through their API service, our tool allows you access to the latest
        information public housing resale data provided by HDB. Currently,
        the data is taken as is, and may not reflect the latest public housing
        transactions reported by the media.

        We built this tool to help you conduct research on the Singapore public
        housing resale market for any purpose, whether you're a prospective
        buyer, seller, or someone just curious about how much your neighbours
        are selling their public homes! Beyond a table of transactions, we have
        included a scatter plot to compare home prices with their price per
        area ( sq metre / sq feet ) and a boxplot distribution of home prices
        or price per area.

        This website is best view on a desktop. Doing property research on
        your phone will be such a pain!

        Also, if you are interested in how our Singapore public housing resale
        market has been trending in the past few years, visit my other
        dashboard, [SG Public Housing Dashboard](https://cliffchew84.github.io/profile/hdb-housing.html"),
        where I cover share broader public housing resale trends, outliers
        and price category breakdowns.""",
        style={"textAlign": "left", "color": "#555", "padding": "5px"},
    ),
    dbc.Row([
        dbc.Col(
            dbc.Button(
                "Filters",
                id="collapse-button",
                className="mb-3",
                color="danger",
                n_clicks=0,
                style={"verticalAlign": "top"}
            ),
            width="auto"
        ),
        dbc.Col(
            html.P(
                id="dynamic-text",
                style={"textAlign": "center", "padding-top": "10px"}
            ),
            width="auto"
        ),
        dbc.Col(
            dbc.Button(
                "Caveats",
                id="collapse-caveats",
                className="mb-3",
                color="danger",
                n_clicks=0,
                style={"verticalAlign": "top"}
            ),
            width="auto"
        ),
    ], justify="center"),
    dbc.Collapse(
        dbc.Card(
            dbc.CardBody([
                dcc.Markdown("""
                1. Area provided by HDB is in square metres. Calculations for
                square feet are done by taking square metres by 10.7639.
                2. Lease left is calculated from remaining lease provided by
                HDB.
                3. Data is taken from HDB as is. This data source seems
                slower that transactions reported in the media.
                4. Information provided here is only meant for research, and
                shouldn't be seen as financial advice.""")
            ], style={"textAlign": "left", "color": "#555", "padding": "5px"}),
        ),
        id="caveats",
        is_open=False,
    ),
    dbc.Collapse(
        dbc.Card(dbc.CardBody([
            html.Div([
                html.Div([
                    html.Label("Months"),
                    dcc.Dropdown(options=[3, 6], value=6, id="month")
                ], style={"display": "inline-block",
                          "width": "7%", "padding": "10px"},
                ),
                html.Div([
                    html.Label("Town"),
                    html.Div(dcc.Dropdown(
                        options=towns, value="All", id="town")),
                ], style={"display": "inline-block",
                          "width": "18%", "padding": "10px"},
                ),
                html.Div([
                    html.Label("Flats"),
                    dcc.Dropdown(multi=True, options=flat_type_grps,
                         value=flat_type_grps, id="flat"),
                ], style={"display": "inline-block",
                          "width": "35%", "padding": "10px"},
                ),
                html.Div([
                    html.Label("Min Lease [Yrs]"),
                    dcc.Input(type="number",
                              placeholder="Add No.",
                              style={"display": "flex",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              id="min_lease"),
                ], style={"display": "flex",  "flexDirection": "column",
                          "width": "12%", "padding": "10px",
                          "verticalAlign": "top"}),
                html.Div([
                    html.Label("Max Lease [Yrs]"),
                    dcc.Input(type="number",
                              placeholder="Add No.",
                              style={"display": "flex",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              id="max_lease"),
                ], style={"display": "flex",  "flexDirection": "column",
                          "width": "12%", "padding": "10px",
                          "verticalAlign": "top"},
                )
            ], style={"display": "flex", "flexDirection": "row",
                      "alignItems": "center"}
            ),
            # Area inputs
            html.Div([
                html.Div([
                    html.Label("Sq Feet | Sq M"),
                    html.Div(dcc.Dropdown(options=['Sq M', "Sq Feet"],
                                          value="Sq Feet", id="area_type")),
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "12%", "padding": "10px"},
                ),
                html.Div([
                    html.Label("Min Area"),
                    dcc.Input(type="number",
                              placeholder="Add No.",
                              style={"display": "inline-block",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              id="min_area"),
                ], style={"display": "flex",  "flexDirection": "column",
                          "width": "12%", "padding": "5px"},
                ),
                html.Div([
                    html.Label("Max Area"),
                    dcc.Input(type="number",
                              placeholder="Add No.",
                              style={"display": "inline-block",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              id="max_area"),
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "12%", "padding": "5px"},
                ),
                html.Div([
                    html.Label("Price | Price / Area"),
                    dcc.Dropdown(options=['Price', "Price / Area"],
                         value="Price", id="price_type"),
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "12%", "padding": "5px"},
                ),
                html.Div([
                    html.Label("Min Price | Price / Area"),
                    dcc.Input(type="number",
                              placeholder="Add No.",
                              style={"display": "inline-block",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              id="min_price"),
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "15%", "padding": "5px"},
                ),
                html.Div([
                    html.Label("Max Price | Price / Area"),
                    dcc.Input(type="number",
                              style={"display": "inline-block",
                                     "border-color": "#E5E4E2",
                                     "padding": "5px"},
                              placeholder="Add No.",
                              id="max_price"),
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "15%", "padding": "5px"},
                ),
                html.Div([
                    html.Label("Submit"),
                    html.Button('Submit', id='submit-button',
                                style={"display": "inline-block",
                                       "border-color": "#E5E4E2",
                                       "padding": "5px"},
                                )
                ], style={"display": "flex", "flexDirection": "column",
                          "width": "8%", "padding": "5px"},
                )
            ], style={"display": "flex", "flexDirection": "row",
                      "alignItems": "center"}),
            html.Div([
                html.Label("""Search by Street Name
        ( Add | separator to include >1 street name )"""),
                dcc.Input(type="text",
                          style={"display": "inline-block",
                                 "border-color": "#E5E4E2",
                                 "padding": "5px"},
                          placeholder="Type the Street Name here",
                          id="street_name"),
            ], style={"display": "flex", "flexDirection": "column",
                      "width": "45%", "padding": "5px"},
            ),
        ]
        )),
        id="collapse",
        is_open=True,
    ),
    # Text box to display dynamic content
    html.Div([
        html.Div([
            dcc.Loading([
                html.Div([
                    html.H3(
                        "Filtered Public Housing Transactions",
                        style={
                            "font-size": "15px",
                            "textAlign": "left",
                            "margin-top": "20px",
                        },
                    ),
                    dag.AgGrid(
                        id="price-table",
                        columnDefs=[
                            {"field": x, "sortable": True} for x in table_cols
                        ],
                        rowData=df[table_cols].to_dict("records"),
                        className="ag-theme-balham",
                        # columnSize="sizeToFit",
                        columnSize="responsiveSizeToFit",
                        dashGridOptions={
                            "pagination": True,
                            "paginationAutoPageSize": True,
                        },
                    ),
                ], style={
                    "height": chart_height,
                    "width": 1200,
                    "padding": "5px",
                    "display": "inline-block",
                },
                )])
        ], style=dict(display="flex"),
        ),
        dcc.Loading([
            html.Div([
                dcc.Graph(id="g0", style={
                    "display": "inline-block", "width": "50%"}),
                dcc.Graph(id="g1", style={
                    "display": "inline-block", "width": "50%"}),
            ]
            )])
    ],
        style={"display": "flex",
               "flexDirection": "column",
               "justifyContent": "center",
               "alignItems": "center",
               "minHeight": "100vh",
               "textAlign": "center",
               }
    )
])


# Standardised Dash Input-Output states
new_input_list = Input('submit-button', 'n_clicks'),
new_state_list = [
    State('month', 'value'),
    State('town', 'value'),
    State('flat', 'value'),
    State('area_type', 'value'),
    State('max_area', 'value'),
    State('min_area', 'value'),
    State('price_type', 'value'),
    State('max_price', 'value'),
    State('min_price', 'value'),
    State('max_lease', 'value'),
    State('min_lease', 'value'),
    State('street_name', 'value'),
    State('data-store', 'children')
]


@callback(Output("price-table", "rowData"), new_input_list, new_state_list)
def update_table(n_clicks, month, town, flat, area_type, max_area, min_area,
                 price_type, max_price, min_price, max_lease, min_lease,
                 street_name, data_json):
    fdf = df_filter(month, town, flat, area_type, max_area, min_area,
                    price_type, max_price, min_price, max_lease, min_lease,
                    street_name, data_json)

    records = fdf.shape[0]
    print(month, town, flat, area_type, max_area, min_area,
          price_type, max_price, min_price, max_lease, min_lease,
          street_name, records)

    return fdf.to_dict("records")


@callback(Output("dynamic-text", "children"), new_input_list, new_state_list)
def update_text(n_clicks, month, town, flat, area_type, max_area, min_area,
                price_type, max_price, min_price, max_lease, min_lease,
                street_name, data_json):
    # Construct dynamic text content based on filter values

    fdf = df_filter(month, town, flat, area_type, max_area, min_area,
                    price_type, max_price, min_price, max_lease, min_lease,
                    street_name, data_json)

    records = fdf.shape[0]

    if price_type == 'Price' and area_type == 'Sq M':
        price_min = fdf.price.min()
        price_max = fdf.price.max()

        area_min = fdf.area_sqm.min()
        area_max = fdf.area_sqm.max()

    elif price_type == 'Price' and area_type == 'Sq Feet':
        price_min = fdf.price.min()
        price_max = fdf.price.max()

        area_min = fdf.area_sq_ft.min()
        area_max = fdf.area_sq_ft.max()

    elif price_type == "Price / Area" and area_type == "Sq M":
        price_min = fdf.price_sq_m.min()
        price_max = fdf.price_sq_m.max()

        area_min = fdf.area_sqm.min()
        area_max = fdf.area_sqm.max()
        price_type = 'Price / Sq M'

    elif price_type == "Price / Area" and area_type == "Sq Feet":
        price_min = fdf.price_sq_ft.min()
        price_max = fdf.price_sq_ft.max()

        area_min = fdf.area_sq_ft.min()
        area_max = fdf.area_sq_ft.max()
        price_type = 'Price / Sq Feet'

    dynamic_text = f"""<b>You searched : </b>
    <b>Town</b>: {town} |
    <b>{price_type}</b>: ${price_min:,} - ${price_max:,} |
    <b>{area_type}</b>: {area_min:,} - {area_max:,}
    """

    if min_lease and max_lease:
        dynamic_text += f" | <b>Lease from</b> {min_lease:,} - {max_lease:,}"
    elif min_lease:
        dynamic_text += f" | <b>Lease >= </b> {min_lease:,}"
    elif max_lease:
        dynamic_text += f" | <b>Lease =< </b> {max_lease:,}"

    if records != 0:
        dynamic_text += f" | <b>Total records</b>: {records:,}"
    else:
        dynamic_text += " | <b>Your search created no results</b>"

    return dcc.Markdown(dynamic_text, dangerously_allow_html=True)


@callback(Output("g0", "figure"), new_input_list, new_state_list)
def update_g0(n_clicks, month, town, flat, area_type, max_area, min_area,
              price_type, max_price, min_price, max_lease, min_lease,
              street_name, data_json):
    fdf = df_filter(month, town, flat, area_type, max_area, min_area,
                    price_type, max_price, min_price, max_lease, min_lease,
                    street_name, data_json)

    price_area = 'price_sq_m'
    price_label = 'Sq M'

    customdata_set = list(fdf[['town', 'street_name', 'lease_mths', 'area_sqm']
                              ].to_numpy())

    if area_type != "Sq M":
        price_area = 'price_sq_ft'
        price_label = 'Sq Ft'
        customdata_set = list(fdf[['town', 'street_name', 'lease_mths',
                                   'area_sq_ft']].to_numpy())

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=fdf['price'],  # unchanged
            x=fdf[price_area],
            customdata=customdata_set,
            hovertemplate='<i>Price:</i> %{y:$,}<br>' +
            '<i>Area:</i> %{customdata[3]:,}<br>' +
            '<i>Price/Area:</i> %{x:$,}<br>' +
            '<i>Town :</i> %{customdata[0]}<br>' +
            '<i>Street Name:</i> %{customdata[1]}<br>' +
            '<i>Lease Left:</i> %{customdata[2]}',
            mode='markers',
            marker_color="rgb(8,81,156)",
        )
    )
    fig.update_layout(
        title=f"Home Prices vs Prices / {price_label}",
        yaxis={"title": "Home Prices"},
        xaxis={"title": f"Prices / {price_label}"},
        width=chart_width,
        height=chart_height,
        showlegend=False,
    )
    return fig


@callback(Output("g1", "figure"), new_input_list, new_state_list)
def update_g1(n_clicks, month, town, flat, area_type, max_area, min_area,
              price_type, max_price, min_price, max_lease, min_lease,
              street_name, data_json):
    fdf = df_filter(month, town, flat, area_type, max_area, min_area,
                    price_type, max_price, min_price, max_lease, min_lease,
                    street_name, data_json)

    price_area = 'price_sq_m'
    price_label = 'Sq M'

    if area_type != "Sq M":
        price_area = 'price_sq_ft'
        price_label = 'Sq Ft'

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            y=fdf[price_area],
            name="Selected Homes",
            boxpoints="outliers",
            marker_color="rgb(8,81,156)",
            line_color="rgb(8,81,156)",
        )
    )
    fig.update_layout(
        title=f"Home Prices / {price_label}",
        yaxis={"title": f"Prices / {price_label}"},
        xaxis={"title": f"{price_label}"},
        width=chart_width,
        height=chart_height,
        showlegend=False,
    )
    return fig


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("caveats", "is_open"),
    [Input("collapse-caveats", "n_clicks")],
    [State("caveats", "is_open")],
)
def toggle_caveat(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run(debug=True)
