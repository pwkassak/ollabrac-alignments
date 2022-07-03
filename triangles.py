#!/usr/local/bin/python3
import pandas as pd
import numpy as np
import bisect
import plotly.express as px

THREE = 3

class Triangles:

	def __init__(self, n):
		self.n = n
		self.triplets = {'x':list(),
						 'y':list(),
						 'z':list()}


	def simulate(self):
		for i in range(self.n):
			x, y = self.random_markers()
			triplet = list()
			for i in range(THREE):
				j = (i + 1) % THREE
				angle = np.arctan2(y[j] - y[i], x[j] - x[i])
				triplet.append(angle)
				angle = np.arctan2(y[i] - y[j], x[i] - x[j])
				triplet.append(angle)

			self.triplets['x'].append(triplet[0])
			self.triplets['y'].append(triplet[2])
			self.triplets['z'].append(triplet[4])

			self.triplets['x'].append(triplet[1])
			self.triplets['y'].append(triplet[2])
			self.triplets['z'].append(triplet[4])

			self.triplets['x'].append(triplet[0])
			self.triplets['y'].append(triplet[3])
			self.triplets['z'].append(triplet[4])

			self.triplets['x'].append(triplet[1])
			self.triplets['y'].append(triplet[3])
			self.triplets['z'].append(triplet[4])

			self.triplets['x'].append(triplet[0])
			self.triplets['y'].append(triplet[2])
			self.triplets['z'].append(triplet[5])

			self.triplets['x'].append(triplet[1])
			self.triplets['y'].append(triplet[2])
			self.triplets['z'].append(triplet[5])

			self.triplets['x'].append(triplet[0])
			self.triplets['y'].append(triplet[3])
			self.triplets['z'].append(triplet[5])

			self.triplets['x'].append(triplet[1])
			self.triplets['y'].append(triplet[3])
			self.triplets['z'].append(triplet[5])

	def plot(self):
		df = pd.DataFrame(self.triplets)
		fig = px.scatter_3d(df, x='x', y='y', z='z')
		fig.update_traces(marker={'size': 3}, opacity=0.01)
		fig.show()

		fig = px.scatter(df, x='x', y='y')
		fig.update_traces(marker={'size': 3}, opacity=0.05)
		fig.update_yaxes(
			scaleanchor='x',
			scaleratio=1
		)
		fig.show()

	def random_markers(self):
		
		r2 = np.random.uniform(0, 1, size=THREE)
		angle = np.random.uniform(0, 2 * np.pi, size=THREE)
		r = np.apply_along_axis(np.sqrt, 0, r2)
		cos = np.apply_along_axis(np.cos, 0, angle)
		sin = np.apply_along_axis(np.sin, 0, angle)
		x = np.multiply(r, cos)
		y = np.multiply(r, sin)
		return x, y


def main():
	n = 50000
	triangles = Triangles(n)
	triangles.simulate()
	triangles.plot()
	

if __name__ == "__main__":
    main()
