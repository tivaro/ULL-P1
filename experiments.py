from DP_segmentation_model  import DP_word_segmentation_model
from PYP_segmentation_model import PYP_word_segmentation_model
import json
import os.path


__DEFAULT_DATAFILE__ = 'br-phono-train.txt'
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

############################################################################################
###################    Experiment 6: PYP varying alpha and beta      ######################
############################################################################################

basename = 'exp06-PYP'
description = 'PYP algorithm with different alpha an beta combination'
datafile = __DEFAULT_DATAFILE__

alphas = [1, 5, 10, 50, 100, 500]
betas = [0.2, 0.4,0.6, 0.8, 1, 0]

for alpha, in alphas:
	for beta in betas:
		
	name = basename + '-alpha-' + `alpha` + '-beta-' + `beta`

	#Initilize the corpus with the right paramters
	s = PYP_word_segmentation_model(datafile, temp_regime_id=3)
	s.alpha = alpha
	s.beta  = beta

	#initilize the boundaries
	s.initialize_boundaries_randomly()

	run_experiment(s, name, description, datafile)


############################################################################################
########################    Experiment 1: different P0 methods     #########################
############################################################################################

basename = 'exp01-P0_method'
description = 'MLE vs uniform P0'
datafile = __DEFAULT_DATAFILE__

name = basename + '-mle'

#Initilize the courpus with the right paramters
s = DP_word_segmentation_model(datafile,P0_method='mle')

#initilize the boundaries
s.initialize_boundaries_randomly()

run_experiment(s, name, description, datafile)

name = basename + '-uniform'

#Initilize the courpus with the right paramters
s = DP_word_segmentation_model(datafile,P0_method='uniform')

#initilize the boundaries
s.initialize_boundaries_randomly()

run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 2: different values of alpha    ########################
############################################################################################

alphas = [1, 2, 5, 10, 20, 50, 100, 200, 500]
basename = 'exp02-alpha-'
description = 'Using default parameters, varying alpha'
datafile = __DEFAULT_DATAFILE__

for alpha in alphas:
	name = basename + `alpha`

	#Initilize the courpus
	s = DP_word_segmentation_model(datafile)

	# set the right paramter
	s.alpha0 = alpha

	#initilize the boundaries
	s.initialize_boundaries_randomly()

	run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 3: different values of p_dash    ########################
############################################################################################

p_dashes = [0.1, 0.3, 0.5, 0.7, 0.9]
basename = 'exp03-p_dash-'
description = 'Using default parameters, varying p_dash'
datafile = __DEFAULT_DATAFILE__

for p_dash in p_dashes:
	name = basename + `p_dash`

	#Initilize the courpus
	s = DP_word_segmentation_model(datafile)

	# set the right paramter
	s.p_dash = p_dash

	#initilize the boundaries
	s.initialize_boundaries_randomly()

	run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 4: different initialisations    ########################
############################################################################################

basename = 'exp04-'
description = 'Trying different initialisations of the corpus'
datafile = __DEFAULT_DATAFILE__


#####################    Experiment 4: different values of p_dash    ########################
name = basename + 'true_init'
#Initilize the courpus
s = DP_word_segmentation_model(datafile)

#dont initialise the boundaries
run_experiment(s, name, description, datafile)

#####################    Experiment 4: different values of p_dash    ########################
name = basename + 'no_init'

#Initilize the courpus
s = DP_word_segmentation_model(datafile)

#remove all boundaries
s.remove_all_boundaries()

run_experiment(s, name, description, datafile)

#####################    Experiment 4: different values of p_dash    ########################
name = basename + 'random_0.33_init'

#Initilize the courpus
s = DP_word_segmentation_model(datafile)

#initialize randomly
s.initialize_boundaries_randomly(1.0 / 3)

run_experiment(s, name, description, datafile)

#####################    Experiment 4: different values of p_dash    ########################
name = basename + 'random_0.66_init'

#Initilize the courpus
s = DP_word_segmentation_model(datafile)

#initialize randomly
s.initialize_boundaries_randomly(2.0 / 3)

run_experiment(s, name, description, datafile)

#####################    Experiment 4: different values of p_dash    ########################
name = basename + 'all_init'

#Initilize the courpus
s = DP_word_segmentation_model(datafile)

#initialize with all possible boundaries
s.initialize_boundaries_randomly(1.0)

run_experiment(s, name, description, datafile)


############################################################################################
###################    Experiment 5: different temperature schemes    ######################
############################################################################################

basename = 'exp05-temp_regime'
description = 'Using default parameters, varying temperature regime'
datafile = __DEFAULT_DATAFILE__
temp_regimes = range(3)

for temp_regime in temp_regimes:
	name = basename + `temp_regime`

	#Initilize the corpus with the right paramters
	s = DP_word_segmentation_model(datafile,temp_regime_id=temp_regime)

	#initilize the boundaries
	s.initialize_boundaries_randomly()

	run_experiment(s, name, description, datafile)