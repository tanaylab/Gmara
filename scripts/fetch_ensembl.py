#!/usr/bin/env python3

import bz2
import gzip
import os
import re
import requests
import shutil
import sys
import tempfile

from collections import defaultdict

FTP_URL = "https://ftp.ensembl.org/pub"

ORGANISMS = {"human": "homo_sapiens", "mouse": "mus_musculus"}

STABLE_ID_PREFIXES = {"human": "ENS", "mouse": "ENSMUS"}

# The `stable_id_event` types, the suffix of the file holding them, and the letter of their stable identifiers.
STABLE_ID_EVENT_TYPES = {"gene": ("Genes", "G"), "transcript": ("Transcripts", "T"), "translation": ("Proteins", "P")}

def main():
    assert len(sys.argv) == 4, "Usage: fetch_ensembl.py species first_release last_release"
    species = sys.argv[1]
    first_release = int(sys.argv[2])
    last_release = int(sys.argv[3])

    sources_dir = f"genes/{species}/namespaces/sources"
    for release in range(first_release, last_release + 1):
        with tempfile.TemporaryDirectory() as download_dir:
            dump = Dump(species, release, download_dir)
            write_gene_names(dump, sources_dir)
            if release == last_release:
                write_identifiers(dump, sources_dir)
                write_stable_id_events(dump, sources_dir)
    remove_older_releases(sources_dir, last_release)
    remove_covered_gene_names(sources_dir)

# Each gene name is taken only from the newest release which has it. A release whose gene names all appear in newer
# releases contributes nothing, so we remove it.
def remove_covered_gene_names(sources_dir):
    releases = []
    for data_file in os.listdir(sources_dir):
        match = re.fullmatch(r"Ensembl\.GeneName\.([0-9]+)\.tsv", data_file)
        if match:
            releases.append(int(match.group(1)))

    newer_names = set()
    for release in sorted(releases, reverse = True):
        path = f"{sources_dir}/Ensembl.GeneName.{release}.tsv"
        with open(path) as file:
            next(file)
            names = {line.rstrip("\n").split("\t")[1] for line in file}
        if names <= newer_names:
            print(f"Remove {path} ...", flush = True)
            os.remove(path)
        newer_names |= names

# The gene names have multiple versions, since Ensembl does not keep their history. All the other data files only hold
# the latest release.
def remove_older_releases(sources_dir, release):
    for data_file in sorted(os.listdir(sources_dir)):
        match = re.fullmatch(r"Ensembl(\.\w+)?\.([0-9]+)\.tsv", data_file)
        if match and match.group(1) != ".GeneName" and int(match.group(2)) != release:
            print(f"Remove {sources_dir}/{data_file} ...", flush = True)
            os.remove(f"{sources_dir}/{data_file}")

# The tables of the Ensembl core MySQL database dump of some release of some species.
class Dump:
    def __init__(self, species, release, download_dir):
        self.species = species
        self.release = release
        self.download_dir = download_dir
        mysql_url = f"{FTP_URL}/release-{release}/mysql"
        # Some releases also have a core database for an older assembly (e.g., GRCh37); we use the newest one.
        assemblies = re.findall(rf'href="{ORGANISMS[species]}_core_{release}_([0-9]+)/"', fetch_text(mysql_url))
        assert len(assemblies) > 0, f"No core database in: {mysql_url}"
        database_name = f"{ORGANISMS[species]}_core_{release}_{max(assemblies, key = int)}"
        self.database_url = f"{mysql_url}/{database_name}"
        self.columns = self.load_columns(database_name)

    def load_columns(self, database_name):
        columns = {}
        table_name = None
        for line in self.read_lines(f"{database_name}.sql.gz"):
            match = re.match(r"CREATE TABLE `(\w+)`", line)
            if match:
                table_name = match.group(1)
                columns[table_name] = []
            elif table_name is not None and re.match(r"\s+`(\w+)`", line):
                columns[table_name].append(re.match(r"\s+`(\w+)`", line).group(1))
            elif line.startswith(")"):
                table_name = None
        return columns

    def read_lines(self, file_name):
        path = f"{self.download_dir}/{file_name}"
        if not download(f"{self.database_url}/{file_name}", path):
            # Release 89 has the (gzipped) files compressed again with bzip2.
            assert download(f"{self.database_url}/{file_name}.bz2", f"{path}.bz2"), \
                f"Missing: {self.database_url}/{file_name}"
            with bz2.open(f"{path}.bz2", "rb") as compressed_file, open(path, "wb") as file:
                shutil.copyfileobj(compressed_file, file)
        # Some old releases have a few bytes which are not valid UTF-8 in free text (e.g. descriptions).
        with gzip.open(path, "rt", errors = "replace") as file:
            for line in file:
                yield line.rstrip("\n")

    # Yield the values of the named columns of each row of a table, with `None` for MySQL's `NULL`. MySQL writes a
    # newline inside a value as a backslash at the end of the line, so such a row continues in the next line.
    def rows(self, table_name, column_names):
        indices = [self.columns[table_name].index(column_name) for column_name in column_names]
        row = ""
        for line in self.read_lines(f"{table_name}.txt.gz"):
            row += line
            if (len(row) - len(row.rstrip("\\"))) % 2 == 1:
                row = row[:-1] + "\n"
                continue
            values = row.split("\t")
            assert len(values) == len(self.columns[table_name]), f"Unexpected {table_name} row: {row}"
            row = ""
            yield [None if values[index] == "\\N" else values[index] for index in indices]

    # Return the stable identifier of each current gene, by its database identifier. This skips the LRG (Locus
    # Reference Genomic) genes, which BioMart does not list either.
    def gene_stable_ids(self):
        if not hasattr(self, "cached_gene_stable_ids"):
            self.cached_gene_stable_ids = {}
            self.gene_display_xref_ids = {}
            for gene_id, stable_id, is_current, display_xref_id \
            in self.rows("gene", ["gene_id", "stable_id", "is_current", "display_xref_id"]):
                if is_current == "1" and not stable_id.startswith("LRG_"):
                    self.cached_gene_stable_ids[gene_id] = stable_id
                    if display_xref_id is not None:
                        self.gene_display_xref_ids[gene_id] = display_xref_id
        return self.cached_gene_stable_ids

    # Return the database identifiers of the current genes on regions which are not part of the reference (primary)
    # assembly, such as alternate haplotypes. Ensembl marks such regions with the `non_ref` attribute.
    def non_reference_gene_ids(self):
        non_reference_attrib_type_ids = {attrib_type_id for attrib_type_id, code
                                         in self.rows("attrib_type", ["attrib_type_id", "code"]) if code == "non_ref"}
        non_reference_seq_region_ids = {seq_region_id for seq_region_id, attrib_type_id
                                        in self.rows("seq_region_attrib", ["seq_region_id", "attrib_type_id"])
                                        if attrib_type_id in non_reference_attrib_type_ids}
        gene_stable_ids = self.gene_stable_ids()
        return {gene_id for gene_id, seq_region_id in self.rows("gene", ["gene_id", "seq_region_id"])
                if gene_id in gene_stable_ids and seq_region_id in non_reference_seq_region_ids}

