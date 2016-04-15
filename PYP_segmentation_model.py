import word_segmentation
from collections import defaultdict, Counter
from random import random
from iProgressBar import ProgressBar
import numpy as np
import utils


class PYP_word_segmentation_model(word_segmentation.Word_segmentation_model):
	"""
	Word segementation based on a unigram PYP model
	"""

	__version__ = 0.8

	#parameters
	alpha = 1 #dirichlet concentration
	beta = 0.2 #PYP beta

	# The seating arrangement
	seating		 	 = defaultdict(lambda: np.array([])) #indexed by word, then a list of table counts (e.g. seating['no'] = [25,4,1] means three tables and 30 occurances)
	K 			 	 = 0 #Total number of tables

	def getWordCounts(self):
		return self.seating

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
			words = word_segmentation.split_utterance(utterance, ut_boundaries)
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
			tables = np.append(self.alpha + (self.beta * self.K), tables)

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
			#sample table to remove word from proportional to customers at table
			word_seating = self.seating[word_or_words]
			tables = word_seating / sum(word_seating)
			table = np.random.choice(len(tables), 1, p=tables)

			#delete the table if there is only one customer
			if word_seating[table] == 1:
				self.K -= 1

				#delete the entry if this was the last table
				if sum(word_seating) == 1:
					self.seating.pop(word_or_words)
				else:
					self.seating[word_or_words] = np.delete(word_seating, table)
				

			else:
				word_seating[table] -= 1

			self.total_word_count -= 1


	def P_corpus(self):
		"""
		Returns the joint probability of all words in the corpus
		(in log probability)
		"""

		pws = []

		for word, tables in self.seating.iteritems():
			pws.append(sum(tables) * (np.log(sum(tables) - 1 + (self.alpha * self.P0(word)) + (self.beta * (self.K - len(tables)) ) )
								- np.log(self.total_word_count - 1 + self.alpha)
								) )
			if np.isnan(pws[len(pws)-1]):
				print 'ERERER', word, tables
		return sum(pws)


	def gibbs_sample_once(self, temperature=1, debug=None):

		#import parameters:
		alpha = self.alpha
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
			prev_b, next_b, boundary_exists, insert_boundary_at = word_segmentation.neighbours(boundaries, boundary)
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

			# We possibly created empty values, remove them from the dict
			[self.seating.pop(w) for w in [w1, w2, w3] if len(self.seating[w]) == 0]

			n_utter_ends = len(self.utterances) - int(utterance_final)
			nu = n_utter_ends if utterance_final else n_total - n_utter_ends

			p_no_boundary = (1.0 * (nw1 + alpha * self.P0(w1) + beta * (K - kw1)) / (n_total + alpha)) * \
							(1.0 * (nu + (rho/2)) / (n_total + rho))

			p_boundary =	(1.0 * (nw2 + alpha * self.P0(w2)  + beta * (K - kw2)) / (n_total + alpha)) * \
							(1.0 * (n_total - n_utter_ends+ (rho/2)) / (n_total + rho) ) * \
							(1.0 * (nw3 + int(w2 == w3) + alpha * self.P0(w3)  + beta * (K - kw3))/ (n_total + 1 + alpha)) * \
							(1.0 * (nu  + int(w2 == w3) + (rho/2)) / (n_total + 1 + rho))

			# Modify probabilities using annealing
			p_boundary    = p_boundary**(1.0 / temperature)
			p_no_boundary = p_no_boundary**(1.0 / temperature)

			#sample proportionally
			mu = p_boundary / (p_boundary + p_no_boundary)
			insert_boundary = mu > random()

			if debug:
				print "     " + " " * (boundary - 1 + insert_boundary_at) + 'V' + ' ' * int(boundary_exists) + 'V'
				print "utt: " + word_segmentation.insert_boundaries(utterance, boundaries)
				print "w1: " + w1
				print "w2: " + w2
				print "w3: " + w3
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