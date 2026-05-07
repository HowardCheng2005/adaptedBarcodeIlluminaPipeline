"""
This script obtains data form Illumina NGS Sequencing and extracts out the barcode region.
This script does the following:
- Run cutadapt to remove the adaptors for the barcode sequence
- Run NGMerge to merge the R2 and R1 reads
- Run quality_filter to filter the reads for unquality and ambiguous bases
"""
import argparse
import os
from Bio.Seq import Seq
import subprocess

from fileManager import create_log, create_dir, get_files

def get_raw_reads_files(directory):
    """
    Get raw reads files.
    :return: forward and reverse raw reads files
    """
    # Get forward and reverse raw reads files in NextSeq2000_raw_reads directory.
    # TODO: Check naming for NextSeq files

    forward_raw_reads = get_files(directory, f"*R1*.fastq.gz")
    reverse_raw_reads = get_files(directory, f"*R2*.fastq.gz")

    #Checks if R1/R2 files exist, and whether the amount of files between the two match
    if (len(forward_raw_reads) != len(reverse_raw_reads)) or (len(forward_raw_reads) == 0) :
        raise ValueError(f"R1/R2 amount of files different")

    # checks is forward and reverse reads match
    for (r1, r2) in zip(forward_raw_reads, reverse_raw_reads):
        expected_r2 = os.path.basename(r1).replace("_R1_", "_R2_")
        actual_r2 = os.path.basename(r2)

        if expected_r2 != actual_r2:
            raise ValueError(f"R1/R2 pairing error")

    return forward_raw_reads, reverse_raw_reads


def rc(primer):
    """
    Get reverse complement of primer.
    :param primer: primer sequence
    :return: reverse complement of primer
    """
    return str(Seq(primer).reverse_complement())

