#!/usr/bin/env python3
"""
下載 COSMOS2015 星系質量函數 (Davidzon+2017, A&A 605, A70)
來源: VizieR J/A+A/605/A70
"""
from astroquery.vizier import Vizier
import pandas as pd
import os

os.makedirs("data/obs_data", exist_ok=True)
Vizier.ROW_LIMIT = -1

print("="*78)
print("COSMOS2015 質量函數下載 (Davidzon+2017)")
print("="*78)

# 嘗試多個目錄
catalogs = [
    "J/A+A/605/A70",       # Davidzon+2017 (COSMOS2015)
    "J/A+A/605/A70/gsmf",  # 質量函數表
    "J/A+A/605/A70/gmf",   # 質量函數表 (另一命名)
    "J/A+A/605/A70/table1",
    "J/A+A/605/A70/table2",
    "J/A+A/605/A70/table3",
    "J/A+A/605/A70/table4",
    "J/A+A/605/A70/table5",
    "J/A+A/605/A70/table6",
]

for cat in catalogs:
    try:
        print(f"\n嘗試: {cat}")
        tbl = Vizier.get_catalogs(cat)
        if tbl and len(tbl) > 0:
            print(f" ✅ 成功! 找到 {len(tbl)} 個表格")
            for i, t in enumerate(tbl):
                df = t.to_pandas()
                print(f"   表 {i}: {len(df)} 行, 欄位: {list(df.columns)[:10]}")
                out = f"data/obs_data/cosmos2015_{cat.replace('/', '_')}_t{i}.csv"
                df.to_csv(out, index=False)
                print(f"   已存: {out}")
        else:
            print(f" ❌ 冇數據")
    except Exception as e:
        print(f" ❌ {type(e).__name__}: {str(e)[:80]}")

# 嘗試搜尋
print("\n\n--- 搜尋 COSMOS2015 相關目錄 ---")
try:
    result = Vizier.find_catalogs("COSMOS2015 Davidzon 2017 stellar mass function")
    for k, v in result.items():
        print(f"  {k}: {v.description[:100] if hasattr(v,'description') else '?'}")
except Exception as e:
    print(f"搜尋失敗: {e}")

print("\n完成!")