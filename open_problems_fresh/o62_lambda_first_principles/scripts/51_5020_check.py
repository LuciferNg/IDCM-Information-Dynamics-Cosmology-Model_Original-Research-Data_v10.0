#!/usr/bin/env python3
"""
O62 九期 51: 項目 3 — 5020 個 (36,98) polytope 對照
=====================================================
確認 canonical 專屬結構:
  1. 6 頂點 (canonical) vs 其他
  2. 7 高-star 內部點 (canonical 專屬?)
  3. -360 = -8×45 (div0 專屬?)
  4. M:48, N:85

用 all_36_98.poly (POLY 格式) 讀 5020 個 polytopes
"""
import sys, os, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 51: 5020 對照")
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

# ============ 1. 讀 all_36_98.poly ============
print("[1] all_36_98.poly 格式")
with open(os.path.join(O53, "all_36_98.poly")) as f:
    content = f.read()
print(f"  檔案大小: {len(content)} bytes")
lines = content.splitlines()
print(f"  行數: {len(lines)}")
print(f"  頭 20 行:")
for l in lines[:20]:
    print(f"    {l[:80]}")

# 偵測格式: PALP 格式?
# PALP: 每 polytope: 頂點數 維度, 然後頂點座標
# 或者: # 開頭 comment
