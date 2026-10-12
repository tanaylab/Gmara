#!/usr/bin/env python3

import gene_names
import os.path
import pandas as pd
import provenance
import re
import shutil
import source_files
import sys
import warnings

TRACK_GENES = []

# The priority of a link which does not specify one. A larger number is a stronger priority.
DEFAULT_PRIORITY = 1

def warn(message):
    warnings.warn(message)

class Gene:
    def __init__(self, source_name, gene_name, is_clean):
        self.source_name = source_name
        self.gene_name = gene_name
        # Whether the name appears in a clean column of some source (that is, not only in a column of aliases).
        self.is_clean = is_clean
        # The (priority, source name) of each link, by the namespace and the name it links to.
        self.links = {}
        self.ensembl_genes = {}
        self.is_connected = False

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
        # The names collected from the newer versions of each source which has multiple versions.
        self.newer_names = {}
        # The EnsemblGenes of sources which are `is_reference` (that is, current genes on the reference assembly).
        self.reference_ensembl_genes = set()

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

        if has_header:
            row_offset = 2
        else:
            row_offset = 1

        if source_spec.get("has_multiple_versions", False):
            newer_names = self.newer_names.setdefault(source_spec["versions_data_file"], set())
        else:
            newer_names = set()
        collected_names = set()

        for link in source_spec["links"]:
            from_namespace_name, from_column, from_separator, from_data, from_csv_columns = \
                get_link_column(frame, link["from"])
            to_namespace_name, to_column, to_separator, to_data, to_csv_columns = get_link_column(frame, link["to"])
            priority = link.get("priority", DEFAULT_PRIORITY)
            if not source_spec["is_newest_version"]:
                priority = source_spec.get("older_versions_priority", priority)
            is_from_clean = link["from"].get("is_clean", True)
            is_to_clean = link["to"].get("is_clean", True)

            print(f"- Collect {source_name}[{from_column} -> {to_column}] ...", flush = True)

            for row in range(len(from_data)):
                from_names = [name for name in split_names(from_namespace_name, from_separator, from_data[row])
                              if name not in newer_names]
                if len(from_names) == 0:
                    continue
                collected_names.update(from_names)
                to_names = split_names(to_namespace_name, to_separator, to_data[row])
                from_source_name = provenance.step(source_name, row + row_offset, from_csv_columns[row])
                to_source_name = provenance.step(source_name, row + row_offset, to_csv_columns[row])
                link_source_name = provenance.step(
                    source_name, row + row_offset, provenance.link(from_csv_columns[row], to_csv_columns[row])
                )
                self.add_names(from_source_name, from_namespace_name, from_names, is_from_clean)
                self.add_names(to_source_name, to_namespace_name, to_names, is_to_clean)
                self.link_names(
                    link_source_name, priority, from_namespace_name, from_names, to_namespace_name, to_names
                )
                if source_spec.get("is_reference", False):
                    for namespace_name, names in ((from_namespace_name, from_names), (to_namespace_name, to_names)):
                        if namespace_name == "EnsemblGene":
                            self.reference_ensembl_genes.update(names)

        # Only after the whole version is collected, so names which this version gives to several genes keep them all.
        newer_names.update(collected_names)

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
                self.add_names(from_source_names[row], from_namespace_name, from_names, True)
                self.add_names(link_source_names[row], to_namespace_names[row], to_names, True)
                self.link_names(link_source_names[row], DEFAULT_PRIORITY,
                                from_namespace_name, from_names, to_namespace_names[row], to_names)

    def add_names(self, source_name, namespace_name, gene_names, is_clean):
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = Namespace(namespace_name)
        namespace = self.namespaces[namespace_name]
        for gene_name in gene_names:
            if gene_name != "":
                if gene_name not in namespace.genes:
                    if gene_name in TRACK_GENES:
                        print(f"TRACK: add_names source_name: {source_name} namespace_name: {namespace_name} gene_name: {gene_name}")
                    namespace.genes[gene_name] = Gene(source_name, gene_name, is_clean)
                elif is_clean and not namespace.genes[gene_name].is_clean:
                    namespace.genes[gene_name].source_name = source_name
                    namespace.genes[gene_name].is_clean = True

    # Remove the names which appear only in columns of aliases, and the links to them. The links from aliases which are
    # also clean names remain.
    def remove_unclean_names(self):
        print("Remove unclean names ...", flush = True)
        for namespace in self.namespaces.values():
            namespace.genes = {gene_name: gene for gene_name, gene in namespace.genes.items() if gene.is_clean}
        for namespace in self.namespaces.values():
            for gene in namespace.genes.values():
                for to_namespace_name, to_links in gene.links.items():
                    to_genes = self.namespaces[to_namespace_name].genes
                    gene.links[to_namespace_name] = {
                        to_gene_name: link for to_gene_name, link in to_links.items() if to_gene_name in to_genes
                    }

    def link_names(
        self, link_source_name, priority, from_namespace_name, from_gene_names, to_namespace_name, to_gene_names
    ):
        from_namespace = self.namespaces[from_namespace_name]
        to_namespace = self.namespaces[to_namespace_name]
        for from_gene_name in from_gene_names:
            if from_gene_name != "":
                for to_gene_name in to_gene_names:
                    if to_gene_name != "" and to_gene_name != from_gene_name:
                        if to_namespace_name not in from_namespace.genes[from_gene_name].links:
                            from_namespace.genes[from_gene_name].links[to_namespace_name] = {}
                        links = from_namespace.genes[from_gene_name].links[to_namespace_name]
                        if to_gene_name not in links or priority > links[to_gene_name][0]:
                            links[to_gene_name] = (priority, link_source_name)
                        from_namespace.links.add(to_namespace_name)
                        if from_gene_name in TRACK_GENES or to_gene_name in TRACK_GENES:
                            print(f"TRACK: link_names source_name: {link_source_name} priority: {priority} from_namespace_name: {from_namespace_name} from_gene_name: {from_gene_name} to_namespace_name: {to_namespace_name} to_gene_name: {to_gene_name}")

    # Connect each EnsemblGene to the EnsemblGenes at the ends of its chains of links (from a retired identifier to its
    # replacements). An EnsemblGene without such links is connected to itself.
    def compute_different_ensembl_genes(self):
        print("Compute different EnsemblGene ...", flush = True)
        for gene_name, gene in self.namespaces["EnsemblGene"].genes.items():
            self.collect_final_ensembl_genes(gene, gene_name, [], [gene_name])
            if len(gene.ensembl_genes) == 0:
                gene.ensembl_genes[gene_name] = gene.source_name
            if gene_name in TRACK_GENES:
                print(f"TRACK: EnsemblGene {gene_name} => {gene.ensembl_genes}")

    # Connect the `into_gene` to the EnsemblGenes at the ends of the chains of links from the EnsemblGene `gene_name`,
    # which is reached by the `link_source_names` (and the `path` of EnsemblGenes).
    def collect_final_ensembl_genes(self, into_gene, gene_name, link_source_names, path):
        genes = self.namespaces["EnsemblGene"].genes
        for to_gene_name, (priority, link_source_name) in genes[gene_name].links.get("EnsemblGene", {}).items():
            if to_gene_name in path:
                continue
            to_gene = genes[to_gene_name]
            to_link_source_names = link_source_names + [link_source_name]
            if len(to_gene.links.get("EnsemblGene", {})) > 0:
                path.append(to_gene_name)
                self.collect_final_ensembl_genes(into_gene, to_gene_name, to_link_source_names, path)
                path.pop()
            else:
                source_name = provenance.JOIN.join(to_link_source_names + [to_gene.source_name])
                if to_gene_name not in into_gene.ensembl_genes \
                or len(source_name) < len(into_gene.ensembl_genes[to_gene_name]):
                    into_gene.ensembl_genes[to_gene_name] = source_name

    # Drop the other EnsemblGenes of each name which is connected to a reference EnsemblGene (such as the copies of the
    # gene on alternate haplotypes, or retired genes).
    def prefer_reference_ensembl_genes(self):
        print("Prefer reference EnsemblGene ...", flush = True)
        for namespace in self.namespaces.values():
            for gene in namespace.genes.values():
                if any(ensembl_gene_name in self.reference_ensembl_genes for ensembl_gene_name in gene.ensembl_genes):
                    gene.ensembl_genes = {
                        ensembl_gene_name: ensembl_source_name
                        for ensembl_gene_name, ensembl_source_name in gene.ensembl_genes.items()
                        if ensembl_gene_name in self.reference_ensembl_genes or ensembl_gene_name.startswith("ENS!")
                    }

    # Connect each namespace after all the other namespaces it links to are connected.
    def connect_to_ensembl_genes(self):
        unconnected_namespaces_names = set([namespace_name for namespace_name in self.namespaces if namespace_name != "EnsemblGene"])
        connected_namespaces_names = set(["EnsemblGene"])

        while len(unconnected_namespaces_names) > 0:
            for from_namespace_name in sorted(unconnected_namespaces_names):
                to_namespaces_names = self.namespaces[from_namespace_name].links - set([from_namespace_name])
                if to_namespaces_names <= connected_namespaces_names:
                    self.connect_namespace_to_ensembl_genes(from_namespace_name)
                    unconnected_namespaces_names.remove(from_namespace_name)
                    connected_namespaces_names.add(from_namespace_name)
                    break
            else:
                assert False, f"cyclic links between the namespaces: {' '.join(sorted(unconnected_namespaces_names))}"

    def connect_namespace_to_ensembl_genes(self, from_namespace_name):
        print(f"- Connect {from_namespace_name} ...", flush = True)
        from_namespace = self.namespaces[from_namespace_name]
        for from_gene_name in from_namespace.genes:
            self.connect_gene_to_ensembl_genes(from_namespace_name, from_gene_name, set())
        for from_gene_name, from_gene in from_namespace.genes.items():
            if len(from_gene.ensembl_genes) == 0:
                from_gene.ensembl_genes[f"ENS!{self.next_index:09}"] = "Unrecognized"
                self.next_index += 1
            if from_gene_name in TRACK_GENES:
                print(f"TRACK: {from_namespace_name} {from_gene_name} => {from_gene.ensembl_genes}")

    # Connect a gene to the EnsemblGenes reached by its links of the strongest rank which reaches a recognized
    # EnsemblGene (or, if none does, which reaches any). Links to other namespaces rank above links within the
    # namespace, so the latter are followed only if the former reach no recognized EnsemblGene. Otherwise, a stronger
    # priority ranks higher. A link to a gene in the same namespace reaches the EnsemblGenes that gene is connected to,
    # so the weaker links of that gene are not followed.
    def connect_gene_to_ensembl_genes(self, namespace_name, from_gene_name, connecting_genes_names):
        from_gene = self.namespaces[namespace_name].genes[from_gene_name]
        if from_gene.is_connected or from_gene_name in connecting_genes_names:
            return from_gene.ensembl_genes
        connecting_genes_names.add(from_gene_name)

        ensembl_genes_by_rank = {}
        for to_namespace_name, to_links in from_gene.links.items():
            to_namespace = self.namespaces[to_namespace_name]
            for to_gene_name, (priority, link_source_name) in to_links.items():
                to_gene = to_namespace.genes[to_gene_name]
                if to_namespace_name == namespace_name:
                    to_ensembl_genes = self.connect_gene_to_ensembl_genes(
                        namespace_name, to_gene_name, connecting_genes_names
                    )
                    to_source_name = f"{link_source_name}{provenance.JOIN}{to_gene.source_name}"
                else:
                    to_ensembl_genes = to_gene.ensembl_genes
                    to_source_name = link_source_name
                if len(to_ensembl_genes) == 0:
                    continue
                is_other_namespace = to_namespace_name != namespace_name
                ensembl_genes = ensembl_genes_by_rank.setdefault((is_other_namespace, priority), {})
                for ensembl_gene_name, ensembl_source_name in to_ensembl_genes.items():
                    if ensembl_source_name == to_gene.source_name:
                        source_name = to_source_name
                    else:
                        source_name = f"{to_source_name}{provenance.JOIN}{ensembl_source_name}"
                    if ensembl_gene_name not in ensembl_genes \
                    or len(source_name) < len(ensembl_genes[ensembl_gene_name]):
                        ensembl_genes[ensembl_gene_name] = source_name

        if len(ensembl_genes_by_rank) > 0:
            rank = max(ensembl_genes_by_rank, key = lambda rank: (
                has_recognized_ensembl_gene(ensembl_genes_by_rank[rank]), rank
            ))
            from_gene.ensembl_genes = ensembl_genes_by_rank[rank]
            if from_gene_name in TRACK_GENES:
                print(f"TRACK {from_gene_name} => rank: {rank} genes: {from_gene.ensembl_genes}")

        connecting_genes_names.remove(from_gene_name)
        from_gene.is_connected = True
        return from_gene.ensembl_genes

    def write(self, names_dir):
        if os.path.exists(names_dir):
            shutil.rmtree(names_dir)
        os.mkdir(names_dir)

        for namespace_name in self.namespaces:
            self.write_namespace(namespace_name, names_dir)

    def write_namespace(self, namespace_name, names_dir):
        print(f"Write names/{namespace_name}.tsv ...", flush = True)
        with open(f"{names_dir}/{namespace_name}.tsv", "w") as file:
            print("name\tensembl_gene\tname_source\tname_mapping", file = file)
            genes = self.namespaces[namespace_name].genes
            for gene_name, gene in sorted(genes.items(), key = lambda item: (str.casefold(item[0]), item[0])):
                assert len(gene.ensembl_genes) > 0
                for ensembl_gene, ensembl_source_name in gene.ensembl_genes.items():
                    print(f"{gene_name}\t{ensembl_gene}\t{gene.source_name}\t{ensembl_source_name}", file = file)

