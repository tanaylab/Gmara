This directory holds the sources of the list of genes:

* `sources.yaml` lists the source files and how to process them.
* `<name>.csv` and/or `<name>.tsv` are comma-separated or tab-separated data source files. The `<name>` is typically
  based on the name(s) of the relevant namespaces it contains data for. It ends with the version of the source (e.g.
  `HGNC.Current.2026-10-06.tsv`), except for `CURATED.tsv`, which is curated manually (based on a survey of the genes
  marked as lateral in 11 atlases).
