import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib import cm

"""
This script makes plots from all files in the "results" folder,
grouped by experiment type.
It seperates filenames on the "-" character.

If the last part is a number, it makes seperate plots for precision, recall
and F0, with the last number on the x-axis (for example, a results folder
containing "exp02-alpha-1.json" and "exp02-alpha-2.json" would make 3 plots
with alpha on the x-axis and either precision, recall or f0 on the
y axes for each plot, done for words, boundaries and lexicons(so 3 lines per plot))

If the last part is not a number, make 3 plots that plot performance on the
y-axis and time on the x-axis. Each file will have its seperate line.

Experiments 6 and 7 are different since they are experiments with PYP.
Therefore these have their own plotting procedures.
"""

matplotlib.rcParams.update({'font.size': 14})

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def append_to_dict(d, key, elem):
    if key not in d:
        d[key] = [elem]
    else:
        d[key].append(elem)

plot_dir = './plot/'
if not os.path.exists(plot_dir):
    print 'making plot directory'
    os.makedirs(plot_dir)

#find all files in the "results" folder
#group all experiment results that are part of the same experiment
experiments = {}
print 'grouping experiments'
for f_name in os.listdir("results"):
    if f_name.endswith(".json"):
        exp_type = str.split(f_name, '-')[0]
        append_to_dict(experiments, exp_type, os.path.splitext(f_name)[0])

