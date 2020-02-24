#!/bin/bash
#SBATCH -N 1
#SBATCH --cpus-per-task=40
#SBATCH -t 10:00:00
#SBATCH -p standard

module purge
module load anaconda

# activate temoa environment
source activate blis-py3

# set the NUM_PROCS env variable for the Python script
export NUM_PROCS=$SLURM_CPUS_PER_TASK

# run
python run_monte_carlo.py