#!/usr/bin/env python3

import csv
import glob
import os
import re
import requests
import sys

DOWNLOAD_PAGE_URL = "https://humantfs.ccbr.utoronto.ca/download.php"

SOURCES_DIR = "genes/human/lists/transcription_factor/sources"

# Ensembl does not have these genes, so their `Ensembl ID` holds a UniProt name instead.
UNIPROT_NAMES = ["DUX1_HUMAN", "DUX3_HUMAN"]

def main():
    assert len(sys.argv) == 1, "Usage: fetch_toronto.py"

    versions = set(re.findall(r"v_([0-9]+\.[0-9]+)", fetch_text(DOWNLOAD_PAGE_URL)))
    version = max(versions, key = lambda version: [int(part) for part in version.split(".")])
    url = f"https://humantfs.ccbr.utoronto.ca/download/v_{version}/DatabaseExtract_v_{version}.csv"
    print(f"Fetch {url} ...", flush = True)

    # Keep the lines (with their CRLF line endings) as they are, except for the ones which are not TFs.
    lines = fetch_text(url).split("\r\n")
    is_tf_index = next(csv.reader([lines[0]])).index("Is TF?")
    kept_lines = [lines[0]]
    for line in lines[1:]:
        if line != "" and next(csv.reader([line]))[is_tf_index] == "Yes":
            for uniprot_name in UNIPROT_NAMES:
                line = line.replace(f",{uniprot_name},", ",,")
            kept_lines.append(line)

    for path in glob.glob(f"{SOURCES_DIR}/Toronto.[0-9]*.csv"):
        os.remove(path)
    path = f"{SOURCES_DIR}/Toronto.{version}.csv"
    print(f"Write {path} ...", flush = True)
    with open(path, "w", newline = "") as file:
        file.write("\r\n".join(kept_lines) + "\r\n")

def fetch_text(url):
    response = requests.get(url, timeout = 600)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    main()
