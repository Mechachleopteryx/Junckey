#!/bin/sh

#SBATCH --partition=lowmem
#SBATCH --mem 6000

# ==============================================================================================
# format_STAR_output_pipeline_cluster_slurm_part2:
#
# Description: This part2 gather all the information generated with the part1 in one file#
#
# Input: arg[1] --> path to the STAR output file (one folder per sample)
#	 arg[2] --> output path where the files will be generated
#    arg[3] --> file with the number of total mapped reads from STAR (run previosuly get_total_mapped_reads.sh)
#    arg[4] --> path to the Junckey scripts
# ==============================================================================================

i_dir=$1
o_dir=$2
total_reads_mapped_dir=$3
#i_dir2=$3
scripts_dir=$4

module load R
#If it's HYDRA
module load RStudio
#If it's MARVIN
#module load Rstudio
module load BEDTools
module load Python

echo "format_STAR_output_pipeline_cluster_slurm_part2: Starting execution. "$(date)

#Store the path where the scripts are (not working in slurm)
MYSELF="$(readlink -f "$0")"
MYDIR="${MYSELF%/*}"

# TODO Problems in rpkm.tab generation on pool_results. This step is not necessary until this part is not fixed
#1. Format the Log.Final.out files
#echo "Formatting Log.Final.out files..."
#Rscript "$MYDIR"/format_Log_STAR.R "$i_dir"/ "$o_dir"/

#2. Pool the reads from all the samples in one file
echo "format_STAR_output_pipeline_cluster_slurm_part2: Gathering all files into one..."
python "$scripts_dir"/pool_results.py "$i_dir" "$o_dir" "$total_reads_mapped_dir"

echo "format_STAR_output_pipeline_cluster_slurm_part2: End of execution. "$(date)
exit 0
