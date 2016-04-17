from DP_segmentation_model  import DP_word_segmentation_model
from PYP_segmentation_model import PYP_word_segmentation_model
import json
import os.path
import argparse
from argparse import RawTextHelpFormatter


__DEFAULT_DATAFILE__ = 'br-phono-train.txt'
__STORE_FOLDER__ = 'results/'


def run_experiment(s, name, description, datafile):
	"""
	This function runs a custom experiment
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
			logs = s.gibbs_sampler(log=['P_corpus', 'n_types', 'n_tokens','temperature','K'])

			# Store the obtained data
			output['logs'] 		 = logs
			output['evaluation'] = s.evaluate()

			#store the boundaries, given the datafile, this is the segementation of the lexicon
			output['boundaries'] = s.boundaries

			try:
				output['seating'] = s.seating
			except:
				pass

			#finally, store everything
			json.dump(output, outfile)


############################################################################################
########################    Experiment 1: different P0 methods     #########################
############################################################################################

def exp01():
	basename = 'exp01-P0_method'
	description = 'MLE vs uniform P0'
	datafile = __DEFAULT_DATAFILE__
	
	name = basename + '-mle'
	
	#Initialize the corpus with the right paramters
	s = DP_word_segmentation_model(datafile,P0_method='mle')
	
	#initialize the boundaries
	s.initialize_boundaries_randomly()
	
	run_experiment(s, name, description, datafile)
	
	name = basename + '-uniform'
	
	#Initialize the corpus with the right paramters
	s = DP_word_segmentation_model(datafile,P0_method='uniform')
	
	#initialize the boundaries
	s.initialize_boundaries_randomly()
	
	run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 2: different values of alpha    ########################
############################################################################################

def exp02():
	alphas = [1, 2, 5, 10, 20, 50, 100, 200, 500]
	basename = 'exp02-alpha-'
	description = 'Using default parameters, varying alpha'
	datafile = __DEFAULT_DATAFILE__

	for alpha in alphas:
		name = basename + `alpha`

		#Initialize the corpus
		s = DP_word_segmentation_model(datafile)

		# set the right paramter
		s.alpha0 = alpha

		#initilize the boundaries
		s.initialize_boundaries_randomly()

		run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 3: different values of p_dash    ########################
############################################################################################

def exp03():
	p_dashes = [0.1, 0.3, 0.5, 0.7, 0.9]
	basename = 'exp03-p_dash-'
	description = 'Using default parameters, varying p_dash'
	datafile = __DEFAULT_DATAFILE__

	for p_dash in p_dashes:
		name = basename + `p_dash`

		#Initialize the corpus
		s = DP_word_segmentation_model(datafile)

		# set the right paramter
		s.p_dash = p_dash

		#initilize the boundaries
		s.initialize_boundaries_randomly()

		run_experiment(s, name, description, datafile)

############################################################################################
#####################    Experiment 4: different initialisations    ########################
############################################################################################

def exp04():
	basename = 'exp04-initialisation'
	description = 'Trying different initialisations of the corpus'
	datafile = __DEFAULT_DATAFILE__


	#####################    Experiment 4: different values of p_dash    ########################
	name = basename + 'true'
	#Initialize the corpus
	s = DP_word_segmentation_model(datafile)

	#dont initialise the boundaries
	run_experiment(s, name, description, datafile)

	#####################    Experiment 4: different values of p_dash    ########################
	name = basename + '0%'

	#Initialize the corpus
	s = DP_word_segmentation_model(datafile)

	#remove all boundaries
	s.remove_all_boundaries()

	run_experiment(s, name, description, datafile)

	#####################    Experiment 4: different values of p_dash    ########################
	name = basename + '33%'

	#Initialize the corpus
	s = DP_word_segmentation_model(datafile)

	#initialize randomly
	s.initialize_boundaries_randomly(1.0 / 3)

	run_experiment(s, name, description, datafile)

	#####################    Experiment 4: different values of p_dash    ########################
	name = basename + '66%'

	#Initialize the corpus
	s = DP_word_segmentation_model(datafile)

	#initialize randomly
	s.initialize_boundaries_randomly(2.0 / 3)

	run_experiment(s, name, description, datafile)

	#####################    Experiment 4: different values of p_dash    ########################
	name = basename + '100%'

	#Initialize the corpus
	s = DP_word_segmentation_model(datafile)

	#initialize with all possible boundaries
	s.initialize_boundaries_randomly(1.0)

	run_experiment(s, name, description, datafile)


############################################################################################
###################    Experiment 5: different temperature schemes    ######################
############################################################################################

def exp05():
	basename = 'exp05-temperature-regime'
	description = 'Using default parameters, varying temperature regime'
	datafile = __DEFAULT_DATAFILE__
	temp_regimes = range(3)

	for temp_regime in temp_regimes:
		name = basename + `temp_regime`

		#Initialize the corpus with the right paramters
		s = DP_word_segmentation_model(datafile,temp_regime_id=temp_regime)

		#initilize the boundaries
		s.initialize_boundaries_randomly()

		run_experiment(s, name, description, datafile)


############################################################################################
###################    Experiment 6: PYP varying alpha and beta      ######################
############################################################################################

def exp06():
	basename = 'exp06-PYP'
	description = 'PYP algorithm with different alpha an beta combination'
	datafile = __DEFAULT_DATAFILE__

	alphas = [1, 2, 5, 10, 20, 50, 100, 500]
	betas = [0.01, 0.1, 0.2, 0.4,0.6, 0.8, 1, 0]

	for alpha in alphas:
		for beta in betas:

			name = basename + '-alpha-' + `alpha` + '-beta-' + `beta`

			#Initialize the corpus with the right paramters
			s = PYP_word_segmentation_model(datafile, temp_regime_id=3)
			s.alpha = alpha
			s.beta  = beta

			#initilize the boundaries
			s.initialize_boundaries_randomly()

			run_experiment(s, name, description, datafile)


############################################################################################
###################    Experiment 7: PYP varying alpha and beta      ######################
############################################################################################

def exp07():
	basename = 'exp07-PYP'
	description = 'DP algorithm with same temp regime as PYP'
	datafile = __DEFAULT_DATAFILE__

	alphas = [1, 2, 5, 10, 20, 50, 100, 500]

	for alpha in alphas:

		name = basename + '-alpha-' + `alpha`

		#Initialize the corpus with the right paramters
		s = DP_word_segmentation_model(datafile, temp_regime_id=3)
		s.alpha = alpha

		#initilize the boundaries
		s.initialize_boundaries_randomly()

		run_experiment(s, name, description, datafile)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
	parser.add_argument('--runall', help="""runs all experiments that were detailed in the report
