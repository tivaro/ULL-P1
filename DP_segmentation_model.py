import word_segmentation
from collections import Counter
from random import random
import numpy as np


class DP_word_segmentation_model(word_segmentation.Word_segmentation_model):
	"""
	Word segementation based on a unigram DP model
	"""

	__version__ = 0.8

	#parameters
	alpha = 20 #dirichlet concentration

	def initialize_lexicon(self, utterances, boundaries):

		#first store the utterances an boundaries
		self.utterances = utterances
		self.boundaries = boundaries

		#update the sample list
		self.sample_list = [(u,b) for u, utterance in enumerate(utterances) for b in range(1, len(utterance) )]

		#finally update the statistics
		self.word_counts      = Counter()
		self.total_word_count = 0

		self.phoneme_counts   = Counter()

		for utterance, ut_boundaries in zip(utterances, boundaries):
			words = word_segmentation.split_utterance(utterance, ut_boundaries)
			self.word_counts += Counter(words)
			self.total_word_count += len(words)

			for phonemes in map(list, words):
				self.phoneme_counts += Counter(phonemes)

		self.total_phoneme_count = sum(self.phoneme_counts.values())
		self.unique_phoneme_count = len(self.phoneme_counts.keys())
		self.P0_cache = {}


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


	def P_corpus(self):
		"""
		Returns the joint probability of all words in the corpus
		(in log probability)
		"""

		pws = []

		for word, count in self.word_counts.iteritems():
			pws.append(count * (np.log(count - 1 + (self.alpha * self.P0(word)))
								- np.log(self.total_word_count - 1 + self.alpha)
								) ) 
		return sum(pws)


	def gibbs_sample_once(self, temperature=1, debug=None):

		#import parameters:
		alpha = self.alpha
		rho    = self.rho

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

			p_no_boundary = (1.0 * (nw1 + alpha * self.P0(w1)) / (n_total + alpha)) * \
							(1.0 * (nu + (rho/2)) / (n_total + rho))

			p_boundary =	(1.0 * (nw2 + alpha * self.P0(w2)) / (n_total + alpha)) * \
							(1.0 * (n_total - n_utter_ends+ (rho/2)) / (n_total + rho) ) * \
							(1.0 * (nw3 + int(w2 == w3) + alpha * self.P0(w3))/ (n_total + 1 + alpha)) * \
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
