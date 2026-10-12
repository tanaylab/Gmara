# Gmara <img src="Gmara.jpg" align="right" height="280" alt="" />
Genes Manifests Archive for RNA Analysis

## TL;DR

This repository holds lists of genes for use in scRNA-seq analysis. They are stored in machine-readable CSV/TSV so they
can be used by software, directly from this repository, optionally with commit tags to ensure reproducibility.

Specifically, the files called `genes/`_species_`/lists/`_list_`/names/`_namespace_`.tsv` contain, in the first column
(called `name`), a list of names of genes of the specified namespace and species. For example, the file
[`genes/human/lists/transcription_factor/names/GeneSymbol.tsv`](genes/human/lists/transcription_factor/names/GeneSymbol.tsv)
contains a list of symbols of human transcription factor genes. You can just access these files directly from github
(using explicit commit tags if you want reproducible results).

The files also contain additional columns which can help in tracking _why_ the gene name is included in the list, by
referring to source files of the list and/or the gene namespaces. These columns and files are described below, but you
do not have to deal with this to just use the list.

In general, this repository is meant to be used as a convenient *initial starting point* for analysis, rather than serve
as a "source of truth". It is designed to make it easy to apply lists to arbitrary data sets regardless of the version
of the gene names used, so the lists include retired/deprecated/aliased/renamed genes. We try to construct the lists
such that if a name does *not* appear in a list, you can be fairly certain that what you are looking up *doesn't* belong
in it (according to any of our sources). If the name *does* appear in the list, then *probably* what you are looking up
belongs in it, but there's no guarantee.

**The analyst is responsible for exercising judgment and common sense when using these lists.**

## Quick access

The repository currently holds the following:

**Human gene lists:**

Namespaces:
  [EnsemblGene](genes/human/namespaces/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/namespaces/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/namespaces/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/namespaces/names/GeneSymbol.tsv),
  [HGNC](genes/human/namespaces/names/HGNC.tsv),
  [RefSeq](genes/human/namespaces/names/RefSeq.tsv),
  [UCSC](genes/human/namespaces/names/UCSC.tsv).

Lists:

* Ribosomal:
  [EnsemblGene](genes/human/lists/ribosomal/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/lists/ribosomal/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/lists/ribosomal/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/lists/ribosomal/names/GeneSymbol.tsv),
  [HGNC](genes/human/lists/ribosomal/names/HGNC.tsv),
  [RefSeq](genes/human/lists/ribosomal/names/RefSeq.tsv),
  [UCSC](genes/human/lists/ribosomal/names/UCSC.tsv).

* Mitochondrial:
  [EnsemblGene](genes/human/lists/mitochondrial/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/lists/mitochondrial/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/lists/mitochondrial/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/lists/mitochondrial/names/GeneSymbol.tsv),
  [HGNC](genes/human/lists/mitochondrial/names/HGNC.tsv),
  [RefSeq](genes/human/lists/mitochondrial/names/RefSeq.tsv),
  [UCSC](genes/human/lists/mitochondrial/names/UCSC.tsv).

* Transcription factors:
  [EnsemblGene](genes/human/lists/transcription_factor/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/lists/transcription_factor/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/lists/transcription_factor/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/lists/transcription_factor/names/GeneSymbol.tsv),
  [HGNC](genes/human/lists/transcription_factor/names/HGNC.tsv),
  [RefSeq](genes/human/lists/transcription_factor/names/RefSeq.tsv),
  [UCSC](genes/human/lists/transcription_factor/names/UCSC.tsv).

* Regulators:
  [EnsemblGene](genes/human/lists/regulator/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/lists/regulator/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/lists/regulator/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/lists/regulator/names/GeneSymbol.tsv),
  [HGNC](genes/human/lists/regulator/names/HGNC.tsv),
  [RefSeq](genes/human/lists/regulator/names/RefSeq.tsv),
  [UCSC](genes/human/lists/regulator/names/UCSC.tsv).

* Lateral:
  [EnsemblGene](genes/human/lists/lateral/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/human/lists/lateral/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/human/lists/lateral/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/human/lists/lateral/names/GeneSymbol.tsv),
  [HGNC](genes/human/lists/lateral/names/HGNC.tsv),
  [RefSeq](genes/human/lists/lateral/names/RefSeq.tsv),
  [UCSC](genes/human/lists/lateral/names/UCSC.tsv).

