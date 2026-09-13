#!/usr/bin/env python3
"""O176 - Parse Kocevski+2025 (arXiv:2510.07376) 70-source table to CSV.
Parses the table from the cached HTML extraction. Output: data/kocevski25_70agn.csv
"""
import re, os, csv

CACHE = "/home/wsl/.hermes/cache/web/arxiv.org-5a63c6e35f.md"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "kocevski25_70agn.csv")

with open(CACHE) as f:
    text = f.read()

# Rows look like: | CEERS 746 | 214.809142 | 52.868484 | 5.624 | ... | 7.19-0.13+0.11{...} | 7.99±0.37{...} | 1 |
# Extract: ID (col1), z (col4), logMBH central (col7), logM* (col8), LRD (col9)
rows = []
for line in text.splitlines():
    if not line.strip().startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 9:
        continue
    ident, ra, dec, z, fha, fwhm, mbh, mstar, lrd = cells[:9]
    # skip header/separator rows
    if ident in ("ID", "---") or not re.match(r"[A-Z]", ident):
        continue
    # central value of logMBH: first float in cell
    m = re.search(r"(-?\d+\.?\d*)", mbh)
    if not m:
        continue
    logmbh = float(m.group(1))
    # logM*: could be upper limit "<< X" or value "X±Y"
    mu = re.search(r"<<\s*(-?\d+\.?\d*)", mstar)
    mst = re.search(r"(-?\d+\.?\d*)", mstar)
    if mu:
        logmstar, is_ul = float(mu.group(1)), True
    elif mst:
        logmstar, is_ul = float(mst.group(1)), False
    else:
        continue
    try:
        zf = float(re.search(r"(-?\d+\.?\d*)", z).group(1))
    except AttributeError:
        continue
    lrd_flag = 1 if lrd.startswith("1") else 0
    rows.append([ident, zf, logmbh, logmstar, is_ul, lrd_flag])

# dedupe by (ident, z)
seen = set()
uniq = []
for r in rows:
    key = (r[0], r[1])
    if key in seen:
        continue
    seen.add(key)
    uniq.append(r)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "z", "logMBH", "logMstar", "Mstar_is_upperlimit", "LRD"])
    w.writerows(uniq)

print(f"parsed {len(uniq)} unique sources -> {OUT}")
n_lrd = sum(1 for r in uniq if r[5])
n_nonlrd = len(uniq) - n_lrd
print(f"LRD: {n_lrd}, non-LRD: {n_nonlrd}")
for lo, hi, label in [(3,4,"3-4"),(4,5,"4-5"),(5,6,"5-6"),(6,7,"6-7")]:
    bin_rows = [r for r in uniq if lo <= r[1] < hi]
    bl = sum(1 for r in bin_rows if r[5])
    print(f"z={label}: {len(bin_rows)} sources ({bl} LRD)")
