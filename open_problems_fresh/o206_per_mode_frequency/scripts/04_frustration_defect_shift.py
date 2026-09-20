#!/usr/bin/env python3
"""
O206 — Script 04: F2c 阻挫邊 (OPAQUE) 作局部缺陷 → 逐模頻率位移
=========================================================
攻擊路線 4 (SESSION_START §四):
  32 條 OPAQUE 阻挫邊 (O182) 作局部缺陷, 計其對模式頻率之擾動

幾何 (O182/O7, 唯讀):
  88 邊 = TRANSPARENT (透明通道), 32 邊 = OPAQUE (同色阻挫 / 拓撲位元)
  模式 profile 沿冷斑測地線: c_n(β) = cos(nβ/2)  (O136 docs/29 Node 0 退化定理: β=0 ⟹ c ≡ 1)
  P(n) = Σ_{88 透明中點} cos²(nβ/2);  O(n) = Σ_{32 阻挫中點} cos²(nβ/2)

⚠️ 誠實界線: O136 已排除方向 #11「阻挫重疊」— 但嗰次係當【質量公式】;
   本 script 係當【|Δm| 分母之逐模位移 δ_n】= 唔同用法, 必須分開裁決
⚠️ 慣例: 本節 β-剖面屬【測地線慣例】, 與 O136 |Δm| 之 D-D 鏈模屬唔同實現 — 必須標明
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, MODES_SORTED, LM,
                      E_ring44, V_position, logscore, sum_V2_dE)

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = ROOT / "o182_88grid_geometry" / "data"
CMB = ROOT / "cmb_cold_spot" / "data"
OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


print("=" * 100)
print("O206 Script 04: F2c — 阻挫邊作局部缺陷之逐模頻率位移")
print("=" * 100)

# ═══ 幾何載入 (唯讀) ═══
nodes = np.loadtxt(CMB / "a5_nodes.txt")
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
U = np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
l_c, b_c = math.radians(209.0), math.radians(-57.0)   # 冷斑 (180+L₇, −(44+F₇))
cold = np.array([math.cos(b_c) * math.cos(l_c), math.cos(b_c) * math.sin(l_c), math.sin(b_c)])

emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip():
        continue
    p = line.split()
    emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
transp_mid = np.array([U[u] + U[v] for _, u, v in emap])
transp_mid /= np.linalg.norm(transp_mid, axis=1, keepdims=True)

fnodes = np.loadtxt(O182 / "g32_frustration_midpoints.txt")
f_mid = np.column_stack([np.cos(np.radians(fnodes[:, 1])) * np.cos(np.radians(fnodes[:, 0])),
                         np.cos(np.radians(fnodes[:, 1])) * np.sin(np.radians(fnodes[:, 0])),
                         np.sin(np.radians(fnodes[:, 1]))])
f_mid /= np.linalg.norm(f_mid, axis=1, keepdims=True)

beta_P = np.arccos(np.clip(transp_mid @ cold, -1, 1))
beta_O = np.arccos(np.clip(f_mid @ cold, -1, 1))
print(f"\n  透明中點 {len(transp_mid)} 個: β ∈ [{np.degrees(beta_P).min():.2f}°, {np.degrees(beta_P).max():.2f}°]")
print(f"  阻挫中點 {len(f_mid)} 個: β ∈ [{np.degrees(beta_O).min():.2f}°, {np.degrees(beta_O).max():.2f}°]")
chk("C1 [O182] 88 透明 + 32 阻挫 = 120 邊",
    len(transp_mid) == 88 and len(f_mid) == 32, "88 + 32 = 120")

n_all = np.arange(1, NC + 1)
P_all = np.array([float((np.cos(n * beta_P / 2) ** 2).sum()) for n in n_all])
O_all = np.array([float((np.cos(n * beta_O / 2) ** 2).sum()) for n in n_all])
OP_all = O_all / P_all
Of_all = O_all / (O_all + P_all)

print(f"\n  {'n':>3} {'P(n)':>12} {'O(n)':>12} {'O/P':>10}")
print("  " + "-" * 42)
for n in A5_MODES:
    print(f"  {n:>3} {P_all[n-1]:>12.6f} {O_all[n-1]:>12.6f} {OP_all[n-1]:>10.6f}")
chk("C2 [慣例=測地線] OP(1) = 4/11 = B/L₅ (O136 docs/16 記錄值)",
    abs(OP_all[0] - 4.0 / 11.0) < 2e-3, f"OP(1) = {OP_all[0]:.6f}, 4/11 = {0.363636:.6f}")

# ═══ 位移測試 ═══
V = V_position()
E0 = E_ring44()
base = logscore(sum_V2_dE(E0, V))
print(f"\n  基準 |Δm| RMS = {base:.4f}")

shapes = {
    "O(n)/P(n) (OP)": OP_all,
    "O(n) (阻挫重疊)": O_all,
    "O/(O+P)": Of_all,
    "ln(O/P)": np.log(OP_all),
    "1/P(n) (透明缺口)": 1.0 / P_all,
}

print(f"\n  {'shape':>18} {'最佳 ε':>12} {'最佳 RMS':>10} {'ε 結構值?':>22}")
print("  " + "-" * 68)
best_overall = (9e9, None, None)
results = {}
for name, shape in shapes.items():
    best = (9e9, None)
    for eps in np.logspace(-4, 2, 240):
        s = logscore(sum_V2_dE(E0 + eps * shape, V))
        if s < best[0]:
            best = (s, float(eps))
    results[name] = {"best_rms": best[0], "best_eps": best[1]}
    struct = []
    for lbl, val in [("1/45=g", 1 / 45), ("μ²=2", 2.0), ("1", 1.0), ("4g=0.0889", 4 / 45)]:
        if abs(best[1] - val) / val < 0.05:
            struct.append(lbl)
    if best[0] < best_overall[0]:
        best_overall = (best[0], name, best[1])
    print(f"  {name:>18} {best[1]:>12.5f} {best[0]:>10.4f} "
          f"{('✓ ' + ','.join(struct)) if struct else 'no':>22}")

chk("C3 [F2c] 冇任何 shape 在結構 ε 下閉合 (RMS < 0.05)",
    all(v["best_rms"] > 0.05 for v in results.values()),
    f"最佳 = {best_overall[1]} (RMS {best_overall[0]:.4f}, ε = {best_overall[2]:.4g})")
chk("C4 [F2c] 最佳改善 < 2× (唔足以解釋 11.7× 缺口)",
    best_overall[0] > base / 2,
    f"{best_overall[0]:.4f} vs 基準 {base:.4f} = {base/best_overall[0]:.2f}× 改善")

# ═══ null test: 隨機 32 邊子集 ═══
print(f"\n{'─'*100}\nnull test: 隨機 32 邊子集 (N=1000) — 觀測阻挫集特異嗎?\n{'─'*100}")
all_mid = np.vstack([transp_mid, f_mid])
all_beta = np.concatenate([beta_P, beta_O])
rng = np.random.default_rng(20260921)
null = []
for _ in range(1000):
    sel = rng.choice(120, size=32, replace=False)
    bs = all_beta[sel]
    o = np.array([float((np.cos(n * bs / 2) ** 2).sum()) for n in n_all])
    p = np.array([float((np.cos(n * all_beta / 2) ** 2).sum()) for n in n_all]) - o
    sh = np.where(p > 0, o / np.maximum(p, 1e-12), 0.0)
    bb = (9e9, None)
    for eps in np.logspace(-4, 2, 60):
        s = logscore(sum_V2_dE(E0 + eps * sh, V))
        if s < bb[0]:
            bb = (s, float(eps))
    null.append(bb[0])
null = np.array(null)
p_val = float((null <= best_overall[0]).mean())
print(f"  null (隨機 32 邊) 最佳 RMS: 中位 = {np.median(null):.4f}, min = {null.min():.4f}")
print(f"  P(≤ 觀測最佳 {best_overall[0]:.4f}) = {p_val:.4f}")
chk("C5 [null] 觀測阻挫集唔顯著 (P > 0.05) ⟹ 無結構優勢",
    p_val > 0.05, f"P = {p_val:.4f}")

# ═══ 裁決 ═══
print(f"\n{'─'*100}\n裁決 (F2c)\n{'─'*100}")
print(f"""
  ① 32 條 OPAQUE 邊確實提供逐模、零參數嘅位移 shape (O(n), OP(n), ...)
  ② 但最佳 RMS = {best_overall[0]:.4f} (基準 {base:.4f}) ⟹ 改善 < 2×, 距閉合門檻 0.05 遠
  ③ null test: 隨機 32 邊子集同樣達到 (P = {p_val:.4f}) ⟹ 觀測阻挫集無結構優勢
  ⟹ F2c 裁決: 🔴 阻挫邊位移【唔】提供 1.80× 殘餘之解
     (與 O136 已排除方向 #11 一致, 但今次係分母位移路徑 — 兩條路徑同時否定)
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "04_f2c_frustration_defect.json", "w") as f:
    json.dump({
        "baseline_rms": base, "shapes": results,
        "best": {"name": best_overall[1], "rms": best_overall[0], "eps": best_overall[2]},
        "null_p": p_val, "OP_n1": float(OP_all[0]),
        "checks_pass": n_pass, "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/04_f2c_frustration_defect.json")
