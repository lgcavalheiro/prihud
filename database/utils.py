'''
Module that provideds several utility function for the database app.
'''

from threading import Thread
import plotly.express as px
from plotly.offline import plot


class ChartThread(Thread):
    ''' Base class for generating charts using multithreading '''

    data_frame, product_name, result = None, None, None

    def __init__(self, data_frame, product_name):
        super().__init__()
        self.data_frame = data_frame
        self.product_name = product_name

    def _update_common_layout(self, figure, title):
        figure.update_layout(
            title=title,
            paper_bgcolor='#18232C',
            font={"color": 'rgb(213, 220, 226)'},
            legend={"font": {"size": 10}})

    def run(self):
        raise NotImplementedError

    def join(self, timeout = None):
        Thread.join(self)
        return self.result


class LineChartThread(ChartThread):
    ''' Class for generating line charts using multithreading '''

    def run(self):
        line_fig = px.line(self.data_frame, x='Collection date',
                           y='Price', color='Alias', markers=True)

        line_fig.for_each_trace(
            lambda trace: trace.update(name=f'{trace.name[:45]}...'))

        self._update_common_layout(
            line_fig, f'{self.product_name} - Price history')

        self.result = plot(line_fig, output_type='div')


class ScatterPlotThread(ChartThread):
    ''' Class for generating scatter plots using multithreading '''

    def run(self):
        scatter_df = self.data_frame.groupby('Alias', as_index=False)[
            'Price'].mean().round(2)

        fig_scatter = px.scatter(
            scatter_df, y="Price", x="Price", color="Alias")

        self._update_common_layout(
            fig_scatter, f'{self.product_name} - Price clusters (mean)')

        fig_scatter.update_traces(marker_size=10)
        fig_scatter.update_layout(scattermode="group", scattergap=0.75)
        fig_scatter.update_xaxes(visible=False)
        fig_scatter.for_each_trace(
            lambda trace: trace.update(name=f'{trace.name[:45]}...'))

        self.result = plot(fig_scatter, output_type='div')


def generate_price_history_charts(data_frame, product_name):
    ''' Function that generates all charts used in the price history view '''

    charts = {}
    scatter = ScatterPlotThread(data_frame, product_name)
    line = LineChartThread(data_frame, product_name)

    line.start()
    scatter.start()

    charts['line_chart'] = line.join()
    charts['scatter_plot'] = scatter.join()

    return charts
