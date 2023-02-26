'''
Module that provideds several utility function for the database app.
'''

import plotly.express as px
from plotly.offline import plot


def __update_common_layout(figure, title):
    figure.update_layout(
        title=title,
        paper_bgcolor='#18232C',
        font={"color": 'rgb(213, 220, 226)'},
        legend={"font": {"size": 10}})


def __generate_line_chart(data_frame, product_name):
    line_fig = px.line(data_frame, x='Collection date', y='Price',
                       color='Alias', markers=True)
    line_fig.for_each_trace(lambda trace: trace.update(
        name=f'{trace.name[:45]}...'))
    __update_common_layout(line_fig, f'{product_name} - Price history')

    return plot(line_fig, output_type='div')


def __generate_scatter_plot(data_frame, product_name):
    scatter_df = data_frame.groupby('Alias', as_index=False)[
        'Price'].mean().round(2)

    fig_scatter = px.scatter(scatter_df, y="Price", x="Price", color="Alias")

    __update_common_layout(
        fig_scatter, f'{product_name} - Price clusters (mean)')

    fig_scatter.update_traces(marker_size=10)
    fig_scatter.update_layout(scattermode="group", scattergap=0.75)
    fig_scatter.update_xaxes(visible=False)
    fig_scatter.for_each_trace(
        lambda trace: trace.update(name=f'{trace.name[:45]}...'))

    return plot(fig_scatter, output_type='div')


def generate_price_history_charts(data_frame, product_name):
    ''' Function that generates all charts used in the price history view '''

    charts = {}
    charts['line_chart'] = __generate_line_chart(data_frame, product_name)
    charts['scatter_plot'] = __generate_scatter_plot(data_frame, product_name)

    return charts
