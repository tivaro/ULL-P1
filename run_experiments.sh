#!/bin/bash
#SBATCH -N 1
#SBATCH -t 22:00:00
module load python

cd ~/ULL-P1

srun -u python "experiments.py" && export subject="SUCCES :)" || export subject="FAILURE :("

#Only mail the user once
export file="emailed_user"
if ! [ -f "./$file" ]
	then
	mailx -s $subject < /dev/null "tivarosite@gmail.com"
	touch "$file"
fi

sleep 20

git add results/*.json

git commit -m "Automated results push"

git push

sleep 20
