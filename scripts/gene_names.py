import re

# The namespaces whose names have no pattern.
FREE_FORM_NAMESPACES = ("GeneSymbol",)

# The pattern of the names in each of the other namespaces.
NAMESPACE_PATTERNS = {
    "EnsemblGene": r"(ENS[A-Z]*G|ASMPATCHG)[0-9]{11}",
    "EnsemblTranscript": r"(ENS[A-Z]*T|ASMPATCHT)[0-9]{11}",
    "EnsemblProtein": r"(ENS[A-Z]*P|ASMPATCHP)[0-9]{11}",
    "HGNC": r"HGNC:[0-9]+",
    "MGI": r"MGI:[0-9]+",
    "RefSeq": r"(NM|NR|NP|XM|XR|XP|YP)_[0-9]+",
    "UCSC": r"uc[0-9]{3}[a-z]{3}\.[0-9]+",
}

# The namespaces whose names may carry a `.<version>` suffix, which is not part of the identity of the gene. In all the
# other namespaces, a `.` is part of the name. For example, `AC092171.3` and `AC092171.5` are different genes.
VERSIONED_NAMESPACES = ("EnsemblGene", "EnsemblTranscript", "EnsemblProtein", "RefSeq")

# A name in a namespace with a pattern is the pattern, then a `.<version>` suffix in the `VERSIONED_NAMESPACES`, then
# junk which contains no letters or digits (such as a trailing `;`). Only the pattern is the actual name.
NAMESPACE_REGEXES = {
    namespace_name: re.compile(
        f"({pattern})" + (r"(\.[0-9]+)?" if namespace_name in VERSIONED_NAMESPACES else "") + r"[^A-Za-z0-9]*"
    )
    for namespace_name, pattern in NAMESPACE_PATTERNS.items()
}

def normalize_name(namespace_name, name):
    """
    Return the normalized ``name`` of a gene in ``namespace_name``. This strips surrounding white space, and converts
    ``NULL`` and ``\\N`` to an empty name. In a namespace with a pattern, it also removes the ``.<version>`` suffix
    and the trailing junk, and asserts that the rest matches the pattern. The namespace must be known.
    """
    assert namespace_name in FREE_FORM_NAMESPACES or namespace_name in NAMESPACE_REGEXES, \
        f"Unknown namespace: {namespace_name}"
    name = name.strip()
    if name == "" or name.upper() in ("NULL", "\\N"):
        return ""
    if namespace_name in FREE_FORM_NAMESPACES:
        return name
    match = NAMESPACE_REGEXES[namespace_name].fullmatch(name)
    assert match is not None, f"Invalid {namespace_name} name: {name}"
    return match.group(1)
