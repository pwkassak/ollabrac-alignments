import numpy as np

def deg2rad(deg: float):
  return (np.pi / 180.0) * deg

def rad2deg(rad: float):
  return ((180.0 / np.pi) * rad) % 360
