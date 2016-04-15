#Delete the email file
export file="emailed_user"
if [ -f "$file" ]
     then
	rm "$file"
fi

export maxTimeout=600

export timeout=0
export no_old_files=-1

while [ $timeout -le $maxTimeout ]
do
export no_new_files="$(ls results -1 | wc -l)"
if [ $no_old_files -ne $no_new_files ];
then
	echo "Files = $no_new_files"
	echo "Starting up node $i"
	sbatch run_experiments.sh
	export no_old_files=$no_new_files
	export timeout=0
fi
timeout=$((timeout+10))
sleep 10
done

echo "File creation timed out ($maxTimeout sec)"
