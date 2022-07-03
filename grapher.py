from bokeh.io import show, export_svgs, export_png
from bokeh.models import HoverTool, PrintfTickFormatter, Span, Scatter, ColumnDataSource, Text, Range1d, Label
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider
import numpy as np
import pandas as pd
from utils import deg2rad
TOOLS = 'tap,save,pan,box_zoom,reset,wheel_zoom'
LINE_WIDTH = 3

class Colors:
  def __init__(self):
    self.clrmap = {'Equinox': 'red',
                   'Solstice': 'gold',
                   'Zenith Passage': 'green',
                   'Pleiades Last Appearance': 'blue'}
    self.dashmap = {'Equinox': 'solid',
                    'Solstice': 'solid',
                    'Zenith Passage': 'solid',
                    'Pleiades Last Appearance': 'dashed'}

# Circular diagram that shows azimuths for all pairs of markers,
# and the target azimuths.
class CircleGrapher:
  def __init__(self, pairs, targets,
               inner_length=0.2, outer_length=0.3,
               text_start_right=0.35,
               text_start_left=0.75):
    self.pairs = pairs
    self.targets = targets
    self.p = None
    self.inner_length = inner_length
    self.outer_length = outer_length
    self.text_start_right = text_start_right
    self.text_start_left = text_start_left
    self.colors = Colors()

  def graph(self):
    self.p = figure(
      tools=TOOLS,
      sizing_mode='stretch_both',
      match_aspect=True,
      title='Observed azimuths between pairs, along with alignment directions.'
    )

    self.p.circle(x=[0], y=[0], radius=1.0, line_color='black', line_width=1, fill_color=None)

    for pair in self.pairs:
      a = deg2rad(pair.azimuth)
      self.p.line(y=[np.cos(a), (1 - self.inner_length) * np.cos(a)],
                  x=[np.sin(a), (1 - self.inner_length) * np.sin(a)],
                  line_color='black')

    for target in self.targets:
      a = deg2rad(target.azimuth)
      self.p.line(y=[np.cos(a), (1 + self.outer_length) * np.cos(a)],
                  x=[np.sin(a), (1 + self.outer_length) * np.sin(a)],
                  line_width=3,
                  line_dash=self.colors.dashmap[target.category],
                  line_color=self.colors.clrmap[target.category])
      self.p.line(y=[(1 - self.inner_length) * np.cos(a), 0],
                  x=[(1 - self.inner_length) * np.sin(a), 0],
                  line_width=3,
                  line_dash=self.colors.dashmap[target.category],
                  line_color=self.colors.clrmap[target.category])

      text = target.category + ':' + target.name
      if a < np.pi:
        glyph = Label(y=self.text_start_right * np.cos(a) + 0.01,
                      x=self.text_start_right * np.sin(a),
                      text=text,
                      text_color='black',
                      angle=-a + np.pi/2)
      else:
        if target.category == "Pleiades Last Appearance":
          glyph = Label(y=self.text_start_left * 1.05 * np.cos(a) - 0.06,
                        x=self.text_start_left * 1.05 * np.sin(a),
                        text="Pleiades Last Appearance",
                        text_color='black',
                        angle=-a + 3 * np.pi / 2)
        else:
          glyph = Label(y=self.text_start_left * np.cos(a) + 0.02,
                        x=self.text_start_left * np.sin(a),
                        text=text,
                        text_color='black',
                        angle=-a + 3 * np.pi / 2)
      self.p.add_layout(glyph)
      self.p.title.align = 'center'
      self.p.xgrid.grid_line_color = None
      self.p.ygrid.grid_line_color = None
      self.p.axis.visible = False

  def show(self):
    show(self.p)

