from argparse import ArgumentParser

def barcode_reader(input):
    with open(input, 'r') as f:
        num_barcodes = []
        barcode_seq = []

        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            num_barcodes.append(int(parts[0]))
            barcode_seq.append(parts[1])

    return num_barcodes, barcode_seq

def barcode_writer(num_barcodes, barcode_seq, offset, output_file, unique=False):
    index = offset
    lines_written = 0

    with open(output_file, 'w') as f:
        for j, barcode in enumerate(barcode_seq):
            if unique:
                index += 1
                f.write(f"{barcode},{index}\n")
                lines_written += 1

            else:
                for _ in range(num_barcodes[j]):
                    index += 1
                    f.write(f"{barcode},{index}\n")
                    lines_written += 1

    return index, lines_written

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input file")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("-n", "--number", required=True, type=int, help="Offset of index")
    parser.add_argument("-u", "--unique", action="store_true", help="Use unique barcodes only once")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    offset = args.number
    use_unique = args.unique

    number_barcodes, barcode_sequence = barcode_reader(input_file)
    final_index, total_lines = barcode_writer(
        number_barcodes,
        barcode_sequence,
        offset,
        output_file,
        unique=use_unique
    )

    print(f"Wrote {total_lines} lines to {output_file}")
    print(f"Final index at {final_index}")