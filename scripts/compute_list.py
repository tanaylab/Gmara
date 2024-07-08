#!/usr/bin/env python3

import os.path
import pandas as pd
import re
import shutil
import sys
import yaml

from glob import glob

TRACK_GENES = []

class Gene:
    def __init__(self, gene_name, source_name):
        self.gene_name = gene_name
        self.source_name = source_name
        self.ensembl_genes = {}

class Namespace:
    def __init__(self, namespaces_dir, namespace_name):
        self.namespace_name = namespace_name
        self.genes = {}

        print(f"Load {namespace_name} namespace ...", flush = True)

        names_path = f"{namespaces_dir}/names/{namespace_name}.tsv"
        frame = pd.read_csv(names_path, dtype = str, keep_default_na = False, header = "infer", sep = "\t")
        for gene_name, source_name, ensembl_gene, ensembl_source \
        in zip(frame.loc[:, "name"], frame.loc[:, "source"], frame.loc[:, "ensembl_gene"], frame.loc[:, "ensembl_source"]):
            if gene_name not in self.genes:
                self.genes[gene_name] = Gene(gene_name, source_name)
            self.genes[gene_name].ensembl_genes[ensembl_gene] = ensembl_source

        ignored_path = f"{namespaces_dir}/sources/{namespace_name}.Ignored.tsv"
        if os.path.isfile(ignored_path):
            frame = pd.read_csv(ignored_path, dtype = str, keep_default_na = False, header = None, sep = "\t")
            self.ignored_genes = set([normalize_name(namespace_name, gene_name) for gene_name in frame.iloc[:, 0]])
        else:
            self.ignored_genes = set()
        self.ignored_genes.add("")