def has_recognized_ensembl_gene(ensembl_genes):
    return any(not ensembl_gene_name.startswith("ENS!") for ensembl_gene_name in ensembl_genes)

# Names containing white space are dropped. These are descriptions (such as some MGI synonyms) rather than names, and
# the lists split their names on white space.
def split_names(namespace_name, separator, names):
    if separator is not None:
        names = names.split(separator)
    else:
        names = [names]
    names = [gene_names.normalize_name(namespace_name, name) for name in names]
    return [name for name in names if not re.search(r"\s", name)]

# Return the namespace, the column name (for messages), the separator, the data of each row of the column of a link, and
# the index of the CSV column it was taken from. The column may be a list of alternative columns, which are tried in
# order until one of them is not empty.
def get_link_column(frame, link):
    namespace_name = link["namespace"]
    columns = link["column"] if isinstance(link["column"], list) else [link["column"]]
    separator = link.get("separator")

    data = None
    csv_columns = None
    for column in columns:
        column_data = frame.loc[:, column].values if isinstance(column, str) else frame.iloc[:, column].values
        csv_column = provenance.csv_column_of(frame, column)
        if data is None:
            data = list(column_data)
            csv_columns = [csv_column] * len(data)
        else:
            for row in range(len(data)):
                if data[row] == "":
                    data[row] = column_data[row]
                    csv_columns[row] = csv_column

    return namespace_name, ";".join(str(column) for column in columns), separator, data, csv_columns

def main():
    assert len(sys.argv) == 2, "Usage: compute_namespaces.py species"
    species = sys.argv[1]

    sources_dir = f"genes/{species}/namespaces/sources"
    namespaces = Namespaces(sources_dir)
    for source_spec in source_files.load_specs(sources_dir):
        namespaces.collect_source(source_spec)
    namespaces.collect_extra()
    namespaces.remove_unclean_names()

    namespaces.compute_different_ensembl_genes()
    namespaces.connect_to_ensembl_genes()
    namespaces.prefer_reference_ensembl_genes()

    names_dir = f"genes/{species}/namespaces/names"
    namespaces.write(names_dir)

if __name__ == "__main__":
    main()
