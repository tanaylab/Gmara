#!/usr/bin/env python3

import os.path
import pandas as pd
import re
import shutil
import sys
import warnings
import yaml

TRACK_GENES = []

def warn(message):
    warnings.warn(message)

class Gene:
    def __init__(self, source_name, gene_name):
        self.source_name = source_name
        self.gene_name = gene_name
        self.links = {}
        self.ensembl_genes = {}

class Namespace:
    def __init__(self, namespace_name):
        self.namespace_name = namespace_name
        self.links = set()
        self.genes = {}

class Namespaces:
    def __init__(self, sources_dir):
        self.sources_dir = sources_dir
        self.namespaces = {}
        self.next_index = 1

    def collect_source(self, source_spec):
        data_file = source_spec["data_file"]
        source_name = data_file[:-4]
        data_path = f"{self.sources_dir}/{data_file}"
        has_header = source_spec.get("has_header", True)
        assert os.path.isfile(data_path), f"not a file: {data_path}"
        print(f"Load {data_file} ...", flush = True)
        frame = pd.read_csv(
            data_path,
            dtype = str,
            keep_default_na = False,
            header="infer" if has_header else None,
            sep = "," if data_path.endswith(".csv") else "\t",
            comment = "#",
        )

        for link in source_spec["links"]:
            from_namespace_name, from_column, from_separator, from_data = get_link_column(frame, link["from"])
            to_namespace_name, to_column, to_separator, to_data = get_link_column(frame, link["to"])

            print(f"- Collect {source_name}[{from_column} -> {to_column}] ...", flush = True)

            for row in range(len(from_data)):
                from_names = split_names(from_namespace_name, from_separator, from_data[row])
                to_names = split_names(to_namespace_name, to_separator, to_data[row])
                from_source_name = f"{source_name}#{row + 2}[{from_column}]"
                to_source_name = f"{source_name}#{row + 2}[{to_column}]"
                link_source_name = f"{source_name}#{row + 2}[{from_column} -> {to_column}]"
                self.add_names(from_source_name, from_namespace_name, from_names)
                self.add_names(to_source_name, to_namespace_name, to_names)
                self.link_names(link_source_name, from_namespace_name, from_names, to_namespace_name, to_names)

    def collect_extra(self):
        for namespace_name in self.namespaces:
            self.collect_extra_namespace(namespace_name)

    def collect_extra_namespace(self, from_namespace_name):
        from_namespace = self.namespaces[from_namespace_name]
        extra_path = f"{self.sources_dir}/{from_namespace_name}.Extra.tsv"
        if os.path.isfile(extra_path):
            print(f"Load {from_namespace_name}.Extra.tsv ...", flush = True)
            frame = pd.read_csv(
                extra_path,
                dtype = str,
                keep_default_na = False,
                header=None,
                sep = "\t",
            )
            print(f"- Collect extra {from_namespace_name} ...", flush = True)

            from_gene_names = frame.iloc[:, 0].values
            from_source_names = frame.iloc[:, 1].values
            to_namespace_names = frame.iloc[:, 2].values
            to_gene_names = frame.iloc[:, 3].values
            link_source_names = frame.iloc[:, 4].values

            for row in range(len(from_source_names)):
                from_names = split_names(from_namespace_name, None, from_gene_names[row])
                to_names = split_names(to_namespace_names[row], None, to_gene_names[row])
                self.add_names(from_source_names[row], from_namespace_name, from_names)
                self.add_names(link_source_names[row], from_namespace_name, to_names)
                self.link_names(link_source_names[row], from_namespace_name, from_names, to_namespace_names[row], to_names)

    def add_names(self, source_name, namespace_name, gene_names):
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = Namespace(namespace_name)
        namespace = self.namespaces[namespace_name]
        for gene_name in gene_names:
            if gene_name != "":
                if gene_name not in namespace.genes:
                    if gene_name in TRACK_GENES:
                        print(f"TRACK: add_names source_name: {source_name} namespace_name: {namespace_name} gene_name: {gene_name}")
                    namespace.genes[gene_name] = Gene(f"{source_name} : {gene_name}", gene_name)

    def link_names(self, link_source_name, from_namespace_name, from_gene_names, to_namespace_name, to_gene_names):
        from_namespace = self.namespaces[from_namespace_name]
        to_namespace = self.namespaces[to_namespace_name]
        for from_gene_name in from_gene_names:
            if from_gene_name != "":
                for to_gene_name in to_gene_names:
                    if to_gene_name != "":
                        if to_namespace_name not in from_namespace.genes[from_gene_name].links:
                            from_namespace.genes[from_gene_name].links[to_namespace_name] = {}
                        if to_gene_name not in from_namespace.genes[from_gene_name].links[to_namespace_name]:
                            from_namespace.genes[from_gene_name].links[to_namespace_name][to_gene_name] = f"{link_source_name} : {to_gene_name}"
                        from_namespace.links.add(to_namespace_name)
                        if from_gene_name in TRACK_GENES or to_gene_name in TRACK_GENES:
                            print(f"TRACK: link_names source_name: {link_source_name} from_namespace_name: {from_namespace_name} from_gene_name: {from_gene_name} to_namespace_name: {to_namespace_name} to_gene_name: {to_gene_name}")
                            if to_namespace_name == from_namespace_name:
                                print(f"TODOX: {from_namespace.genes[from_gene_name].links[to_namespace_name]}")

    def compute_different_ensembl_genes(self):
        print("Compute different EnsemblGene ...", flush = True)
        for gene_name in self.namespaces["EnsemblGene"].genes:
            self.combine_gene_to_ensembl_genes("EnsemblGene", gene_name, None, gene_name, [])
        for gene_name, gene in self.namespaces["EnsemblGene"].genes.items():
            if len(gene.ensembl_genes) == 0:
                gene.ensembl_genes[gene_name] = gene.source_name
            if gene_name in TRACK_GENES:
                print(f"TRACK: EnsemblGene {gene_name} => {gene.ensembl_genes}")

    def connect_to_ensembl_genes(self):
        unconnected_namespaces_names = set([namespace_name for namespace_name in self.namespaces if namespace_name != "EnsemblGene"])
        connected_namespaces_names = set(["EnsemblGene"])

        while len(unconnected_namespaces_names) > 0:
            for from_namespace_name in unconnected_namespaces_names:
                if self.connect_namespace_to_ensembl_genes(from_namespace_name, connected_namespaces_names):
                    unconnected_namespaces_names.remove(from_namespace_name)
                    connected_namespaces_names.add(from_namespace_name)
                    break

    def connect_namespace_to_ensembl_genes(self, from_namespace_name, connected_namespaces_names):
        from_namespace = self.namespaces[from_namespace_name]
        for to_namespace_name in connected_namespaces_names:
            if to_namespace_name in connected_namespaces_names and to_namespace_name in from_namespace.links:
                self.connect_namespaces_to_ensembl_genes(from_namespace_name, to_namespace_name)
                return True

    def connect_namespaces_to_ensembl_genes(self, from_namespace_name, to_namespace_name):
        print(f"- Connect {from_namespace_name} -> {to_namespace_name} ...", flush = True)
        for from_gene_name, from_gene in self.namespaces[from_namespace_name].genes.items():
            self.connect_gene_to_ensembl_genes(from_gene_name, from_gene, to_namespace_name)
        for from_gene_name in self.namespaces[from_namespace_name].genes:
            self.combine_gene_to_ensembl_genes(from_namespace_name, from_gene_name, None, from_gene_name, [])
        for from_gene_name, from_gene in self.namespaces[from_namespace_name].genes.items():
            if len(from_gene.ensembl_genes) == 0:
                from_gene.ensembl_genes[f"ENS!{self.next_index:09}"] = "Unrecognized"
                self.next_index += 1
            if from_gene_name in TRACK_GENES:
                print(f"TRACK: {from_namespace_name} {from_gene_name} => {from_gene.ensembl_genes}")

    def connect_gene_to_ensembl_genes(self, from_gene_name, from_gene, to_namespace_name):
        if to_namespace_name not in from_gene.links:
            return
        to_namespace = self.namespaces[to_namespace_name]
        for to_gene_name, link_source_name in from_gene.links[to_namespace_name].items():
            to_gene = to_namespace.genes[to_gene_name]
            for ensembl_gene_name, ensembl_source_name in to_gene.ensembl_genes.items():
                if ensembl_source_name == to_gene.source_name:
                    source_name = link_source_name
                else:
                    source_name = f"{link_source_name} => {ensembl_source_name}"
                if (ensembl_gene_name not in from_gene.ensembl_genes or len(source_name) < len(from_gene.ensembl_genes[ensembl_gene_name])):
                    from_gene.ensembl_genes[ensembl_gene_name] = source_name

    def combine_gene_to_ensembl_genes(self, namespace_name, into_gene_name, link_source_name, from_gene_name, path):
        into_gene = self.namespaces[namespace_name].genes[into_gene_name]
        from_gene = self.namespaces[namespace_name].genes[from_gene_name]

        if from_gene_name != into_gene_name:
            items = from_gene.ensembl_genes.items()
            if namespace_name == "EnsemblGene":
                items = list(items)
                items.append((from_gene_name, from_gene.source_name))
            for ensembl_gene_name, ensembl_source_name in items:
                if ensembl_source_name == from_gene.source_name:
                    source_name = from_gene.source_name
                else:
                    source_name = f"{from_gene.source_name} => {ensembl_source_name}"
                if link_source_name is not None:
                    source_name = f"{link_source_name} => {source_name}"
                if ensembl_gene_name not in into_gene.ensembl_genes or len(source_name) < len(into_gene.ensembl_genes[ensembl_gene_name]):
                    into_gene.ensembl_genes[ensembl_gene_name] = source_name
                    if into_gene_name in TRACK_GENES or from_gene_name in TRACK_GENES or ensembl_gene_name in TRACK_GENES:
                        print("TRACK {into_gene_name} => {ensembl_gene_name} via {from_gene_name} by: {source_name}")

        if from_gene_name in path or namespace_name not in from_gene.links:
            return

        path.append(from_gene_name)
        for link_gene_name, link_source_name in from_gene.links[namespace_name].items():
            self.combine_gene_to_ensembl_genes(namespace_name, into_gene_name, link_source_name, link_gene_name, path)
        path.pop()

        return from_gene

    def write(self, names_dir):
        if os.path.exists(names_dir):
            shutil.rmtree(names_dir)
        os.mkdir(names_dir)

        for namespace_name in self.namespaces:
            self.write_namespace(namespace_name, names_dir)

    def write_namespace(self, namespace_name, names_dir):
        print(f"Write names/{namespace_name}.tsv ...", flush = True)
        with open(f"{names_dir}/{namespace_name}.tsv", "w") as file:
            print("name\tsource\tensembl_gene\tensembl_source", file = file)
            genes = self.namespaces[namespace_name].genes
            for gene_name, gene in sorted(genes.items(), key = lambda k: str.casefold(str(k))):
                assert len(gene.ensembl_genes) > 0
                for ensembl_gene, ensembl_source_name in gene.ensembl_genes.items():
                    print(f"{gene_name}\t{gene.source_name}\t{ensembl_gene}\t{ensembl_source_name}", file = file)

