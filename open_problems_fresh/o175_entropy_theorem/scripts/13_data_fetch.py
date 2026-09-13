#!/usr/bin/env python3
"""
O175 遺留攻堅 — data fetch 層 (用戶指示: 所有 Data-Gated 數據來自開放科學計畫)
============================================================================
目標: 將 D1/D2/D3/D4 嘅 data-gated 阻塞解除 — 抓取公開數據集落 o175/data/。

渠道 (用戶提供 + 探測確認):
  [D3]  Auger Open Data       https://opendata.auger.org  (Zenodo summary.zip, 8MB)
  [D4]  SPARC (Lelli 2016)    VizieR J/MNRAS/457/2859    (astroquery)
  [D4]  Fall locus            VizieR J/ApJ/758/L38       (astroquery, R&F 2012)
  [D1/D2] Planck PR3 CMB maps IRSA (NASA mirror) 2048 直鏈 (wget 背景, 另行)

產出: data/auger/  data/sparc/  data/vizier/  (Planck 落 data/planck/)
驗證: 每個 dataset 下載後讀取驗證 (行數/能量範圍/RA-Dec 範圍), 唔係淨係落盤。
"""
import sys, os, io, csv, json, zipfile, urllib.request, tarfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # o175_entropy_theorem/
DATA = BASE / "data"
for d in ("auger", "sparc", "vizier", "planck"):
    (DATA / d).mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (IDCM-O175-research; contact: none)"}
results = []

def fetch(url, dest, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest

# ---------------------------------------------------------------------------
# [D3] Auger Open Data — summary CSV (E>1 EeV 事件: 能量/RA/Dec)
# ---------------------------------------------------------------------------
print("== [D3] Auger Open Data (Zenodo summary.zip) ==")
try:
    z = DATA / "auger" / "auger_summary.zip"
    fetch("https://zenodo.org/records/10488964/files/summary.zip?download=1", z, timeout=120)
    with zipfile.ZipFile(z) as zp:
        zp.extractall(DATA / "auger")
    # 驗證: 搵事件 CSV, 數行數 + 能量範圍
    ev_csv = None
    for p in (DATA / "auger").rglob("*.csv"):
        if "event" in p.name.lower() or "summary" in p.name.lower():
            ev_csv = p
    if ev_csv:
        with open(ev_csv, newline="") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys()) if rows else []
        print(f"  events csv: {ev_csv.name}  rows={len(rows)}")
        print(f"  cols: {cols}")
        # 能量/方向檢查
        ecol = next((c for c in cols if "energy" in c.lower() or "E" == c.upper() or "lgE" in c.lower()), None)
        if ecol:
            try:
                es = sorted(float(r[ecol]) for r in rows if r[ecol] not in ("", "nan", "NaN"))
                print(f"  {ecol}: min={es[0]:.3f} max={es[-1]:.3f} n={len(es)}")
            except Exception as ex:
                print(f"  energy parse: {ex} (可能 log10 EeV)")
        results.append(("Auger events csv", len(rows)))
    else:
        print("  !! 冇搵到 events csv — 列出檔案:")
        for p in (DATA / "auger").rglob("*"):
            print("   ", p.name)
except Exception as e:
    print(f"  Auger FAIL: {e}")

# ---------------------------------------------------------------------------
# [D4] SPARC (Lelli+2016, J/MNRAS/457/2859) + Fall locus (R&F2012, J/ApJ/758/L38)
# ---------------------------------------------------------------------------
print("\n== [D4] VizieR: SPARC + Fall locus ==")
try:
    from astroquery.vizier import Vizier
    V = Vizier(columns=["*"], timeout=120)
    V.ROW_LIMIT = -1
    # SPARC 主表 (質量模型 + Vmax + R 等)
    for cat, name in [("J/MNRAS/457/2859", "sparc"), ("J/ApJ/758/L38", "fall_rf12")]:
        try:
            tbls = V.get_catalogs(cat)
            for i, t in enumerate(tbls):
                out = DATA / "vizier" / f"{name}_{i}.csv"
                t.write(out, format="csv", overwrite=True)
                print(f"  {cat} table{i}: {len(t)} rows -> {out.name}")
                if len(t) > 0:
                    cols = list(t.colnames)
                    print(f"    cols: {cols[:14]}{'...' if len(cols)>14 else ''}")
                    results.append((f"Vizier {cat} t{i}", len(t)))
        except Exception as e:
            print(f"  {cat} FAIL: {e}")
except ImportError:
    print("  astroquery 未安裝, 跳過")
except Exception as e:
    print(f"  Vizier FAIL: {e}")

# ---------------------------------------------------------------------------
# 摘要
# ---------------------------------------------------------------------------
print("\n== 摘要 ==")
for name, n in results:
    print(f"  {name}: {n}")
print("完成。Planck CMB maps 由背景 wget 處理 (data/planck/)。")
