#!/bin/sh
# Downloads the Sanskrit source texts from sanskritdocuments.org (not stored in this repo).
set -e
cd "$(dirname "$0")"
B=https://sanskritdocuments.org
for f in durga700 tantradurgA700 deviiatharva siddhakunjikaa prAdhAnikarahasyam vaikRitikarahasyam mUrtirahasyam; do
  curl -fsS -o "$f.itx" "$B/doc_devii/$f.itx"
done
curl -fsS -o rAtrisUktam.itx "$B/doc_veda/rAtrisUktam.itx"
echo "Sources downloaded."
