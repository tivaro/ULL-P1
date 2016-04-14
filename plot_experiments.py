import json
import os

#find all files in the results folder
#group all experiment results that are part of the same experiment
experiments = {}
for f_name in os.listdir("results"):
    if f_name.endswith(".json"):
        exp_type = str.split(f_name)[0]
        if exp_type not in experiments:
            experiments[exp_type] = [f_name]
        else:
            experiments[exp_type].append(f_name)
            
#produce plots for each experiment
for exp_type in experiments:
    precision = []
    recall = []
    f0 = []
    file_list = experiments[exp_type]
    for file_name in file_list:
        f = open('results/' + file_name, 'r')
        exp_output = json.load(f)
        evaluation = exp_output['evaluation']
        print evaluation[0]
        precision.append(evaluation[0])
        recall.append(evaluation[1])
        f0.append(evaluation[2])
