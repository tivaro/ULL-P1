# ULL-P1

This repository defines two word-segmentation models and a Gibbs sampler to do inference. We experiment with a Dirichlet-Prior (DP) and a Pitman-Yor Process (PYP). We evaluate both models on the CHILDES corpus.

## The models

### The general model
Both models are based on the segmentation-model described in Goldwater at al., 2009. The DP model is an exact implementation of this method whereas the PYP model is the model based on the generative story that used Pitman-Yor Processes rather than Dirichlet Processes.

[word_segmentation.py](word_segmentation) defines the basic abstract class for the word-segmentation model as well as some utils. A segmentation-model needs to be initialised with a corpus file with which it will be initialised. The corpus is stored as a list of utterances (sentences) in `self.utterances`. The current segmentation is stored as a list of active boundary locations. These locations are specified in a nested way, the first index being the utterance, and the second index being the boundary location. 

E.g. The following segmentation
 >'I amhere'
  'Ilik e it'

would be represented as follows:
`
s.utterances = ['Iamhere', 'Ilikeit']
s.boundaries = [[1], [4,5]]
`

The abstract class contains methods for boundary initialisation, backoff-probabilities, model-evaluation and a Gibbs sampler container method. The method `self.gibbs_sampler(...)` performs the iteration of single Gibbs sampler-iterations and performs logging of interesting variables.

The true Gibbs sampling, as well as the probability of the current segmentation and lexicon initialisation are model-specific and have to be implemented in `self.gibbs_sample_once(...)`, `self.P_corpus()` and `self.initialize_lexicon(...)` respectively.

In order to make the implementation as fast as possible, the Word_segementation class keeps track of several counts instead of evaluating the counts at each iteration again. In order to do this, these counts need to be updated every time a boundary is updated. 

Boundary manipulation occurs when the boundaries are (re)-initialised, and in the Gibbs sampler. Even though boundary initialisation is implemented in the abstract class, `self.initialize_lexicon(...)` is called in order to update all the counters. Updating of the counts is model-dependent and needs to be implemented in the subclass.

### DP-model

The DP-model was implemented according to Goldwater et al. in the class in [DP_segmentation_model.py](DP_segmentation_model.py). The only relevant counts are token-counts and utterance-counts (which are constant). The functions `self.add_word_count(...)` and `self.substract_word_count(...)` deal with updating type-specific counts and the general token count. 

The Gibbs sampler uses pseudo-counts, subtracting 1 from the counts for the probability on the corpus excluding the word under consideration. Furthermore, the sampler only updates the counts when the sampled boundary will result in a change w.r.t. the old situation. Together, this leads to a high performance allowing many iterations per second.


### PYP-model 

The PYP-Model is based on the DP-model, but a discount factor is concluded. The formulas for the corpus probability and for the Gibbs sampler are derived in our [report](report/report.pdf). Because of the discount factor, the probabilities do not simplify to counts, and we will have to keep track of the clustering arrangement.

In parallel with the Chinese Restaurant metaphor, we call a cluster a table, and we store our seating arrangement in `self.seating`. The seating arrangement is represented as a list of table counts, indexed by type. E.g. `self.seating['am']=[3, 2]` represents a seating arrangement with two tables, one with a count of 3, and one with a count of 2 for the token 'am'.

The methods `self.add_customer(...)` and `self.remove_customer(...)` deal with adding and subtracting tokens from the seating arrangement. Words are added/removed from one of the clusters stochastically, according to the probabilities defined in our [report](report/report.pdf).

Because the seating arrangement affects the probabilities in the Gibbs sampler, we explicitly have to model the corpus with the tokens under consideration removed. As a result, the Gibbs sampler always calls `self.remove_customer(...)` in order to calculate the probabilities. Even if no change is made w.r.t. the old situation, `self.add_customer(...)` has to be called in order to (re-)add the new tokens after sampling the boundary.  


## Running Experiments

Several experiments are conducted in order to find the effect of various parameters on the performance of the models .The experiments are defined in [experiments.py](experiments.py), and can be run from the command line.

For more information on how to set which parameters, use the following command:
`python experiments.py -h`

The results of the experiments (logs, and a final evaluation) is stored in the results folder as a .json file.

In order to run all experiments, use the following command:
`python experiments.py -runall`

The file [plot_experiments.py](plot_experiments) will make plots for every .json file in the results folder and write the plots to the plot/ folder.

We also conducted a qualitative analysis, [print_utterances.py](print_utterances.py) loads the final segmentation for each experiment file, and writes the segmentation as readable strings (with spaces at each boundary location) to the utterances folder. Metrics for each utterance are also reported.

Lastly, some utility files are included

- [run_experiments.sh](run_experiments.sh) and [batch_run.sh](batch_run.sh) to run experiments from a HPC cloud-computing server.
- [colormaps.py](colormaps.py), [iProgressBar.py](iProgressBar.py) and [utils.py](utils.py) define utilities for plotting and running the experiments.
- [demos.py](demos.py) defines demos that provide insight into our code as well as some tests used for debugging.

The final report is located in [report/report.pdf](report/report.pdf)

Due to the large size, not all data-files are added.