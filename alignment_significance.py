#!/usr/local/bin/python3
from geometry import AlignmentTarget
from computer import Computer, compute_all_azimuths
from grapher import LocationGrapher, CircleGrapher, SignificanceGrapher
from reader import DataReader

# Define constants, including the alignment targets.
DATA_FILE = './resources/Marcahuasi_markers.csv'
TOLERANCES = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5]
NUMBER_SIMULATED = 100
NUMBER_EXAMPLES = 1
ALIGNMENT_TARGETS = [AlignmentTarget("Equinox", "rise", 90),
                     AlignmentTarget("Equinox", "set", 270),
                     AlignmentTarget("Solstice", "Jun 21 rise", 66),
                     AlignmentTarget("Solstice", "Jun 21 set", 292),
                     AlignmentTarget("Solstice", "Dec 21 rise", 112),
                     AlignmentTarget("Solstice", "Dec 21 set", 246),
                     AlignmentTarget("Zenith Passage", "rise", 100.5),
                     AlignmentTarget("Zenith Passage", "set", 257.5),
                     AlignmentTarget("Pleiades Last Appearance", "Pleiades on horizon", 290.8)]


def main():

  # Read and create Markers from the data file.
  data_reader = DataReader(DATA_FILE)
  data_reader.read_marker_locations()

  # Create diagram using all pairs and targets.
  all_pairs = compute_all_azimuths(data_reader.markers)
  circle_grapher = CircleGrapher(all_pairs, ALIGNMENT_TARGETS)
  circle_grapher.graph()
  circle_grapher.show()

  # Loop through each tolerance and compare the observed
  # number of alignments with the number that match when
  # the markers are simulated randomly.
  for tolerance in TOLERANCES:
    computer = Computer(markers=data_reader.markers,
                        alignment_targets=ALIGNMENT_TARGETS,
                        tolerance=tolerance)

    # Graph the locations of the markers on a map.
    grapher = LocationGrapher(computer.markers, tolerance)
    grapher.graph()

    # Determine how many alignments there are and graph
    # them on the map, color-coding the type of alignment.
    observed_alignments = computer.determine_alignments(computer.markers)
    grapher.plot_alignments(observed_alignments)
    grapher.show()

    # Simulate the same number of random markers in the same region
    # num_simulated times, and for each set of simulated markers,
    # determine the number that match. Return num_examples of simulated
    # sets of markers only for the purpose of graphing them on a map
    # for inspection.
    list_of_simulated_markers = computer.simulate(num_simulated=NUMBER_SIMULATED,
                                                  num_examples=NUMBER_EXAMPLES)
    # Plot the returned sets of simulated markers and alignments for
    # inspection.
    for simulated_markers in list_of_simulated_markers:
      grapher = LocationGrapher(simulated_markers, tolerance)
      grapher.graph()
      matches = computer.determine_alignments(simulated_markers)
      grapher.plot_alignments(matches)
      grapher.show()

    # Plot and report the statistical significance estimates.
    significance_grapher = SignificanceGrapher(len(data_reader.markers),
                                               tolerance,
                                               computer.matches_list)
    significance_grapher.graph(observed_alignments=len(observed_alignments))
    computer.report_significance(observed_alignments=len(observed_alignments))


if __name__ == "__main__":
  main()
