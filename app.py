from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from flask_caching import Cache
# from asinparser import AsinParser
from wordcloud import WordCloud
import pandas as pd
import os
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from nlp import get_top_keywords

def plotly_wordcloud(data_frame):
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""
    complaints_text = list(data_frame.dropna().values)

    if len(complaints_text) < 1:
        return {}, {}, {}

    # join all documents in corpus
    text = " ".join(list(complaints_text))

    word_frequency = get_top_keywords(data_frame)
    word_cloud = WordCloud(max_words=100, max_font_size=90)
    word_cloud.generate_from_frequencies(word_frequency)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[0])
        y_arr.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        textposition="top center",
        hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 250],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 450],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}
    word_list_top = word_list[:25]
    word_list_top.reverse()
    freq_list_top = freq_list[:25]
    freq_list_top.reverse()

    frequency_figure_data = {
        "data": [
            {
                "y": word_list_top,
                "x": freq_list_top,
                "type": "bar",
                "name": "",
                "orientation": "h",
            }
        ],
        "layout": {"height": "550", "margin": dict(t=20, b=20, l=100, r=20, pad=4)},
    }
    treemap_trace = go.Treemap(
        labels=word_list_top, parents=[""] * len(word_list_top), values=freq_list_top
    )
    treemap_layout = go.Layout({"margin": dict(t=10, b=10, l=5, r=5, pad=4)})
    treemap_figure = {"data": [treemap_trace], "layout": treemap_layout}
    return wordcloud_figure_data, frequency_figure_data, treemap_figure

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

WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("Most frequently used words in complaints")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-frequencies",
                            children=[dcc.Graph(id="frequency_figure")],
                            type="default",
                        )
                    ),
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Treemap",
                                        children=[
                                            dcc.Loading(
                                                id="loading-treemap",
                                                children=[dcc.Graph(id="bank-treemap")],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Wordcloud",
                                        children=[
                                            dcc.Loading(
                                                id="loading-wordcloud",
                                                children=[
                                                    dcc.Graph(id="bank-wordcloud")
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=8,
                    ),
                ]
            )
        ]
    ),
]

BODY = dbc.Container(
    [
        
        dbc.Card(WORDCLOUD_PLOTS)
    ],
    className="mt-12",
)


# get df from db
df = pd.read_csv('data/aws_reviews_sample.csv')
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        "Import ASIN or ASINS: ",
        dcc.Input(type='text', id='asin-input')
    ]),
    html.Button('Submit', id='submit-button'),
    html.Div(id='print-reviews-output'),

    html.Div(children=[BODY])
])

@app.callback(
       [
        Output("bank-wordcloud", "figure"),
        Output("frequency_figure", "figure"),
        Output("bank-treemap", "figure"),
        Output("no-data-alert", "style"),
    ],
    Input('submit-button', 'n_clicks'),
    State('asin-input', 'value')
)
def print_reviews(n_clicks, asin):
    
    if n_clicks==0:
        return None
    # if asin is None:
    #     return None
    asin = 'B09S6FWS7W'
    global df
    df_asin = df[df['asin'] == asin]
    # if df_asin.empty:
    #     df_asin = parse_reviews(asin)
    
    local_df = df_asin['review']
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

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
