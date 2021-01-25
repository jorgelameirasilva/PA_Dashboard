import dash 
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
from db_consumer import find_in_db
from portfolio_allocation import get_allocations
import pandas as pd

table_columns = ["ETF", "Weight", "Position(Shares)"]

app = dash.Dash(__name__)
server = app.server


etf_description_df = find_in_db("etf_description")

etf_description_df = etf_description_df[etf_description_df["symbol"].str.endswith("US_5")]

app.layout = html.Div([
    html.H1("Portfolio Optimization"),

    dcc.Dropdown(
            id="etf-names-drop",
            options = [{"label": "All", "value":"All"}] + [{"label":x, "value": x} for x in set(etf_description_df["description"].values)], 
            multi=True
        ),
    html.P(id="warning-etfs"),
    dcc.Slider(id="steps", 
                    min=10000,
                    max=100000000,
                    step=1000,
                    value=100000),

    html.P(id="prt-value"),
    html.Div([
        
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in table_columns]
    ),
        html.Div([
            html.P(id="annual-return", children=["Expected Annual Return"] ),
            html.P(id="annual-vol", children=["Annual Volitility"]),
            html.P(id="sharpe", children=["Sharpe Ratio"])
             
            
        ],id="results")

    ], className="bottom-div")

])

@app.callback(
    [ Output("table", "data"), Output("prt-value", "children"), Output("warning-etfs", "children"), Output("annual-return", "children"), Output("annual-vol", "children")
    , Output("sharpe", "children")],
    [Input("etf-names-drop", "value"),  Input("steps", "value")]
)
def update_weights_table(v, portfolio_value):
    if v == None:
        return pd.DataFrame().to_dict("records"),  f"Portfolio Value: {portfolio_value:,} Dollars",  "You have to Pick at least 3 etfs to start the asset allocation !", "", "", ""

    tickers_list = []
    if len(v) >2:
        for i in v:
            symb  = etf_description_df[etf_description_df["description"] == i]["symbol"].values[0]
            tickers_list.append(symb)
        allocations, performance = get_allocations(tickers_list, portfolio_value)

        ret = f"Expected Annual Return: {performance['return'].values[0] * 100:.2f}%"
        vol = f"Annual Volitility: {performance['vol'].values[0]* 100:.2f}%"
        sharpe = f"Sharpe Ratio: {performance['sharpe'].values[0]* 100:.2f}%"


        return allocations.to_dict("records"), f"Portfolio Value: {portfolio_value:,} Dollars", "", ret, vol, sharpe

    return pd.DataFrame().to_dict("records"),  f"Portfolio Value: {portfolio_value:,} Dollars", "You have to Pick at least 3 etfs to start the asset allocation !", "", "", ""


if __name__ == "__main__":
    app.run_server(debug=True)