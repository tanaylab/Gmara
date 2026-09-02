import re

# Provenance records where a piece of data came from, as a sequence of steps joined by `JOIN`. Each step is written
# as `<source>:<line>[<csv_columns>]`, where `<source>` is the name of a source data file (without its suffix),
# `<line>` is the 1-based number of the line in it, and `<csv_columns>` are the 0-based indices of the CSV columns of
# that line the data was taken from: a single index, two indices around `LINK` for a link from one CSV column to
# another, and `ALTERNATIVE`-separated indices for CSV columns which are tried in order until one is not empty.
#
# For example, `HGNC.Current:37136[1>0]` says that line 37136 of `HGNC.Current.tsv` links the value of its CSV column
# 1 to the value of its CSV column 0. The CSV columns are identified by index rather than by name to keep the
# provenance small; their names are in the header line of the source data file itself.
#
# The separators are all outside vim's default `isfname`, so that `gF` on a step opens the source data file at the
# line, given `set path+=genes/<species>/namespaces/sources` and `set suffixesadd=.tsv`.

JOIN = ";"
LINK = ">"
ALTERNATIVE = "|"

STEP = re.compile(r"([\w./-]+):([0-9]+)\[([0-9|>]+)\]")

def step(source_name, line, csv_columns):
    """
    Return the provenance step naming the ``line`` of the source data file ``source_name``, in its ``csv_columns``.
    """
    return f"{source_name}:{line}[{csv_columns}]"

def origin(source_name, csv_columns):
    """
    Return a reference to the ``csv_columns`` of the source data file ``source_name``, without naming a line in it.

    This is used for the `Missing` and `Ignored` files, whose entries outlive the line they were seen in - the list
    sources are hand-edited, so by the time anyone reads the entry the line holds some other gene. It is also used
    for data sets which are not in this repository at all, and so have no line to point at.
    """
    return f"{source_name}[{csv_columns}]"

def link(from_csv_columns, to_csv_columns):
    """
    Return the CSV columns of a provenance step which links the ``from_csv_columns`` to the ``to_csv_columns``.
    """
    return f"{from_csv_columns}{LINK}{to_csv_columns}"

def columns_of(frame, column):
    """
    Return the CSV columns of a provenance step for the source data ``frame`` ``column``, as it is specified in the
    sources YAML file - either a single CSV column (by name, or by index if the file has no header line), or a list
    of alternative such CSV columns.
    """
    if isinstance(column, list):
        return ALTERNATIVE.join(str(frame.columns.get_loc(alternative)) for alternative in column)
    return str(frame.columns.get_loc(column))

def value_indices(csv_columns):
    """
    Return the indices of the source data file CSV columns which may hold the value a provenance step arrived at, to
    be tried in order until one of them is not empty.

    For a link, these are the CSV columns it links to, since these are the ones holding the value.
    """
    if LINK in csv_columns:
        csv_columns = csv_columns.split(LINK)[1]
    return [int(index) for index in csv_columns.split(ALTERNATIVE)]
