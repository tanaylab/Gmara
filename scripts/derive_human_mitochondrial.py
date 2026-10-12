#!/usr/bin/env python3

import pandas as pd
import provenance
import source_files
import sys

NAMESPACE_SOURCES_DIR = "genes/human/namespaces/sources"
LIST_SOURCES_DIR = "genes/human/lists/mitochondrial/sources"
DATA_FILE = "HGNC.Current.{version}.tsv"

# The protein-coding genes of the mitochondrial genome.
SYMBOL_PREFIX = "MT-"
LOCUS_TYPE = "gene with protein product"

def main():
    assert len(sys.argv) == 1, "Usage: derive_human_mitochondrial.py"

    version_file = source_files.single(NAMESPACE_SOURCES_DIR, DATA_FILE)
    frame = pd.read_csv(f"{NAMESPACE_SOURCES_DIR}/{version_file}", dtype = str, keep_default_na = False, sep = "\t")
    source_name = version_file[:-4]
    symbol_column = str(frame.columns.get_loc("symbol"))

    rows = []
    for row, (symbol, hgnc_id, locus_type) in enumerate(zip(frame.symbol, frame.hgnc_id, frame.locus_type)):
        if symbol.startswith(SYMBOL_PREFIX) and locus_type == LOCUS_TYPE:
            rows.append((symbol, hgnc_id, provenance.step(source_name, row + 2, symbol_column)))

    source_files.write_derived(LIST_SOURCES_DIR, DATA_FILE, version_file, rows)

if __name__ == "__main__":
    main()
