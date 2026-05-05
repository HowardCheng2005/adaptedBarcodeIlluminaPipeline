import os
import argparse
import subprocess

from fileManager import create_log, create_dir, get_files

# TODO: Add bootstrapping, learn stats stuff

def downsample(input_files, out_dir, random_state, downsample_proportion):
    """
    Downsample fastq files.
    :param input_file      s: list of input files
    :param out_dir: output directory
    :param random_state: random state used for sampling
    :return: downsampled files
    """
    logger.info("Starting downsample...")

    # Set downsample proportion
    logger.info(f"Downsample proportion: {downsample_proportion}")

    # Downsample files
    for file in input_files:
        proportion = downsample_proportion[file]
        logger.info(f"Downsampling {file} with proportion {proportion}...")

        # Downsample using SeqKit
        out_file = os.path.join(out_dir, file.split("/")[-1])
        cmd = f"{SEQKIT_EXE} sample -p {proportion} -s {random_state} {file} -o {out_file}"

        try:
            logger.info(subprocess.check_output(cmd, shell=True).decode("utf-8"))
        except subprocess.CalledProcessError as e:
            logger.error(f"Error: {e}")

    logger.info("Downsample done!")

    return None

def get_proportions(files):
    """
    Given a list of fastq files, obtain the proportion each needs to be downsampled to obtain equal
    number of reads in each file.
    :param files: List of fastq files
    :return: Dict containing porportions
    """

    proportions = []
    for i in range(len(files)):
        with open(files[i], 'r') as f:
            proportions.append(len(f.readlines()))

    smallest = min(proportions)
    result = {}

    for p in range(len(proportions)):
        result[files[p]] = smallest/proportions[p]

    return result

if __name__ == "__main__":
    STATUS = 1
    SEQKIT_EXE = "/Users/r.fu/opt/anaconda3/envs/barcodedDMS/bin/seqkit"

    # Specify random state
    # Ask user to specify random state using argparse with the flag --random_state
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--random_state", type=int, help="Random state used for sampling in SeqKit")
    args = parser.parse_args()
    random_state = args.random_state

    # Create log file
    logger = create_log(random_state)

    # Set input directory
    in_dir = os.path.join(os.getcwd(), "Quality_Fitered")
    logger.info(f"Input directory: {in_dir}")

    # Get input files
    dir = os.path.join(os.getcwd(), "Quality_Filtered")
    input_files = get_files(dir, "*_quality_merged.fastq")

    # Set output directory
    out_root_dir = create_dir(os.getcwd(), "downsample_outputs")
    out_dir = create_dir(out_root_dir, f"downsample_{random_state}")
    logger.info(f"Output directory: {out_dir}")

    # Downsample files
    downsample_proportion = get_proportions(input_files)
    downsample(input_files, out_dir, random_state, downsample_proportion)

    logger.info("Downsampling done")
