for i in {0..30..1}
do
echo "Starting up node $i"
sbatch run_experiments.sh
sleep 10
done
