#!/usr/bin/env python3

import json
import os
import pandas as pd
import requests
import sys
import time

def main():
    assert len(sys.argv) == 2, "Usage: complete_namespaces.py species"
    species = sys.argv[1]

    sources_dir = f"genes/{species}/namespaces/sources"
    for name in os.listdir(sources_dir):
        if name.endswith(".Missing.tsv"):
            namespace_name = name[:-12]
            complete_namespace(namespace_name, sources_dir)

def complete_namespace(namespace_name, sources_dir):
    print(f"Complete identifiers for {namespace_name} ...")
    complete_function = globals().get(f"complete_{namespace_name}")

    missing_genes = {}

    missing_path = f"{sources_dir}/{namespace_name}.Missing.tsv"
    if os.path.isfile(missing_path):
        frame = pd.read_csv(missing_path, dtype = str, keep_default_na = False, header = None, sep = "\t")
        for gene_name, source_name in zip(frame.iloc[:, 0], frame.iloc[:, 1]):
            missing_genes[gene_name] = source_name

    ignored_path = f"{sources_dir}/{namespace_name}.Ignored.tsv"
    if os.path.isfile(ignored_path):
        frame = pd.read_csv(ignored_path, dtype = str, keep_default_na = False, header = None, sep = "\t")
        ignored_names = set([normalize_name(namespace_name, gene_name) for gene_name in frame.iloc[:, 0]])
    else:
        ignored_names = set()

    for gene_name, source_name in sorted(missing_genes.items(), key = lambda k: str.casefold(str(k))):
        gene_name = normalize_name(namespace_name, gene_name)
        if gene_name not in ignored_names \
                and (complete_function is None or not complete_function(sources_dir, gene_name, source_name)):
            ignored_names.add(gene_name)
            print(f"The missing gene: {gene_name} from: {source_name} will be ignored from the namespace: {namespace_name}")
            with open(ignored_path, "a") as file:
                print(f"{gene_name}\t{source_name}", file = file)

    if os.path.isfile(missing_path):
        os.remove(missing_path)

def complete_EnsemblGene(sources_dir, ensembl_id, source_name):
    url = f"http://tark.ensembl.org/api/transcript/search/?identifier_field={ensembl_id}&expand=genes"
    time.sleep(0.01)  # Throttle requests to avoid appearing to be a DDOS attack.
    page = requests.get(url)
    data = json.loads(page.content)

    active_ids = set()
    for datum in data:
        stable_id = normalize_name("EnsemblGene", datum.get("stable_id", ensembl_id))
        if stable_id != ensembl_id:
            active_ids.add(stable_id)
        for gene in datum.get("genes", []):
            stable_id = normalize_name("EnsemblGene", gene.get("stable_id", ensembl_id))
            if stable_id != ensembl_id:
                active_ids.add(stable_id)

    if len(active_ids) == 0:
        return False

    for active_id in active_ids:
        active_namespace = ensembl_namespace_of(active_id)
        store_extra(sources_dir, "EnsemblGene.Extra.tsv", ensembl_id, active_namespace, active_id, source_name, url)
    print(f"Found {len(active_ids)} mappings for the missing Ensembl {ensembl_id}")
    return True

def ensembl_namespace_of(ensemnl_id):
    if ensemnl_id.startswith("ENSG") or ensemnl_id.startswith("ENSMUSG"):
        return "EnsemblGene"
    if ensemnl_id.startswith("ENST") or ensemnl_id.startswith("ENSMUST"):
        return "EnsemblTranscript"
    if ensemnl_id.startswith("ENSP") or ensemnl_id.startswith("ENSMUSP"):
        return "EnsemblProtein"
    assert False, f"Don't know the namespace for the Ensembl identifier: {ensemnl_id}"

def normalize_name(namespace_name, name):
    if namespace_name == "UCSC":
        return name
    parts = name.split(".")
    if len(parts) == 2:
        return parts[0]
    else:
        return name

def store_extra(sources_dir, extra_path, gene_name, other_namespace_name, other_gene_name, source_name, link_source_name):
    with open(f"{sources_dir}/{extra_path}", "a+") as file:
        print(f"{gene_name}\t{source_name}\t{other_namespace_name}\t{other_gene_name}\t{link_source_name}", file = file)

if __name__ == "__main__":
    main()