#produce plots for each experiment
for exp_type in experiments:
    file_list = experiments[exp_type]
    experiment_name = str.split(file_list[0], '-')[1]
    experiment_print_name = experiment_name
    experiment_print_name = experiment_print_name.replace("_", " ")
    experiment_print_name = experiment_print_name.replace("p dash", "$p_\$$")
    experiment_print_name = experiment_print_name.replace("alpha", r"$\alpha$")
    experiment_print_name = experiment_print_name.replace("P0", "$P_0$")    

    
    # These experiments are somewhat different
    if exp_type == 'exp06':
        print 'processing data for ' + exp_type
        alphas    = []
        betas     = []

        precision = {}
        recall    = {}
        f0        = {}
        logs      = []



        for file_name in file_list:

            f = open('results/' + file_name + '.json', 'r')
            print file_name
            exp_output = json.load(f)
            evaluation = exp_output['evaluation']
            logs.append(exp_output['logs'])

            betas.append( float( str.split(file_name, '-')[-1]) )
            alphas.append(float( str.split(file_name, '-')[-3]) )

            #print evaluation
            for k in evaluation:
                append_to_dict(precision, k, evaluation[k][0])
                append_to_dict(recall, k, evaluation[k][1])
                append_to_dict(f0, k, evaluation[k][2])

        print 'making plots for ' + exp_type


        evaluation = {'precision': precision,
                    'recall': recall,
                    'F0': f0}

        for x in evaluation.keys():
            plt.figure(figsize=(20, 6))

            for i, k in enumerate(precision.keys()):

                plt.subplot(1,3,i + 1)
                plt.title(k)
                m = np.array(evaluation[x][k])

                #tweak the values a littlebit for the size of the markers
                size_scale = 800 * m
                

                plt.scatter(alphas, betas, c=m, s=size_scale)
                plt.xscale('log')
                plt.xlabel(r'$\alpha$')
                plt.clim(0,1)

                if i == 0: plt.ylabel(r'$\beta$')
                if (i + 1) == len(precision): plt.colorbar()

            plt.suptitle(x)
            plt.savefig(plot_dir + 'PYP-' + x + '.eps', format='eps')
            plt.clf() #clear the plot figure

            #store for the next plot
            exp06 = {}
            exp06['evaluation'] = evaluation
            exp06['alphas'] = alphas
            exp06['betas']  = betas



        print 'making more plots for ' + exp_type 
        
        #subplot: word, word type, log p
        colors = [ cm.jet(1.0 * x / len(set(betas))) for x in range(len(set(betas))) ]

        for i, y  in enumerate(['P_corpus','n_types','n_tokens']):

            plt.subplot(1,3, i + 1)
            plt.title(y)

            #lines, use nice colors
            for b, beta in enumerate(set(betas)):
                alpha  = 20
                useInd = np.where((np.asarray(exp06['betas']) == beta) & (np.asarray(exp06['alphas']) == alpha))[0][0]

                #get correspondint betas and sort alphas and indices
                y_axis = logs[useInd][y]
                x_axis = range(1, len(y_axis)+1)
                plt.plot(x_axis, y_axis, label=r'$\beta=%.2f$' % beta, c=colors[b])


            plt.xlabel('iteration', fontsize=18)
            plt.ylabel('$\ln \ \ p(\mathbf{w})$', fontsize=14) #TODO find a better name for this
            plt.legend(loc='lower right', title=experiment_print_name + ':')
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.savefig(plot_dir + experiment_name + '-' + 'log_prob.eps', format='eps')
        plt.clf() #clear the plot figure

        


    elif exp_type =='exp07':
        print 'Subselecting data from exp06'
        #select only experiments where beta = 0
        useInds = np.where(np.asarray(exp06['betas']) == 0)[0]
    
        #get correspondint alphas and sort alphas and indices
        #get corresponding alphas and sort alphas and indices
        alphas = np.array(exp06['alphas'])[useInds]
        alphas, useInds = zip(*sorted(zip(alphas,useInds)))
        useInds = list(useInds)

        #Now select beta and sort for all measurements
        PYP = {'evaluation':{},
               'alphas':list(alphas)}
        for key, value in exp06['evaluation'].iteritems():

            PYP['evaluation'][key] = {}
            for a,b in value.iteritems():
                PYP['evaluation'][key][a] = np.array(b)[useInds]


        #load data for exp07
        evaluation = {'precision' : {},
                      'recall' : {},
                      'F0' : {}}
        colors = {'boundaries':'b','lexicon':'g','words':'r'}
        alphas = []
        #this will store the values on the x-axis
        #gather all the values
        for file_name in file_list:
            alphas.append(float(str.split(file_name, '-')[-1]))
            f = open('results/' + file_name + '.json', 'r')
            print file_name
            exp_output = json.load(f)
            cur_eval = exp_output['evaluation']
            #print evaluation
            for k in cur_eval:
                append_to_dict(evaluation['precision'], k, cur_eval[k][0])
                append_to_dict(evaluation['recall'], k, cur_eval[k][1])
                append_to_dict(evaluation['F0'], k, cur_eval[k][2])

        print 'making plots for ' + exp_type
        for measure in evaluation.keys():
            plt.figure()
            sorted_x = sorted(alphas)
            for k in precision:
                sorted_y = [p for (x,p) in sorted(zip(alphas,evaluation[measure][k]))]
                plt.plot(sorted_x, sorted_y,                marker='.', label='DP ' + k, c=colors[k])
                plt.plot(PYP['alphas'], PYP['evaluation'][measure][k], marker='.', label='PYP ' + k, c=colors[k],linestyle='--')

            plt.xlabel(r'$\alpha$', fontsize=18)
            plt.ylabel(measure, fontsize=14)
            plt.ylim([0, 1])
            plt.legend(loc='lower right')
            plt.savefig(plot_dir + 'DP-vs-PYP' + '-' + measure + '.eps', format='eps')
        plt.clf() #clear the plot figure          


    #Check if we have to plot numbers on the x-axis
    elif is_number(str.split(file_list[0], '-')[-1]):
        print 'processing data for ' + exp_type
        precision = {}
        recall = {}
        f0 = {}
        x_axis = [] #this will store the values on the x-axis
        #gather all the values
        for file_name in file_list:
            x_axis.append(float(str.split(file_name, '-')[-1]))
            f = open('results/' + file_name + '.json', 'r')
            print file_name
            exp_output = json.load(f)
            evaluation = exp_output['evaluation']
            #print evaluation
            for k in evaluation:
                append_to_dict(precision, k, evaluation[k][0])
                append_to_dict(recall, k, evaluation[k][1])
                append_to_dict(f0, k, evaluation[k][2])
        #plot the stuff and save it
        print 'making plots for ' + exp_type
        sorted_x = sorted(x_axis)


        for k in precision:
            sorted_precision = [p for (x,p) in sorted(zip(x_axis,precision[k]))]
            plt.plot(sorted_x, sorted_precision, marker='.', label=k)
        plt.xlabel(experiment_print_name, fontsize=18)
        plt.ylabel('Precision', fontsize=14)
        plt.ylim([0, 1])
        plt.legend(loc='lower right')
        plt.savefig(plot_dir + experiment_name + '-' + 'precision.eps', format='eps')
        plt.clf() #clear the plot figure

        for k in recall:
            sorted_recall = [r for (x,r) in sorted(zip(x_axis,recall[k]))]
            plt.plot(sorted_x, sorted_recall, marker='.', label=k)
        plt.xlabel(experiment_print_name, fontsize=18)
        plt.ylabel('Recall', fontsize=14)
        plt.ylim([0, 1])
        plt.legend(loc='lower right')
        plt.savefig(plot_dir + experiment_name + '-' + 'recall.eps', format='eps')
        plt.clf() #clear the plot figure

        for k in f0:
            sorted_f0 = [f for (x,f) in sorted(zip(x_axis,f0[k]))]
            plt.plot(sorted_x, sorted_f0, marker='.', label=k)
        plt.xlabel(experiment_print_name, fontsize=18)
        plt.ylabel('$F_0$', fontsize=14)
        plt.ylim([0, 1])
        plt.legend(loc='lower right')
        plt.savefig(plot_dir + experiment_name + '-' + 'f0.eps', format='eps')
        plt.clf() #clear the plot figure


    else: #we have to plot log probabilities over time
        print 'processing data for ' + exp_type
        performance = {}
        for file_name in file_list:
            f = open('results/' + file_name + '.json', 'r')
            print file_name
            exp_output = json.load(f)
            logs = exp_output['logs']
            if 'P_corpus' in logs:
                performance[str.split(file_name, '-')[-1]] = logs['P_corpus']

        for k in performance:
            x_axis = range(1, len(performance[k])+1)
            plt.plot(x_axis, performance[k], label=k)
        plt.xlabel('iteration', fontsize=18)
        plt.ylabel('$\ln \ \ p(\mathbf{w})$', fontsize=14) #TODO find a better name for this
        plt.legend(loc='lower right', title=experiment_print_name + ':')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.savefig(plot_dir + experiment_name + '-' + 'log_prob.eps', format='eps')
        plt.clf() #clear the plot figure
