from collections import defaultdict, Counter
from random import random
from iProgressBar import ProgressBar
import numpy as np
import utils


class segmented_corpus:
	"""

	"""

	__version__ = 0.8

	#parameters
	alpha0 = 1 #dirichlet concentration
	beta = 0.2 #PYP beta
	temp_regime = (20000, np.arange(0.1,1.1,0.1)) #temperature steps for gibbs sampling (annealing) in a tuple (total_iterations, regime)
	rho = 2 #parameter of beta prior over utterance end
	p_dash = 0.5 #probability of ending a word (in P_0)


	# The seating arrangement
	seating		 	 = defaultdict(lambda: np.array([])) #indexed by word, then a list of table counts (e.g. seating['no'] = [25,4,1] means three tables and 30 occurances)
	K 			 	 = 0 #Total number of tables
	total_word_count = 0

	phoneme_counts = Counter()
	total_phoneme_count = 0
	P0_cache = {}

	utterances = [] #list of utterances (unseparated)
	boundaries = [] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries (range 1-len(utterance)-1)

	# for evaluation purposes
	original_word_counts = defaultdict(lambda: np.array([]))
	original_seating = []

	#list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = []

	P0_method = None

	def __init__(self, corpusfile=None, temp_regime_id=0, P0_method='uniform'):

		if corpusfile:
			utterances, boundaries = utils.load_segmented_corpus(corpusfile)
			self.initialize_lexicon(utterances, boundaries)

			self.original_boundaries = self.boundaries[:]
			self.original_seating = self.seating.copy()

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

		self.P0_method = P0_method # 'mle' or 'uniform'

	def initialize_lexicon(self, utterances, boundaries):

		#first store the utterances an boundaries
		self.utterances = utterances
		self.boundaries = boundaries

		#update the sample list
		self.sample_list = [(u,b) for u, utterance in enumerate(utterances) for b in range(1, len(utterance) )]

		#finally update the statistics
		self.seating = defaultdict(lambda: np.array([]))
		self.K 		 = 0

		self.phoneme_counts   = Counter()

		for utterance, ut_boundaries in zip(utterances, boundaries):
			words = segmented_corpus.split_utterance(utterance, ut_boundaries)
			self.add_customer(words)

			for phonemes in map(list, words):
				self.phoneme_counts += Counter(phonemes)

		self.total_phoneme_count = sum(self.phoneme_counts.values())
		self.unique_phoneme_count = len(self.phoneme_counts.keys())
		self.P0_cache = {}

	def add_customer(self, word_or_words):
		if isinstance(word_or_words, list):
			[self.add_customer(word) for word in word_or_words]
		else:

			# Calculate the probabilities for exisint tables accorinding to the PYP process 
			tables = (self.seating[word_or_words] - self.beta).clip(min=0)

			# Calculate the probability for a new table (append to beginnning)
			tables = np.append(self.alpha0 + (self.beta * self.K), tables)

			# Normalise probabilities
			tables = tables / sum(tables)

			# Pick a new / exisiting table
			table = np.random.choice(len(tables), 1, p=tables)

			#print word_or_words, self.K, tables
			if table == 0:
				# create new table
				self.K += 1
				self.seating[word_or_words] = np.append(self.seating[word_or_words], 1)
			else:
				# add to existing table (substract one because table[0] = the new table )
				self.seating[word_or_words][table - 1] += 1

			self.total_word_count += 1

	def remove_customer(self, word_or_words):
		if isinstance(word_or_words, list):
			[self.remove_customer(word) for word in word_or_words]
		else:
			word_seating = self.seating[word_or_words]
			tables = word_seating / sum(word_seating)
			table = np.random.choice(len(tables), 1, p=tables)

			if word_seating[table] == 1:
				self.seating[word_or_words] = np.delete(word_seating, table)
			else:
				word_seating[table] -= 1

			self.total_word_count -= 1


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

		pws = []

		for word, tables in self.seating.iteritems():
			pws.append(sum(tables) * (np.log( (self.P0(word) * self.alpha0) + sum(tables) + (self.beta * (self.K - len(tables)) ) )
								- np.log(self.total_word_count - 1 + self.alpha0)
								) )
		return sum(pws)


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

		#import parameters:
		alpha0 = self.alpha0
		rho    = self.rho
		beta   = self.beta

		#allow the funcion to sample just one boundary for demonstration purposes
		boundaries = self.sample_list
		if debug: boundaries = [debug]

		#loop over all boundary locations
		for u, boundary in boundaries:
			utterance   = self.utterances[u]
			boundaries  = self.boundaries[u]

			#Find previous and next boundary
			prev_b, next_b, boundary_exists, insert_boundary_at = segmented_corpus.neighbours(boundaries, boundary)
			prev_b = prev_b or 0
			utterance_final = not next_b

			#find start, end
			w1 = utterance[prev_b:next_b]
			w2 = w1[:boundary-prev_b]
			w3 = w1[boundary-prev_b:]

			# Remove the words that are not shared by the two hypothesis
			if boundary_exists:
				self.remove_customer([w2, w3])
			else:
				self.remove_customer(w1)

			# calculate the word counts over all the OTHER words,
			# this means that we should substract the counts for the part under consideration (w1)
			# if the boundary exists, thrn we need to substract 2 words (w2 and w3 are in there right now)
			# if the boundary does not exist, then we neet to substract 1 word (w1 is in there now)
			n_total   = self.total_word_count
			K 		  = self.K

			# calculate word counts in h-
			nw1 = sum(self.seating[w1])
			nw2 = sum(self.seating[w2])
			nw3 = sum(self.seating[w3])

			# calculate table counts in h-
			kw1 = len(self.seating[w1])
			kw2 = len(self.seating[w2])
			kw3 = len(self.seating[w3])			

			n_utter_ends = len(self.utterances) - int(utterance_final)
			nu = n_utter_ends if utterance_final else n_total - n_utter_ends

			p_no_boundary = (1.0 * (nw1 + alpha0 * self.P0(w1) + beta * (K - kw1)) / (n_total + alpha0)) * \
							(1.0 * (nu + (rho/2)) / (n_total + rho))

			p_boundary =	(1.0 * (nw2 + alpha0 * self.P0(w2)  + beta * (K - kw2)) / (n_total + alpha0)) * \
							(1.0 * (n_total - n_utter_ends+ (rho/2)) / (n_total + rho) ) * \
							(1.0 * (nw3 + int(w2 == w3) + alpha0 * self.P0(w3)  + beta * (K - kw3))/ (n_total + 1 + alpha0)) * \
							(1.0 * (nu  + int(w2 == w3) + (rho/2)) / (n_total + 1 + rho))

			# Modify probabilities using annealing
			p_boundary    = p_boundary**(1.0 / temperature)
			p_no_boundary = p_no_boundary**(1.0 / temperature)

			#sample proportionally
			mu = p_boundary / (p_boundary + p_no_boundary)
			insert_boundary = mu > random()

			if debug:
				print 'p( B):', p_boundary, '*' * int(insert_boundary)
				print 'p(-B):', p_no_boundary, '*' * int(not insert_boundary)
				print ' (mu=', mu, ')'

			if insert_boundary:
				# re-add the words
				self.add_customer([w2, w3])

				#update boundary
				if not boundary_exists:
					self.boundaries[u].insert(insert_boundary_at,boundary)

			else:
				# re-add the words
				self.add_customer(w1)

				#update boundary
				if boundary_exists:
					self.boundaries[u].pop(insert_boundary_at)


	def evaluate(self):
		"""
		Returns a dict of tuples (precicion, recall, F0) for:
		'words',
		'boundaries',
		'lexicon'
		"""
		words = utils.eval_words(self.boundaries, self.original_boundaries)
		boundaries = utils.eval_boundaries(self.boundaries, self.original_boundaries)
		lexicon = utils.eval_lexicon(self.seating, self.original_seating)

		return {'words': words, 'boundaries':boundaries, 'lexicon':lexicon}


	def print_evaluation(self):
		evaluation = self.evaluate()

		print '=== Evaluation ========================'
		print 'Pw = %.3f, Rw = %.3f, Fw = %.3f' % evaluation['words']
		print 'Pb = %.3f, Rb = %.3f, Fb = %.3f' % evaluation['boundaries']
		print 'Pl = %.3f, Rl = %.3f, Fl = %.3f' % evaluation['lexicon']

	@staticmethod
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

	@staticmethod
	def split_utterance(utterance, boundaries):
		return [utterance[(i):(j)] for i, j in zip([0]+boundaries, boundaries+[None])]

	@staticmethod
	def insert_boundaries(utterance, boundaries, delimiter = '.'):
		return delimiter.join(segmented_corpus.split_utterance(utterance, boundaries))



