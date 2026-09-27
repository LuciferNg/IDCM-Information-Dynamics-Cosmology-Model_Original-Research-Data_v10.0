#!/usr/bin/env bash
# O130 -- download DESI DR1 official clustering measurements (xi(s) poles + windows)
# Source: data.desi.lbl.gov/public/dr1/vac/dr1/full-shape-bao-clustering/v1.0/data/recsym/correlation/
set -u
BASE="https://data.desi.lbl.gov/public/dr1/vac/dr1/full-shape-bao-clustering/v1.0/data/recsym/correlation"
DEST="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o130_wavelet_analysis_tools/data/desi"
mkdir -p "$DEST"
cd "$DEST"

TRACERS="BGS_BRIGHT-21.5_GCcomb_z0.1-0.4 ELG_LOPnotqso_GCcomb_z1.1-1.6 LRG%2BELG_LOPnotqso_GCcomb_z0.8-1.1 LRG_GCcomb_z0.4-0.6 LRG_GCcomb_z0.6-0.8 LRG_GCcomb_z0.8-1.1 QSO_GCcomb_z0.8-2.1"

for t in $TRACERS; do
  for pre in "correlation-recsym-poles" "window_correlation-recsym-poles"; do
    f="${pre}_${t}.h5"
    [ -s "$f" ] && { echo "skip $f"; continue; }
    curl -fsSL --max-time 120 -o "$f" "$BASE/$f" && echo "ok   $f ($(stat -c%s "$f") bytes)" || echo "FAIL $f"
  done
done
curl -fsSL --max-time 60 -o dr1_vac_recsym_correlation.sha256sum "$BASE/dr1_vac_dr1_full-shape-bao-clustering_v1.0_data_recsym_correlation.sha256sum" && echo "ok   sha256sum"
echo "--- files ---"
ls -la *.h5 2>/dev/null | awk '{print $5, $9}'
