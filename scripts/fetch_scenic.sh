#!/bin/bash
# Usage: fetch_scenic.sh species
# Fetch the latest SCENIC list of transcription factors into the species list sources, replacing the previous one.
set -euo pipefail

SPECIES=$1
case $SPECIES in
human) FILE_NAME=allTFs_hg38.txt;;
mouse) FILE_NAME=allTFs_mm.txt;;
esac
URL=https://resources.aertslab.org/cistarget/tf_lists/$FILE_NAME
SOURCES_DIR=genes/$SPECIES/lists/transcription_factor/sources

# SCENIC does not version these lists, so we use the date the file was last modified on the server.
LAST_MODIFIED=`curl -sS --fail -I $URL | grep -i '^last-modified:' | sed 's/^[^:]*: //' | tr -d '\r'`
VERSION=`date -u -d "$LAST_MODIFIED" +%Y-%m-%d`
echo "Fetch SCENIC $SPECIES $VERSION ..."

rm -f $SOURCES_DIR/SCENIC.[0-9]*.tsv
curl -sS --fail -o $SOURCES_DIR/SCENIC.$VERSION.tsv $URL
