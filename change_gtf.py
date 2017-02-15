"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

change_gtf.py: given an geneAnnotated.bed generate with GenestoJunctions.R,
it associates the genes in the junctions of this file to the ones provided in the
other junctions file
"""

import sys
import time

def main():
    try:

        geneAnnotated_path = sys.argv[1]
        junctions_path = sys.argv[2]
        output_path = sys.argv[3]

        # geneAnnotated_path = "/projects_rg/Annotation/Junctions/aux.sorted.geneAnnotated.bed"
        # junctions_path = "/projects_rg/Annotation/Junctions/Junctions_psi_clusters_TCGA_RefSeq.tab"
        # output_path = "/projects_rg/Annotation/Junctions/Junctions_psi_clusters_TCGA_Ensembl.tab"

        print("Starting execution: "+time.strftime('%H:%M:%S')+"\n")

        ############################################################################################
        #1. Read the geneAnnotated_file and save all the junction-gene associations in a dictionary
        # and the junction type
        ############################################################################################

        print("Reading "+geneAnnotated_path+"...")

        dict_junction_gene, dict_junction_type = {}, {}
        with open(geneAnnotated_path) as f:
            next(f)
            for line in f:
                tokens = line.rstrip().split("\t")
                # Add 1 to the end cordinate and substitute by :
                tokens2 = tokens[0].split(";")[:-1]
                tokens2[2] = str(int(tokens2[2]) + 1)
                id_formatted = ":".join(tokens2)

                dict_junction_gene[id_formatted] = tokens[7]
                dict_junction_type[id_formatted] = tokens[8]

        ############################################################################################
        #2. Read the junctions_file and associate to the existing junctions the new saved genes
        ############################################################################################

        print("Formatting " + junctions_path + "...")

        outFile = open(output_path, 'w')

        with open(junctions_path) as f:
            outFile.write(next(f))
            for line in f:
                tokens = line.rstrip().split("\t")
                id_formatted = ":".join(tokens[0].split(":")[:-1])
                if (id_formatted in dict_junction_gene):
                    tokens[6] = dict_junction_gene[id_formatted]
                    tokens[5] = dict_junction_type[id_formatted]
                else:
                    #If the key doesn't exist, assign the junction to no gene and the junction type to 5 (new junction)
                    tokens[6] = ""
                    tokens[5] = str(5)
                new_line = "\t".join(tokens)
                outFile.write(new_line + "\n")

        outFile.close()
        print("Saved " + output_path)

        print("\nDone. Exiting program. "+time.strftime('%H:%M:%S')+"\n")

        exit(0)

    except Exception as error:
        print('ERROR: ' + repr(error))
        print("Aborting execution")
        sys.exit(1)


if __name__ == '__main__':
    main()