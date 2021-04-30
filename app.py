import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# model
from model import prediction
from sklearn.svm import SVR

def get_stock_price_fig(df):

    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")

    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig


external_stylesheet = [
    {
        'href': 'assets/style.css',
        'rel': 'stylesheet'
    }
]

# create a dash instance
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
server = app.server

app.layout = html.Div([

    html.Div(
        [
            html.P("Welcome to STOCK-DASH", className="start"),
            html.Div([
                # stock code input
                html.P('Enter stock code: '),
                dcc.Input(id='input', type='text'),
                html.Button('Submit', id='button'),
            ], className="stock_code"),
            html.Div([
                # date range picker input
                html.P('Enter time duration: '),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=dt(2021, 1, 1),
                    end_date=dt(2021, 3, 1),
                )
            ], className="date_picker"),
            html.Div([
                # stock price button
                html.Button('Stock Price', id='stock_button'),

                # indicator buttons
                html.Button('Indicators', id='indicator_button'),

                # number of days of forecast input
                dcc.Input(id='number_of_days', type='text'),
                                   
                # forecast button
                html.Button('Forecast', id='forecast_button'),
            ], className="forecast"),
        ],
        className="inputs"),

    html.Div(
        [
            html.Div([
                html.Img(id="logo"),
                html.P(id="ticker") 
            ], 
            className="header"),

            html.Div(
                # description
                id="description", className="description_ticker"
            ),

            html.Div([
                # stock price plot
            ], id="graphs-content"),

            html.Div([
                # Indicator plot
            ], id="main-content"),

            html.Div([
                # forecast plot
            ], id="forecast-content"),
        ],
        className="content"),
],
className="container")


#callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        return "Please enter a legitimate stock code to get details."
        # raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None


# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