class Names:
    def __init__(self, sources_dir, namespaces_dir):
        self.namespaces_dir = namespaces_dir
        self.sources_dir = sources_dir
        self.namespaces = {}
        self.ensembl_genes = {}

        for namespace_path in os.listdir(f"{namespaces_dir}/names"):
            base_path = os.path.basename(namespace_path)
            namespace_name = base_path.split(".")[0]
            self.namespaces[namespace_name] = Namespace(namespaces_dir, namespace_name)

    def collect_source(self, list_name, sources_spec):
        data_file = sources_spec["data_file"]
        source_name = ".".join(data_file.split(".")[:-1])
        data_path = f"{self.sources_dir}/{data_file}"
        has_header = sources_spec.get("has_header", True)
        print(f"Load {data_file} ...", flush = True)
        frame = pd.read_csv(
            data_path,
            dtype = str,
            keep_default_na = False,
            header="infer" if has_header else None,
            sep = "," if data_path.endswith(".csv") else "\t",
            comment = "#",
        )

        if has_header:
            row_offset = 2
        else:
            row_offset = 1

        n_rows = None
        columns = []
        for column_name, namespace_name in sources_spec["columns"].items():
            if isinstance(column_name, int):
                gene_names = frame.iloc[:, column_name].values
            else:
                gene_names = frame.loc[:, column_name].values
            n_rows = len(gene_names)
            columns.append((column_name, namespace_name, gene_names))

        for row in range(n_rows):
            ensembl_genes = None
            for (column_name, namespace_name, gene_names) in columns:
                ensembl_genes = self.compute_column_ensembl_genes(
                    list_name, source_name, row + row_offset, column_name, namespace_name, gene_names[row], ensembl_genes
                )
            if ensembl_genes is not None:
                if len(ensembl_genes) == 0:
                    print(f"No EnsemblGene matches all of the columns of {source_name}#{row}:")
                    for (column_name, namespace_name, gene_names) in columns:
                        print(f"- {column_name} ({namespace_name}): {split_names(namespace_name, gene_names[row])}")
                else:
                    if len(ensembl_genes) > 1:
                        print(f"The columns of {source_name}#{row} match multiple EnsemblGenes:")
                        for ensembl_gene_name, ensembl_source_name in ensembl_genes.items():
                            print(f"  {ensembl_gene_name} via: {ensembl_source_name}")
                    for ensembl_gene_name, ensembl_source_name in ensembl_genes.items():
                        if ensembl_gene_name not in self.ensembl_genes:
                            self.ensembl_genes[ensembl_gene_name] = ensembl_source_name

    def compute_column_ensembl_genes(self, list_name, source_name, row, column_name, namespace_name, gene_names, ensembl_genes):
        namespace = self.namespaces[namespace_name]

        all_gene_names = split_names(namespace_name, gene_names)
        gene_names = []
        for gene_name in all_gene_names:
            if gene_name in namespace.genes:
                gene_names.append(gene_name)
            elif gene_name not in namespace.ignored_genes:
                namespace.ignored_genes.add(gene_name)
                with open(f"{self.namespaces_dir}/sources/{namespace_name}.Missing.tsv", "a") as file:
                    print(f"Missing: {source_name}#{row}[{column_name}] gene: {gene_name} from namespace: {namespace_name}", flush = True)
                    print(f"{gene_name}\t{list_name}/{source_name}#{row}[{column_name}] : {gene_name}", file = file)

        if len(gene_names) == 0:
            return ensembl_genes

        column_ensembl_genes = {}
        for gene_name in gene_names:
            gene = namespace.genes[gene_name]
            for ensembl_gene_name, ensembl_source_name in gene.ensembl_genes.items():
                if gene.source_name == ensembl_source_name:
                    gene_source_name = ensembl_source_name
                else:
                    gene_source_name = f"{gene.source_name} => {ensembl_source_name}"
                ensembl_gene_source_name = f"{source_name}#{row}[{column_name}] : {gene_name} => {gene_source_name}"
                if ensembl_gene_name not in column_ensembl_genes or len(ensembl_gene_source_name) < len(column_ensembl_genes[ensembl_gene_name]):
                    column_ensembl_genes[ensembl_gene_name] = ensembl_gene_source_name
                    if gene_name in TRACK_GENES:
                        print(f"TRACK {gene_name} maps to: {ensembl_gene_name} via: {ensembl_gene_source_name}")

        if ensembl_genes is None:
            return column_ensembl_genes

        return {
            ensembl_gene_name: ensembl_source_name
            for ensembl_gene_name, ensembl_source_name
            in ensembl_genes.items()
            if ensembl_gene_name in column_ensembl_genes
        }

    def write(self, names_dir):
        if os.path.exists(names_dir):
            shutil.rmtree(names_dir)
        os.mkdir(names_dir)

        for namespace_name, namespace in self.namespaces.items():
            print(f"Write names/{namespace_name}.tsv ...", flush = True)
            with open(f"{names_dir}/{namespace_name}.tsv", "w") as file:
                print("name\tsource\tensembl_gene\tensembl_source", file = file)
                namespace = self.namespaces[namespace_name]
                for gene_name, gene in sorted(namespace.genes.items(), key = lambda k: str.casefold(str(k))):
                    for ensembl_gene_name, ensembl_source_name in sorted(gene.ensembl_genes.items(), key = lambda k: str.casefold(str(k))):
                        if ensembl_source_name != gene.source_name:
                            ensembl_source_name = f"{gene.source_name} => {ensembl_source_name}"
                        if ensembl_gene_name in self.ensembl_genes:
                            print(f"{gene_name}\t{ensembl_source_name}\t{ensembl_gene_name}\t{self.ensembl_genes[ensembl_gene_name]}", file = file)

def split_names(namespace_name, names):
    return [normalize_name(namespace_name, name) for name in re.split(r"[| ,;\t]", names)]

def normalize_name(namespace_name, name):
    name = name.strip()
    if name.upper() == "NULL":
        return ""
    if namespace_name == "UCSC":
        return name
    parts = name.split(".")
    if len(parts) == 2:
        name = parts[0]
    return name

def main():
    assert len(sys.argv) == 3, "Usage: compute_list.py species list"
    species = sys.argv[1]
    list_name = sys.argv[2]

    sources_dir = f"genes/{species}/lists/{list_name}/sources"
    with open(f"{sources_dir}/sources.yaml") as file:
        sources_spec = yaml.safe_load(file)

    namespaces_dir = f"genes/{species}/namespaces"
    names = Names(sources_dir, namespaces_dir)
    for source_spec in sources_spec:
        names.collect_source(list_name, source_spec)

    names_dir = f"genes/{species}/lists/{list_name}/names"
    names.write(names_dir)

if __name__ == "__main__":
    main()
