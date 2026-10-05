#!/usr/bin/env python3
"""
O53 問題 3: (36,98) 真實多面體構造 — 第一部分
================================================
用 CYTools fetch 真實 (36,98) polytope:
1. 有幾多個唔等價 polytope? (limit=100 掃描)
2. 第一個 polytope 嘅基本結構 (vertices, points, dimension)
3. 存檔做 PALP 格式 (.poly) 供 poly.x 分析

Run: /usr/bin/python3 scripts/04_fetch_polytope.py
"""
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.13/site-packages"))

from cytools import fetch_polytopes, config

# 非 favorable CY 需要 experimental features
try:
    config.enable_experimental_features()
    print("[config] experimental features enabled")
except Exception as e:
    print(f"[config] warning: {e}")

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
os.makedirs(OUTDIR, exist_ok=True)

print("=" * 64)
print("O53 Q3: CY₃(36,98) 真實多面體構造")
print("=" * 64)

# --- 1. 掃描唔等價 polytope 數量 ---
print("\n[1] 掃描 (36,98) polytope 數量 (limit=100)...")
polys = list(fetch_polytopes(h11=36, h21=98, limit=100, lattice="N"))
print(f"    fetch 到 {len(polys)} 個 polytope")

# 去重 (以 vertices 集合)
seen = set()
unique = []
for p in polys:
    pts = p.points()
    # 用 vertices 嘅 tuple 做 hash
    key = tuple(sorted(tuple(int(x) for x in v) for v in p.vertices()))
    if key not in seen:
        seen.add(key)
        unique.append(p)
print(f"    去重後: {len(unique)} 個唔等價 polytope")

# --- 2. 第一個 polytope 結構 ---
if unique:
    P = unique[0]
    print(f"\n[2] 第一個 polytope 結構:")
    pts = P.points()
    verts = P.vertices()
    print(f"    N-lattice points: {len(pts)}")
    print(f"    vertices: {len(verts)}")
    print(f"    ambient dimension: {P.dimension()}")

    # 保存做 PALP 格式 (.poly)
    # PALP 格式: 第一行維度+點數, 之後每行一個點
    poly_path = os.path.join(OUTDIR, "cy36_98_p1.poly")
    with open(poly_path, "w") as f:
        f.write(f"{P.dimension()} {len(pts)}\n")
        for pt in pts:
            f.write(" ".join(str(int(x)) for x in pt) + "\n")
    print(f"    ✅ PALP 格式寫入: {poly_path}")

    # 保存 metadata
    meta = {
        "n_polytopes_total": len(polys),
        "n_unique": len(unique),
        "first_polytope": {
            "n_points": len(pts),
            "n_vertices": len(verts),
            "dimension": P.dimension(),
        }
    }
    meta_path = os.path.join(OUTDIR, "cy36_98_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"    ✅ metadata 寫入: {meta_path}")

    # --- 3. 三角剖分 + CY 結構 ---
    print(f"\n[3] 三角剖分 + CY 結構:")
    try:
        tri = P.triangulate(make_star=True, verbosity=0)
        tv = tri.get_toric_variety()
        cy = tv.get_cy() if hasattr(tv, 'get_cy') else None
        print(f"    triangulation OK")
        print(f"    simplices: {len(tri.simplices())}")
    except Exception as e:
        print(f"    triangulation 失敗: {e}")
        try:
            tri = P.triangulate(backend="qhull", verbosity=0)
            tv = tri.get_toric_variety()
            print(f"    qhull triangulation OK, simplices: {len(tri.simplices())}")
        except Exception as e2:
            print(f"    qhull 都失敗: {e2}")

else:
    print("    ❌ 冇搵到 (36,98) polytope!")
    sys.exit(1)

print("\n" + "=" * 64)
print("✅ 完成 — 下一步: poly.x 檢查對稱性 + CYTools 真實 d_ijk")
print("=" * 64)
