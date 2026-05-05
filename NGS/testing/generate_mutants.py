"""
This file generates simulated mutants for the barcoded DMS library project.
It will produce a barcode followed by the AA mutation it corresponds to
The data is based on the following wildtype AA sequence

MEAIIMTTLPNLTTDAGDSSFWLTGALSLSEMLANSSHSHSTGSTTSTAGSSATESSAVNVGKDHDKHVNDSVSTGLSN
YSNYPSYIHYRDKYDLSYIAKVNPFWLQFEPPKSSTFLIMAALYCLISVVGCVGNAFVIFMFANRKSLRTPANILVMNL
AICDFLMLIKCPIAIYNNIKEGPALGDIACRLYGFVGGLSGTCAIGTLTAIALDRYNVVVHPLQPLRRCSRLRSYLIIL
LIWCYSFLFAVMPALDIGLSVYVPEGFLTTCSFDYLNKEMPARIFMALFFVAAYCIPLTSIVYSYFYILKVVFTASRIQ
SNKDKAKTEQKLAFIVAAIIGLWFLAWSPYAIVAMMGVFGLERHITPLGSMIPALFCKTAACVDPYLYAATHPRFRVEV
RMLFYGRG

where the DNA barcode is flanked by a barcode amplicon sequence
"""
import random

PROTEIN_SEQUENCE = ("FEPPKSSTFLIMAALYCLISVVGCVGNAFVIFMFANRKSLRTPANILVMNLAICDFLMLI"
                    "KCPIAIYNNIKEGPALGDIACRLYGFVGGLSGTCAIGTLTAIALDRYNVVVHPLQPLRRC"
                    "SRLRSYLIILLIWCYSFLFAVMPALDIGLSVYVPEGFLTTCSFDYLNKEMPARIFMALFF"
                    "VAAYCIPLTSIVYSYFYILKVVFTASRIQSNKDKAKTEQKLAFIVAAIIGLWFLAWSPYA"
                    "IVAMMGVFGLERHITPLGSMIPALFCKTAACVDPYLYAATHPRFRVEVRMLFYGRG")

AMINO_ACIDS = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y', '*']

BARCODE = "NNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNNWSNNN" # Barcode Region
USED_BARCODES = set()
N = ["A", "C", "T", "G"]
W = ["A", "T"]
S = ["C", "G"]
possible_bases = {"N": N, "W": W, "S": S}

LENGTH = 296

def generate_single_mutant(position):
    """
    Generates mutants based on mutations of a specific amino acid.
    Returns these mutants as a list
    """
    old = PROTEIN_SEQUENCE[position]
    return [f"{old}{position + 1}{a}" for a in AMINO_ACIDS if a != old ]

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

if __name__ == '__main__':
    with open("mutants.txt", 'w') as m:
        generate_barcode(BARCODE)
        for i in range(LENGTH):
            for mutant in generate_single_mutant(i):
                m.write(f"{generate_barcode(BARCODE)}\t{mutant}\n")
