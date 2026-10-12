#!/usr/bin/env python3

import pandas as pd
import provenance
import source_files
import sys

NAMESPACE_SOURCES_DIR = "genes/human/namespaces/sources"
LIST_SOURCES_DIR = "genes/human/lists/lateral/sources"
DATA_FILE = "HGNC.Current.{version}.tsv"

# The HGNC gene groups of the mitochondrial ribosomal proteins: 646 (all), 1994 (large subunit) and 1996 (small
# subunit). These include a few genes named for another function, such as DAP3.
GENE_GROUP_IDS = {"646", "1994", "1996"}

def main():
    assert len(sys.argv) == 1, "Usage: derive_human_lateral.py"

    version_file = source_files.single(NAMESPACE_SOURCES_DIR, DATA_FILE)
    frame = pd.read_csv(f"{NAMESPACE_SOURCES_DIR}/{version_file}", dtype = str, keep_default_na = False, sep = "\t")
    source_name = version_file[:-4]
    symbol_column = str(frame.columns.get_loc("symbol"))

    rows = []
    for row, (symbol, hgnc_id, gene_group_ids) in enumerate(zip(frame.symbol, frame.hgnc_id, frame.gene_group_id)):
        if set(gene_group_ids.replace('"', "").split("|")) & GENE_GROUP_IDS:
            rows.append((symbol, hgnc_id, provenance.step(source_name, row + 2, symbol_column)))

    source_files.write_derived(LIST_SOURCES_DIR, DATA_FILE, version_file, rows)

if __name__ == "__main__":
    main()
