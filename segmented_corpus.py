class segmented_corpus:
	"""

	"""

	words_$ = Counter() #word counts at utterance boundary
	words_u = Counter() #other word counts

	utterances = [] #list of utterances (unseparated)
	boundaries = [] #list of list of indexes of utterance boundaries (indexed by utterance)

	boundary_ids[] #a continious list of (utterance_id, boundary_id)
	

	def __init__(self):
		pass

	def load_segmented_corpus(filename, utterance_delimiter = '\n', word_delimiter = ' '):
		pass


def gibs_sampler():
	pass

	#parameters:
	temperature = 1 #temperature (annealing)
	alpha0 = #dirichlet concentration
	tau = #
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

		#update boundary

