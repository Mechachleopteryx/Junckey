
#The next code will convert the sjcount file from STAR output to BED
#We will modify the start and end cordinates for making them coincide with the exon cordinates of the gtf annotation. We will substract 2 to the start and add 1 to the end
#arg[1]: sjcount file
#arg[2]: output file

cat("\tSTARtoBED.R: Starting\n")

suppressMessages(require(data.table))

CHARACTER_command_args <- commandArgs(trailingOnly=TRUE)

sj_count <- fread(file=CHARACTER_command_args[1],sep="\t")
# sj_count <- fread(file="/projects_rg/Bellmunt/STAR/whole_cohort_v2/20160527-vh100-pool5-CWZ3082-1/SJ.out.tab",sep="\t")

colnames(sj_count) <- c("chrom","first_bp_intron","last_bp_intron","strand","intron_motif"
                    ,"annotated","unique_junction_reads","multimap_junction_reads"
                    ,"max_overhang")
#Don't forget to print the number without the scientifc notation (i.e. 2.7e+13)
sj_count$first_bp_intron <- gsub("\\s","",as.character(format(sj_count$first_bp_intron - 2, scientific = FALSE)))
sj_count$last_bp_intron <- gsub("\\s","",as.character(format(sj_count$last_bp_intron + 1, scientific = FALSE)))
sj_count$strand2 <- ifelse(sj_count$strand=="1","+",ifelse(sj_count$strand=="2","-",NA))
sj_count$score <- 0
#There are some blank spaces in the fields. Remove it with gsub
sj_count$id <- paste0(gsub("\\s","",as.character(sj_count$chrom)),";",gsub("\\s","",sj_count$first_bp_intron),";",gsub("\\s","",sj_count$last_bp_intron),";",sj_count$strand2)
#Remove the ones without strand
sj_count_filter <- sj_count[which(!is.na(sj_count$strand2)),]
sj_count_filter2 <- sj_count_filter[,c("chrom","first_bp_intron","last_bp_intron","id","unique_junction_reads","strand2","annotated")]

#save the file
write.table(sj_count_filter2,file=CHARACTER_command_args[2],sep="\t",row.names=FALSE,col.names=FALSE,quote=FALSE)
cat("\tSTARtoBED.R: Created SJ.out.bed\n")
cat("\tSTARtoBED.R: Finish\n")

