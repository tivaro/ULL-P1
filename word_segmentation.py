from collections import Counter
from random import random
from iProgressBar import ProgressBar
import numpy as np
import utils


class Word_segmentation_model(object):
	"""
	General / Abstract class for word segmentation,
	to be inherited by the version using a DP or a PYP process

	"""

	__version__ = 0.8

	#parameters
	temp_regime = (20000, np.arange(0.1,1.1,0.1)) #temperature steps for gibbs sampling (annealing) in a tuple (total_iterations, regime)
	rho = 2 #parameter of beta prior over utterance end
	p_dash = 0.5 #probability of ending a word (in P_0)

	word_counts		 = Counter() #other word counts
	total_word_count = 0

	utterances = [] #list of utterances (unseparated)
	boundaries = [] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries (range 1-len(utterance)-1)

	#list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = []

	# for evaluation purposes
	original_word_counts = Counter()
	original_boundaries = []

	#counts and cache for phoneme probability
	phoneme_counts = Counter()
	total_phoneme_count = 0
	P0_cache = {}
	P0_method = None



	def __init__(self, corpusfile=None, temp_regime_id=0, P0_method='uniform'):

		if corpusfile:
			utterances, boundaries = utils.load_segmented_corpus(corpusfile)
			self.initialize_lexicon(utterances, boundaries)

			self.original_boundaries  = self.boundaries[:]
			self.original_word_counts = self.getWordCounts()

		#temp_regimes decides the amount of iterations and the temperature regime
		temp_regimes = []
		temp_regimes.append([20000, np.arange(0.1,1.1,0.1)])
		temp_regimes.append([30000, np.arange(0.1,1.6,0.1)])
		temp_regimes.append([40000, np.arange(0.002,1.002,0.002)])
		self.temp_regime = temp_regimes[temp_regime_id]
		#compute the time steps when we have to change temperatures
		self.temp_regime.append(int(self.temp_regime[0]/len(self.temp_regime[1])))
		self.temp_regime = tuple(self.temp_regime)
		#print(self.temp_regime)
		"""
		for example:
		iterations = 20000
		len(steps) = 10
		iterations/len(steps) = 2000
		"""

		self.P0_method = P0_method # 'mle' or 'uniform'

	def initialize_lexicon(self, utterances, boundaries):
		raise(NotImplementedError)

	def initialize_boundaries_randomly(self, boudary_proportion=0.3):

		#Remove all boundaries and import sample list, utternaces and boundaries
		self.remove_all_boundaries()
		sample_list = self.sample_list
		boundaries  = self.boundaries
		utterances = self.utterances

		#randomly select the defined proportion of boundaries
		boundary_ids = range(len(sample_list))
		np.random.shuffle(boundary_ids)
		to = int(round(len(sample_list) * boudary_proportion))
		chosen_boundaries = boundary_ids[:to]

		#sort the list again because the boundaries stored in the object have to be sorted.
		chosen_boundaries.sort()

		#append the chosen boundaries to the (now initialised empty boundary list)
		[boundaries[sample_list[i][0]].append(sample_list[i][1]) for i in chosen_boundaries]

		#reinitialise to set the right counts
		self.initialize_lexicon(utterances, boundaries)


	def remove_all_boundaries(self):
		utterances = self.utterances
		boundaries = [[] for _ in range(len(utterances))]
		self.initialize_lexicon(utterances, boundaries)

	def P_phoneme(self, x):
		if self.P0_method == 'mle':
			return self.phoneme_counts[x] / float(self.total_phoneme_count)

		return 1.0 / float(self.unique_phoneme_count)

	def P0(self, word):
		if word not in self.P0_cache:
			M = len(word)
			Pphoneme = np.prod([self.P_phoneme(x) for x in list(word)])

			self.P0_cache[word] = self.p_dash * ((self.p_dash)**(M-1)) * Pphoneme

		return self.P0_cache[word]

	def P_corpus(self):
		"""
		Returns the joint probability of all words in the corpus
		(in log probability)
		"""
		raise(NotImplementedError)

	def gibbs_sampler(self, log=[], debug=None):
		"""
		Performs gibs sampling according to the iteration/temperature scheme in s.temp_regime
		the variable log should be a list with values that should be logged after each iteration (the log is returned)
		possible elements are:
			'P_corpus': the probabilty of the entire corpus
			'n_types': the lexicon size
			'n_tokens': the number of tokens
			'temperature': the temperature used at each iteration
		"""

		iterations, temp_steps, step_size = self.temp_regime
		p = ProgressBar(iterations)

		# initialize log
		logs = {var:[] for var in log}

		for i in range(iterations):

			#update temperature
			if i % step_size == 0:
				temperature = 1/temp_steps[i/step_size]

			#do one iteration and update progressbar
			self.gibbs_sample_once(debug=debug, temperature=1)
			p.animate(i)

			#update log
			if 'P_corpus'    in log: logs['P_corpus'].append( self.P_corpus())
			if 'n_types'     in log: logs['n_types'].append( len(self.word_counts))
			if 'n_tokens'    in log: logs['n_tokens'].append( self.total_word_count)
			if 'temperature' in log: logs['temperature'].append( temperature)


		if log: return logs


	def gibbs_sample_once(self, temperature=1, debug=None):
		raise(NotImplementedError)

	def getWordCounts(self):
		return self.word_counts

	def evaluate(self):
		"""
		Returns a dict of tuples (precicion, recall, F0) for:
		'words',
		'boundaries',
		'lexicon'
		"""

		words = utils.eval_words(self.boundaries, self.original_boundaries)
		boundaries = utils.eval_boundaries(self.boundaries, self.original_boundaries)
		lexicon = utils.eval_lexicon(self.getWordCounts(), self.original_word_counts)

		return {'words': words, 'boundaries':boundaries, 'lexicon':lexicon}

	def print_evaluation(self):
		evaluation = self.evaluate()

		print '=== Evaluation ========================'
		print 'Pw = %.3f, Rw = %.3f, Fw = %.3f' % evaluation['words']
		print 'Pb = %.3f, Rb = %.3f, Fb = %.3f' % evaluation['boundaries']
		print 'Pl = %.3f, Rl = %.3f, Fl = %.3f' % evaluation['lexicon']


######################################################################################
############################ STATIC MODULE FUNCITONS #################################
######################################################################################

def neighbours(sorted_list, entry, full_description = True):
	"""
	Input: sorted list, entry (a possible feature enty)
	Output: (prev_neighbour, next_neighbour, entry_exists, insert_entry)
	where insert_entry indicates the place to insert the entry to keep the list sorted
	"""

	prev_neighbour = None
	next_neighbour = None
	entry_exists   = False
	insert_entry   = len(sorted_list)


	for n,e in enumerate(sorted_list):

		if e < entry:
			prev_neighbour = e
		elif e == entry:
			entry_exists = True
		else:
			next_neighbour = e
			insert_entry = n
			break

	#insert_entry should equal the next element if entry does not exit, but it's true location if entry exists
	insert_entry -= int(entry_exists)

	if full_description:
		return prev_neighbour, next_neighbour, entry_exists, insert_entry
	else:
		return prev_neighbour, next_neighbour

def split_utterance(utterance, boundaries):
	return [utterance[(i):(j)] for i, j in zip([0]+boundaries, boundaries+[None])]

def insert_boundaries(utterance, boundaries, delimiter = '.'):
	return delimiter.join(word_segmentation.split_utterance(utterance, boundaries))
