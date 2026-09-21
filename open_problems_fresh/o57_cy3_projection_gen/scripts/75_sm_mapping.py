#!/usr/bin/env python3
"""
O57 十二期 75: φ^(-i) / 2^(-i) 完整質量譜 → SM 9 費米子對應
================================================================
scripts/74 發現: φ^(-i) 117 finite, 2^(-i) 116 finite range 1.3e9

關鍵測試: 用完整質量譜 fit SM 9 費米子
  1. 攞 φ^(-i) 同 2^(-i) 完整 volumes
  2. e^-V 質量譜 (117 個)
  3. 揀 9 個最佳對應 SM (3 type × 3 gen)
  4. χ²/log-err 評估
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十二期 75: 完整譜 → SM 對應")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

def get_masses(t36):
    t32 = np.array([t36[b-1] for b in basis])
    cv = np.array(cy.compute_curve_volumes(t32))
    pos = cv[cv > 1e-10]
    masses = np.exp(-pos)
    ms = np.sort(masses)[::-1]
    return ms, pos

# ============ 2. 兩個候選譜 ============
print("\n[2] 質量譜")
for name, t36 in [("φ^(-i)", phi**(-np.arange(36))), ("2^(-i)", 2.0**(-np.arange(36)))]:
    ms, pos = get_masses(t36)
    n_fin = np.sum(ms > 1e-30)
    print(f"  {name}: {len(pos)} pos, {n_fin} finite, top5: {[f'{m:.3e}' for m in ms[:5]]}")
    print(f"    range: {ms[0]/ms[-1] if ms[-1]>0 else 'inf':.1e}")

# ============ 3. SM 對應 ============
print("\n[3] SM 9 費米子對應")
m_SM = np.array([2.2, 1270, 172760, 4.7, 93, 4180, 0.511, 105.66, 1776.86])  # MeV
names = ["u", "c", "t", "d", "s", "b", "e", "mu", "tau"]

for name, t36 in [("φ^(-i)", phi**(-np.arange(36))), ("2^(-i)", 2.0**(-np.arange(36)))]:
    ms, pos = get_masses(t36)
    n_fin = np.sum(ms > 1e-30)
    print(f"\n  --- {name} ({n_fin} finite) ---")
    if n_fin >= 9:
        # 揀 9 個最大質量 (細 volume) 對應
        model_m = ms[:9]
        # 要 fit 尺度: model 值係 e^-V (0~1), SM 係 MeV
        # 比例: 用 m_t (top, 最大) 校準
        # model[0] 對應邊個 SM? 唔知 — 試所有排列!
        # 簡單: 按大小排序對應
        sm_sorted = np.sort(m_SM)[::-1]
        # log-err (相對比例)
        log_ratios = np.log(model_m) - np.log(sm_sorted)
        # 校準: 平均 offset
        offset = np.mean(log_ratios)
        log_err = np.std(log_ratios)
        print(f"    model (sorted): {[f'{m:.3e}' for m in model_m]}")
        print(f"    SM (sorted): {[f'{m:.1f}' for m in sm_sorted]}")
        print(f"    log-err (校準後): {log_err:.4f}")
        check(f"{name} log-err < 1.5 (量級匹配)", log_err < 1.5, f"({log_err:.3f})")
    else:
        print(f"    ❌ 唔夠 9 個")

# ============ 4. 3×3 分組 ============
print("\n[4] 3×3 分組 (type × gen)")
# 用 φ^(-i): 117 個質量, 按大小分 9 組 (每組 13 個 = 117/9)
ms, pos = get_masses(phi**(-np.arange(36)))
if len(ms) >= 9:
    # 用每組最大
    groups = []
    for g in range(9):
        sl = slice(g*13, (g+1)*13) if g < 8 else slice(g*13, None)
        groups.append(ms[sl].max())
    print(f"  9 組代表: {[f'{m:.3e}' for m in groups]}")
    print(f"  組比: {[f'{groups[i]/groups[i+1]:.1f}' for i in range(8)]}")
    print(f"  φ⁴ = {phi**4:.1f}, φ⁸ = {phi**8:.1f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十二期 75 總結:")
print("=" * 72)
print(f"""
  完整譜 SM 對應:
  ─────────────────────────────────
  1. φ^(-i): 117 finite
  2. 2^(-i): 116 finite range 1.3e9
  3. 對應結果: 睇上面

  誠實: e^-V 質量係 0~1 之間嘅數 (無量綱)
  → 需要質量尺度校準 (M0 或者 v)
  → log-err 先反映結構匹配
""")

results = {
    "test": "O57 十二期 75: SM 對應",
    "passed": passed, "failed": failed
}
with open("data/75_sm_mapping.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十二期 75 完成!")
