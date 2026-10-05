#!/usr/bin/env python3
"""
O53: CYTools fetch 對照 polytope (h11=36 家族)
=================================================
fetch_polytopes 支持 h11/h12 篩選 — 試 fetch (36, 94)
quark 死咗但可能 fallback 去 hep
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: CYTools fetch (36,94)")
print("=" * 70)

import cytools

# 試 fetch (36,94) — 短 timeout
try:
    pts = cytools.fetch_polytopes(h11=36, h12=94, timeout=15, limit=3)
    print(f"fetch (36,94): {type(pts)}, count={len(pts) if hasattr(pts, '__len__') else 'N/A'}")
    for i, p in enumerate(pts):
        if i >= 3:
            break
        print(f"  [{i}] h11={p.h11()}, h12={p.h12()}, n_pts={len(p.points())}")
        # 儲存
        out = os.path.join(BASE, f'control_36_94_fetch_{i}.poly')
        with open(out, 'w') as f:
            for v in p.vertices():
                f.write(' '.join(str(x) for x in v) + '\n')
        print(f"      ✅ Saved: {out}")
except Exception as e:
    print(f"fetch FAIL: {type(e).__name__}: {str(e)[:200]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)