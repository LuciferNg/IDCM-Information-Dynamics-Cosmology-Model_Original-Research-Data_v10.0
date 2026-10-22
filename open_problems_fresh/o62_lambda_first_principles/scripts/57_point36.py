#!/usr/bin/env python3
"""
O62 十期 57: point 36 身份 + 真正 anomaly 修正
==============================================
發現: active = 37 點 (0-36), 但 kappa 只到 35!
point 36: star>0 (active) 但唔喺 kappa36

hypothesis: 
  - h11 = 36 → 36 個 Kähler divisors = 0-35?
  - point 36 = div0 (scaling) 或者第 37 個 active?
  - anomaly (·,36) 29 個 = point 36 嘅特殊地位

檢查:
  1. point 36 嘅 star 值
  2. point 36 係咪喺 kappa 檔案?
  3. point 36 對應邊個 divisor?
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 57: point 36 身份")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
simplices = d["simplices"]
pts = np.array(d["points"], dtype=float)
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1

print(f"[1] point 36 身份")
print(f"  point 36 座標: {pts[36]}")
print(f"  point 36 star: {star.get(36, 0)}")
print(f"  point 36 喺 kappa? 唔係 (kappa 只 0-35)")

# point 36 係咪 = div0? 
# div0 = point 0 = (0,0,0,0)
print(f"  point 0: {pts[0]}, star: {star.get(0, 0)}")
print(f"  point 36 = point 0? {np.allclose(pts[36], pts[0])}")

# 邊個點係 (0,0,0,0)?
origin_pts = [i for i in range(48) if np.allclose(pts[i], 0)]
print(f"  (0,0,0,0) 點: {origin_pts}")

# point 36 座標特殊?
print(f"\n[2] point 36 同其他 active 點關係")
print(f"  所有 active 點 (star>0): {[i for i in range(48) if star.get(i,0) > 0]}")

# kappa 檔案係咪真係 36×36×36?
print(f"\n[3] kappa 檔案 shape")
print(f"  kappa36 shape: {kappa36.shape}")
# intersection_full 嘅 kappa 原始 shape?
kappa_full = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"]
karr = np.array(kappa_full)
print(f"  intersection_full kappa shape: {karr.shape}")

# 如果 karr 係 48³ 或者 36³?
if karr.shape[0] > 36:
    # 檢查 index 36 嘅 kappa
    print(f"  kappa[36,36,36] = {karr[36,36,36] if karr.shape[0] > 36 else 'N/A'}")
    print(f"  kappa[36,j,k] 非零: {np.count_nonzero(karr[36])}")
    # 有冇 kappa[0,0,0] = -360?
    print(f"  kappa[0,0,0] = {karr[0,0,0]}")

# ============ 總結 ============
print("\n" + "=" * 72)
print("十期 57 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 57: point 36",
    "p36": pts[36].tolist(), "star36": star.get(36, 0),
    "origin": origin_pts,
    "kappa_shape": list(karr.shape),
    "passed": 0, "failed": 0
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "57_point36.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("完成")
