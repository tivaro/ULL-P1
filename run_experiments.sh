#!/bin/bash
#SBATCH -N 1
#SBATCH -t 22:00:00
module load python

cd ~/ULL-P1

srun -u python "experiments.py" && export subject="SUCCES :)" || export subject="FAILURE :("

mailx -s $subject < /dev/null "tivarosite@gmail.com"

sleep 20

git add results/*.json

git commit -m "Automated results push"

git push

sleep 20