### DEMO CODE ###
def gibbs_demo():
	s = segmented_corpus('br-phono-train.txt')

	print 'Init correctely'
	for _ in range(4):
		print s.P_corpus()
		s.gibbs_sample_once()
	print s.P_corpus()

	print 'Init random'
	s.initialize_boundaries_randomly()
	for _ in range(4):
		print s.P_corpus()
		s.gibbs_sample_once()
	print s.P_corpus()

	#s.initialize_lexicon(['hoihoeishet','watisdit','ditisleuk','ditisditisditis'], [[3,6,8],[2,5],[2,5,7],[3,5,8,10,11,12]])
	print s.P_corpus()
	s.gibbs_sample_once()
	print s.P_corpus()
	s.gibbs_sample_once()
	print s.P_corpus()
	s.gibbs_sample_once()
	print s.P_corpus()
	#s.gibbs_sample_once(debug=(1,1) )
	#s.gibbs_sample_once(debug=(1,2) )
	#s.gibbs_sample_once(debug=(1,3) )
	#s.gibbs_sample_once(debug=(1,5) )
	#s.gibbs_sample_once(debug=(1,6) )
	#s.gibbs_sample_once(debug=(3,11) )
	#s.gibbs_sample_once(debug=(3,13) )
	#s.gibbs_sample_once()


