# Gmara <img src="Gmara.jpg" align="right" height="280" alt="" />
Genes Manifests Archive for RNA Analysis

## TL;DR

This repository holds lists of genes for use in scRNA-seq analysis. They are stored in machine-readable CSV.TSV so they
can be used by software, directly from this repository, optionally with commit tags to ensure reproducibility.

Specifically, the files called `genes/`_species_`/lists/`_list_`/names/`_namespace_`.tsv` contain, in the first column
(called `name`), a list of names of genes of the specified namespace and species. For example, the file
[genes/human/lists/transcription_factor/names/GeneSymbol.tsv](genes/human/lists/transcription_factor/names/GeneSymbol.tsv)
contains a list of symbols of human transcription factor genes. You can just access these files directly from github
(using explicit commit tags if you want reproducible results).

The files also contain a second column called `provenance` which can help in tracking _why_ the gene name is included in
the list, by referring to source files of the list and/or the gene namespaces. These files are described below, but
you do not have to deal with this to just use the list.

In general, this repository is meant to be used as a convenient *initial starting point* for analysis, rather than serve
as a "source of truth". It is designed to make it easy to apply lists to to arbitrary data sets regardless of the
version of the genes names was used, so the lists include retired/deprecated/aliased/renamed genes. That is, we
construct the lists such that if a name does *not* appear in a list, you can be fairly certain that what you are
looking up *doesn't* belong in it. If the name *does* appear in the list, then *probably* what you are looking up
belongs in it, but there's no guarantee.

**The analyst is responsible for exercising judgment and common sense when using these lists.**

## Details

The lists here track only "known" genes and explicitly ignore clones and fragments (e.g. "AC005041.3"). That is, we
assume that to be note-worthy enough to be included in a list (e.g., transcription factors), the gene should be
sufficiently known to be listed in the genes databases, as opposed to being a numbered fragment in some assembly. This
assumption holds well for the well-studied genomes (e.g. `human` and `mouse`) we are focusing on. It will not hold for
less-studied genomes.

