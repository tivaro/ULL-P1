#!/bin/bash
#SBATCH -N 1
#SBATCH -t 22:00:00
module load python

if [ srun -u python "SVM.py" ]; then
	mailx -s "Experiment completed\! :)" < /dev/null "tivarosite@gmail.com"
else
	mailx -s "Experiment failed :(" < /dev/null "tivarosite@gmail.com"
fi

sleep 20
