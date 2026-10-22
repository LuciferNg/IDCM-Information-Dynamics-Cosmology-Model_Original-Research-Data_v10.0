#!/usr/bin/env python3
"""
O32-35: 自動化觀測數據下載 — astroquery VizieR
================================================
從 VizieR 下載 GAMA 星系質量函數原始數據
用於 IDCM 預言嘅 χ² 實證檢驗

來源: Wright et al. 2017, MNRAS 470, 2839
     (GAMA: Galaxy stellar mass function to z=0.1)
"""
import os
import sys
import pandas as pd
from astroquery.vizier import Vizier

DATA_DIR = "data/obs_data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_catalog(catalog_id, name, vizier=Vizier):
    """下載 VizieR 目錄並保存為 CSV"""
    print(f"\n--- 下載 {name} ({catalog_id}) ---")
    vizier.ROW_LIMIT = -1
    try:
        tables = vizier.get_catalogs(catalog_id)
        print(f"找到 {len(tables)} 個表格")
        for i, table in enumerate(tables):
            # 轉換為 pandas DataFrame
            df = table.to_pandas()
            out_path = f"{DATA_DIR}/{name}_{i}.csv"
            df.to_csv(out_path, index=False)
            print(f"  Table {i}: {len(df)} 行, 欄位: {list(df.columns)}")
            print(f"  → 已存: {out_path}")
        return tables
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        return None

# ===== 1. GAMA 星系質量函數 (Wright+2017) =====
# 論文: J/MNRAS/470/2839 (MNRAS 470, 2839)
# 備用: J/MNRAS/421/959 (Baldry+2012, GAMA-I)
print("="*78)
print("GAMA 星系質量函數數據下載")
print("="*78)

# 嘗試主要目錄
for cat_id in ["J/MNRAS/470/2839", "J/MNRAS/421/959", "J/MNRAS/421/959/gsmf"]:
    print(f"\n嘗試: {cat_id}")
    Vizier.ROW_LIMIT = -1
    try:
        tables = Vizier.get_catalogs(cat_id)
        if tables:
            print(f"✅ 成功! {len(tables)} 個表格")
            for i, table in enumerate(tables):
                df = table.to_pandas()
                out_path = f"{DATA_DIR}/gama_gsmf_{i}.csv"
                df.to_csv(out_path, index=False)
                print(f"  Table {i}: {len(df)} 行, {list(df.columns)}")
            break
    except Exception as e:
        print(f"  ❌ {e}")
        continue

# ===== 2. VizieR 搜尋 GAMA 質量函數 =====
print("\n" + "="*78)
print("VizieR 搜尋: GAMA + GSMF")
print("="*78)
Vizier.ROW_LIMIT = 10
try:
    result = Vizier.find_catalogs("GAMA galaxy stellar mass function")
    for k, v in result.items():
        print(f"  {k}: {v.description}")
except Exception as e:
    print(f"  ❌: {e}")

# ===== 3. 列出所有可用目錄 =====
print("\n" + "="*78)
print("可用 GAMA 相關目錄")
print("="*78)
try:
    result = Vizier.find_catalogs("GAMA galaxy mass function")
    for k, v in list(result.items())[:5]:
        print(f"  {k}: {v.description}")
except Exception as e:
    print(f"  ❌: {e}")

# ===== 4. 試下用 ASCII 格式直接下載 =====
print("\n" + "="*78)
print("嘗試 ASCII TSV 直接下載")
print("="*78)
import requests
for cat_url in [
    "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/MNRAS/470/2839",
    "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/MNRAS/421/959",
]:
    try:
        r = requests.get(cat_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code == 200 and len(r.text) > 100:
            name = cat_url.split("=")[-1].replace("/", "_")
            with open(f"{DATA_DIR}/raw_{name}.tsv", "w") as f:
                f.write(r.text)
            print(f"✅ {name}: {len(r.text)} 字元, 行數: {r.text.count(chr(10))}")
        else:
            print(f"❌ {cat_url}: status {r.status_code}")
    except Exception as e:
        print(f"❌ {cat_url}: {e}")

print("\n" + "="*78)
print("下載完成!")
print("="*78)
print(f"數據目錄: {DATA_DIR}/")
for f in sorted(os.listdir(DATA_DIR)):
    fpath = os.path.join(DATA_DIR, f)
    size = os.path.getsize(fpath)
    print(f"  {f} ({size} bytes)")