def boundary_reset_test():
	s = segmented_corpus('br-phono-toy.txt')
	s.gibbs_sample_once(debug=(1,1) )
	s.remove_all_boundaries()
	s.gibbs_sample_once(debug=(1,1) )

def boundary_random_test():
	s = segmented_corpus('br-phono-toy.txt')
	s.gibbs_sample_once(debug=(1,1) )
	s.initialize_boundaries_randomly()
	s.gibbs_sample_once(debug=(1,1) )

def gibbs_test():
	s = segmented_corpus('br-phono-toy.txt')
	s.remove_all_boundaries()
	s.gibbs_sampler()

	#just to show the results
	s.gibbs_sample_once(debug=(0,1) )
	s.gibbs_sample_once(debug=(1,1) )
	s.gibbs_sample_once(debug=(2,1) )
	s.gibbs_sample_once(debug=(3,1) )

	s.print_evaluation()

def joint_prop_test():
	s = segmented_corpus('br-phono-toy.txt')
	print s.P_corpus()
	s.remove_all_boundaries()
	print s.P_corpus()
	s.gibbs_sampler()
	print s.P_corpus()

def gibbs_log_demo():
	"""
	Shows the effect of gibs sampling iterations
	"""
	import matplotlib.pyplot as plt
	s = segmented_corpus('br-phono-toy.txt')
	s.remove_all_boundaries()
	logs = s.gibbs_sampler(log=['P_corpus', 'n_types', 'n_tokens'])

	fig, ax1 = plt.subplots()
	plt.xlabel('Iteration')

	l1 = ax1.plot(logs['P_corpus'],'-r', label='joint probability')
	ax1.set_ylabel('Joint log probability')

	ax2 = ax1.twinx()
	l2 = ax2.plot(logs['n_types'], label='Types')
	l3 = ax2.plot(logs['n_tokens'],label='Tokens')
	ax2.set_ylabel('Count')

	#create combined legend
	lns = l1+l2+l3
	plt.legend(lns, [l.get_label() for l in lns], loc=0)

	plt.legend()
	plt.show()

def eval_demo():
	s = segmented_corpus('br-phono-toy.txt')
	s.print_evaluation()
	s.remove_all_boundaries()
	s.print_evaluation()
	s.gibbs_sampler()
	s.print_evaluation()


def main():
	#gibbs_demo()
	#boundary_reset_test()
	#boundary_random_test()
	#gibbs_test()
	#joint_prop_test()
	#gibbs_log_demo()
	eval_demo()

if __name__ == '__main__':
	main()



