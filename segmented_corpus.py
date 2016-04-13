from collections import Counter
from random import random
from iProgressBar import ProgressBar
import numpy as np
import utils


class segmented_corpus:
	"""

	"""

	__version__ = 0.8

	#parameters
	alpha0 = 20 #dirichlet concentration
	temp_regime = (20000, np.arange(0.1,1.1,0.1)) #temperature steps for gibbs sampling (annealing) in a tuple (total_iterations, regime)
	rho = 2 #parameter of beta prior over utterance end
	p_dash = 0.5 #probability of ending a word (in P_0)

	word_counts		 = Counter() #other word counts
	total_word_count = 0

	utterances = [] #list of utterances (unseparated)
	boundaries = [] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries (range 1-len(utterance)-1)

	# for evaluation purposes
	original_word_counts = Counter()
	original_boundaries = [] 

	#list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = []

	def __init__(self, corpusfile=None, temp_regime_id=0):

		if corpusfile:
			utterances, boundaries = utils.load_segmented_corpus(corpusfile)
			self.initialize_lexicon(utterances, boundaries)

			self.original_boundaries = self.boundaries[:]
			self.original_word_counts = self.word_counts.copy()

		#temp_regimes decides the amount of iterations and the temperature regime
		temp_regimes = []
		temp_regimes.append([20000, np.arange(0.1,1.1,0.1)])
		temp_regimes.append([40000, np.arange(0.002,1.002,0.002)])
		self.temp_regime = temp_regimes[temp_regime_id]
		#compute the time steps when we have to change temperatures
		self.temp_regime.append(int(self.temp_regime[0]/len(self.temp_regime[1])))
		self.temp_regime = tuple(self.temp_regime)
		print(self.temp_regime)
		"""
		for example:
		iterations = 20000
		len(steps) = 10
		iterations/len(steps) = 2000
		"""

	def initialize_lexicon(self, utterances, boundaries):

		#first store the utterances an boundaries
		self.utterances = utterances
		self.boundaries = boundaries

		#update the sample list
		self.sample_list = [(u,b) for u, utterance in enumerate(utterances) for b in range(1, len(utterance) )]

		#finally update the statistics
		self.word_counts      = Counter()
		self.total_word_count = 0

		for utterance, ut_boundaries in zip(utterances, boundaries):
			words = segmented_corpus.split_utterance(utterance, ut_boundaries)
			self.word_counts += Counter(words)
			self.total_word_count += len(words)


	def substract_word_count(self, word_or_words, times = 1):
		"""
		Substract counts of a word, or a list of word from the counter, ensuring nonnegative values and updating the total count
		"""
		if isinstance(word_or_words, list):
			[self.substract_word_count(word, times) for word in word_or_words]
		else:
			self.total_word_count -= self.word_counts[word_or_words]
			if self.word_counts[word_or_words] - times > 0:
				self.word_counts[word_or_words] -= times
			else:
				del self.word_counts[word_or_words]
			self.total_word_count += self.word_counts[word_or_words]

	def add_word_count(self, word_or_words, times = 1):
		"""
		Substract counts of a word, or a list of word from the counter, updating the total count
		"""
		if isinstance(word_or_words, list):
			[self.add_word_count(word, times) for word in word_or_words]
		else:
			self.word_counts[word_or_words] += times
			self.total_word_count += times


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



	def P0(self, word):
		M = len(word)
		#right now let's use a uniform phoneme distribution
		#TODO: look this up and find a sensible value!
		Pphoneme = 1.0 / 30
		return self.p_dash * ((self.p_dash)**(M-1) ) * (Pphoneme ** M)

	def P_corpus(self):
		"""
		Returns the joint probability of all words in the corpus
		(in log probability)
		"""

		pws = [ (1.0 * (count - 1 + self.alpha0 * self.P0(word)) / (self.total_word_count - 1 + self.alpha0))
						for word, count in self.word_counts.iteritems()]

		return sum(np.log(pws))


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

			if debug:
				print "     " + " " * (boundary - 1 + insert_boundary_at - boundary_exists) + 'V' + ' ' * int(boundary_exists) + 'V'
				print "utt: " + segmented_corpus.insert_boundaries(utterance, boundaries)
				print "w1: " + w1
				print "w2: " + w2
				print "w3: " + w3

			# calculate the word counts over all the OTHER words,
			# this means that we should substract the counts for the part under consideration (w1)
			# if the boundary exists, thrn we need to substract 2 words (w2 and w3 are in there right now)
			# if the boundary does not exist, then we neet to substract 1 word (w1 is in there now)
			n_total   = max(self.total_word_count - 1 - int(boundary_exists), 0)

			nw1 = max(self.word_counts[w1] - int(not boundary_exists), 0)
			nw2 = max(self.word_counts[w2] - int(boundary_exists), 0)
			nw3 = max(self.word_counts[w3] - int(boundary_exists), 0)


			n_utter_ends = len(self.utterances) - int(utterance_final)
			nu = n_utter_ends if utterance_final else n_total - n_utter_ends

			p_no_boundary = (1.0 * (nw1 + alpha0 * self.P0(w1)) / (n_total + alpha0)) * \
							(1.0 * (nu + (rho/2)) / (n_total + rho))

			p_boundary =	(1.0 * (nw2 + alpha0 * self.P0(w2)) / (n_total + alpha0)) * \
							(1.0 * (n_total - n_utter_ends+ (rho/2)) / (n_total + rho) ) * \
							(1.0 * (nw3 + int(w2 == w3) + alpha0 * self.P0(w3))/ (n_total + 1 + alpha0)) * \
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

			if insert_boundary != boundary_exists:
				# we have to update the boundary and the counts

				if insert_boundary:

					if debug: print "Insertamos"
					if debug: print self.boundaries[u], self.total_word_count

					# Insert boundary
					self.boundaries[u].insert(insert_boundary_at,boundary)

					# Update counts
					self.substract_word_count(w1)
					self.add_word_count([w2, w3])

					if debug: print self.boundaries[u], self.total_word_count

				else:
					if debug: print "Eliminamos"
					if debug: print self.boundaries[u], self.total_word_count

					# Remove boundary
					self.boundaries[u].pop(insert_boundary_at)

					# Update counts
					self.substract_word_count([w2, w3])
					self.add_word_count(w1)

					if debug: print self.boundaries[u], self.total_word_count


	def evaluate(self):
		"""
		Returns a dict of tuples (precicion, recall, F0) for:
		'words',
		'boundaries',
		'lexicon'
		"""
		words = utils.eval_words(self.boundaries, self.original_boundaries)
		boundaries = utils.eval_boundaries(self.boundaries, self.original_boundaries)
		lexicon = utils.eval_lexicon(self.word_counts, self.original_word_counts)

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
	s = segmented_corpus()
	s.initialize_lexicon(['hoihoeishet','watisdit','ditisleuk','ditisditisditis'], [[3,6,8],[2,5],[2,5,7],[3,5,8,10,11,12]])
	s.gibbs_sample_once(debug=(1,1) )
	s.gibbs_sample_once(debug=(1,2) )
	s.gibbs_sample_once(debug=(1,3) )
	s.gibbs_sample_once(debug=(1,5) )
	s.gibbs_sample_once(debug=(1,6) )
	s.gibbs_sample_once(debug=(3,11) )
	s.gibbs_sample_once(debug=(3,13) )
	s.gibbs_sample_once()

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
	boundary_random_test()
	#gibbs_test()
	#joint_prop_test()
	#gibbs_log_demo()
	#eval_demo()

if __name__ == '__main__':
	main()



