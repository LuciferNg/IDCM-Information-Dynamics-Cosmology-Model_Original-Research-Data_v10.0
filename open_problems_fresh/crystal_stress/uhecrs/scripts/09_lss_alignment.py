#!/usr/bin/env python3
"""
路線 2: DESI / Euclid 大尺度結構 — A₅ 網格對齊檢驗
=====================================================
物理邏輯 (Gemini):
  如果 A₅ 網格係空間骨架, 巨型空洞中心 + 星系團高密度節點
  應該強烈對齊於 120 條大圓弧 (60 節點嘅邊投影)。

IDCM 結構預測:
  1. 空洞中心 (Void Centers) 分佈:
     - 空洞中心應該避開 60 節點 (節點 = 物質凝聚 = 唔係空洞!)
     - 空洞中心應該傾向喺 32 條阻挫邊附近 (應力集中 → 物質被抽走?)
  2. 星系團 (Clusters) 分佈:
     - 星系團高密度節點應該對齊 60 A₅ 節點投影
     - 投影 = 天球上嘅 60 點 + 120 條大圓弧
  3. 統計量:
     - 空洞中心到最近節點嘅角距離 (期望 > 隨機)
     - 星系團到最近節點嘅角距離 (期望 < 隨機)
     - 大圓弧相關: 星系分佈沿 120 條大圓嘅過量

數據 (公開):
  - DESI DR1 (2025-01): 1900 萬天體, 完整光譜
  - DESI DR2 (2026-06 剛發布?): 更多天體
  - SDSS: 已公開空洞目錄 (e.g. Wang et al. 2023)
  - Euclid Q1: 2025-03 公開

呢個 script: 框架 + 用 SDSS 空洞目錄做初步 (如果搵到公開數據)
"""
import math, os, json

phi = (1 + 5**0.5)/2
eps = (1/phi)/4

print("="*70)
print("DESI 大尺度結構 — A₅ 網格對齊檢驗框架")
print("="*70)

# ============ 1. 節點/邊幾何 ============
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
edges = []
with open(os.path.join(CMB_DATA, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        edges.append(((float(p[4]), float(p[5])), (float(p[6]), float(p[7]))))

print(f"節點: {len(nodes)}, 阻挫邊: {len(edges)}")

# 120 條邊 = 全部 A₅ 邊 (唔止阻挫邊) — 需要完整邊列表
# 而家有 32 條阻挫邊; 完整 120 條邊喺 faces.txt / 其他 cmb 數據
print(f"注意: 完整 A₅ 有 120 條邊, 而家只有 32 條阻挫邊")
print(f"→ 完整邊列表需要從 60 節點幾何重新生成 (08_a5_group_nodes.py)")

# ============ 2. 統計預測 ============
print(f"\n{'='*70}")
print("統計預測 (可證偽)")
print(f"{'='*70}")
print(f"""
空洞中心 (Void Centers):
  H1. 空洞中心到最近 A₅ 節點嘅角距離中位數 > 隨機期望
      (空洞避開節點 — 節點係物質凝聚點)
      隨機期望: 60 節點均勻天球 → 中位數 ~ 10.5° (已算過)
      IDCM 預測: 空洞中位數 > 12°?

星系團 (Clusters):
  H2. 星系團到最近 A₅ 節點嘅角距離中位數 < 隨機期望
      (星系團對齊節點)
      IDCM 預測: 星系團中位數 < 9°?

大圓弧 (Great Circles):
  H3. 沿 120 條大圓嘅星系過量
      (A₅ 邊 = 大圓弧投影)
      每條大圓 ±2° 帶狀區, 統計星系數密度
      IDCM 預測: 帶狀區內星系密度過量 > 0

宇稱:
  H4. 空洞/星系團分佈有 A₅ 離散對稱 (Icosahedral symmetry)
      → 統計量: 分佈對 A₅ 群嘅對稱性檢驗
      (把天球分為 60 個 node cell, 比較 cell 間密度差異)
""")

# ============ 3. 數據需求 ============
print(f"{'='*70}")
print("數據需求")
print(f"{'='*70}")
print(f"""
優先:
  1. DESI DR1/DR2 星系目錄 (公開, 需下載)
     - https://data.desi.lbl.gov/
     - 需要: RA, Dec, z
  2. SDSS 空洞目錄 (公開)
     - Wang et al. 2023: SDSS DR16 void catalog
     - 需要: RA, Dec, z (空洞中心)
  3. Planck SZ 星系團目錄 (公開)
     - PSZ2: 1653 個星系團 (RA, Dec, z)
     - https://heasarc.gsfc.nasa.gov/W3Browse/planck/plancksz.html

方法:
  1. 下載星系團目錄 (PSZ2 最細 — 1653 個)
  2. 計算每個到最近節點距離
  3. MC 比較 (打散 RA 保持 dec 視場)
  4. 睇 H2 係咪成立 (星系團對齊節點)
""")

# ============ 4. 嘗試 Planck SZ 星系團目錄 ============
print(f"{'='*70}")
print("Planck SZ 星系團目錄 — 初步測試")
print(f"{'='*70}")

# 檢查有冇本地數據
import os
sz_files = []
for root, dirs, files in os.walk('/home/wsl/Projects/IDCM/IDCM-v10.0'):
    for f in files:
        if 'psz' in f.lower() or 'sz' in f.lower() and f.endswith(('.csv', '.dat', '.fits')):
            sz_files.append(os.path.join(root, f))
if sz_files:
    print(f"搵到本地 SZ 數據: {sz_files}")
else:
    print(f"本地冇 SZ 數據 — 需要下載")
    print(f"PSZ2 目錄: https://heasarc.gsfc.nasa.gov/W3Browse/planck/plancksz.html")
    print(f"(1653 個星系團, RA/Dec/z)")

# 保存框架
os.makedirs('data', exist_ok=True)
with open('data/lss_alignment_framework.json', 'w') as f:
    json.dump({
        "predictions": {
            "H1": "void centers avoid nodes (median d > random ~10.5 deg)",
            "H2": "clusters align with nodes (median d < random)",
            "H3": "galaxy excess along 120 great circles",
            "H4": "A5 icosahedral symmetry in LSS distribution"
        },
        "data_needed": ["DESI DR1/DR2", "SDSS void catalog", "Planck PSZ2 clusters"],
        "status": "framework ready, data pending"
    }, f, indent=2)
print(f"\n已保存 data/lss_alignment_framework.json")