There are [too many ways](https://xkcd.com/927/) to uniquely identify a gene. We use
[Ensembl](https://www.ensembl.org/info/genome/genebuild/gene_names.html) as our "source of truth" for "what is a gene".
That is, we assume that "different" EnsemblGene identifiers refer to different "genes" (and allow for some EnsemblGene
identifiers to be mapped to others, e.g. when they are retired). For each namespace other than EnsemblGene, we keep
track of the (possibly one-to-many) mapping between its names and EnsemblGene. For example, each `GeneSymbol` may map to
one of several `EnsemblGene` due to changes in our understanding over time. When other namespace identifiers don't map
to any EnsemblGene identifier, we still accept them, and assume all such identifiers that map to each other refer to the
same "gene" (e.g., `HGNC:7424`, `MT-CSB1`, `MTCSB1` and `CSB-I` are all considered to be equivalent, even though there's
no EnsemblGene for it; instead we assign these genes a unique *unstable* *non*-Ensembl identifier, e.g.
`ENS!000000946`).

The cost of Ensembl identifiers stability is that they aren't human readable. Data sets therefore often use GeneSymbol
identifiers instead. We take this mapping from [HGNC](https://www.genenames.org/) for human genes and from
[MGI](https://www.informatics.jax.org/) for mouse genes, which make a valiant effort to put some order into this
constantly evolving namespaces.

In general we recommend that for the most reliable results, data sets use EnsemblGene identifiers to uniquely identify
genes and look them up in lists, and only use GeneSymbol identifiers for display in graphs and figures for readability.

We also map other stable gene identifiers to EnsemblGene identifiers, for example [HGNC](https://www.genenames.org/) and
[UCSC](https://genome.ucsc.edu/) stable identifiers, based on the mapping specified by the Ensembl database.

For convenience, we also keep track of the mapping from transcript and protein identifiers (`EnsemblTranscript` and
`EnsemblProtein` namespaces), as well as mapping from [RefSeq](https://www.ncbi.nlm.nih.gov/refseq/) sequence
identifiers to Ensembl gene identifiers. However, **this repository is only concerned with genes**; the semantics of a
list of, say, EnsemblProtein identifiers is still "does the *gene* associated with the protein belong in a list" rather
than "does the specific *protein* belong in the list". We basically map whatever-it-is to (one or more possible)
EnsemblGene identifier(s) and look that up in the "master" list containing EnsemblGene identifiers.

We provide a version of each list for each of the supported namespaces, based on the mapping we collected between them
and EnsemblGene identifiers. To compute each list, we try to isolate the specific EnsemblGene(s) identified by each
entry. In general when a list provides multiple names from multiple namespaces for some entry, we intersect the sets of
possible EnsemblGenes for these names. If the result is empty, then something is very wrong. If it contains more than
one possible EnsemblGene, it is noteworthy, but possible; we include in the list all the EnsemblGenes that map to all the
identifiers given for the list entry.

## Status

This repository is still in its "alpha" phase - *anything* may change without notice. This will be updated to "beta"
when the structure stabilizes and we have a few useful lists in place for human and mouse. It will be updated to
"production" when the structure will be expected never to change again without providing some backward compatibility
features.

The repository content is expected to always keep evolving due to updates to the relevant gene namespaces (which are a
constantly moving target), and by the addition of new species and/or gene lists, or updates to the existing lists.

Feedback and contributions are welcome!

## Structure

The data is stored in the following tree:

* All data is under the `genes` directory.
    * A sub-directory exists for each organism (e.g., `human`, `mouse`).
        * A `namespaces` sub-directory contains a description of the gene namespaces used.
            * A `sources` sub-directory contains the source files we collected the gene namespaces from.
            * A `names` sub-directory contains the actual gene names.
        * A `lists` sub-directory` contains the actual gene lists.
            * Each list is a sub-directory.
                * A `sources` sub-directory contains the sources of the gene list.
                * A `names` sub-directory contains the actual gene names.

Additional sub-directories may be added in the future.

## API and Versioning

There's no API provided here. The idea is that you can fetch the (simple CSV/TSV) data file(s) you need directly through
the github URLs using `wget`, `curl` or any other method for fetching HTTP data. That said, it is possible to provide an
API for fetching specific data using these URLs (see for example the `Gmara` module of
[Metacells.jl](https://github.com/tanaylab/Metacells.jl).

Since this is a github repository, you can always refer to a specific commit of this repository in the URLs to get the
same data. This is useful anywhere reproducibility is important (e.g. vignettes and published results).

## Lists

Each list is a sub-directory under the `lists` sub-directory, holding the following:

* `README.md` contains a free text in markdown format that describes the semantics of the list.

* The `names` sub-directory contains, for each namespace, _namespace_`.tsv` with the following columns:

  * `name` contains the identifier of the gene in the namespace, in alphabetical order. For example, `SOX4` is listed in the
    human transcription factors list in the GeneSymbol namespace.

  * `source` contains the source of the mapping from the `name` to the EnsemblGene namespace. This is useful for
    debugging. For example `HGNC.Current#37136[symbol] : SOX4 => HGNC.Current#37136[symbol -> hgnc_id] : HGNC:11200 =>
    Ensembl.HGNC#20684[HGNC ID -> Gene stable ID] : ENSG00000124766` indicates that the `HGNC.Current` source file, in
    line `37136`, contains a column `symbol` with a value `SOX4` (which is why this GeneSymbol exists). This was mapped
    to `HGNC:11200` by the association between the `hgnc_id` and the `symbol` columns of the same line. Finally, the
    HGNC identifier was mapped to `ENSG00000124766` by association between the `HGNC ID` and `Gene stable ID` columns in
    line `20684` of the source file `Ensembl.HGNC`.

  * `ensembl_gene` contains the identifier of the gene in the EnsemblGene namespace, which was included in the list. For
    example, `ENSG00000124766` for `SOX4`. If several such identifiers are possible, the file will contain multiple
    lines.

  * `ensembl_source` contains the source of the inclusion of the EnsemblGene in the list. This is useful for debugging.
    For example, `Toronto#1146[Ensembl ID] : ENSG00000124766 => Ensembl#20660[Gene stable ID] : ENSG00000124766`
    indicates the `Toronto` source file for the list, in line `1146`, in the `Ensembl ID` column, contained
    `ENSG00000124766`. This was verified to be an active identifier in the `Ensembl` source file line `20660` in the
    `Gene stable ID` column. If the identifier was retired, this will contain a mapping from the retired identifier to
    the active one.

* To compute the above, we begin with a set of manually curated "source of truth" files. These are TSV or CSV files
  under the `sources` sub-directory which have at least one column containing names (of some namespace). In addition we
  have a single `sources.yaml` file which contains a sequence of mappings with the following keys, as well as a comment
  describing the source:

  * ``data_file`` holds the name of the CSV or TSV source data file.

  * ``has_header`` is a Boolean specifying whether the data file has a header line (default: `true`).

  * `columns` holds a mapping whose key is the column name (or 0-based index if there are no headers), and whose value
    is a name of a namespace.

  The computed canonical list names are any EnsemblGene identifiers that are agreed on by the identifiers in all the
  columns of each list entry. For other namespaces, these are the identifiers that map to any of these EnsemblGenes.
  This is computed using ``scripts/compute_list.py``.

## Namespaces


"The naming of cats is a difficult matter" - T. S. Eliot

We scrape data from several sources for maintaining a mapping between the different gene name spaces. We use the
following data model for handling gene namespaces:

* We use a separate set of namespaces for each organism. That is, EnsemblGene for human and mouse are two distinct
  unrelated namespaces. We do not address mapping of genes between species.

* In each namespace, identifiers may be mapped to each other (to represent changes in the namespace over time). These
  mappings are directional. For EnsemblGene, we consider all the identifiers that do not map to anything to be
  "different"; identifiers in all other namespaces are mapped to a set of such "different" identifiers (ideally, to just
  one).

* It is assumed that once an identifier was added to a namespace, it is never fully removed. It may be that multiple old
  identifiers are combined into a new one or that an old identifier is split into several new ones, or possibly that the
  identifier is "retired" (no longer used) - but would be kept to allow processing old data.

  While most namespaces follow this rule, some (Ensembl!) don't make it easy to dump the full list of retired
  identifiers. Whenever we encounter specific retired identifiers for these namespaces we use Web APIs to fetch their
  data. That is, our list of identifiers in a namespace "should" contain all active identifiers, it may lack specific
  retired ones (open an issue if you have a set of specific retired identifiers you want us to add to the data).
 
  In cases of a true ambiguity (an old gene being renamed to a new identifier, and another different gene given the old
  identifier) we (try to) collect the set of possible EnsemblGenes for the identifier, and hope this ambiguity will be
  resolved by other identifiers of other namespaces given to the same list entry.

* Stored identifiers are "normalized". In most namespaces, this means removing the `.[0-9]` version suffix from the
  name. To lookup a name in a list or a namespace, you need to normalize the query gene name accordingly. The UCSC
  namespace is an exception in that the `.[0-9]` suffix seems to be an inherent part of the identifier. By convention,
  names are in mixed case, different in different namespaces; for example, `SOX4` for the human gene and `Sox4` for the
  mouse gene.

* We maintain *directed* mapping between the namespaces, that is, other than aliases that map a namespace to itself, all
  mappings bring us closer towards the EnsemblGene namespace.

To compute all the above, we begin with a set of "source of truth" files. These are TSV or CSV files under the `sources`
sub-directory which have at least two column containing names, to establish links between names (within the same
namespace or across namespaces).

We use a `sources.yaml` file which contains a sequence of mappings with the following keys, as well as a comment
describing the source:

* ``data_file`` holds the name of the CSV or TSV source data file. We omit the `.csv` or `.tsv` suffix when we identify
  the source in provenance fields.

* `links` holds a sequence of directed links between two identifiers. Each is a mapping with the keys `from`, `to` which
  contains a mapping with the following keys:

  * `column` identifies the column containing the identifier.
  * `namespace` contains the name of the namespace the identifier belongs to.
  * `separator` is an optional character used to separate multiple identifiers within the column (e.g., `|`).

Links are established either between a namespace and itself (from an alias or renamed identifier to a more current one)
or between a namespace and EnsemblGene (or a namespace closer to EnsemblGene).

In addition to the above, the `sources` sub-directory optionally contains the following:

* _namespace_`.Missing.tsv` contains names and sources we have seen (in some list or data set) that do not exist in any
  of the source files. This is a temporary file which is read and deleted by ``scripts/complete_namespace.py``. This
  happens because some namespaces (Ensembl!) do not list all the names they actually know about in their "dump the whole
  database" data, because "reasons".

* _namespace_`.Extra.tsv` contain names and sources for missing names that we fetched from web APIs (using
  ``scripts/complete_namespaces.py``).

* _namespace_`.Ignored.tsv` contains names and sources that we have looked up in the web APIs and couldn't find any data
  for. These names are *not* included in the namespace. Ideally, there shouldn't be any such names. In the best case,
  they are simply typos; in the worst case, these are names that were used once and were lost to history.

To represent the result, in the `names` sub-directory we keep the following files:

* _namespace_`.tsv` contains the following columns:

  * `name` contains the name of the gene in the namespace, in alphabetical order. For example, `SOX4`.

  * `source` contains the source of the name. For example `HGNC.Current#37136[symbol] : SOX4` indicates that `SOX4` was
    the value of the `symbol` column of the `HGNC.Current` source file in line `37136`.

  * `ensembl_gene` contains the name of the EnsemblGene the gene maps to. For example, `ENSG00000124766` for `SOX4`.

  * `ensembl_source` contains the source of the mapping of the gene to the EnsemblGene. For example,
    `HGNC.Current#37136[symbol -> hgnc_id] : HGNC:11200 => Ensembl.HGNC#20684[HGNC ID -> Gene stable ID] :
    ENSG00000124766` indicates that `SOX` was mapped to the HGNC id `HGNC:11200` by the association between columns
    `hgnc_id` and `symbol` in line `37136` of the `HGNC.Current` source file. This was in turn mapped to the EnsemblGene
    identifier `ENSG00000124766` by the association between the `HGNC ID` and `Gene stable ID` columns in line `20684`
    of the source file `Ensembl.HGNC`.

We follow all the links, including the extra data, and compute for every identifier, in every namespace, the possible
EnsemblGenes it may map to. This computation is done by ``scripts/compute_namespaces.py``.

## Updates

Updating this repository is done by adding new species, namespaces (sources) and lists (sources). Everything is rebuilt
by invoking `make` at the top-level directory. If any of the added data refers to missing gene names, you will have to
re-run `make` again to update the namespaces based on the recomputed `Extra` files. To be certain just re-run `make`
until it says `Nothing to be done`.
