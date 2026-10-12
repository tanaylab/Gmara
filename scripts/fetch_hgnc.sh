#!/bin/bash
# Usage: fetch_hgnc.sh
# Fetch the latest monthly HGNC release into the human namespace sources, replacing the previous one.
set -euo pipefail

ARCHIVE_URL=https://storage.googleapis.com/public-download-files/hgnc/archive/archive/monthly/tsv
LISTING_URL="https://storage.googleapis.com/storage/v1/b/public-download-files/o?prefix=hgnc/archive/archive/monthly/tsv/hgnc_complete_set_&fields=items(name)"
SOURCES_DIR=genes/human/namespaces/sources

VERSION=`curl -sS --fail "$LISTING_URL" | grep -o 'hgnc_complete_set_[0-9-]*\.txt' | sed 's/hgnc_complete_set_//;s/\.txt//' | sort | tail -1`
echo "Fetch HGNC $VERSION ..."

rm -f $SOURCES_DIR/HGNC.Current.[0-9]*.tsv $SOURCES_DIR/HGNC.Withdrawn.[0-9]*.tsv
curl -sS --fail -o $SOURCES_DIR/HGNC.Current.$VERSION.tsv $ARCHIVE_URL/hgnc_complete_set_$VERSION.txt
# Remove `@`, shorten `Entry Withdrawn` to `Withdrawn`, and keep only the HGNC ID of each merged-into report.
curl -sS --fail $ARCHIVE_URL/withdrawn_$VERSION.txt \
| sed 's/@//g;s/Entry Withdrawn/Withdrawn/g;s/|[^ ,]*//g' > $SOURCES_DIR/HGNC.Withdrawn.$VERSION.tsv
