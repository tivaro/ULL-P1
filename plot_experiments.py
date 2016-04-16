import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

"""
This script makes plots from all files in the "results" folder,
grouped by experiment type.
It seperates filenames on the "-" character.

If the last part is a number, it makes seperate plots for precision, recall
and F0, with the last number on the x-axis (for example, a results folder
containing "exp02-alpha-1.json" and "exp02-alpha-2.json" would make 9 plots
with alpha on the x-axis and precision, either precision, recall or f0 on the
y axes for each plot, done for words, boundaries and lexicons)

If the last part is not a number, make 3 plots that plot performance on the
y-axis and time on the x-axis. Each file will have its seperate line.
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

    
    # These experiments are somewhot different
    if exp_type == 'exp06':
        print 'processing data for ' + exp_type
        alphas    = []
        betas     = []

        precision = {}
        recall    = {}
        f0        = {}



        for file_name in file_list:
            x_axis.append(float(str.split(file_name, '-')[-1]))
            f = open('results/' + file_name + '.json', 'r')
            print file_name
            exp_output = json.load(f)
            evaluation = exp_output['evaluation']

            betas.append( str.split(file_name, '-')[-1])
            alphas.append(str.split(file_name, '-')[-3])

            #print evaluation
            for k in evaluation:
                append_to_dict(precision, k, evaluation[k][0])
                append_to_dict(recall, k, evaluation[k][1])
                append_to_dict(f0, k, evaluation[k][2])

        print 'making plots for ' + exp_type

        measure = np.array(precision['boundaries'])

        #tweak the values a littlebit for the size of the markers
        #size_scale = -1.0 / np.log(measure)
        #size_scale = 300 * size_scale
        size_scale = 800 * measure
        

        plt.scatter(alphas, betas, c=measure, s=size_scale)
        plt.xscale('log')
        plt.xlabel(r'$\alpha$')
        plt.ylabel(r'$\beta$')
        plt.clim(0,1)
        plt.colorbar()
        plt.savefig(plot_dir +  'exp06.eps', format='eps')
        plt.clf() #clear the plot figure                
        


    elif exp_type =='exp07':
        print 'JOW7'

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
        """
        print precision
        print recall
        print f0
        """
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
