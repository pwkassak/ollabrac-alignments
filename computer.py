import numpy as np
import bisect
from pyproj import Transformer
from geometry import Marker, PairOfMarkers, Match

def compute_all_azimuths(markers):
  pairs = []
  for i in range(len(markers)):
    for j in range(len(markers)):
      if j == i:
        continue

      pair = PairOfMarkers(markers[i], markers[j])
      pairs.append(pair)

  return pairs

class Computer:
  def __init__(self, markers, alignment_targets, tolerance, count_aligned_pair_only_once=False):
    self.markers = markers
    self.alignment_targets = alignment_targets
    self.tolerance = tolerance
    self.count_aligned_pair_only_once = count_aligned_pair_only_once
    self.matches_list = []

  def determine_xy_center_and_radius(self):
    n_markers = len(self.markers)
    center_x = 0
    center_y = 0
    for i in range(n_markers):
      m = self.markers[i]
      center_x += m.x
      center_y += m.y

    center_x /= n_markers
    center_y /= n_markers

    rad = 0
    for i in range(n_markers):
      m = self.markers[i]
      r = np.sqrt((m.x - center_x) ** 2 + (m.y - center_y) ** 2)
      rad = rad if rad > r else r

    return center_x, center_y, rad

  def random_markers(self):
    n_markers = len(self.markers)
    center_x, center_y, rad0 = self.determine_xy_center_and_radius()
    r2 = np.random.uniform(0, rad0 ** 2, size=n_markers)
    angle = np.pi * np.random.uniform(0, 2, size=n_markers)
    r = np.apply_along_axis(np.sqrt, 0, r2)
    cos = np.apply_along_axis(np.cos, 0, angle)
    sin = np.apply_along_axis(np.sin, 0, angle)
    x = np.multiply(r, cos) + center_x
    y = np.multiply(r, sin) + center_y

    transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
    lat, lon = transformer.transform(x, y)

    names = [f'Random {i}' for i in range(n_markers)]

    markers = [Marker(x0, y0, lat0, lon0, names0) for (x0, y0, lat0, lon0, names0) in zip(x, y, lat, lon, names)]
    return markers

  def determine_alignments(self, markers):
    n_markers = len(markers)
    matches = []
    for i in range(n_markers):
      for j in range(n_markers):
        if j == i:
          continue

        pair = PairOfMarkers(markers[i], markers[j])

        for a in self.alignment_targets:
          if np.abs(pair.azimuth - a.azimuth) < self.tolerance:
            matches.append(Match(pair, a))

    # Reduce alignment count to only count pairs once if requested.
    match_map = {}
    if self.count_aligned_pair_only_once:
      for m in matches:
        if m.unique_pair() not in match_map:
          match_map[m.unique_pair()] = m
      matches = match_map.values()

    return matches

  def simulate(self, num_simulated, num_examples):
    examples = []
    for i in range(num_simulated):
      markers = self.random_markers()
      if len(examples) < num_examples:
        examples.append(markers)
      matches = self.determine_alignments(markers)
      num_matches = len(matches)
      self.matches_list.append(num_matches)
      if (i + 1) % 1000 == 0:
        print(f'iteration {i + 1} / {num_simulated}')
    self.matches_list.sort()
    return examples

  def report_significance(self, observed_alignments=0):

    i_left = bisect.bisect_left(self.matches_list, observed_alignments)
    i_right = bisect.bisect_right(self.matches_list, observed_alignments)
    v = 0.5 * (float(i_left) + float(i_right))
    significance = 1 - v / len(self.matches_list)
    print(
      f'The p-value for {observed_alignments} alignments on {self.n_markers} markers is {significance:.5f} (angle tolerance {self.tolerance} deg)')
    return significance


