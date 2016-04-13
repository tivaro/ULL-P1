import segmented_corpus as sc
import json
import os.path


__DEFAULT_DATAFILE__ = 'br-phono-toy.txt'
__STORE_FOLDER__ = 'results/'


def run_experiment(s, name, description, datafile):
	"""
	LOL
	"""

	outfile = __STORE_FOLDER__ + name +'.json'

	# Check if this node is not blocked yet
	if not os.path.isfile(outfile):

		#open the file first so that the other nodes know that this experiment is blocked
		with open(outfile, 'a') as outfile:
			print "RUNNING EXPERIMENT:" + name

			#Store basic variables that we know allready
			output = {}
			output['name'] = name
			output['description'] = description
			output['datafile'] = datafile
			output['version'] = s.__version__

			# run the sampler
			logs = s.gibbs_sampler(log=['P_corpus', 'n_types', 'n_tokens','temperature'])

			# Store the obtained data
			output['logs'] 		 = logs
			output['evaluation'] = s.evaluate()

			#store the boundaries, given the datafile, this is the segementation of the lexicon
			output['boundaries'] = s.boundaries

			#finally, store everything
			json.dump(output, outfile)


name = 'test'
description = 'This is a test'

#Initilize the courpus
s = sc.segmented_corpus(__DEFAULT_DATAFILE__)

#initilize the boundaries
s.initialize_boundaries_randomly()

run_experiment(s, name, description, __DEFAULT_DATAFILE__)

#n_boundaries         =  s.total_word_count - len(s.utterances)
#n_boundary_locations = len(s.sample_list)
#print 1.0 * n_boundaries / n_boundary_locations
