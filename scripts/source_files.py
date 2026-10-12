import os
import re
import yaml

# The `data_file` of a source in a sources YAML file may contain a `VERSION` placeholder. It stands for the version of
# the source data, as it appears in the file name. The name of the source includes the version, so the provenance says
# which version of the source data was used.
#
# Normally a single file matches. Updating the source replaces this file with a newer one, and the sources YAML file
# stays the same. A source which `has_multiple_versions` keeps a file for each version. Each of these files is a
# separate source. Each name in the `from` column of their links is taken only from the newest version which has it,
# since a newer version knows better what the name refers to.

VERSION = "{version}"

VERSION_PATTERN = r"[0-9][0-9.-]*"

def matching(sources_dir, data_file):
    """
    Return the names of the files in ``sources_dir`` which match the ``data_file`` of a source, ordered by version.
    """
    if VERSION not in data_file:
        return [data_file]
    prefix, suffix = data_file.split(VERSION)
    pattern = re.compile(f"{re.escape(prefix)}({VERSION_PATTERN}){re.escape(suffix)}")
    versions = {}
    for name in os.listdir(sources_dir):
        match = pattern.fullmatch(name)
        if match:
            versions[name] = [int(part) for part in re.split(r"[.-]", match.group(1)) if part != ""]
    return sorted(versions, key = lambda name: (versions[name], name))

def single(sources_dir, data_file):
    """
    Return the name of the single file in ``sources_dir`` which matches the ``data_file`` of a source.
    """
    data_files = matching(sources_dir, data_file)
    assert len(data_files) == 1, f"Expected a single version of: {sources_dir}/{data_file}: {' '.join(data_files)}"
    return data_files[0]

def write_derived(sources_dir, data_file, version_file, rows):
    """
    Write a source of a list in ``sources_dir``, derived from the ``version_file`` of a namespace source, whose
    ``data_file`` contains the ``VERSION`` placeholder. The derived source has the same name as the ``version_file``,
    and replaces any other version of it. Each of the ``rows`` holds a gene name, the identifier of the gene in the
    source data, and the provenance of the source data it was derived from. They are written sorted by the name,
    ignoring case.
    """
    for old_file in matching(sources_dir, data_file):
        if old_file != version_file:
            print(f"Remove {sources_dir}/{old_file} ...", flush = True)
            os.remove(f"{sources_dir}/{old_file}")
    path = f"{sources_dir}/{version_file}"
    print(f"Write {path} ...", flush = True)
    with open(path, "w") as file:
        for name, identifier, source in sorted(rows, key = lambda row: (str.casefold(row[0]), row)):
            print(f"{name}\t{identifier}\t{source}", file = file)

def load_specs(sources_dir):
    """
    Return the source specifications of the sources YAML file in ``sources_dir``. The ``data_file`` of a specification
    must match a single file, unless it ``has_multiple_versions``, in which case the specification is repeated for each
    of the files which match it, newest first. Each returned specification also holds the original ``data_file`` (with
    the ``VERSION`` placeholder) as its ``versions_data_file``, and whether it ``is_newest_version``.
    """
    with open(f"{sources_dir}/sources.yaml") as file:
        sources_spec = yaml.safe_load(file)

    specs = []
    for source_spec in sources_spec:
        data_files = matching(sources_dir, source_spec["data_file"])
        assert len(data_files) > 0, f"No data files match: {sources_dir}/{source_spec['data_file']}"
        assert len(data_files) == 1 or source_spec.get("has_multiple_versions", False), \
            f"Multiple versions of: {sources_dir}/{source_spec['data_file']}: {' '.join(data_files)}"
        for index, data_file in enumerate(reversed(data_files)):
            specs.append({
                **source_spec,
                "data_file": data_file,
                "versions_data_file": source_spec["data_file"],
                "is_newest_version": index == 0,
            })
    return specs
