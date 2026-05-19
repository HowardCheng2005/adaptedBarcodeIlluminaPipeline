import gzip
import os
from argparse import ArgumentParser
from Bio import SeqIO

def analyze_fastq(input_fastq_file, forward_read, reverse_read):

    forward_read_id = []
    reverse_read_id = []
    total_forward_reads = 0
    total_reverse_reads = 0
    total_no_reads = 0

    with gzip.open(input_fastq_file, "rt") as f:
        for record in SeqIO.parse(f, "fastq"):
            id = record.id
            seq = str(record.seq).upper()

            if forward_read.upper() in seq:
                forward_read_id.append(id)
                total_forward_reads += 1
            elif reverse_read.upper() in seq:
                reverse_read_id.append(id)
                total_reverse_reads += 1
            else:
                total_no_reads += 1


    print("total no marker reads:", total_no_reads)
    print("total reads containing forward invariant:", total_forward_reads)
    print("total reads containing reverse complement:", total_reverse_reads)

    return forward_read_id, reverse_read_id



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input_fastq", required=True, help="Input fastq file")
    parser.add_argument("-o", "--output_dir", required=True, help="Output directory")
    parser.add_argument("-f", "--forward_marker", required=True, help="Forward read")
    parser.add_argument("-r", "--reverse_marker", required=True, help="Reverse read")
    args = parser.parse_args()

    input_fastq_file = args.input_fastq
    output_dir = args.output_dir
    forward_marker = args.forward_marker
    reverse_marker = args.reverse_marker

    forward_ids, reverse_ids = analyze_fastq(input_fastq_file, forward_marker, reverse_marker)

    with open(os.path.join(output_dir, "forward_ids.txt"), "w") as fw:
        fw.write("\n".join(forward_ids))

    with open(os.path.join(output_dir, "reverse_ids.txt"), "w") as fw:
        fw.write("\n".join(reverse_ids))
