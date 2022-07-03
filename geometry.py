from utils import rad2deg, deg2rad
import numpy as np

class AlignmentTarget:

  def __init__(self, category, name, azimuth):
    self.category = category
    self.name = name
    self.azimuth = azimuth

class Marker:

  def __init__(self, x, y, lat, lon, name):
    self.x = x
    self.y = y
    self.lat = lat
    self.lon = lon
    self.name = name

class PairOfMarkers:

  def __init__(self, marker1: Marker, marker2: Marker):
    self.marker1 = marker1
    self.marker2 = marker2

    lat1 = deg2rad(self.marker1.lat)
    lat2 = deg2rad(self.marker2.lat)
    lon1 = deg2rad(self.marker1.lon)
    lon2 = deg2rad(self.marker2.lon)

    delta_lon = lon2 - lon1

    azimuth_radians = np.arctan2(np.sin(delta_lon) * np.cos(lat2),
                                 np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon))

    self.azimuth = rad2deg(azimuth_radians)

class Match:

  def __init__(self, pair: PairOfMarkers, target: AlignmentTarget):
    self.pair = pair
    self.target = target

  def unique_pair(self):
    names = [self.pair.marker1.name, self.pair.marker2.name]
    names.sort()
    return ' and '.join(names)
