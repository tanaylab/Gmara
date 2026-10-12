#!/bin/bash
# Usage: fetch_mgi.sh
# Fetch the latest MGI markers report into the mouse namespace sources, replacing the previous one.
set -euo pipefail

HOME_URL=https://www.informatics.jax.org/
REPORT_URL=https://www.informatics.jax.org/downloads/reports/MRK_List1.rpt
SOURCES_DIR=genes/mouse/namespaces/sources

# MGI identifies its data by the release and the date of the (weekly) database update, e.g. `6.29.2026-09-29`.
STATUS=`curl -sS --fail $HOME_URL | sed 's/<[^>]*>/ /g' | tr -s ' \n' ' ' | grep -o 'last database update [0-9/]* MGI [0-9.]*'`
RELEASE=`echo "$STATUS" | sed 's/.* MGI //'`
DATE=`echo "$STATUS" | sed 's/last database update \([0-9]*\)\/\([0-9]*\)\/\([0-9]*\) .*/\3-\1-\2/'`
VERSION=$RELEASE.$DATE
echo "Fetch MGI $VERSION ..."

rm -f $SOURCES_DIR/MGI.[0-9]*.tsv
curl -sS --fail -o $SOURCES_DIR/MGI.$VERSION.tsv $REPORT_URL
