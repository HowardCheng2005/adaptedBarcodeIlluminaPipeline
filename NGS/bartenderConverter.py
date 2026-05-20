import argparse
import gzip
import os
import glob

from Bio import SeqIO


def read_converter(read_files, output_file):
    read_count = 0

    with open(output_file, "w") as out:
        for file in read_files:
            with gzip.open(file, "rt") as f:
                for record in SeqIO.parse(f, "fastq"):
                    read = str(record.seq)

                    if len(read) == 38:
                        bartender_read = f"{read},{read_count}\n"
                        out.write(bartender_read)
                        read_count += 1
    return read_count

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_directory", required=True, help="Input fastq directory")
    parser.add_argument("-o", "--output_directory", required=True, help="Output directory")

    args = parser.parse_args()

    input_dir = args.input_directory
    output_dir = args.output_directory

    os.makedirs(output_dir, exist_ok=True)

    input_files = sorted(glob.glob(os.path.join(input_dir, "*merged.fastq.gz")))
    output_file = os.path.join(output_dir, "bartender_input.txt")

    count = read_converter(input_files, output_file)

    print(f"Finished. Wrote {count} reads to {output_file}")