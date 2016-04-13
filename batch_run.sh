for i in {0..30..1}
do
sbatch run_experiments.sh
echo "Starting up node"
sleep 10
done