def cutadapt(forward_raw_reads, reverse_raw_reads, forward_adaptor, reverse_adaptor):
    """
    Cut adaptors from raw reads using the cutadapt package.
    The adaptor we cut is based on the resulting data.

    Creates these cut reads in a directory called cutadapt.

    :param forward_raw_reads: raw uncut forwards reads from NextSeq
    :param reverse_raw_reads:raw uncut reverse reads from NextSeq
    :return output files produced
    """
    LOG.info("Start cutadapt...")

    # Log cutadapt path and version
    LOG.info(f"Cutadapt path: {subprocess.check_output(['which', 'cutadapt']).decode('utf-8').strip()}")
    LOG.info(f"Cutadapt version: {subprocess.check_output(['cutadapt', '--version']).decode('utf-8').strip()}")

    # Create output directory.
    out_dir = create_dir(os.getcwd(), "cutadapt")
    LOG.info(f"Output directory: {out_dir}")

    # Create forward file names.
    forward_cutadapt_files = [os.path.join(out_dir,
                                           f.split("/")[-1].replace(".fastq", "_cutadapt.fastq"))
                              for f in forward_raw_reads]
    LOG.info(f"Forward output files:{forward_cutadapt_files}")

    # Create reverse file names.
    reverse_cutadapt_files = [os.path.join(out_dir,
                                           f.split("/")[-1].replace(".fastq", "_cutadapt.fastq"))
                              for f in reverse_raw_reads]
    LOG.info(f"Reverse output files:{reverse_cutadapt_files}")

    # Setup cutadapt commands and flags
    cutadapt_commands = [["cutadapt"] +
                         [f"-a", f"{forward_adaptor}...{reverse_adaptor}"] +
                         [f"-A", f"{rc(reverse_adaptor)}...{rc(forward_adaptor)}"] +
                         [f"-o", f"{forward_cutadapt_files[i]}"] +
                         [f"-p", f"{reverse_cutadapt_files[i]}"] +
                         [f"{forward_raw_reads[i]}"] +
                         [f"{reverse_raw_reads[i]}"]
                         for i in range(len(forward_raw_reads))]

    # Cut adapters from forward and reverse reads.
    for command in cutadapt_commands:
        LOG.info(f"Running cutadapt command: {' '.join(command)}")
        try:
            LOG.info(subprocess.check_output(command).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            LOG.error(f"Error: {e}")

    LOG.info("Cutadapt done.")
    return forward_cutadapt_files, reverse_cutadapt_files

def NGmerge(forward_cutadapt_reads, reverse_cutadapt_reads):
    """
    Merge paired-end reads using the NGmerge package

    Creates these merged reads in a directory called NGmerge.

    :param forward_cutadapt_reads: forward reads obtained from cutadapt
    :param reverse_cutadapt_reads: reverse reads obtained from cutadapt
    :return output files produced
    """
    LOG.info("Start NGmerge...")

    # Set output directory.
    out_dir = create_dir(os.getcwd(), "NGmerge")
    LOG.info(f"Output directory: {out_dir}")

    # Create output file names.
    merged_files = [os.path.join(out_dir, f.split("/")[-1].replace("R1_001_cutadapt.fastq", "merged.fastq"))
                    for f in forward_cutadapt_reads]
    LOG.info(f"Output files: {merged_files}")

    # Create output log files. These will store the mismatches detected by NGmerge
    log_files = []
    for i in range(len(merged_files)):
        filename = merged_files[i].split("/")[-1].replace("merged.fastq", "mismatch.log")
        log_files.append(os.path.join(os.getcwd(), "logs", filename))

    # NGmerge commands.
    NGmerge_commands = [["NGmerge"] +
        ["-b", "-j", log_files[i]] +
        # ["-p", "0"] + TODO: See if need this parameter to remove all mismatched sequences
        ["-1", f"{forward_cutadapt_reads[i]}"] +
        ["-2", f"{reverse_cutadapt_reads[i]}"] +
        ["-o", f"{merged_files[i]}"]
        for i in range(len(merged_files))
    ]

    # Run NGmerge commands.
    for command in NGmerge_commands:
        LOG.info(f"Running NGmerge command: {' '.join(command)}")
        try:
            LOG.info(subprocess.check_output(command).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            LOG.error(f"Error: {e}")

    LOG.info("NGmerge done.")
    return merged_files

def quality_filter(merged_reads):
    """
    Filter merged reads by length, and filter out ambiguous bases,
    using the fastp package.

    For barcoding, quality and length must be very strict, as small changes
    in the barcode can result in a completely different variant.

    Creates these filtered reads in a directory called Quality_Filtered.

    :param merged_reads: the merged reads obtained from NGmerge
    """
    LOG.info("Start Quality Filtering...")

    # Set output directory.
    out_dir = create_dir(os.getcwd(), "Quality_Filtered")
    LOG.info(f"Output directory: {out_dir}")

    # Create output file names.
    filtered_reads = [os.path.join(out_dir, f.split("/")[-1].replace("merged.fastq", "quality_merged.fastq"))
                    for f in merged_reads]
    LOG.info(f"Output files: {filtered_reads}")

    # NGmerge commands.
    quality_filter_commands = [["fastp"] +
        ["-i", f"{merged_reads[i]}"] +
        ["-o", f"{filtered_reads[i]}"] +
        ["-l", f"{LENGTH}"] +
        ["-q", f"{QUALITY}"] +
        ["-u", f"{UNQUALIFIED}"] +
        ["-n", "0"] # No ambiguous bases should be present
        for i in range(len(merged_reads))
    ]

    # Run NGmerge commands.
    for command in quality_filter_commands:
        LOG.info(f"Running Quality Filter command: {' '.join(command)}")
        try:
            LOG.info(subprocess.check_output(command).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            LOG.error(f"Error: {e}")

    LOG.info("Quality filtering done.")
    return filtered_reads


def main(directory, forward_primer, reverse_primer):
    """
    Main function for our NGS analysis
    :param directory: directory of input data
    :return: cut, merged, and quality filtered files
    """
    # Get forward and reverse reads files and store in separate lists.
    forward_raw_reads_files, reverse_raw_reads_files = get_raw_reads_files(directory)
    LOG.info(f"Forward raw files: {forward_raw_reads_files}")
    LOG.info(f"Reverse raw files: {reverse_raw_reads_files}")
    LOG.info(f"Forward primer: {forward_primer}")
    LOG.info(f"Reverse primer: {reverse_primer}")
    # Run cutadapt and get clean cutadapt files
    forward_cutadapt_files, reverse_cutadapt_files = (
        cutadapt(forward_raw_reads_files, reverse_raw_reads_files, forward_primer, reverse_primer))
    LOG.info(f"Forward files: {forward_cutadapt_files}")
    LOG.info(f"Reverse files: {reverse_cutadapt_files}")
    # Run NGmerge and get clean merged files
    merged_files = NGmerge(forward_cutadapt_files, reverse_cutadapt_files)
    LOG.info(f"Merged files: {merged_files}")
    # Run Quality Filtering and get clean filtered files
    return quality_filter(merged_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script performs cutting, "
                                                 "merging, and quality filtering on"
                                                 "NGS data")

    # Required arguments
    # UPDATED: USES PATH TO DIRECTORY INSTEAD OF NAME OF DIRECTORY
    # note: make sure that the library and maxiprep reads are in different folders
    parser.add_argument('-d', required=True, help="Directory pathway for input data")
    # Pathway should not be used due to conda environment
    parser.add_argument('-p', required=False, help="Pathway to NGS libraries")
    parser.add_argument('-t', required=False, default=3, help="Threads to run the program, deafult is 3")
    parser.add_argument('-q', required=False, default=15, help="Quality Threshold")
    parser.add_argument('-f', required=True, help="Forward Primer")
    parser.add_argument('-r', required=True, help="Reverse Primer")

    args = parser.parse_args()

    # Set Status, Random, Logfile for testing purposes.
    STATUS = 0
    DIR = args.d
    THREADS = args.t
    LOG = create_log(STATUS)

    # Pathways (ngs libraries already downloaded via conda)
    # CUTADAPT_EXE = f"{args.p}/cutadapt"
    # NGMERGE_EXE = f"{args.p}/NGmerge"
    # FASTP_EXE = f"{args.p}/fastp"

    # Quality Filtering Parameters
    # TODO: Quality filtering parameters will differ based on experimental data
    QUALITY = args.q # Quality threshold for each base to be qualified
    UNQUALIFIED = 0 # Percent of bases that can be unqualified
    LENGTH = 38 # Length of the barcode

    # Set forward and reverse primers and get their reverse complements.
    forward_primer = args.f
    # 'AGCTCGGATCCACTAGTAACGACCTCAAGTGTGCTGGAAGT' # TODO: check forward primer
    reverse_primer = args.r
    # 'TCTGCAGATATCCATCACACTGGAGGTCGATC' # TODO: check reverse primer

    # Run main function
    filtered_files = main(DIR, forward_primer, reverse_primer)

