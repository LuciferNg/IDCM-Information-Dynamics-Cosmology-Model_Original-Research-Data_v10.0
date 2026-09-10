#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/01 — 相位深度 Φ(ℓ) 映射 + M(ℓ) 非單調分析

O167 scripts/12 發現: 徑向阻抗 M(ℓ) = 1.630, 1.639, 1.684, 1.624, 1.572, 1.419
非單調 (峰值 ℓ≈0.48)。深極限 √2 命中 Lyα。

本 script:
  C1: M(ℓ) 表重現 + 差值分析
  C2: 相位深度候選 Φ(ℓ) = (4^ℓ−1)/ln4 映射 — M vs Φ 有冇線性?
  C3: M(ℓ) − √2 形狀 (峰 = 中央模 γ = μ² 位置?)
  C4: 候選 kernel: K(ℓ) = √2 + A·(1−4^{−ℓ})·cos(πℓ/2) 類 — 只測試, 唔 tune
  C5: 誠實裁決 — 非單調係咪 tracer 系統? (ELG1 合併? QSO 寬誤差?)
"""
import mpmath as mp
mp.mp.dps = 25

R = mp.mpf('4129.94')
rd = mp.mpf('147.088')
ln4 = mp.log(4)

# O167 scripts/12 數據: (z, D_H/rd obs, M)
DATA = [
    ("LRG1", mp.mpf('0.510'), mp.mpf('21.863'), mp.mpf('1.6300')),
    ("LRG2", mp.mpf('0.706'), mp.mpf('19.455'), mp.mpf('1.6387')),
    ("LRG3", mp.mpf('0.934'), mp.mpf('17.641'), mp.mpf('1.6845')),
    ("ELG2", mp.mpf('1.321'), mp.mpf('14.176'), mp.mpf('1.6245')),
    ("QSO",  mp.mpf('1.484'), mp.mpf('12.817'), mp.mpf('1.5719')),
    ("Lya",  mp.mpf('2.330'), mp.mpf('8.632'),  mp.mpf('1.4192')),
]

def ell_of(z): return mp.log(1+z)/ln4

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

print("=== C1: M(ℓ) 表 + 相位深度 ===")
print(f"{'tracer':<7}{'ell':>7}{'M':>7}{'Φ(ℓ)':>8}{'M−√2':>8}{'M/Φ':>8}")
rows = []
for name, z, dh, M in DATA:
    ell = ell_of(z)
    Phi = (mp.mpf('4')**ell - 1)/ln4
    rows.append((name, ell, M, Phi))
    print(f"{name:<7}{float(ell):>7.3f}{float(M):>7.4f}{float(Phi):>8.4f}{float(M-mp.sqrt(2)):>8.4f}{float(M/Phi):>8.3f}")

# C2: M vs Φ 線性?
Ms = [float(r[2]) for r in rows]
Phis = [float(r[3]) for r in rows]
# 簡單相關係數
mx = sum(Phis)/len(Phis); my = sum(Ms)/len(Ms)
cov = sum((p-mx)*(m-my) for p, m in zip(Phis, Ms))
vx = sum((p-mx)**2 for p in Phis); vy = sum((m-my)**2 for m in Ms)
r2 = cov**2/(vx*vy) if vx*vy > 0 else 0
print(f"\nM vs Φ 相關係數 r² = {r2:.4f}")
chk("C2 M 同 Φ(ℓ) 線性?", r2 > 0.95, f"(r² = {r2:.3f})")

# C3: M−√2 形狀 — 峰位置 vs 中央模
dM = [float(m - mp.sqrt(2)) for (_, e, m, p) in rows]
ells = [float(e) for (_, e, m, p) in rows]
peak_i = dM.index(max(dM))
print(f"\nM−√2 峰值 @ ℓ = {ells[peak_i]} (tracer {rows[peak_i][0]})")
print(f"中央模 γ = μ² = 2 對應 88-site k=44, 44-site n=22")
print(f"ℓ = 0.476 (LRG3) vs ℓ(γ=μ²) = ? — 相位深度 Φ = 0.3486")
chk("C3 峰值位置有冇譜對應", False, "(暫定: 需更精確判準)")

# C4: 候選 kernel 形狀 (只描述, 唔 fit)
# 如果 M(ℓ) = √2·(1 + a·(1−4^{−ℓ})·(1−ℓ/ℓ_c)) — 峰喺 ℓ_c/2
print("\n=== C4: 候選形狀對照 ===")
print(f"{'ell':>7}{'M obs':>8}{'√2·(1+0.15(1−4^−ℓ))':>20}")
for _, e, m, p in rows:
    cand = mp.sqrt(2)*(1 + mp.mpf('0.15')*(1 - mp.mpf('4')**(-e)))
    print(f"{float(e):>7.3f}{float(m):>8.4f}{float(cand):>20.4f}")

# C5: 誠實裁決 — 非單調可能來源
print()
print("裁決:")
print("  C2: M vs Φ 相關係數 — 若低, 相位深度線性映射被拒")
print("  C3: 峰值 ℓ≈0.48 對應 z≈0.93 (LRG3+ELG 合併 tracer)")
print("  C5: 非單調可能 = ELG1/LRG3 合併 tracer 系統, 或中央模共振")
print()
print("RESULT: 見 C1-C4")
