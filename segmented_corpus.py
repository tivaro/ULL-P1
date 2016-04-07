from collections import Counter
import numpy as np
import utils

class segmented_corpus:
	"""

	"""

	final_words		= Counter() #word counts at utterance boundary
	utter_words		= Counter() #other word counts
	boundary_count  = 0

	utterances = ['hoihoeishet','watisdit'] #list of utterances (unseparated)
	boundaries = [[3,6,8],[2,4]] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries (range 1-len(utterance)-1)


	#list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = [(u,b) for u, utterance in enumerate(utterances) for b in range(1, len(utterance) )]
	print sample_list
	

	def __init__(self):
		pass

	def initialize_boundaries_randomly():
		pass


	def gibs_sampler(self, debug=None):

		#parameters:
		#temperature = 1 #temperature (annealing)
		#alpha0 = #dirichlet concentration
		#rho = 2
		#p$ #word ending probability


		#Randomly draw boundary location
		u, boundary = debug or self.sample_list[np.random.randint(len(self.sample_list))]
		utterance   = self.utterances[u]
		boundaries  = self.boundaries[u]

		#Find previous and next boundary
		prev_b, next_b, boundary_exists, insert_boundary_at = segmented_corpus.neighbours(boundaries, boundary)
		prev_b = prev_b or 0

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
	def insert_boundaries(utterance, boundaries, delimiter = '.'):
		return delimiter.join([utterance[(i):(j)] for i, j in zip([0]+boundaries, boundaries+[None])])


s= segmented_corpus()
s.gibs_sampler((1,1) )
s.gibs_sampler((1,2) )
s.gibs_sampler((1,3) )
s.gibs_sampler((1,5) )
s.gibs_sampler((1,6) )
