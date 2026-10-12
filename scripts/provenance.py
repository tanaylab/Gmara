import re

# Provenance records where a piece of data came from, as a sequence of steps joined by `JOIN`. Each step is written
# as `<source>:<line>[<csv_columns>]`, where `<source>` is the name of a source data file (without its suffix),
# `<line>` is the 1-based number of the line in it, and `<csv_columns>` are the 0-based indices of the CSV columns of
# that line the data was taken from: a single index, or two indices around `LINK` for a link from one CSV column to
# another.
#
# For example, `HGNC.Current.2026-10-06:33501[1>0]` says that line 33501 of `HGNC.Current.2026-10-06.tsv` links the
# value of its CSV column 1 to the value of its CSV column 0. The CSV columns are identified by index rather than by
# name to keep the provenance small; their names are in the header line of the source data file itself. The source of
# a list is prefixed by the name of the list (`<list>/<source>`).
#
# The separators are all outside vim's default `isfname`, so that `gF` on a step opens the source data file at the
# line, given the vim settings in the README.

JOIN = ";"
LINK = ">"

STEP = re.compile(r"([\w./-]+):([0-9]+)\[([0-9>]+)\]")

def step(source_name, line, csv_columns):
    """
    Return the provenance step naming the ``line`` of the source data file ``source_name``, in its ``csv_columns``.
    """
    return f"{source_name}:{line}[{csv_columns}]"

def count_steps(source_name):
    """
    Return the number of steps in the provenance ``source_name``.
    """
    return source_name.count(JOIN) + 1

def join_steps(steps):
    """
    Return the provenance consisting of the ``steps``. If there are no steps, this is a lone ``JOIN``, so that a field
    holding it is never empty.
    """
    if len(steps) == 0:
        return JOIN
    return JOIN.join(steps)

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

def csv_column_of(frame, column):
    """
    Return the CSV column of a provenance step for the source data ``frame`` ``column``, as it is specified in the
    sources YAML file (by name, or by index if the file has no header line).
    """
    return str(frame.columns.get_loc(column))

def value_index(csv_columns):
    """
    Return the index of the source data file CSV column which holds the value a provenance step arrived at. For a link,
    this is the CSV column it links to.
    """
    if LINK in csv_columns:
        csv_columns = csv_columns.split(LINK)[1]
    return int(csv_columns)
