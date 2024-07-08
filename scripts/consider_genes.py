#!/usr/bin/env python3

import os.path
import pandas as pd
import re
import shutil
import sys
import yaml

from glob import glob

class Namespace:
    def __init__(self, namespaces_dir, name):
        self.name = name
        names_path = f"{namespaces_dir}/names/{name}.tsv"
        print(f"Load {name} names ...", flush = True)
        frame = pd.read_csv(names_path, dtype = str, keep_default_na = False, header = "infer", sep = "\t")
        self.gene_names = set(frame.loc[:, "name"])

class Names:
    def __init__(self, namespaces_dir, namespace_name):
        self.namespaces_dir = namespaces_dir
        self.namespace = Namespace(namespaces_dir, namespace_name)
        self.gene_names = set()

    def collect_list_file(self, namespace_name, list_path):
        print(f"Load {list_path} ...", flush = True)
        with open(list_path) as file:
            for gene_name in file.readlines():
                gene_name = normalize_name(namespace_name, gene_name[:-1])
                self.gene_names.add(gene_name)

    def verify_names(self):
        print(f"Verify names ...", flush = True)

        ignored_path = f"{self.namespaces_dir}/sources/{self.namespace.name}.Ignored.txt"
        if os.path.isfile(ignored_path):
            ignored_names = set([gene_name[:-1] for gene_name in open(ignored_path).readlines()])
        else:
            ignored_names = set()

        missing_path = f"{self.namespaces_dir}/sources/{self.namespace.name}.Missing.txt"
        if os.path.isfile(missing_path):
            missing_names = set([gene_name[:-1] for gene_name in open(missing_path).readlines()])
        else:
            missing_names = set()

        new_missing_names = set()
        for gene_name in sorted(self.gene_names):
            if gene_name not in self.namespace.gene_names:
                if gene_name in ignored_names:
                    print(f"The gene: '{gene_name}' is ignored from the namespace: {self.namespace.name}", flush = True)
                elif gene_name in missing_names:
                    print(f"The gene: '{gene_name}' is already missing from the namespace: {self.namespace.name}", flush = True)
                else:
                    new_missing_names.add(gene_name)

        if len(new_missing_names) > 0:
            with open(missing_path, "a") as file:
                for gene_name in sorted(new_missing_names):
                    print(f"The gene: '{gene_name}' is added to missing from the namespace: {self.namespace.name}", flush = True)
                    print(f"{gene_name}", file = file)

def normalize_name(namespace_name, name):
    if namespace_name == "UCSC":
        return name.lower()
    parts = name.split(".")
    if len(parts) == 2:
        name = parts[0]
    return name.upper()

def main():
    assert len(sys.argv) >= 3, "Usage: consider_genes.py species namespace list_file..."
    species = sys.argv[1]
    namespace_name = sys.argv[2]

    namespaces_dir = f"genes/{species}/namespaces"
    names = Names(namespaces_dir, namespace_name)

    for list_path in sys.argv[3:]:
        names.collect_list_file(namespace_name, list_path)

    names.verify_names()

if __name__ == "__main__":
    main()
