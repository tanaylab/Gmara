#!/usr/bin/env python3

import pandas as pd
import provenance
import re
import source_files
import sys

NAMESPACE_SOURCES_DIR = "genes/mouse/namespaces/sources"
LIST_SOURCES_DIR = "genes/mouse/lists/ribosomal/sources"
DATA_FILE = "MGI.{version}.tsv"

# The current protein-coding markers named as cytoplasmic ribosomal proteins. This includes the retro-copies (such as
# Rpl27rt), but not the kinases and binding proteins (such as Rps6ka1).
MARKER_NAME = re.compile(r"ribosomal protein (L|S|lateral stalk).*")
EXCLUDED_MARKER_NAME = re.compile(r".*(kinase|binding protein).*")

def main():
    assert len(sys.argv) == 1, "Usage: derive_mouse_ribosomal.py"

    version_file = source_files.single(NAMESPACE_SOURCES_DIR, DATA_FILE)
    frame = pd.read_csv(f"{NAMESPACE_SOURCES_DIR}/{version_file}", dtype = str, keep_default_na = False, sep = "\t")
    source_name = version_file[:-4]
    symbol_column = str(frame.columns.get_loc("Marker Symbol"))

    rows = []
    for row, (symbol, mgi_id, status, feature_type, marker_name) in enumerate(zip(
        frame["Marker Symbol"], frame["MGI Accession ID"], frame["Status"], frame["Feature Type"], frame["Marker Name"]
    )):
        if status == "O" and feature_type == "protein coding gene" \
        and MARKER_NAME.fullmatch(marker_name) and not EXCLUDED_MARKER_NAME.fullmatch(marker_name):
            rows.append((symbol, mgi_id, provenance.step(source_name, row + 2, symbol_column)))

    source_files.write_derived(LIST_SOURCES_DIR, DATA_FILE, version_file, rows)

if __name__ == "__main__":
    main()
