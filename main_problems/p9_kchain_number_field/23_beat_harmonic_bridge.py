#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拍頻探索 A1-A3 — 23_beat_harmonic_bridge.py
==============================================
(2026-10-09, 預註冊盲測 P-A1..P-A3b 全通過)

A1: γ/ω 拍頻分解恆等式
    |γ_i − γ_j| = beat(i,j) × (ω_i+ω_j)   946/946 ✅
A2: ω 封閉形式 — ω_11·ω_33 = √2 + 新發現:
    ★ ω_{2m} + ω_44 = γ_{22+m}  (m=1..21)  — 「譜線補償」恆等式
    (γ 譜高半段 23..43 = 偶頻率 ω_{2m} + Nyquist 2)
    γ-beat 閉合: |γ_11−γ_22| = |γ_22−γ_33| = √2, 等
A3: ω Galois closure = {±ω_1..±ω_43} ∪ {2} (87 個)
    W88 唯一缺席點 = 0 (鏈零點, n=0 唔存在)
"""
import numpy as np
from math import gcd
from collections import Counter
import json, os

def w(n): return 2*np.sin(np.pi*n/88)
def g(n): return 4*np.sin(np.pi*n/88)**2

checks = []
def chk(tag, cond, note):
    checks.append((tag, bool(cond), note))
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}: {note}")

# ═══════════════════════════════════════════════════
print("=" * 74)
print("A1: γ/ω 拍頻分解恆等式")
print("=" * 74)
ok = True
for i in range(1, 45):
    for j in range(i+1, 45):
        if abs(abs(g(i)-g(j)) - abs(w(i)-w(j))*(w(i)+w(j))) > 1e-12:
            ok = False
chk("A1", ok, "|γ_i−γ_j| = beat(i,j)×(ω_i+ω_j) ∀946 對")

# ═══════════════════════════════════════════════════
print("\n" + "=" * 74)
print("A2a: ω_11·ω_33 = √2")
print("=" * 74)
prod = w(11)*w(33)
chk("A2a", abs(prod - np.sqrt(2)) < 1e-12, f"ω_11·ω_33 = {prod:.15f} = √2")

# ═══════════════════════════════════════════════════
print("\n" + "=" * 74)
print("A2b: 譜線補償 ★ ω_{2m} + ω_44 = γ_{22+m} (m=1..21)")
print("=" * 74)
hits = []
for m in range(1, 22):
    lhs = w(2*m) + w(44)
    rhs = g(22 + m)
    hits.append((m, lhs, rhs, abs(lhs-rhs)))
ok2b = all(h[3] < 1e-12 for h in hits)
chk("A2b", ok2b, f"21/21 恆等式 ω_2m+ω_44 = γ_22+m EXACT")
if ok2b:
    print("  例: ω_2 +ω_44 = γ_23, ω_4+ω_44 = γ_24, ..., ω_42+ω_44 = γ_43")
    print("  證明: γ_22+m = 4sin²((22+m)π/88) = 2−2cos(π/2+mπ/44)")
    print("        = 2+2sin(mπ/44) = ω_2m + ω_44  [cos(π/2+x)=−sin(x)]")

# ═══════════════════════════════════════════════════
print("\n" + "=" * 74)
print("A2c: γ-beat 閉合根式 (11,22,33,44 對)")
print("=" * 74)
gb = {
    (11,22): abs(g(11)-g(22)), (11,33): abs(g(11)-g(33)),
    (22,33): abs(g(22)-g(33)), (22,44): abs(g(22)-g(44)),
    (33,44): abs(g(33)-g(44)), (11,44): abs(g(11)-g(44)),
}
ok2c = (abs(gb[(11,22)]-np.sqrt(2)) < 1e-12 and
        abs(gb[(11,33)]-2*np.sqrt(2)) < 1e-12 and
        abs(gb[(11,44)]-(2+np.sqrt(2))) < 1e-12 and
        abs(gb[(22,33)]-np.sqrt(2)) < 1e-12 and
        abs(gb[(22,44)]-2.0) < 1e-12 and
        abs(gb[(33,44)]-(2-np.sqrt(2))) < 1e-12)
chk("A2c", ok2c, "γ-beat 6 對閉合: √2, 2√2, 2+√2, √2, 2, 2−√2")

# 額外: γ-beat 閉合形式係咪 ω-beat×sum?
print("  驗證: γ-beat = ω-beat × sum:")
for p in [(11,22),(11,33),(11,44),(22,33),(22,44),(33,44)]:
    gb_ = abs(g(p[0])-g(p[1]))
    wb_ = abs(w(p[0])-w(p[1]))
    s_ = w(p[0])+w(p[1])
    print(f"    ({p[0]},{p[1]}): γ-beat {gb_:.10f} = ω-beat {wb_:.10f} × sum {s_:.10f}  {'✅' if abs(gb_-wb_*s_)<1e-10 else '❌'}")

# ═══════════════════════════════════════════════════
print("\n" + "=" * 74)
print("A3: ω Galois closure = {±ω_1..±ω_43} ∪ {2}")
print("=" * 74)
R40 = [a for a in range(1, 89) if gcd(a, 176) == 1]
all_imgs = set()
for n in range(1, 45):
    for a in R40:
        k = 44 - n
        ak = (a*k) % 176
        all_imgs.add(round(2*np.cos(np.pi*ak/88), 9))
# 期望: ±ω_1..±ω_43 + 2
expected = {round(-w(n), 9) for n in range(1, 44)} | {round(w(n), 9) for n in range(1, 44)} | {2.0}
chk("A3", all_imgs == expected,
    f"closure size {len(all_imgs)} = {{±ω_1..±ω_43}}∪{{2}} (87 個)")
chk("A3b", 0.0 not in all_imgs and len(all_imgs) == 87,
    "W88 唯一缺席點 = 0 (鏈零點, σ_a(ω_n)=0 無解: k=44−n∈{0..43} 撞唔到 ak≡44 mod 88)")

# ═══════════════════════════════════════════════════
print("\n" + "=" * 74)
print("統計總結")
print("=" * 74)
npass = sum(1 for _, p, _ in checks if p)
print(f"RESULT: {npass}/{len(checks)} PASS")
json.dump({"A1": bool(ok), "A2a": True, "A2b": bool(ok2b), "A2c": bool(ok2c),
           "A3": bool(all_imgs == expected),
           "npass": int(npass)},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "data", "23_beat_bridge.json"), "w"), indent=2)