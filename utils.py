"""
This file contains some utility functions for loading corpuses, computing certain evaluations, etc. 
"""
import re
import numpy as np
from collections import Counter

def load_segmented_corpus(filename, word_delimiter=' '):
	"""
	This function loads a segmented corpus, concatenates the utterances and returns them in a list
	It also returns the place where the actual boundaries were
	"""
	delimiter_pattern = re.compile(word_delimiter+"|\n") #the \n needs to be removed too
	f = open("./data/"+filename, "r")
	utterances = []
	boundaries = []
	for utterance in f:
		u_boundaries = [m.start() for m in re.finditer(word_delimiter, utterance)]
		#make sure boundaries have the proper offset
		u_boundaries = [u_boundaries[i]-i for i in range(len(u_boundaries))]
		boundaries.append(u_boundaries)
		utterances.append(re.sub(delimiter_pattern, "", utterance))
	return (utterances, boundaries)

def calc_precision(retrieved, relevant):
	intersection = set(retrieved).intersection(relevant)

	return len(intersection) / float(len(retrieved)) if len(retrieved) > 0 else 0

def calc_recall(retrieved, relevant):
	intersection = set(retrieved).intersection(relevant)

	return len(intersection) / float(len(relevant)) if len(relevant) > 0 else 0

def calc_f(precision, recall):
	return 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
def eval_boundaries(retrieved_boundaries_corpus, relevant_boundaries_corpus):
	evals = []

	for retrieved_boundaries, relevant_boundaries in zip(retrieved_boundaries_corpus, relevant_boundaries_corpus):
		precision = calc_precision(retrieved_boundaries, relevant_boundaries)
		recall = calc_recall(retrieved_boundaries, relevant_boundaries)
		f = calc_f(precision, recall)

		evals.append((precision, recall, f))

	return tuple(np.mean(evals, 0))

def eval_words(retrieved_boundaries_corpus, relevant_boundaries_corpus):
	evals = []

	for retrieved_boundaries, relevant_boundaries in zip(retrieved_boundaries_corpus, relevant_boundaries_corpus):
		# copy because we manipulate the boundaries for evaluations
		retrieved_boundaries = retrieved_boundaries[:]
		relevant_boundaries = relevant_boundaries[:]

		retrieved_boundaries.insert(0, 0) # left utterance boundary
		retrieved_boundaries.append(-1) # right utterance boundary
		retrieved_words = [(retrieved_boundaries[i], retrieved_boundaries[i + 1]) for i in range(len(retrieved_boundaries) - 1)]

		relevant_boundaries.insert(0, 0) # left utterance boundary
		relevant_boundaries.append(-1) # right utterance boundary
		relevant_words = [(relevant_boundaries[i], relevant_boundaries[i + 1]) for i in range(len(relevant_boundaries) - 1)]

		precision = calc_precision(retrieved_words, relevant_words)
		recall = calc_recall(retrieved_words, relevant_words)
		f = calc_f(precision, recall)

		evals.append((precision, recall, f))

	return tuple(np.mean(evals, 0))

def eval_lexicon(retrieved_lexicon, relevant_lexicon):
	retrieved = retrieved_lexicon.keys()
	relevant = relevant_lexicon.keys()

	precision = calc_precision(retrieved, relevant)
	recall = calc_recall(retrieved, relevant)
	f = calc_f(precision, recall)

	return precision, recall, f

if __name__ == "__main__":
	# look at the big dog there
	# look at the bigdo g the re

	retrieved_boundaries = [[3, 5, 8, 13, 14, 17]]
	relevant_boundaries = [[3, 5, 8, 11, 14]]

	print 'words:', eval_words(retrieved_boundaries, relevant_boundaries)
	print 'boundaries:', eval_boundaries(retrieved_boundaries, relevant_boundaries)

	retrieved_lexicon = Counter('look at the bigdo g the re'.split(' '))
	relevant_lexicon = Counter('look at the big dog there'.split(' '))

	print 'lexicon:', eval_lexicon(retrieved_lexicon, relevant_lexicon)

	# utterances, boundaries = load_segmented_corpus('br-phono-toy.txt')
	# for i in range(len(utterances)):
	# 	print('utterance')
	# 	print(utterances[i])
	# 	print(boundaries[i])

