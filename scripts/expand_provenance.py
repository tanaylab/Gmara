#!/usr/bin/env python3

import os.path
import provenance
import source_files
import sys
import yaml

from glob import glob

# The columns of the namespace names files.
NAMESPACE_COLUMNS = ["name", "ensembl_gene", "name_source", "name_mapping"]

# The columns of the list names files.
LIST_COLUMNS = [
    "name", "ensembl_gene", "list_name", "name_source", "name_mapping", "list_source", "list_mapping", "common_mapping"
]

# The columns which do not hold provenance.
VALUE_COLUMNS = ("name", "ensembl_gene", "list_name")

class Source:
    def __init__(self, path, has_header):
        self.path = path
        self.has_header = has_header
        self.separator = "," if path.endswith(".csv") else "\t"
        self.header = None
        self.cells = {}

def collect_sources(species):
    sources = {}
    collect_sources_dir(sources, f"genes/{species}/namespaces/sources", None)
    for sources_dir in sorted(glob(f"genes/{species}/lists/*/sources")):
        collect_sources_dir(sources, sources_dir, os.path.basename(os.path.dirname(sources_dir)))
    return sources

def collect_sources_dir(sources, sources_dir, list_name):
    for source_spec in source_files.load_specs(sources_dir):
        data_file = source_spec["data_file"]
        source_name = data_file[:data_file.rindex(".")]
        if list_name is not None:
            source_name = f"{list_name}/{source_name}"
        source = Source(f"{sources_dir}/{data_file}", source_spec.get("has_header", True))
        assert source_name not in sources, f"ambiguous source: {source_name}"
        sources[source_name] = source

# Return each row (of a namespace or a list names file) as a dictionary by column name.
def collect_rows(lines):
    rows = []
    for line in lines:
        fields = line.rstrip("\n").split("\t")
        if fields not in (NAMESPACE_COLUMNS, LIST_COLUMNS):
            columns = NAMESPACE_COLUMNS if len(fields) == len(NAMESPACE_COLUMNS) else LIST_COLUMNS
            assert len(fields) == len(columns), f"not a names file line: {line}"
            rows.append(dict(zip(columns, fields)))
    return rows

# The lines we need are scattered all over source data files which are far too large to hold in memory, so we first
# collect the lines all the rows ask for, and only then scan each of the source data files once.
def fetch_cells(sources, rows):
    for row in rows:
        for column, provenance_text in row.items():
            if column in VALUE_COLUMNS:
                continue
            for step in provenance_text.split(provenance.JOIN):
                match = provenance.STEP.fullmatch(step)
                if match is not None:
                    source = sources.get(match.group(1))
                    if source is not None:
                        source.cells[int(match.group(2))] = None

    for source in set(sources.values()):
        if len(source.cells) > 0:
            fetch_source_cells(source)

def fetch_source_cells(source):
    with open(source.path) as file:
        for line, text in enumerate(file, start = 1):
            cells = text.rstrip("\n").split(source.separator)
            if line == 1 and source.has_header:
                source.header = cells
            if line in source.cells:
                source.cells[line] = cells

# The name and the EnsemblGene come first, followed by the other columns in the order of the names file.
def expand_row(sources, row):
    expanded = {"name": row["name"], "ensembl_gene": row["ensembl_gene"]}
    for column, text in row.items():
        if column not in expanded:
            expanded[column] = text if column in VALUE_COLUMNS else expand_provenance(sources, text)
    return expanded

# An empty provenance (a lone `JOIN`) has no steps.
def expand_provenance(sources, provenance_text):
    return [expand_step(sources, text) for text in provenance_text.split(provenance.JOIN) if text != ""]

def expand_step(sources, text):
    match = provenance.STEP.fullmatch(text)
    source = None if match is None else sources.get(match.group(1))
    if source is None:
        return {"step": text}

    line, columns = int(match.group(2)), match.group(3)
    step = {"step": text, "file": source.path, "line": line}

    if provenance.LINK in columns:
        from_columns, to_columns = columns.split(provenance.LINK)
        step["from_csv_column"] = named_columns(source, from_columns)
        step["to_csv_column"] = named_columns(source, to_columns)
    else:
        step["csv_column"] = named_columns(source, columns)

    cells = source.cells[line]
    if cells is None:
        step["error"] = "no such line"
    else:
        step["value"] = value_of(cells, columns)

    return step

def named_columns(source, column):
    """
    Return the name of the source data file CSV column, or its index if it has no header line.
    """
    return column if source.header is None else source.header[int(column)]

def value_of(cells, columns):
    index = provenance.value_index(columns)
    return cells[index] if index < len(cells) else ""

def main():
    assert len(sys.argv) >= 2, "Usage: expand_provenance.py species [names_file ...]"
    species = sys.argv[1]

    if len(sys.argv) > 2:
        lines = [line for path in sys.argv[2:] for line in open(path)]
    else:
        lines = sys.stdin.readlines()

    sources = collect_sources(species)
    rows = collect_rows(lines)
    fetch_cells(sources, rows)

    yaml.safe_dump(
        [expand_row(sources, row) for row in rows],
        sys.stdout,
        sort_keys = False,
        default_flow_style = False,
        width = 200,
    )

if __name__ == "__main__":
    main()
