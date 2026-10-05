#!/usr/bin/env python3
"""
O53 路徑三: 對照 polytope 驗證 + Hodge 數
==============================================
HF 提取嘅 control polytope (20 vertices) — 驗證 Hodge 數
"""
import os, json, math, sys, subprocess
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 路徑三: 對照 polytope 驗證")
print("=" * 70)

for name in ['cy36_98_hf', 'control_h11_36_h12_94']:
    path = os.path.join(BASE, name + '.poly')
    if not os.path.exists(path):
        print(f"  ❌ {name}: 唔存在")
        continue
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    n_pts = len(lines)
    dim = len(lines[0].split())
    print(f"\n{name}: {n_pts} points, dim={dim}")
    
    # PALP 計算 Hodge
    inp = f"{n_pts} {dim}\n" + "\n".join(lines) + "\n"
    try:
        r = subprocess.run(['/usr/bin/poly.x', '-v'], input=inp, 
                          capture_output=True, text=True, timeout=60)
        # 搵 Hodge
        import re
        for line in r.stdout.split('\n'):
            if re.search(r'H:\d+,\d+', line) or 'M:' in line:
                print(f"  PALP: {line.strip()}")
    except Exception as e:
        print(f"  PALP err: {e}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)