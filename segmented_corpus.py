from collections import Counter
import numpy as np
import utils

class segmented_corpus:
	"""

	"""

	word_counts		 = Counter() #other word counts
	boundary_count   = 0
	total_word_count = 0

	utterances = [] #list of utterances (unseparated)
	boundaries = [] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries (range 1-len(utterance)-1)



	#list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = [(u,b) for u, utterance in enumerate(utterances) for b in range(1, len(utterance) )]

	def __init__(self):
		self.initialize_lexicon(['hoihoeishet','watisdit','isditleuk'], [[3,6,8],[2,5],[2,5,7]])

	def initialize_lexicon(self, utterances, boundaries):

		#first store the utterances an boundaries
		self.utterances = utterances
		self.boundaries = boundaries

		#now update the statistics
		self.word_counts      = Counter()
		self.boundary_count   = 0
		self.total_word_count = 0

		for utterance, ut_boundaries in zip(utterances, boundaries):
			words = segmented_corpus.split_utterance(utterance, ut_boundaries)
			self.word_counts += Counter(words)
			self.total_word_count += len(words)

		#use the fact that each utterance has words -1 boundaries
		self.boundary_count   = self.total_word_count - len(self.utterances)



	def initialize_boundaries_randomly():
		pass


	def P0(self, word):
		p_dash = 0.5
		M = len(word)
		#right now let's use a uniform phoneme distribution
		#TODO: look this up and find a sensible value!
		Pphoneme = 1.0 / 26
		return p_dash * ((p_dash)**(M-1) ) * (Pphoneme ** M)


	def gibs_sampler(self, debug=None):

		#parameters:
		#temperature = 1 #temperature (annealing)
		alpha0 = 20 #dirichlet concentration
		rho = 2 #parameter of beta prior over utterance end
		#p# = 0.5


		#Randomly draw boundary location
		u, boundary = debug or self.sample_list[np.random.randint(len(self.sample_list))]
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
			boundaries.insert(insert_boundary_at, boundary)
			boundaries.pop(insert_boundary_at)
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

		p_boundary 	  =	(1.0* (nw1 + alpha0 * self.P0(w1)) / (n_total + alpha0)) * \
						(1.0 *(nu + (rho/2)) / (n_total + rho))

		p_no_boundary =	(1.0 * (nw2 + alpha0 * self.P0(w2)) / (n_total + alpha0)) * \
						(1.0 * (n_total - n_utter_ends+ (rho/2)) / (n_total + rho) ) * \
						(1.0 * (nw3 + int(w2 == w3) + alpha0 * self.P0(w3))/ (n_total + 1 + alpha0)) * \
						(1.0 * (nu  + int(w2 == w3) + (rho/2)) / (n_total + 1 + rho))

		print 'p( B):', p_boundary
		print 'p(-B):', p_no_boundary


		#print p_boundary


		#calculate P1
		#git commit -m "Implemented gibbs sampling untill finding the two words corresponding to both hypotheses"

		#calculate P2

		#sample proportionally

		#if changed:
			#update counts
		#	if word is utterance end:
				#put in words_$
		#	else:
				#put in words_u

			#update boundary (and boundary_count)


		#Hypothesis 2: A  boundary: split words w2 and w3

		# h- : all words in the corpus except w1, w2 and w3

		#w1 in h- + alpha0 * P(w1)   #nu in h- + rho/2
		#------------------------  x ------------------
	#        total(h-)            total(h-) + tau


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


s = segmented_corpus()
s.gibs_sampler((1,1) )
s.gibs_sampler((1,2) )
s.gibs_sampler((1,3) )
s.gibs_sampler((1,5) )
s.gibs_sampler((1,6) )
