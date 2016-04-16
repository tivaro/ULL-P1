import json
import os
import utils
from segmented_corpus import segmented_corpus
from operator import itemgetter

# Make output directory
utterances_dir = 'utterances/'

if not os.path.exists(utterances_dir):
    os.makedirs(utterances_dir)

# Read results files
results_dir = 'results/'

data = {}

for filename in os.listdir(results_dir):
    if filename.endswith('.json'):
        data[filename] = json.load(open(results_dir + filename, 'r'))

def apply_boundaries(file, datafile, boundaries):
    utterances, actual_boundaries = utils.load_segmented_corpus(datafile)

    results = []

    for utterance, actual_boundaries, boundaries in zip(utterances, actual_boundaries, boundaries):
        delimiter = ' '

        actual_utterance = segmented_corpus.insert_boundaries(utterance, actual_boundaries, delimiter=delimiter)
        predicted_utterance = segmented_corpus.insert_boundaries(utterance, boundaries, delimiter=delimiter)

        precision, recall, f0 = utils.eval_words([boundaries], [actual_boundaries])

        results.append((actual_utterance, predicted_utterance, precision, recall, f0))

    sorted_results = sorted(results, key=itemgetter(4), reverse=True)

    output = '\n'.join(map(lambda x: 'actual: ' + x[0] + '\n' + 'predicted: ' + x[1] + '\n' + ('prec: %.3f ' % x[2]) + ('recall: %.3f ' % x[3]) + ('f0: %.3f ' % x[4]) + '\n', sorted_results))

    file = open(utterances_dir + file.replace('json', 'txt'), 'w').write(output)

for file, experiment in data.items():
    apply_boundaries(file, experiment['datafile'], experiment['boundaries'])
