#!/usr/local/bin/python3
import pandas as pd
import numpy as np
import bisect
from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d

class Simulator:
	def __init__(self, n_markers, target_azimuths, tolerance):
		if n_markers > 50:
			raise '''number of markers cannot exceed 50, 
					 otherwise there are too many alignments 
					 to check'''

		self.n_markers = n_markers # number of markers
		self.target_azimuths = target_azimuths
		self.tolerance = tolerance
		self.matches_list = []
	
	# sample n random markers within a radius of 1.0
	def random_markers(self):
		r2 = np.random.uniform(0, 1, size=self.n_markers)
		angle = np.pi * np.random.uniform(0, 2, size=self.n_markers)
		r = np.apply_along_axis(np.sqrt, 0, r2)
		cos = np.apply_along_axis(np.cos, 0, angle)
		sin = np.apply_along_axis(np.sin, 0, angle)
		x = np.multiply(r, cos)
		y = np.multiply(r, sin)
		return (x, y)

	def alignments(self, markers):
		alignments = []
		for i in range(self.n_markers):
			x1 = markers[0][i]
			y1 = markers[1][i]
			for j in range(i + 1, self.n_markers):
				x2 = markers[0][j]
				y2 = markers[1][j]
				azimuth1 = (180.0 / np.pi) * (np.arctan2( y2 - y1, x2 - x1 ) + np.pi)
				azimuth2 = (180.0 + azimuth1) % 360.0
				alignments.append(azimuth1)
				alignments.append(azimuth2)

		return alignments

	def count_matches(self, alignments):
		matches = 0
		for i in range(len(alignments)):
			alignment = alignments[i]
			for j in range(len(self.target_azimuths)):
				target = self.target_azimuths[j]
				if np.abs(target - alignment) < self.tolerance:
					matches += 1
		return matches


	def simulate(self, n_simulated):
		for i in range(n_simulated):
			markers = self.random_markers()
			alignments = self.alignments(markers)
			matches = self.count_matches(alignments)
			self.matches_list.append(matches)
			if (i+1) % 1000 == 0:
				print(f'iteration {i+1} / {n_simulated}')
		self.matches_list.sort()

	def plot_density(self):
		p = figure(title=f'density of alignments for {self.n_markers} randomly chosen markers within a radius. Angle tolerance {self.tolerance} deg',
					sizing_mode='stretch_both'
					)

		max_val = self.matches_list[-1]
		bins = [i - 0.5 for i in range(0, max_val+1, 1)]
		hist, edges = np.histogram(self.matches_list, density=True, bins=bins)
		p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
		p.xaxis.axis_label = 'alignments'
		p.yaxis.axis_label = 'Pr(alignments | random markers)'
		ticks = [i for i in range(self.matches_list[-1])]
		p.xaxis.ticker = ticks
		p.x_range=Range1d(-0.5, self.matches_list[-1])
		show(p)

	def report_significance(self, matches):
		
		i_left = bisect.bisect_left(self.matches_list, matches)
		i_right = bisect.bisect_right(self.matches_list, matches)
		v = 0.5 * (float(i_left) + float(i_right))
		significance = 1 - v / len(self.matches_list)
		print(f'p-value for {matches} alignments on {self.n_markers} markers is {significance:.5f} (angle tolerance {self.tolerance} deg)')
		return significance

	def graph_significance(self):
		p = figure(title=f'p-values for number of alignments for {self.n_markers} markers, angle tolerance: {self.tolerance} deg',
			       sizing_mode='stretch_both')
		p.xaxis.axis_label = 'observed'
		p.yaxis.axis_label = 'Pr(alignments > observed | random markers)'
		n = len(self.matches_list) + 1
		y = [float(i)/n for i in range(n, 0, -1)]
		p.line(x=([0] + self.matches_list), y=y)
		p.line(x=[0, self.matches_list[-1]], 
			   y=[0.05, 0.05], 
			   color='black', 
			   line_width=2)
		ticks = [i for i in range(self.matches_list[-1])]
		p.xaxis.ticker = ticks
		p.x_range=Range1d(-0.5, self.matches_list[-1])
		show(p)

def main():
	n_markers = 7
	target_azimuths = [66,    # June solstice sunrise,
					   90,    # equinox sunrise (both of them, in March and September)
					   100.5, # zenith passage (sun direct overhead at noon) sunrise (both of them, in February and October)
					   112,   # December solstice sunrise
					   246,   # December solstice sunset
					   257.5, # zenith passage (sun direct overhead at noon) sunset (both of them, in Feb and Oct)
					   270,   # equinox sunset (both of them, in March and Sept)
					   292]   # June solstice sunset
	simulator = Simulator(n_markers=n_markers, 
		                  target_azimuths=target_azimuths,
		                  tolerance=2.5)
	simulator.simulate(n_simulated=50000)
	simulator.plot_density()
	simulator.graph_significance()
	simulator.report_significance(matches=11)


if __name__ == "__main__":
    main()


