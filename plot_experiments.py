import json
import os
import matplotlib.pyplot as plt
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
    #Check if we have to plot numbers on the x-axis
    if is_number(str.split(file_list[0], '-')[-1]):
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
            plt.plot(sorted_x, sorted_precision, marker='.')
            plt.xlabel(experiment_name)
            plt.ylabel('precision')
            plt.savefig(plot_dir + experiment_name +'-'+ k +'-'+ 'precision.png')
            plt.clf() #clear the plot figure

            sorted_recall = [r for (x,r) in sorted(zip(x_axis,recall[k]))]
            plt.plot(sorted_x, sorted_recall, marker='.')
            plt.ylabel('recall')
            plt.savefig(plot_dir + experiment_name +'-'+ k +'-'+ 'recall.png')
            plt.clf() #clear the plot figure

            sorted_f0 = [f for (x,f) in sorted(zip(x_axis,f0[k]))]
            plt.plot(sorted_x, sorted_f0, marker='.')
            plt.ylabel('f0')
            plt.savefig(plot_dir + experiment_name +'-'+ k +'-'+ 'f0.png')
            plt.clf() #clear the plot figure
    else: #we have to plot performance over time (???)
        pass
