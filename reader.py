import pandas as pd
from pyproj import Transformer
from geometry import Marker

# Class that reads in data from a csv and converts
# from lat lon to x/y using pyproj.
class DataReader:

  def __init__(self, filename: str):
    self.filename = filename
    self.markers = None

  def read_marker_locations(self):
    df = pd.read_csv(self.filename,
                     usecols=['LUGAR', 'Latitude (dec) (y)', 'Longitude (dec) (x)'])
    df = df.dropna()

    df['lon'] = df['Longitude (dec) (x)']
    df['lat'] = df['Latitude (dec) (y)']

    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    df['x'], df['y'] = transformer.transform(df['lat'], df['lon'])

    self.markers = [Marker(x0, y0, lat, lon, name) for (x0, y0, lat, lon, name) in zip(df['x'],
                                                                                       df['y'],
                                                                                       df['lat'],
                                                                                       df['lon'],
                                                                                       df['LUGAR'])]