**Mouse gene lists:**

Namespaces:
  [EnsemblGene](genes/mouse/namespaces/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/namespaces/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/namespaces/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/namespaces/names/GeneSymbol.tsv),
  [MGI](genes/mouse/namespaces/names/MGI.tsv),
  [RefSeq](genes/mouse/namespaces/names/RefSeq.tsv),
  [UCSC](genes/mouse/namespaces/names/UCSC.tsv).

Lists:

* Ribosomal:
  [EnsemblGene](genes/mouse/lists/ribosomal/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/lists/ribosomal/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/lists/ribosomal/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/lists/ribosomal/names/GeneSymbol.tsv),
  [MGI](genes/mouse/lists/ribosomal/names/MGI.tsv),
  [RefSeq](genes/mouse/lists/ribosomal/names/RefSeq.tsv),
  [UCSC](genes/mouse/lists/ribosomal/names/UCSC.tsv).

* Mitochondrial:
  [EnsemblGene](genes/mouse/lists/mitochondrial/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/lists/mitochondrial/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/lists/mitochondrial/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/lists/mitochondrial/names/GeneSymbol.tsv),
  [MGI](genes/mouse/lists/mitochondrial/names/MGI.tsv),
  [RefSeq](genes/mouse/lists/mitochondrial/names/RefSeq.tsv),
  [UCSC](genes/mouse/lists/mitochondrial/names/UCSC.tsv).

* Transcription factors:
  [EnsemblGene](genes/mouse/lists/transcription_factor/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/lists/transcription_factor/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/lists/transcription_factor/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/lists/transcription_factor/names/GeneSymbol.tsv),
  [MGI](genes/mouse/lists/transcription_factor/names/MGI.tsv),
  [RefSeq](genes/mouse/lists/transcription_factor/names/RefSeq.tsv),
  [UCSC](genes/mouse/lists/transcription_factor/names/UCSC.tsv).

* Regulators:
  [EnsemblGene](genes/mouse/lists/regulator/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/lists/regulator/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/lists/regulator/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/lists/regulator/names/GeneSymbol.tsv),
  [MGI](genes/mouse/lists/regulator/names/MGI.tsv),
  [RefSeq](genes/mouse/lists/regulator/names/RefSeq.tsv),
  [UCSC](genes/mouse/lists/regulator/names/UCSC.tsv).

* Lateral:
  [EnsemblGene](genes/mouse/lists/lateral/names/EnsemblGene.tsv),
  [EnsemblProtein](genes/mouse/lists/lateral/names/EnsemblProtein.tsv),
  [EnsemblTranscript](genes/mouse/lists/lateral/names/EnsemblTranscript.tsv),
  [GeneSymbol](genes/mouse/lists/lateral/names/GeneSymbol.tsv),
  [MGI](genes/mouse/lists/lateral/names/MGI.tsv),
  [RefSeq](genes/mouse/lists/lateral/names/RefSeq.tsv),
  [UCSC](genes/mouse/lists/lateral/names/UCSC.tsv).

## Details

