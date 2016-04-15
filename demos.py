import DP_segmentation_model  as DP
import PYP_segmentation_model as PYP

### DEMO CODE ###

def print_title(title):
	l = 80
	s = 4
	x = (l - len(title) - (2 * s)) / 2

	print "=" * l
	print "=" * x + " " * s + title + " " * s + "=" * x
	print "=" * l

def gibbs_demo():
	print_title("GIBBS DEMO")

	for model in [DP.DP_word_segmentation_model, PYP.PYP_word_segmentation_model]:
		print 'Model =', model
		s = model()
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
	print_title("BOUNDARY RESET TEST")
	s = DP.DP_word_segmentation_model('br-phono-toy.txt')
	s.gibbs_sample_once(debug=(1,1) )
	s.remove_all_boundaries()
	s.gibbs_sample_once(debug=(1,1) )

def boundary_random_test():
	print_title("RANDOM BOUNDARY TEST")
	s = DP.DP_word_segmentation_model('br-phono-toy.txt')
	s.gibbs_sample_once(debug=(1,1) )
	s.initialize_boundaries_randomly()
	s.gibbs_sample_once(debug=(1,1) )

def gibbs_test():
	print_title("GIBBS TEST")
	s = DP.DP_word_segmentation_model('br-phono-toy.txt')
	s.remove_all_boundaries()
	s.gibbs_sampler(iterations=100)

	#just to show the results
	s.gibbs_sample_once(debug=(0,1) )
	s.gibbs_sample_once(debug=(1,1) )
	s.gibbs_sample_once(debug=(2,1) )
	s.gibbs_sample_once(debug=(3,1) )

	s.print_evaluation()

def joint_prob_test():
	print_title("P CORPUS DEMO")
	for model in [DP.DP_word_segmentation_model, PYP.PYP_word_segmentation_model]:
		print 'Model =', model
		s = model('br-phono-toy.txt')	

		print s.P_corpus()
		s.remove_all_boundaries()
		print s.P_corpus()
		s.gibbs_sampler(iterations=100)
		print s.P_corpus()

def gibbs_log_demo():
	"""
	Shows the effect of gibs sampling iterations
	"""
	import matplotlib.pyplot as plt
	s = DP.DP_word_segmentation_model('br-phono-toy.txt')
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
	print_title("EVALUATION DEMO")
	for model in [DP.DP_word_segmentation_model, PYP.PYP_word_segmentation_model]:
		print 'Model =', model
		s = model('br-phono-toy.txt')		
		s.print_evaluation()
		s.remove_all_boundaries()
		s.print_evaluation()
		s.gibbs_sampler(iterations=100)
		s.print_evaluation()

def PYP_as_DP_demo():
	"""
	Set beta in the PYP to 0 and check if it behaves the same as the DP model
	"""
	print_title("PYP AS DP demo")
	print "Set beta in the PYP to 0 and check if it behaves the same as the DP model"

	DPM  = DP.DP_word_segmentation_model
	PYPM = PYP.PYP_word_segmentation_model

	DPM.alpha  = 10
	PYPM.alpha = 10
	PYPM.beta  = 0

	DPM  = DPM('br-phono-train.txt')
	PYPM = PYPM('br-phono-train.txt')

	print '#types', len(DPM.word_counts.keys()),  len(PYPM.seating.keys())
	print '#occurences bUk', DPM.word_counts['bUk'], sum(PYPM.seating['bUk'])
	print 'P(W)', DPM.P_corpus(), PYPM.P_corpus()

	DP_log  = DPM.gibbs_sampler(iterations=15, log=['P_corpus'])
	PYP_log = PYPM.gibbs_sampler(iterations=15, log=['P_corpus'])

	import matplotlib.pyplot as plt
	plt.plot(DP_log['P_corpus'], label='DP')
	plt.plot(PYP_log['P_corpus'], label='PYP')
	plt.legend()
	plt.show()

	print PYP_log['P_corpus']

def main():
	#gibbs_demo()
	#boundary_reset_test()
	#boundary_random_test()
	#eval_demo()
	#gibbs_test()
	#joint_prob_test()
	#gibbs_log_demo()

	PYP_as_DP_demo()

if __name__ == '__main__':
	main()

