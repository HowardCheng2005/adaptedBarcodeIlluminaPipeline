"""
This file generates simulated sequence data for the barcoded DMS library project.
The data is based on the following DNA barcode

AGCTCGGATCCACTAGTAACGACCTCAAGTGTGCTGGAAGT
NNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNN
TCTGCAGATATCCATCACACTGGAGGTCGATC

where the DNA barcode is flanked by a barcode amplicon sequence
"""
import argparse
import os
import random

from Bio.Seq import Seq

# TODO: Note each bin has the same set of heterpogenous primers
BARCODE_FULL = ("AGCTCGGATCCACTAGTAACGACCTCAAGTGTGCTGGAAGT"
           "NNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNN"
           "TCTGCAGATATCCATCACACTGGAGGTCGATC")

# TODO: Ensure that barcode is not prone to errors (e.g. no four A's in a row)
BARCODE = "NNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNN" # Barcode Region

FORWARD_PRIMER = "TAGCATGCATAGGCCTATCACGATTGATAGCG"
REVERSE_PRIMER = "CTTACTAGTCTAGCCCTCTAGATGCATGCTC"
AMPLICON1 = "AGCTCGGATCCACTAGTAACGACCTCAAGTGTGCTGGAAGT" # Region prior
AMPLICON2 = "TCTGCAGATATCCATCACACTGGAGGTCGATC" # Region after

USED_BARCODES = set()

N = ["A", "C", "T", "G"]
W = ["A", "T"]
S = ["C", "G"]
possible_bases = {"N": N, "W": W, "S": S}

def rc(primer):
    """
    Get reverse complement of primer.
    :param primer: primer sequence
    :return: reverse complement of primer
    """
    return str(Seq(primer).reverse_complement())

def generate_barcode(barcode:str):
    """
    Generates a barcode based on a barcode template
    :param barcode: template for barcode
    :return: barcode
    """
    result = ""
    while result in USED_BARCODES:
        for base in barcode:
            result += random.choice(possible_bases[base])
    USED_BARCODES.add(result)
    return result

def generate_quality():
    """
    Generates quality scores for each nucleotide in the full barcode
    :return: sequence of errors
    """
    result = ""
    for _ in range(len(BARCODE_FULL + FORWARD_PRIMER + REVERSE_PRIMER)):
        result += chr(random.randint(50, 70))
    return result

def write_fasta(filename, data):
    with open(filename, 'w') as file:
        for name, sequence in data.items():
            file.write(f"@{name}\n")
            file.write(f"{sequence}\n")
            file.write(f"+\n")
            file.write(f"{generate_quality()}\n")

def get_mutation_dict(mutants_file):
    result = set()
    for line in mutants_file:
        result.add(line.split("\t")[0])
    return result

def simMutants(mutants_file):
    mutations = list(get_mutation_dict(mutants_file))
    result = []
    for _ in range(NUM_MUTANTS):
        result.append(random.choice(mutations))
    return result

def mutate(barcode):
    barcode_list = list(barcode)
    pos = random.randint(1,len(barcode))
    base = random.randint(1,4)
    bases = ['A','T','C','G']
    barcode_list[pos - 1] = bases[base - 1]
    return ''.join(barcode_list)

def simMutantData(mutant_file, directory, mismatches):
    mutants = simMutants(mutant_file)
    with open(mismatches, 'a') as f:
        f.write(f"Mismatches in {directory}\n")
    for r in range(1, BINS + 1):
        dir = os.path.join(os.getcwd(), directory)
        os.makedirs(dir, exist_ok=True)
        mutantData_R2 = {}
        mutantData_R1 = {}

        for i in range(READS):
            barcode = random.choice(mutants)
            num = random.randint(1,100)
            if num == 1:
                old = barcode
                barcode = mutate(barcode)
                if old != barcode:
                    with open(mismatches, 'a') as f:
                        f.write(f"Bin: {r}, Mutant: {i}, Old: {old}, Mutated: {barcode}\n")
            else:
                old = barcode
            mutantData_R2[f"Mutant_{i}"] = (FORWARD_PRIMER + AMPLICON1 +
                                            barcode +
                                            AMPLICON2 + rc(REVERSE_PRIMER))

            mutantData_R1[f"Mutant_{i}"] = (REVERSE_PRIMER +
                                            rc(FORWARD_PRIMER + AMPLICON1 +
                                               old + AMPLICON2))
            if i%10000==0:
                print(f"Bin {r}, Mutant {i} R2")
                print(mutantData_R2[f"Mutant_{i}"])

        write_fasta(os.path.join(dir, f"{directory}{r}_R2.fastq"), mutantData_R2)
        write_fasta(os.path.join(dir, f"{directory}{r}_R1.fastq"), mutantData_R1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script performs simulates the creation"
                                                 "of NGS data that should be run through the pipeline")

    # Required argument with -d short flag
    parser.add_argument('-d', required=True, help="Directory we want to put data in")
    parser.add_argument('-n', required=True, help="Number of reads we want to simulate")
    parser.add_argument('-m', required=True, help="Number of mutants we want to simulate")

    args = parser.parse_args()
    DIR = args.d
    READS = int(args.n)
    BINS = 4
    NUM_MUTANTS = int(args.m)
    with open("Simulations/mutants.txt", 'r') as m:
        simMutantData(m, DIR, 'mismatches.txt')
