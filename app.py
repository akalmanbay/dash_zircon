from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# from asinparser import AsinParser
import pandas as pd
import dash_bootstrap_components as dbc

from src.wordcloud_components import plotly_wordcloud, WORDCLOUD_DASH_PLOTS

# get df from db
df = pd.read_csv("data/aws_reviews_sample.csv")
app = Dash(__name__)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("Bank Customer Complaints", className="ml-2")
                    ),
                ],
                align="center",
                # no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

BODY = dbc.Container(
    [dbc.Card(WORDCLOUD_DASH_PLOTS)],
    className="mt-12",
)

app.layout = html.Div(
    [
        html.Div(["Import ASIN or ASINS: ", dcc.Input(type="text", id="asin-input")]),
        html.Button("Submit", id="submit-button"),
        html.Div(id="print-reviews-output"),
        html.Div(children=[BODY]),
    ]
)


@app.callback(
    [
        Output("bank-wordcloud", "figure"),
        Output("frequency_figure", "figure"),
        Output("bank-treemap", "figure"),
        Output("no-data-alert", "style"),
    ],
    Input("submit-button", "n_clicks"),
    State("asin-input", "value"),
)
def print_reviews(n_clicks, asin):

    if n_clicks == 0:
        return None
    # if asin is None:
    #     return None
    asin = "B09S6FWS7W"
    global df
    df_asin = df[df["asin"] == asin]
    # if df_asin.empty:
    #     df_asin = parse_reviews(asin)

    local_df = df_asin["review"]
    wordcloud, frequency_figure, treemap = plotly_wordcloud(local_df)
    alert_style = {"display": "none"}
    if (wordcloud == {}) or (frequency_figure == {}) or (treemap == {}):
        alert_style = {"display": "block"}
    print("redrawing bank-wordcloud...done")
    return (wordcloud, frequency_figure, treemap, alert_style)


# def parse_reviews(asin):
#     global df
#     asin_parser = AsinParser()
#     df_asin = pd.DataFrame(asin_parser.get_reviews(asin))
#     df_asin['asin'] = asin
#     df = pd.concat([df, df_asin])
#     # save df to db
#     # df.to_csv('aws_reviews_sample.csv')
#     return df_asin

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True)
