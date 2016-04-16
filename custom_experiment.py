parser = argparse.ArgumentParser()
parser.add_argument('--cf', help='corpus file')
parser.add_argument('--t', help='temperature regime. will also influence 
                                the amount of iterations.')
parser.add_argument('--p_0', help='p_0')
parser.add_argument('--a', help='alpha_0')
parser.add_argument('--p_dash', help='p_dash')
parser.add_argument('--init', help="Initialization. valid options are \n 
                    'true_init': \n'no_init': \n
                    'random_0.33_init': initialize 1/3 of the boundaries randomly \n
                    'random_0.66_init': initialize 1/3 of the boundaries randomly \n
                    'all_init': initialize all of the boundaries randomly
                    ")
parser.parse_args()
corpusfile = 'br-phono-train.txt'
temp_regime_id = 0
P0_method='uniform'
initialization = 'true_init'
if cf:
    corpusfile = cf
if t:
    temp_regime_id= t
if p_0:
    P0_method= p_0
s = DP_word_segmentation_model(corpus_file, temp_regime_id, P0_method)
if a:
    s.alpha_0 = a
if p_dash:
    s.p_dash = p_dash
if init:
    if init == 'true_init':
        pass
    if init == 'no_init':
        s.remove_all_boundaries()
    elif init == 'random_0.33_init':
        s.initialize_boundaries_randomly(1.0 / 3)
    elif init == 'random_0.66_init':
        s.initialize_boundaries_randomly(2.0 / 3)
    elif init == 'all_init':
        s.initialize_boundaries_randomly(1.0)
    else:
        return 'incorrect init argument'
