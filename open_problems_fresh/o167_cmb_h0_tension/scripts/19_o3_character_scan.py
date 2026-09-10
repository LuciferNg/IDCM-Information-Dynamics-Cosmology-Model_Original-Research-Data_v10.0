#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/19 — O3 機制層快測: A₅ 特徵標掃描 421

問題: 421 = L₄|A₅|+1 有冇群論來源 (特徵標組合)?

A₅ 特徵標表 (標準, 5 conjugacy classes):
  類階: 1, 15, 20, 12, 12  (1A, 2A, 3A, 5A, 5B)
  χ1:   1  1   1   1   1   (trivial)
  χ2:   3  -1  0   φ   -ψ  (φ = (1+√5)/2, ψ = (1−√5)/2)
  χ3:   3  -1  0   -ψ  φ
  χ4:   4  0   1  -1  -1
  χ5:   5  1   -1  0   0

測試: 421 或 420 係咪 Σ c_i·χ_i(g)·χ_j(g) 或特徵標乘積嘅線性組合 (c_i 小整數)?
"""
import mpmath as mp
mp.mp.dps = 20

phi = (1+mp.sqrt(5))/2
psi = (1-mp.sqrt(5))/2

# A₅ character table (rows = irreps, cols = classes [1A,2A,3A,5A,5B])
# ψ = (1−√5)/2 ≈ −0.618 (本身就負)
CHI = [
    [1, 1, 1, 1, 1],
    [3, -1, 0, phi, psi],
    [3, -1, 0, psi, phi],
    [4, 0, 1, -1, -1],
    [5, 1, -1, 0, 0],
]
NAMES = ["triv", "3a", "3b", "4", "5"]
CLASS_ORDERS = [1, 15, 20, 12, 12]
CENTRALIZERS = [60, 4, 3, 5, 5]  # |C_G(g)| for 1A,2A,3A,5A,5B

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

# C1: 群階 = Σ dim² (基本事實)
order = sum(CHI[i][0]**2 for i in range(5))
print(f"|A₅| = Σ dim² = {order}")
chk("C1 |A₅| = 60", order == 60)

# C2: 特徵標正交 — Σ_χ χ(g)² = |C_G(g)| (centralizer order), 唔係 |G|δ
ortho_ok = True
for c in range(5):
    s = sum(CHI[i][c]**2 for i in range(5))
    if abs(s - CENTRALIZERS[c]) > 1e-6:
        ortho_ok = False
        print(f"    類 {c}: Σχ² = {float(s)} vs |C_G| = {CENTRALIZERS[c]}")
chk("C2 特徵標正交 Σχ²(g) = |C_G(g)|", ortho_ok)

# C3: 掃描 — 421/420 係咪特徵標乘積 χ_i(g)·χ_j(g) 或 Σ 組合?
# 所有成對乘積 (5×5 對), 檢查 = 420, 421
found = []
for i in range(5):
    for j in range(5):
        for c in range(5):
            v = CHI[i][c]*CHI[j][c]
            if abs(v - 420) < 1e-6 or abs(v - 421) < 1e-6:
                found.append((NAMES[i], NAMES[j], CLASS_ORDERS[c], v))
chk("C3 特徵標乘積 = 420/421", len(found) > 0)
for f in found:
    print(f"    {f[0]}×{f[1]} @ 類階{f[2]} = {f[3]}")

# C4: Σ c·χ 掃描 (小整數組合 c ∈ [-5,5]) — 目標 420/421
targets = [420, 421]
hits = []
for c1 in range(-5, 6):
    for c2 in range(-5, 6):
        for c3 in range(-5, 6):
            for c4 in range(-5, 6):
                for c5 in range(-5, 6):
                    combo = [c1, c2, c3, c4, c5]
                    # 喺 1A 類嘅值
                    v1A = sum(combo[i]*CHI[i][0] for i in range(5))
                    if v1A in targets:
                        # 檢查喺 2A 類 (行和 = ?)
                        row = [sum(combo[i]*CHI[i][c] for i in range(5)) for c in range(5)]
                        # 只記錄全整數 (代數整數) 組合
                        if all(abs(r - round(float(r))) < 1e-6 for r in row):
                            hits.append((combo, v1A))
print(f"整數特徵標組合 → 420/421: {len(hits)} 個")
for combo, v in hits[:5]:
    print(f"    {combo} → {v} (1A)")

chk("C4 特徵標整數組合命中 420/421", len(hits) > 0)

# C5: 正則表示特徵標: χ_reg(g) = |G|δ_{g,1} → Σχ² = |G|²
reg_sum = sum(CHI[i][0]**2 * CLASS_ORDERS[0] for i in range(5))  # 唔啱, 正則 = Σ dim²·χ_i
# 正則: χ_reg(g) = Σ_i dim_i χ_i(g)
reg = [sum(CHI[i][0]*CHI[i][c] for i in range(5)) for c in range(5)]
print(f"    正則特徵標 (1A..5B): {[float(r) for r in reg]} — 應該 (60, 0, 0, 0, 0)")
chk("C5 正則表示 χ_reg = (60,0,0,0,0)", abs(reg[0]-60) < 1e-6 and all(abs(x) < 1e-6 for x in reg[1:]))

print()
print("RESULT:", "5/5 PASS" if (order==60 and ortho_ok and len(found)>0 and len(hits)>0 and abs(reg[0]-60)<1e-6) else "x", "PASS")
print("裁決: 見 hits — 若 C3/C4 有命中 → 421/420 有特徵標來源")
print("      若冇命中 → A₅ 群論唔直接出 421 (421 prime, 特徵標係代數整數)")
print("      → O3 機制層留新 O (60-頂點群配分理論)")
