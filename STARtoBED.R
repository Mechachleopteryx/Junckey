#!/soft/R/R-3.2.3/bin/Rscript

#The next code will convert the sjcount file from STAR output to BED
#We will modify the start and end cordinates for making them coincide with the exon cordinates of the gtf annotation. We will substract 2 to the start and add 1 to the end
#arg[1]: sjcount file
#arg[2]: output file

CHARACTER_command_args <- commandArgs(trailingOnly=TRUE)

sj_count <- read.table(file=CHARACTER_command_args[1],sep="\t")
colnames(sj_count) <- c("chrom","first_bp_intron","last_bp_intron","strand","intron_motif"
                    ,"annotated","unique_junction_reads","multimap_junction_reads"
                    ,"max_overhang")
sj_count$first_bp_intron <- sj_count$first_bp_intron - 2
sj_count$last_bp_intron <- sj_count$last_bp_intron + 1
sj_count$strand2 <- ifelse(sj_count$strand=="1","+",ifelse(sj_count$strand=="2","-",NA))
sj_count$score <- 0
sj_count$id <- paste0(sj_count$chrom,";",sj_count$first_bp_intron,";",sj_count$last_bp_intron,";",sj_count$strand2)
sj_count_filter <- sj_count[which(!is.na(sj_count$strand2)),]
sj_count_filter2 <- sj_count_filter[,c("chrom","first_bp_intron","last_bp_intron","id","unique_junction_reads","strand2","annotated")]

#save the file
write.table(sj_count_filter2,file=CHARACTER_command_args[2],sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)