Can not be used in combination with other parameters.""", default=False)
	parser.add_argument('--cf', help='corpus file', default='br-phono-train.txt')
	parser.add_argument('--t', help='temperature regime. will also influence the amount of iterations.', type=int, default=0)
	parser.add_argument('--p_0', help='p_0', type=str, default='uniform')
	parser.add_argument('--a', help='alpha_0', type=int, default=20)
	parser.add_argument('--b', help='beta_0. Only used for PYP experiments', type=int, default=0)
	parser.add_argument('--p_dash', help='p_dash', type=int, default=0.5)
	parser.add_argument('--init', help="""Initialization. valid options are: 
'true_init': initializes algorithm with the correct boundaries 
'no_init': initializes without boundaries 
'random_0.33_init': initialize 1/3 of the boundaries randomly
'random_0.66_init': initialize 1/3 of the boundaries randomly
'all_init': initialize all of the boundaries randomly
			    """, type=str, default='true_init')
	args = parser.parse_args()
	if args.runall:
		exp07()
		exp06()
		exp01()
		exp02()
		exp03()
		exp04()
		exp05()
	else:
		s = DP_word_segmentation_model(args.cf, args.t, args.p_0)
		if args.b:
			s = PYP_word_segmentation_model(args.cf, args.t, args.p_0)
			s.beta = args.b 
		else:
			s = DP_word_segmentation_model(args.cf, args.t, args.p_0)
		s.alpha = args.a
		s.p_dash = args.p_dash
		if args.init == 'true_init':
			pass
		elif args.init == 'no_init':
			s.remove_all_boundaries()
		elif args.init == 'random_0.33_init':
			s.initialize_boundaries_randomly(1.0 / 3)
		elif args.init == 'random_0.66_init':
			s.initialize_boundaries_randomly(2.0 / 3)
		elif args.init == 'all_init':
			s.initialize_boundaries_randomly(1.0)
		else:
			raise Exception('incorrect init argument')
		run_experiment(s, 'custom experiment', '', args.cf)
