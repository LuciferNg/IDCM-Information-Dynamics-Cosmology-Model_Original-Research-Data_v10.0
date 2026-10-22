#!/usr/bin/env python3
"""
11_audit_fix_theta_field.py — 審計修正: data/edge_formula.txt 嘅 theta_formula 欄
===============================================================================
2026-10-22 全量審計發現:
  scripts/07_edge_formula_verify.py line 121 喺群元素 loop 內重新賦值 `theta`,
  令 line 136 寫入 data 檔嘅 theta_formula = loop 最後一個群元素角度 (113.54247385°),
  唔係公式計算值 (26.091357°)。

  ⚠️ stdout 正確 (公式 θ = 26.091357°, 偏差 0.000011°), theta2 亦正確。
  ⚠️ 所有文檔 (02_results.md / final_result.md / 01_problem_record.md / 03_delta_closure.md)
     引用嘅係 26.091357° — **冇被污染**。

本腳本: 唔改 07 (歷史記錄不可回溯修改); 只重算正確值並修正 data 檔,
        保留原錯值作 append-only 歷史註記。
"""
import math, numpy as np, os, shutil, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "edge_formula.txt")

# ── 1. 備份原檔 ──
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = DATA + f".bak_{ts}"
shutil.copy2(DATA, bak)
print(f"✅ 備份: {os.path.basename(bak)}")

# ── 2. 讀原值 (保留作歷史) ──
orig = {}
with open(bak) as f:
    for ln in f:
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            parts = ln.split()
            for p in parts:
                if "=" in p:
                    k, v = p.split("=", 1)
                    orig[k] = v
print(f"原 theta_formula = {orig.get('theta_formula')}  ← 變量覆蓋 bug")

# ── 3. 重算正確值 (獨立計算, 唔用 07 嘅變量) ──
phi = (1 + 5**0.5) / 2
inv_phi = 1 / phi
verts = []
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            verts.append((sx, sy, sz))
for sx in (-1, 1):
    for sy in (-1, 1):
        verts.append((0, sx * inv_phi, sy * phi))
        verts.append((sx * inv_phi, sy * phi, 0))
        verts.append((sx * phi, 0, sy * inv_phi))
verts_n = np.array([np.array(v) / np.linalg.norm(v) for v in verts])

ra0, dec0 = 48.2999, -20.4373   # a5_nodes 節點 0 (高精度)
v = np.array([math.cos(math.radians(dec0)) * math.cos(math.radians(ra0)),
              math.cos(math.radians(dec0)) * math.sin(math.radians(ra0)),
              math.sin(math.radians(dec0))])
d3 = min(math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))) for a in verts_n)

# 兩條等價公式
theta_a = math.degrees(math.acos(-0.5 + 1.5 * math.cos(math.radians(d3))**2))       # cos(120°)=−1/2
theta_b = math.degrees(math.acos(math.cos(math.radians(d3))**2
                                 - math.sin(math.radians(d3))**2 / 2))               # 球面直接
obs = 26.091346

print(f"\n重算:")
print(f"  δ              = {d3:.8f}°")
print(f"  θ (cos120°式)  = {theta_a:.8f}°")
print(f"  θ (球面直接式) = {theta_b:.8f}°")
print(f"  兩式一致       = {abs(theta_a - theta_b):.2e}°")
print(f"  觀測           = {obs:.6f}°")
print(f"  偏差           = {abs(theta_a - obs):.8f}°")

assert abs(theta_a - theta_b) < 1e-9, "兩條公式唔一致!"
assert abs(theta_a - 26.091357) < 1e-6, "θ 唔係文檔值 26.091357!"

# ── 4. 寫修正檔 (正確值 + append 歷史註記) ──
with open(DATA, "w") as f:
    f.write(f"delta={d3:.8f}\n")
    f.write(f"theta_formula={theta_a:.8f} theta_obs={obs:.8f}\n")
    f.write(f"delta_rev={float(orig.get('delta_rev', 15.10850925)):.8f}\n")
    f.write(f"theta2={theta_b:.8f}\n")
    f.write(f"# audit 2026-10-22: theta_formula 原值 {orig.get('theta_formula')} "
            f"係 07_edge_formula_verify.py L121 loop 變量覆蓋 bug (非公式值);\n")
    f.write(f"#   正解 = {theta_a:.8f} (= theta2, 兩式等價); stdout 一直正確, 文檔未受污染\n")

print(f"\n✅ 已修正 data/edge_formula.txt")
print(f"   原檔備份: {os.path.basename(bak)}")
print(f"\n修正後內容:")
print(open(DATA).read())