# Plot of markers and their alignments for a given tolerance
# on a map.
class LocationGrapher:

  def __init__(self, markers, tolerance):
    self.tolerance = tolerance
    self.markers = markers
    self.target_azimuths = None
    self.p = None
    self.num_alignments = 0
    self.colors = Colors()

  def plot_alignments(self, alignments):

    self.num_alignments = len(alignments)
    for a in alignments:
      self.p.line(x=[a.pair.marker1.x, a.pair.marker2.x],
                  y=[a.pair.marker1.y, a.pair.marker2.y],
                  legend_label=a.target.category,
                  line_width=2,
                  line_dash=self.colors.dashmap[a.target.category],
                  line_color=self.colors.clrmap[a.target.category])

    if len(alignments) > 0:
      self.p.legend.location = "top_left"
      self.p.legend.title = "Alignment Category"

    self.p.title.text = f'''Placements and alignments (tolerance +/- {self.tolerance} degrees)\nNumber of alignments: {self.num_alignments}'''

  def show(self):
    show(self.p)

  def graph(self):

    self.p = figure(
      tools=TOOLS,
      sizing_mode='stretch_both',
      x_axis_type="mercator",
      y_axis_type="mercator"
    )

    tile_provider = get_provider('CARTODBPOSITRON_RETINA')
    self.p.add_tile(tile_provider)

    list_of_dict = [{k: v for k, v in vars(m).items()} for m in self.markers]
    df = pd.DataFrame(list_of_dict)
    source = ColumnDataSource(df)

    glyph = Scatter(x='x', y='y', size=12, marker='circle')
    self.p.add_glyph(source, glyph)

    glyph = Text(x='x', y='y', text='name', text_color='black')
    self.p.add_glyph(source, glyph)

    hover = HoverTool(tooltips=[('x', '@x'),
                                ('y', '@y'),
                                ('marker', '@name')])

    self.p.add_tools(hover)

    self.p.x_range = Range1d(-8525455, -8524750)
    self.p.y_range = Range1d(-1320350, -1319870)

    self.p.xaxis.formatter = PrintfTickFormatter(format='%8.5f')
    self.p.yaxis.formatter = PrintfTickFormatter(format='%8.5f')

# Graph of the distribution of number of alignments for
# null hypothesis of randomly distributed markers in the region,
# along with where the observed number at Marcahuasi lies. This
# is the graph of p-value as function of observed alignments.
class SignificanceGrapher:

  def __init__(self, n_markers, tolerance, matches_list):
    self.n_markers = n_markers
    self.tolerance = tolerance
    self.matches_list = matches_list

  def graph(self, observed_alignments=0):
    p = figure(
      title=f'''P-values for number of alignments for {self.n_markers} markers\nAngle tolerance: {self.tolerance} deg\nObserved number of alignments: {observed_alignments}''',
      sizing_mode='stretch_both')

    p.xaxis.axis_label = 'observed'
    p.yaxis.axis_label = 'Pr(alignments > observed | random markers)'
    n = len(self.matches_list) + 1
    y = [1] + [float(i) / n for i in range(n, 0, -1)] + [0]
    x_extent = max(self.matches_list[-1], observed_alignments) + 1
    x = [-0.01, 0] + self.matches_list + [x_extent]

    p.line(x=x, y=y,
           legend_label='p-value as function of alignments',
           line_width=5)
    vline = Span(location=observed_alignments,
                 dimension='height',
                 line_color='red',
                 line_width=2)
    vlabel = Label(x=observed_alignments, y=200, y_units='screen', text=f'observed_alignments')
    p.add_layout(vlabel)
    sig = 0.05
    hline = Span(location=sig,
                 dimension='width',
                 line_color='black',
                 line_width=2,
                 )
    hlabel = Label(x=200, y=sig, x_units='screen', text=f'significance threshold ({sig})')
    p.add_layout(hlabel)
    p.renderers.extend([vline, hline])

    p.xaxis.ticker = [i for i in range(x[-1] + 1)]
    p.x_range = Range1d(-0.01, x[-1])
    p.y_range = Range1d(0, 1.2)
    show(p)

# Graph of the probability density function of number
# of alignments were the markers distributed randomly in
# the region.
class DensityGrapher:

  def __init__(self, n_markers, matches_list):
    self.n_markers = n_markers
    self.matches_list = matches_list

  def graph(self):
    p = figure(
      title=f'density of alignments for {self.n_markers} randomly chosen markers within a radius. Angle tolerance {self.tolerance} deg',
      sizing_mode='stretch_both'
    )

    max_val = self.matches_list[-1]
    bins = [i - 0.5 for i in range(0, max_val + 1, 1)]
    hist, edges = np.histogram(self.matches_list, density=True, bins=bins)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
    p.xaxis.axis_label = 'alignments'
    p.yaxis.axis_label = 'Pr(alignments | random markers)'
    ticks = [i for i in range(self.matches_list[-1])]
    p.xaxis.ticker = ticks
    p.x_range = Range1d(-0.5, self.matches_list[-1])
    show(p)
