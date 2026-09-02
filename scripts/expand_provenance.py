#!/usr/bin/env python3

import os.path
import provenance
import sys
import yaml

from glob import glob

HEADER = "name\tsource\tensembl_gene\tensembl_source"

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
    with open(f"{sources_dir}/sources.yaml") as file:
        sources_spec = yaml.safe_load(file)

    for source_spec in sources_spec:
        data_file = source_spec["data_file"]
        source_name = data_file[:data_file.rindex(".")]
        source = Source(f"{sources_dir}/{data_file}", source_spec.get("has_header", True))
        assert source_name not in sources, f"ambiguous source: {source_name}"
        sources[source_name] = source
        if list_name is not None:
            sources[f"{list_name}/{source_name}"] = source

def collect_rows(lines):
    rows = []
    for line in lines:
        line = line.rstrip("\n")
        if line != HEADER:
            fields = line.split("\t")
            assert len(fields) == 4, f"not a names file line: {line}"
            rows.append(fields)
    return rows

# The lines we need are scattered all over source data files which are far too large to hold in memory, so we first
# collect the lines all the rows ask for, and only then scan each of the source data files once.
def fetch_cells(sources, rows):
    for name, source_name, ensembl_gene, ensembl_source in rows:
        for provenance_text in (source_name, ensembl_source):
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

def expand_row(sources, row):
    name, source_name, ensembl_gene, ensembl_source = row
    return {
        "name": name,
        "ensembl_gene": ensembl_gene,
        "source": expand_provenance(sources, source_name),
        "ensembl_source": expand_provenance(sources, ensembl_source),
    }

def expand_provenance(sources, provenance_text):
    return [expand_step(sources, text) for text in provenance_text.split(provenance.JOIN)]

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

def named_columns(source, columns):
    """
    Return the name of the source data file CSV column(s), or their index if it has no header line - a single name
    for a single CSV column, and a list of names for a list of alternative CSV columns.
    """
    names = [column if source.header is None else source.header[int(column)]
             for column in columns.split(provenance.ALTERNATIVE)]
    return names[0] if len(names) == 1 else names

def value_of(cells, columns):
    for index in provenance.value_indices(columns):
        if index < len(cells) and cells[index] != "":
            return cells[index]
    return ""

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
