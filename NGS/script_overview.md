# Summary of Scripts
These scripts perform the pipeline specified in Figure 4 and the Methods section "Aim #1: Barcoded Computational Pipeline Overview" of our report.

<img width="599" height="385" alt="Screenshot 2026-04-14 at 5 51 28 PM" src="https://github.com/user-attachments/assets/c1b1b6df-3d6d-4196-87de-63f9ec2a79ff" />

## Pipeline Overview
### NGS_analysis.py
This script performs the main processing of fastq files. It obtains the raw fastq reads, and then runs cutadapt, NGmerge, and fastp quality filtering. The final output is merged .fastq files that are quality sorted.

### downsample.py
Performs the additional downsampling step. It does this by downsampling each fastq file such that each file contains the same numbe rof reads. This is important to ensure each file/bin contains the same number of reads and prevent high-depth bins from affecting the results.

### fileManager.py
Functions to manage files, directories, as well as run the log file, needed by NGS_analysis.py and downsample.py.

### conda_install.sh
Shell script to install all needed conda libraries. Conda needs to be downloaded, as well as an environment activated to work. For informaiton on this, see bioconda documentation.

## Testing Overview
These scripts are used to perform testing on our NGS-barcode pipeline.

### simData.py
Simulate Iluumina sequencing data, 4 bins with an R1 and R2 file in each. Each read contains the adaptor sequences trimmed off by cutadapt, as well as a barcode obtained from generate_mutants.py (see below). It also contains quality scores, as well as randomly mutated bases to test if NGmerge is properly able to assign a consensus read. 

### generate_mutants.py
Generate a file mutants.txt containing random barcode-variant associations for every single variant.