def split_names(namespace_name, separator, names):
    if separator is not None:
        names = names.split(separator)
    else:
        names = [names]
    return [normalize_name(namespace_name, name) for name in names]

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

def get_link_column(frame, link):
    namespace_name = link["namespace"]
    column = link["column"]
    separator = link.get("separator")

    if isinstance(column, str):
        data = frame.loc[:, column].values
    else:
        data = None
        columns = column
        for column in columns:
            data = frame.loc[:, column].values
            if data is None:
                data = data
            else:
                mask = data == ""
                data[mask] = data[mask]
        column = ";".join(columns)

    return namespace_name, column, separator, data

def main():
    assert len(sys.argv) == 2, "Usage: compute_namespaces.py species"
    species = sys.argv[1]

    sources_dir = f"genes/{species}/namespaces/sources"
    sources_yaml = f"genes/{species}/namespaces/sources/sources.yaml"
    with open(sources_yaml) as file:
        sources_spec = yaml.safe_load(file)

    namespaces = Namespaces(sources_dir)
    for source_spec in sources_spec:
        namespaces.collect_source(source_spec)
    namespaces.collect_extra()

    namespaces.compute_different_ensembl_genes()
    namespaces.connect_to_ensembl_genes()

    names_dir = f"genes/{species}/namespaces/names"
    namespaces.write(names_dir)

if __name__ == "__main__":
    main()
