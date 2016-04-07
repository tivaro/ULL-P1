"""
This file contains some utility functions for loading corpuses, etc.
"""
import re

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

if __name__ == "__main__":
	utterances, boundaries = load_segmented_corpus('br-phono-toy.txt')
	for i in range(len(utterances)):
		print('utterance')
		print(utterances[i])
		print(boundaries[i])
	
