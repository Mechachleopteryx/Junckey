"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

Get_PSI.py: calculate the PSI inclusion of the reads of the samples using the clusters
 generated by LeafCutter and returns a file with all the PSI values together, removing those clusters with NA values
 The input of this file should be the path where the LeafCutter files are located, and the readCOunts file
"""

import sys
import pandas as pd
import os
import logging
from copy import deepcopy
from argparse import ArgumentParser, RawTextHelpFormatter

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

description = \
    "Description:\n\n" + \
    "calculate the PSI inclusion of the reads of the samples using the clusters generated by LeafCutter and " \
    "returns a file with all the PSI values together, removing those clusters with NA values. The input of " \
    "this file should be the path where the LeafCutter files are located, and the readcounts file \n"

parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter,
                        add_help=True)
parser.add_argument("-l", "--leafcutter", required=True,
                    help="LeafCutter path")
parser.add_argument("-r", "--readcounts", required=True,
                    help="File with the read counts per junction")
parser.add_argument("-t", "--threshold", required=False, default=10,
                    help="Minimum number of reads per junction and per sample for generating a PSI value. (Default: 10 reads)")
parser.add_argument("-o", "--output", required=True,
                    help="Output file")

def main():

    args = parser.parse_args()

    try:

        LeafCutter_path = args.leafcutter
        readCounts_path = args.readcounts
        threshold = int(args.threshold)
        output_path = args.output

        # LeafCutter_path = "/projects_rg/SCLC_cohorts/Comparison_SCLC_PUCA_LUAD_LUSC/LeafCutter_output"
        # readCounts_path = "/projects_rg/SCM/tables/readCounts_SCLC_PUCA_LUAD_LUSC_Junckey.tab"
        # threshold = 10
        # output_path = "/projects_rg/SCLC_cohorts/Comparison_SCLC_PUCA_LUAD_LUSC/Junctions_PSI_clusters.tab"

        #############################################################################################################
        #1. Load the files generated by LeafCutter with the cluster numbers and return a file with all the PSI values
        #############################################################################################################

        bashCommand = "ls "+LeafCutter_path+"/*sorted.gz"
        cluster_files = os.popen(bashCommand, "r")

        for line in cluster_files:

            logger.info("Loading file: " + line.rstrip() + "...")
            file = pd.read_table(line.rstrip(), header=None, delimiter=" ", compression='gzip', skiprows=1)
            #For each line, calculate the PSI normalizing across the total number of reads per cluster
            psi_list = []
            for i in range(0, len(file.index)):
                aux = file.iloc[i,1].split("/")
                #If the denominator is not over the threshold, don't generate PSI
                if(float(aux[1])>=float(threshold)):
                    PSI = float(aux[0])/float(aux[1])
                else:
                    PSI = "NaN"
                psi_list.append(PSI)

            file['PSI'] = psi_list

            #Save the dataframe
            output_path_aux = LeafCutter_path + "/" + line.rstrip().split("/").pop()
            file.to_csv(output_path_aux[:-3], sep=" ", index=False,  float_format='%.f', header=False)

        #########################
        #2. Merge all the files #
        #########################

        bashCommand = "ls "+LeafCutter_path+"/*sorted"
        cluster_files = os.popen(bashCommand, "r")
        counter = 0

        logger.info("Merging files...")

        for line in cluster_files:

            #Load each file
            file = pd.read_table(line.rstrip(), header=None, delimiter=" ")#.dropna()
            #Remove the column with the reads
            del file[1]
            sampleId = line.rstrip().split("/").pop().split(".junc")[0]
            file = file.rename(columns={0: "Index", 2: sampleId})
            if(counter!=0):
                #merge both files
                file_merged = file_merged.merge(file,left_on="Index", right_on="Index", how='inner')
            else:
                file_merged = deepcopy(file)
            counter += 1

        #Split the index for having this info in different columns
        index_splitted = file_merged['Index'].apply(lambda x: x.split(":"))
        chr = list(map(lambda x: x[0],index_splitted))
        start = list(map(lambda x: x[1],index_splitted))
        end = list(map(lambda x: x[2],index_splitted))
        cluster = list(map(lambda x: x[3],index_splitted))
        id2 = file_merged['Index'].apply(lambda x: ";".join(x.split(":")[:-1])).tolist()

        #Add this lists to file_merged
        file_merged['start'] = start
        file_merged['end'] = end
        file_merged['chr'] = chr
        file_merged['cluster'] = cluster
        file_merged['id2'] = id2

        #####################################################################
        #3. Enrich the output. Get the Junction type and the associated genes
        #####################################################################

        logger.info("Loading "+readCounts_path+"...")
        readCounts = pd.read_table(readCounts_path, delimiter="\t")

        #Format previously the id. Add 1 to the end (Leafcutter adds 1 to the end cordinates)
        id3 = readCounts['id'].apply(lambda x: ";".join(x.split(";")[0:2])+";"+(str(int(x.split(";")[2])+1))).tolist()
        readCounts['id2'] = id3

        #We are interested just in a few columns
        readCounts = readCounts[['id2', 'strand','Associated_genes', 'Type_junction']]

        #Merge this info with the previous file for getting the Junction type and the associated genes
        file_merged2 = file_merged.merge(readCounts, left_on="id2", right_on="id2", how='inner')

        #Put it in the proper order for the vcf file
        sorted_columns = sorted(file_merged2.columns)

        # Remove the columns at the end and put it at the beginning
        sorted_columns.remove('cluster')
        sorted_columns.remove('chr')
        sorted_columns.remove('end')
        sorted_columns.remove('start')
        sorted_columns.remove('strand')
        sorted_columns.remove('Associated_genes')
        sorted_columns.remove('Type_junction')
        sorted_columns.remove('Index')
        sorted_columns.insert(0, "Associated_genes")
        sorted_columns.insert(0, "Type_junction")
        sorted_columns.insert(0, "strand")
        sorted_columns.insert(0, "cluster")
        sorted_columns.insert(0, "end")
        sorted_columns.insert(0, "start")
        sorted_columns.insert(0, "chr")
        sorted_columns.insert(0, "Index")

        file_merged3 = file_merged2.reindex(columns=sorted_columns)
        del file_merged3["id2"]

        #Sort the file
        # file_merged_sorted = file_merged3.sort(['chr', 'cluster', 'start', 'end'])   #DEPRECATED
        file_merged_sorted = file_merged3.sort_values(['chr', 'cluster', 'start', 'end'])


        #Save the dataframe
        logger.info("Creating file "+output_path+"...")
        file_merged_sorted.to_csv(output_path, sep="\t", index=False, na_rep='NaN')

        logger.info("Done. Exiting program.")

        exit(0)

    except Exception as error:
        logger.error(repr(error))
        logger.error("Aborting execution")
        sys.exit(1)


if __name__ == '__main__':
    main()