def fetch_text(url):
    response = requests.get(url, timeout = 600)
    response.raise_for_status()
    return response.text

# Download a URL into a file. Return whether it exists.
def download(url, path):
    print(f"Download {url} ...", flush = True)
    with requests.get(url, stream = True, timeout = 600) as response:
        if response.status_code == 404:
            return False
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size = 1 << 20):
                file.write(chunk)
    return True

def write_gene_names(dump, sources_dir):
    gene_stable_ids = dump.gene_stable_ids()
    display_xref_ids = set(dump.gene_display_xref_ids.values())
    labels = {xref_id: label for xref_id, label in dump.rows("xref", ["xref_id", "display_label"])
              if xref_id in display_xref_ids}
    rows = {(gene_stable_ids[gene_id], labels[xref_id]) for gene_id, xref_id in dump.gene_display_xref_ids.items()}
    write_table(f"{sources_dir}/Ensembl.GeneName.{dump.release}.tsv", ["Gene stable ID", "Gene name"], rows)

# Write the tables we used to download from BioMart, in the same layouts. The table of the transcripts and proteins of
# each gene is split by whether the gene is on the reference assembly.
def write_identifiers(dump, sources_dir):
    gene_stable_ids = dump.gene_stable_ids()

    transcript_gene_ids = {}
    transcript_stable_ids = {}
    for transcript_id, gene_id, stable_id, is_current \
    in dump.rows("transcript", ["transcript_id", "gene_id", "stable_id", "is_current"]):
        if is_current == "1" and gene_id in gene_stable_ids:
            transcript_gene_ids[transcript_id] = gene_id
            transcript_stable_ids[transcript_id] = stable_id

    translation_transcript_ids = {}
    translation_stable_ids = {}
    for translation_id, transcript_id, stable_id \
    in dump.rows("translation", ["translation_id", "transcript_id", "stable_id"]):
        if transcript_id in transcript_stable_ids:
            translation_transcript_ids[translation_id] = transcript_id
            translation_stable_ids[translation_id] = stable_id

    database_names = ["UCSC", "RefSeq_mRNA", "RefSeq_ncRNA", "RefSeq_peptide"]
    database_names.append("HGNC" if dump.species == "human" else "MGI")
    database_ids = {external_db_id: db_name
                    for external_db_id, db_name in dump.rows("external_db", ["external_db_id", "db_name"])
                    if db_name in database_names}
    xrefs = {}
    for xref_id, external_db_id, accession, label \
    in dump.rows("xref", ["xref_id", "external_db_id", "dbprimary_acc", "display_label"]):
        if external_db_id in database_ids:
            xrefs[xref_id] = (database_ids[external_db_id], accession, label)

    # The `(accession, label)` of the xrefs of each object, by database name and object type.
    object_xrefs = defaultdict(lambda: defaultdict(set))
    for ensembl_id, object_type, xref_id in dump.rows("object_xref", ["ensembl_id", "ensembl_object_type", "xref_id"]):
        if xref_id in xrefs:
            database_name, accession, label = xrefs[xref_id]
            object_xrefs[(database_name, object_type)][ensembl_id].add((accession, label))

    def gene_of_transcript(transcript_id):
        return gene_stable_ids[transcript_gene_ids[transcript_id]]

    def xrefs_of(database_name, object_type, ensembl_id):
        return object_xrefs[(database_name, object_type)].get(ensembl_id) or [("", "")]

    protein_stable_ids = defaultdict(list)
    for translation_id, transcript_id in translation_transcript_ids.items():
        protein_stable_ids[transcript_id].append(translation_stable_ids[translation_id])
    transcript_rows = [(transcript_id, gene_of_transcript(transcript_id), transcript_stable_ids[transcript_id], protein)
                       for transcript_id in transcript_gene_ids
                       for protein in protein_stable_ids.get(transcript_id) or [""]]

    identifiers = ["Gene stable ID", "Transcript stable ID", "Protein stable ID"]
    identifier_rows = {(gene, transcript, protein) for _, gene, transcript, protein in transcript_rows}
    non_reference_genes = {gene_stable_ids[gene_id] for gene_id in dump.non_reference_gene_ids()}
    write_table(f"{sources_dir}/Ensembl.Reference.{dump.release}.tsv", identifiers,
                {row for row in identifier_rows if row[0] not in non_reference_genes})
    write_table(f"{sources_dir}/Ensembl.NonReference.{dump.release}.tsv", identifiers,
                {row for row in identifier_rows if row[0] in non_reference_genes})

    if dump.species == "human":
        write_table(f"{sources_dir}/Ensembl.HGNC.{dump.release}.tsv", identifiers + ["HGNC ID", "HGNC symbol"],
                    {(gene, transcript, protein, accession, label)
                     for transcript_id, gene, transcript, protein in transcript_rows
                     for accession, label in xrefs_of("HGNC", "Gene", transcript_gene_ids[transcript_id])})
        write_table(f"{sources_dir}/Ensembl.UCSC.{dump.release}.tsv", identifiers + ["UCSC Stable ID"],
                    {(gene, transcript, protein, accession)
                     for transcript_id, gene, transcript, protein in transcript_rows
                     for accession, _ in xrefs_of("UCSC", "Transcript", transcript_id)})
    else:
        write_table(f"{sources_dir}/Ensembl.MGI.{dump.release}.tsv", ["Gene stable ID", "MGI ID"],
                    {(gene, accession)
                     for gene_id, gene in gene_stable_ids.items()
                     for accession, _ in xrefs_of("MGI", "Gene", gene_id)})
        write_table(f"{sources_dir}/Ensembl.UCSC.{dump.release}.tsv", ["Gene stable ID", "UCSC Stable ID"],
                    {(gene_of_transcript(transcript_id), accession)
                     for transcript_id in transcript_gene_ids
                     for accession, _ in xrefs_of("UCSC", "Transcript", transcript_id)})

    for kind in ("mRNA", "ncRNA"):
        write_table(f"{sources_dir}/Ensembl.RefSeq_{kind}.{dump.release}.tsv", ["Gene stable ID", f"RefSeq {kind} ID"],
                    {(gene_of_transcript(transcript_id), accession)
                     for transcript_id in transcript_gene_ids
                     for accession, _ in xrefs_of(f"RefSeq_{kind}", "Transcript", transcript_id)})
    write_table(f"{sources_dir}/Ensembl.RefSeq_peptide.{dump.release}.tsv", ["Gene stable ID", "RefSeq peptide ID"],
                {(gene_of_transcript(transcript_id), accession)
                 for translation_id, transcript_id in translation_transcript_ids.items()
                 for accession, _ in xrefs_of("RefSeq_peptide", "Translation", translation_id)})

# Split the `stable_id_event` table by type, keeping only the unique pairs of old and new stable identifiers. The table
# repeats most pairs in each mapping session, so keeping all its lines makes the files too big. We skip the lines
# which do not mention any identifier of their type, which are errors in the Ensembl data.
def write_stable_id_events(dump, sources_dir):
    prefix = STABLE_ID_PREFIXES[dump.species]
    pairs = defaultdict(set)
    for line in dump.read_lines("stable_id_event.txt.gz"):
        values = line.split("\t")
        suffix, letter = STABLE_ID_EVENT_TYPES[values[5]]
        if f"{prefix}{letter}" in line:
            pairs[suffix].add((values[0], values[2]))
        else:
            print(f"Skip stable_id_event line: {line}", flush = True)
    for suffix, _ in STABLE_ID_EVENT_TYPES.values():
        write_table(f"{sources_dir}/Ensembl.{suffix}.{dump.release}.tsv", ["Old stable ID", "New stable ID"],
                    pairs[suffix])

def write_table(path, header, rows):
    print(f"Write {path} ...", flush = True)
    with open(path, "w") as file:
        print("\t".join(header), file = file)
        for row in sorted(rows):
            print("\t".join(row), file = file)

if __name__ == "__main__":
    main()
