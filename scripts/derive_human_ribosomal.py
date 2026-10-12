#!/usr/bin/env python3

import pandas as pd
import provenance
import source_files
import sys

NAMESPACE_SOURCES_DIR = "genes/human/namespaces/sources"
LIST_SOURCES_DIR = "genes/human/lists/ribosomal/sources"
DATA_FILE = "HGNC.Current.{version}.tsv"

# The HGNC gene groups of the cytoplasmic ribosomal proteins: 728 (small subunit) and 729 (large subunit).
GENE_GROUP_IDS = {"728", "729"}

# These encode ribosomal proteins fused to ubiquitin(-like) proteins.
EXCLUDED_SYMBOLS = {"FAU", "UBA52"}

def main():
    assert len(sys.argv) == 1, "Usage: derive_human_ribosomal.py"

    version_file = source_files.single(NAMESPACE_SOURCES_DIR, DATA_FILE)
    frame = pd.read_csv(f"{NAMESPACE_SOURCES_DIR}/{version_file}", dtype = str, keep_default_na = False, sep = "\t")
    source_name = version_file[:-4]
    symbol_column = str(frame.columns.get_loc("symbol"))

    rows = []
    for row, (symbol, hgnc_id, gene_group_ids) in enumerate(zip(frame.symbol, frame.hgnc_id, frame.gene_group_id)):
        if set(gene_group_ids.replace('"', "").split("|")) & GENE_GROUP_IDS and symbol not in EXCLUDED_SYMBOLS:
            rows.append((symbol, hgnc_id, provenance.step(source_name, row + 2, symbol_column)))

    source_files.write_derived(LIST_SOURCES_DIR, DATA_FILE, version_file, rows)

if __name__ == "__main__":
    main()
