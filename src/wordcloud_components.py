from wordcloud import WordCloud
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objs as go
from src.nlp import Extractor


def plotly_wordcloud(data_frame):
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""
    complaints_text = list(data_frame.dropna().values)
    extractor = Extractor()

    if len(complaints_text) < 1:
        return {}, {}, {}

    word_frequency = extractor.get_top_keywords(data_frame)
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
    return frequency_figure_data, treemap_figure


WORDCLOUD_DASH_PLOTS = [
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
                        [
                            dcc.Loading(
                                id="loading-frequencies",
                                children=[dcc.Graph(id="frequency_figure")],
                                type="default",
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id="loading-treemap",
                                children=[dcc.Graph(id="bank-treemap")],
                                type="default",
                            )
                        ]
                    ),
                ]
            )
        ]
    ),
]