A list may include genes which are known only by a clone-based name (e.g. `AC092171.3`), such as some genes of the
lateral list. Ensembl stopped using most of these names after release 103. Data sets still use them, so we keep the
gene names of all Ensembl releases (see `has_multiple_versions`).

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
identifiers instead, typically without specifying some particular version of a mapping between them and Ensembl
identifiers. We take this mapping from [HGNC](https://www.genenames.org/) for human genes and from
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

## Provenance

Every names file has provenance columns recording *why* the name is there and *why* it maps to its EnsemblGene:
`name_source` and `name_mapping`, and in a list also `list_source`, `list_mapping` and `common_mapping` (see
[Lists](#lists)). This is meant for debugging; you do not need it to just use the lists.

A provenance is a sequence of steps separated by `;`. Each step is written _source_`:`_line_`[`_csv_columns_`]`,
naming the 1-based _line_ of the _source_ data file (under one of the `sources` sub-directories), and the 0-based
indices of the CSV columns of that line the data was taken from:

* A single index, e.g. `HGNC.Current.2026-10-06:33501[1]` - line `33501` of `HGNC.Current.2026-10-06.tsv` holds the
  value `SOX4` in its CSV column `1` (`symbol`), which is why this GeneSymbol exists.

* Two indices around `>`, e.g. `Ensembl.GeneName.116:5575[1>0]` - line `5575` of `Ensembl.GeneName.116.tsv` maps the
  value of its CSV column `1` (`Gene name`) to the value of its CSV column `0` (`Gene stable ID`).

The name of a source includes its version, so the provenance says which version of the source data was used. In a
list, the name of a source of the list is prefixed by the name of the list, e.g.
`transcription_factor/Toronto.1.01:1146[1]`. This is because sources of different lists may have the same name.

Some names do not map to any EnsemblGene. The `name_mapping` of such a name ends with the step `Unrecognized`.

Names fetched from web APIs have other kinds of steps. Their `name_source` names the source and CSV columns, without a
line. Their `name_mapping` contains the URL of the web API call.

The _namespace_`.Missing.tsv`, _namespace_`.Extra.tsv` and _namespace_`.Ignored.tsv` files record only the source and
the CSV columns, without a line, e.g. `regulator/CURATED[0]`. Their entries outlive the line they were seen in - the
list sources are hand-edited, so by the time anyone reads the entry the line holds some other gene - and some of them
name a data set which is not in this repository at all, and so has no line to point at.

The CSV columns are identified by index rather than by name to keep the data files small; their names are in the
header line of the source data file itself. To see a provenance spelled out, pipe the names file lines through
`scripts/expand_provenance.py`, which looks up every step and reports it in YAML:

```
$ grep -P '^SOX4\t' genes/human/lists/transcription_factor/names/GeneSymbol.tsv | scripts/expand_provenance.py human
- name: SOX4
  ensembl_gene: ENSG00000124766
  list_name: ENSG00000124766
  name_source:
  - step: HGNC.Current.2026-10-06:33501[1]
    file: genes/human/namespaces/sources/HGNC.Current.2026-10-06.tsv
    line: 33501
    csv_column: symbol
    value: SOX4
  name_mapping:
  - step: HGNC.Current.2026-10-06:33501[1>0]
    file: genes/human/namespaces/sources/HGNC.Current.2026-10-06.tsv
    line: 33501
    from_csv_column: symbol
    to_csv_column: hgnc_id
    value: HGNC:11200
  - step: Ensembl.HGNC.116:157489[3>0]
    file: genes/human/namespaces/sources/Ensembl.HGNC.116.tsv
    line: 157489
    from_csv_column: HGNC ID
    to_csv_column: Gene stable ID
    value: ENSG00000124766
  list_source:
  - step: transcription_factor/Toronto.1.01:1146[1]
    file: genes/human/lists/transcription_factor/sources/Toronto.1.01.csv
    line: 1146
    csv_column: Ensembl ID
    value: ENSG00000124766
  list_mapping:
  - step: Ensembl.Reference.116:157409[0]
    file: genes/human/namespaces/sources/Ensembl.Reference.116.tsv
    line: 157409
    csv_column: Gene stable ID
    value: ENSG00000124766
  common_mapping: []
```

An empty provenance (`;`) is reported as an empty list (`[]`).

For a mouse gene:

```
$ grep -P '^Sox4\t' genes/mouse/namespaces/names/GeneSymbol.tsv | scripts/expand_provenance.py mouse
- name: Sox4
  ensembl_gene: ENSMUSG00000076431
  name_source:
  - step: MGI.6.29.2026-09-29:21265[13]
    file: genes/mouse/namespaces/sources/MGI.6.29.2026-09-29.tsv
    line: 21265
    csv_column: Current Marker Symbol (if withdrawn)
    value: Sox4
  name_mapping:
  - step: MGI.6.29.2026-09-29:21265[13>12]
    file: genes/mouse/namespaces/sources/MGI.6.29.2026-09-29.tsv
    line: 21265
    from_csv_column: Current Marker Symbol (if withdrawn)
    to_csv_column: Current MGI Accession ID (if withdrawn)
    value: MGI:98366
  - step: Ensembl.MGI.116:21087[1>0]
    file: genes/mouse/namespaces/sources/Ensembl.MGI.116.tsv
    line: 21087
    from_csv_column: MGI ID
    to_csv_column: Gene stable ID
    value: ENSMUSG00000076431
```

The reported `value` is the whole cell, so for a CSV column holding several names (e.g. `Marker Synonyms
(pipe-separated)`) it shows all of them rather than the single one the step matched; that one is the `name` of the
row.

The separators were also chosen so that a step is a jump target in an editor. In vim, given

```
:set path+=genes/human/namespaces/sources,genes/human/lists
:set suffixesadd=.tsv,.csv
:set includeexpr=substitute(v:fname,'/','/sources/','')
```

pressing `gF` on a step opens the source data file at the line. The `includeexpr` maps a step of a list source
(`<list>/<source>`) to its data file in `genes/<species>/lists/<list>/sources`.

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
        * A `lists` sub-directory contains the actual gene lists.
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

* The `names` sub-directory contains, for each namespace, _namespace_`.tsv`. It has a single line for each name. The
  lines are sorted by the `ensembl_gene`, so all the names of each gene are adjacent. The columns are:

  * `name` contains the identifier of the gene in the namespace. For example, `SOX4` is listed in the human
    transcription factors list in the GeneSymbol namespace.

  * `ensembl_gene` contains the identifier of the gene in the EnsemblGene namespace, which was included in the list.
    For example, `ENSG00000124766` for `SOX4`. If the name maps to several such genes, this is the one with the fewest
    provenance steps (and then the smallest identifier).

  * `list_name` contains the name given by the list entry which included the `ensembl_gene` in the list. For example,
    the `SOX4` line of the transcription factors list has the `list_name` `ENSG00000124766`, since the `Toronto.1.01`
    source gives the Ensembl identifier.

  * `name_source` contains the [provenance](#provenance) of the `name`, that is, where it appears in the namespace
    sources. For example, `HGNC.Current.2026-10-06:33501[1]` for `SOX4`.

  * `name_mapping` contains the [provenance](#provenance) of the mapping from the `name` to the `ensembl_gene`, up to
    the `common_mapping`. For example, `HGNC.Current.2026-10-06:33501[1>0];Ensembl.HGNC.116:157489[3>0]` for `SOX4`.

  * `list_source` contains the [provenance](#provenance) of the list entry, that is, where it appears in the list
    sources. For example, `transcription_factor/Toronto.1.01:1146[1]` for `SOX4`. This is line `1146` of the
    `Toronto.1.01` source file of the `transcription_factor` list, in its column `1` (`Ensembl ID`).

  * `list_mapping` contains the [provenance](#provenance) of the mapping from the `list_name` to the `ensembl_gene`, up
    to the `common_mapping`. For example, `Ensembl.Reference.116:157409[0]` for `SOX4`. This verifies that
    `ENSG00000124766` is an active identifier. If the identifier was retired, this also contains the mapping from the
    retired identifier to the active one.

  * `common_mapping` contains the steps which follow both the `name_mapping` and the `list_mapping`. Both mappings
    share these steps, so they are written only once. For example, for `S9` in the human ribosomal list (whose
    `list_name` is `RPS9`), this is
    `HGNC.Current.2026-10-06:29120[1];HGNC.Current.2026-10-06:29120[1>0];Ensembl.HGNC.116:330835[3>0]`, since both `S9`
    and `RPS9` reach the gene via the symbol `RPS9`.

  An empty provenance (such as the `common_mapping` of `SOX4`) is written as `;`.

* To compute the above, we begin with a set of "source of truth" files. These are TSV or CSV files under the `sources`
  sub-directory which have at least one column containing names (of some namespace). Some are manually curated
  (`CURATED.tsv`). Others are fetched from an external source, or derived from a namespace source (see
  [Updates](#updates)). In addition we have a single `sources.yaml` file which contains a sequence of mappings with
  the following keys, as well as a comment describing the source:

  * `data_file` holds the name of the CSV or TSV source data file. It may contain a `{version}` placeholder for the
    version of the source (see [Updates](#updates)).

  * `has_header` is a Boolean specifying whether the data file has a header line (default: `true`).

  * `columns` holds a mapping whose key is the column name (or 0-based index if there are no headers), and whose value
    is a name of a namespace.

  The computed canonical list names are any EnsemblGene identifiers that are agreed on by the identifiers in all the
  columns of each list entry. For other namespaces, these are the identifiers that map to any of these EnsemblGenes.
  This is computed using `scripts/compute_list.py`.

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

* Stored identifiers are "normalized". Each namespace other than GeneSymbol has a pattern for its names (for example,
  `ENSG00000124766` for EnsemblGene). A name in such a namespace must start with the pattern. The pattern may be
  followed by a `.[0-9]` version suffix (in the Ensembl and RefSeq namespaces), and then by junk which contains no
  letters or digits (such as a trailing `;`). Normalizing removes both. In the GeneSymbol namespace, a `.[0-9]` suffix
  is part of the name. For example, `AC092171.3` and `AC092171.5` are different genes. Names which contain white space
  are dropped, since these are descriptions rather than names. To lookup a name in a list or a namespace, you need to
  normalize the query gene name accordingly (see `normalize_gene_name` in Metacells.jl). The case of a name is never
  changed. Names are in mixed case, different in different namespaces; for example, `SOX4` for the human gene and
  `Sox4` for the mouse gene.

* We maintain *directed* mapping between the namespaces, that is, other than aliases that map a namespace to itself, all
  mappings bring us closer towards the EnsemblGene namespace.

To compute all the above, we begin with a set of "source of truth" files. These are TSV or CSV files under the `sources`
sub-directory which have at least two columns containing names, to establish links between names (within the same
namespace or across namespaces).

We use a `sources.yaml` file which contains a sequence of mappings with the following keys, as well as a comment
describing the source:

* `data_file` holds the name of the CSV or TSV source data file. We omit the `.csv` or `.tsv` suffix when we identify
  the source in provenance fields. It may contain a `{version}` placeholder for the version of the source (see
  [Updates](#updates)).

* `has_header` is a Boolean specifying whether the data file has a header line (default: `true`).

* `has_multiple_versions` is a Boolean specifying whether we keep a data file for each version of the source (default:
  `false`). Each of these files is a separate source. Each name in the `from` column of the links is taken only from
  the newest version which has it. We use this for the Ensembl gene names, since Ensembl does not keep their history.

* `older_versions_priority` is the `priority` of the links of all but the newest version of a source which
  `has_multiple_versions` (default: the `priority` of each link).

* `is_reference` is a Boolean specifying whether the EnsemblGenes of the source are the current genes on the reference
  (primary) assembly (default: `false`).

* `links` holds a sequence of directed links between two identifiers. Each is a mapping with the keys `from`, `to` which
  contains a mapping with the following keys:

  * `column` identifies the column containing the identifier, by name (or 0-based index if there is no header line).
    It may also be a list of such columns. These are tried in order until one of them is not empty.
  * `namespace` contains the name of the namespace the identifier belongs to.
  * `separator` is an optional character used to separate multiple identifiers within the column (e.g., `|`).
  * `is_clean` is a Boolean specifying whether the column holds clean names, rather than aliases (default: `true`).

  A link may also have a `priority`, which is an integer (default: `1`). A larger number is a stronger priority.

Links are established either between a namespace and itself (from an alias or renamed identifier to a more current one)
or between a namespace and EnsemblGene (or a namespace closer to EnsemblGene).

In addition to the above, the `sources` sub-directory optionally contains the following:

* _namespace_`.Missing.tsv` contains names and sources we have seen (in some list or data set) that do not exist in any
  of the source files. This is a temporary file which is read and deleted by `scripts/complete_namespaces.py`. This
  happens when a list or a data set uses a name which is not in any of the source files. Note that Ensembl does not
  keep the history of its gene names, so we keep the gene names of all its releases (see `has_multiple_versions`).

* _namespace_`.Extra.tsv` contains data we fetched from web APIs for missing names (using
  `scripts/complete_namespaces.py`). Each line holds the name, its source, the namespace and name it maps to, and the
  URL of the web API call.

* _namespace_`.Ignored.tsv` contains names and sources that we have looked up in the web APIs and couldn't find any data
  for. These names are *not* included in the namespace. Ideally, there shouldn't be any such names. In the best case,
  they are simply typos; in the worst case, these are names that were used once and were lost to history.

To represent the result, in the `names` sub-directory we keep the following files:

* _namespace_`.tsv` has a line for each name and each EnsemblGene it maps to, sorted by the name. The columns are:

  * `name` contains the name of the gene in the namespace. For example, `SOX4`.

  * `ensembl_gene` contains the identifier of the EnsemblGene the name maps to. For example, `ENSG00000124766` for
    `SOX4`.

  * `name_source` contains the [provenance](#provenance) of the name, that is, where it appears in the sources. For
    example, `HGNC.Current.2026-10-06:33501[1]` says that line `33501` of the `HGNC.Current.2026-10-06` source file
    contains `SOX4` in its column `1` (`symbol`).

  * `name_mapping` contains the [provenance](#provenance) of the mapping from the name to the EnsemblGene. For example,
    `HGNC.Current.2026-10-06:33501[1>0];Ensembl.HGNC.116:157489[3>0]` for `SOX4`. Line `33501` of the
    `HGNC.Current.2026-10-06` source file maps `SOX4` (column `1`, `symbol`) to `HGNC:11200` (column `0`, `hgnc_id`).
    Line `157489` of the `Ensembl.HGNC.116` source file then maps `HGNC:11200` (column `3`, `HGNC ID`) to
    `ENSG00000124766` (column `0`, `Gene stable ID`). A mapping may take several steps. For example, a previous symbol
    is first mapped to the current symbol, which is then mapped to the EnsemblGene.

For every name in every namespace, `scripts/compute_namespaces.py` computes the EnsemblGenes it maps to, as follows:

* A name exists only if it appears in a clean column of some source. A column marked `is_clean: false` holds aliases
  which may be descriptions or nicknames (such as the HGNC `alias_symbol` column and the MGI synonyms column). Its links
  are used only for names which also appear in some clean column.

* A name maps to the EnsemblGenes reached by its links to other namespaces. Only if none of these reach an EnsemblGene,
  it maps to the EnsemblGenes reached by its links within its own namespace (such as from a previous symbol to the
  current symbol).

* Among these links, only those with the highest `priority` are used. For example, an HGNC symbol beats a gene name of
  the latest Ensembl release, which beats a previous symbol, which beats a gene name of an older Ensembl release.

* If a name maps to a reference EnsemblGene (see `is_reference` below), it maps only to the reference ones (and not to
  the copies of a gene on alternate haplotypes, or to retired genes).

## Updates

Updating this repository is done by adding new species, namespaces (sources) and lists (sources), and by updating the
external sources to their newer versions.

Each external source is fetched by a script. The script names the data file by the version of the source, using the
versioning scheme of the source itself:

* `scripts/fetch_ensembl.py <species> <first release> <last release>` fetches the Ensembl data, e.g.
  `Ensembl.Reference.116.tsv`. Only the last release of the identifiers and their links is kept. The genes of this
  release are split into `Ensembl.Reference` (the genes on the reference assembly) and `Ensembl.NonReference` (the
  others, such as the copies of a gene on alternate haplotypes). The gene names are kept for all the releases (see
  `has_multiple_versions` above).

* `scripts/fetch_hgnc.sh` fetches the latest monthly HGNC release, e.g. `HGNC.Current.2026-10-06.tsv`.

* `scripts/fetch_mgi.sh` fetches the MGI markers. MGI identifies its data by its release and the date of its database
  update, e.g. `MGI.6.29.2026-09-29.tsv`.

* `scripts/fetch_scenic.sh <species>` and `scripts/fetch_toronto.py` fetch the transcription factor lists.

Each fetch script replaces the previous version of the data file. The `sources.yaml` files refer to the data files
using the `{version}` placeholder, so they do not change. Some list sources are derived from a namespace source by
`scripts/derive_<species>_<list>.py`. The derived data file has the same name (and version) as the namespace source
data file. Invoking `make` re-derives it when the namespace sources change.

Everything is rebuilt by invoking `make` at the top-level directory. If any of the added data refers to missing gene
names, you will have to re-run `make` again to update the namespaces based on the recomputed `Extra` files. To be
certain just re-run `make` until it says `Nothing to be done`.
