import utils

class segmented_corpus:
	"""

	"""

	words_$ 		= Counter() #word counts at utterance boundary
	words_u 		= Counter() #other word counts
	boundary_count  = 0

	utterances = ['hoihoeishet','watisdit'] #list of utterances (unseparated)
	boundaries = [[2,5,7],[3,4]] #list of list. indexed by utterance_id each entry containing a list with the positions of the boundaries


	#boundary_ids[] #list of tuples (utterance_id, boundary_id) used for sampling
	sample_list = [(x,n) for n, utterance in enumerate(utterances) for x in range(len(utterance))]
	

	def __init__(self):
		pass

	def initialize_boundaries_randomly():
		pass


	def gibs_sampler():

		#parameters:
		temperature = 1 #temperature (annealing)
		alpha0 = #dirichlet concentration
		rho = #
		p$ #word ending probability


		#Randomly draw boundary location
		w1 = #string from previous to next boundary location (or uterance end)
		w2 = #split w1 by proposed boundary, first half 
		w3 = #split w1 by proposed boundary, remainder 


		#calculate P1

		#calculate P2

		#sample proportionally

		if changed:
			#update counts
			if word is utterance end:
				#put in words_$
			else:
				#put in words_u

			#update boundary (and boundary_count)


		#Hypothesis 2: A  boundary: split words w2 and w3

		# h- : all words in the corpus except w1, w2 and w3

		#w1 in h- + alpha0 * P(w1)   #nu in h- + rho/2
		#------------------------  x ------------------
	#        total(h-)            total(h-) + tau

