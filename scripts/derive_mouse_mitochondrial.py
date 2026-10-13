#!/usr/bin/env python3

import pandas as pd
import provenance
import source_files
import sys

NAMESPACE_SOURCES_DIR = "genes/mouse/namespaces/sources"
LIST_SOURCES_DIR = "genes/mouse/lists/mitochondrial/sources"
DATA_FILE = "MGI.{version}.tsv"

# The current gene markers of the mitochondrial genome: the protein-coding, ribosomal RNA and transfer RNA genes.
SYMBOL_PREFIX = "mt-"
FEATURE_TYPES = {"protein coding gene", "rRNA gene", "tRNA gene"}

def main():
    assert len(sys.argv) == 1, "Usage: derive_mouse_mitochondrial.py"

    version_file = source_files.single(NAMESPACE_SOURCES_DIR, DATA_FILE)
    frame = pd.read_csv(f"{NAMESPACE_SOURCES_DIR}/{version_file}", dtype = str, keep_default_na = False, sep = "\t")
    source_name = version_file[:-4]
    symbol_column = str(frame.columns.get_loc("Marker Symbol"))

    rows = []
    for row, (symbol, mgi_id, status, feature_type) \
    in enumerate(zip(frame["Marker Symbol"], frame["MGI Accession ID"], frame["Status"], frame["Feature Type"])):
        if symbol.startswith(SYMBOL_PREFIX) and status == "O" and feature_type in FEATURE_TYPES:
            rows.append((symbol, mgi_id, provenance.step(source_name, row + 2, symbol_column)))

    source_files.write_derived(LIST_SOURCES_DIR, DATA_FILE, version_file, rows)

if __name__ == "__main__":
    main()
