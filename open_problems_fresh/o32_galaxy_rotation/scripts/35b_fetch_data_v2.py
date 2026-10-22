#!/usr/bin/env python3
"""
O32-35b: astroquery VizieR 數據下載 v2
========================================
嘗試 GAMA DR3 同其他可用目錄
"""
import os
import pandas as pd
from astroquery.vizier import Vizier

DATA_DIR = "data/obs_data"
os.makedirs(DATA_DIR, exist_ok=True)
Vizier.ROW_LIMIT = -1

# GAMA DR3 (Baldry+ 2018, J/MNRAS/474/3875)
# 包含 galaxy property catalog
print("="*78)
print("GAMA DR3 數據下載 (Baldry+ 2018)")
print("="*78)
try:
    tables = Vizier.get_catalogs("J/MNRAS/474/3875")
    print(f"找到 {len(tables)} 個表格")
    for i, t in enumerate(tables):
        df = t.to_pandas()
        out = f"{DATA_DIR}/gama_dr3_{i}.csv"
        df.to_csv(out, index=False)
        print(f"  Table {i}: {len(df)} 行, 欄位: {list(df.columns)[:10]}...")
        print(f"  → {out}")
except Exception as e:
    print(f"  ❌: {e}")

# 試 GAMA DR4 (J/MNRAS/513/439)
print("\n" + "="*78)
print("GAMA DR4 數據 (Driver+ 2022)")
print("="*78)
try:
    tables = Vizier.get_catalogs("J/MNRAS/513/439")
    print(f"找到 {len(tables)} 個表格")
    for i, t in enumerate(tables):
        df = t.to_pandas()
        out = f"{DATA_DIR}/gama_dr4_{i}.csv"
        df.to_csv(out, index=False)
        print(f"  Table {i}: {len(df)} 行, 欄位: {list(df.columns)[:10]}...")
        print(f"  → {out}")
except Exception as e:
    print(f"  ❌: {e}")

# 試 Baldry+2012 GAMA GSMF (J/MNRAS/421/959)
print("\n" + "="*78)
print("GAMA GSMF (Baldry+ 2012)")
print("="*78)
try:
    tables = Vizier.get_catalogs("J/MNRAS/421/959")
    print(f"找到 {len(tables)} 個表格")
    for i, t in enumerate(tables):
        df = t.to_pandas()
        out = f"{DATA_DIR}/gama_gsmf_baldry_{i}.csv"
        df.to_csv(out, index=False)
        print(f"  Table {i}: {len(df)} 行, 欄位: {list(df.columns)}")
        print(f"  → {out}")
except Exception as e:
    print(f"  ❌: {e}")

# 報告
print("\n" + "="*78)
print("下載結果")
print("="*78)
for f in sorted(os.listdir(DATA_DIR)):
    fpath = os.path.join(DATA_DIR, f)
    print(f"  {f} ({os.path.getsize(fpath)} bytes)")