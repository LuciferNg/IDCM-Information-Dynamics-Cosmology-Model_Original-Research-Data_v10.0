#!/usr/bin/env python3
"""
O53 路徑一 (深化): q = -ln(J*)/2π 嘅 1/12 格點結構
=====================================================
發現: q ∈ [0.518, 1.072], 離 1/12 格點 mean 0.0195!

分析:
  1. q 值 vs 1/12 格點 {1/2, 7/12, 2/3, 3/4, 5/6, 11/12, 1}
  2. q = m/12 嘅整數 m 分佈
  3. e^(-2π·q) = instanton 因子 — 有冇物理意義?
  4. 同 K_Chain 44/88 關係
"""
import os, json, math, sys
import numpy as np
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 路徑一深化: q = m/12 格點")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
lnJ = np.log(J0)
q = -lnJ / (2*math.pi)

print(f"\n[1] q 值 (36 個):")
q12 = np.round(q*12)/12
print(f"    q:    {np.array2string(q, precision=3)}")
print(f"    m=12q: {np.array2string(np.round(q*12).astype(int), precision=0)}")
# 分佈
m = np.round(q*12).astype(int)
print(f"    m 分佈: {dict(sorted(Counter(m.tolist()).items()))}")
print(f"    m 範圍: {m.min()} 至 {m.max()}")
print(f"    m 值: {sorted(set(m.tolist()))}")

# --- [1] m = 12q 有冇結構? ---
print(f"\n[2] m = 12q 分析:")
print(f"    m ∈ {sorted(set(m.tolist()))}")
print(f"    m 數: {len(set(m.tolist()))} 個唔同值 (36 個 q)")
# 6-13?
print(f"    m 範圍 6-13 → 8 個值?")
print(f"    m/12: {sorted(set((m/12).tolist()))}")

# --- [2] 對應 instanton 因子 ---
print(f"\n[3] Instanton 因子 e^(-2πq) = e^(-πm/6):")
for mm in sorted(set(m.tolist())):
    qq = mm/12
    factor = math.exp(-2*math.pi*qq)
    print(f"    m={mm:2d}: q={qq:.4f}, e^(-2πq) = {factor:.6f} = {factor*100:.2f}%")

# --- [3] 1/12 格點誤差 ---
print(f"\n[4] 格點誤差:")
q12_err = np.abs(q - q12)
print(f"    mean|Δ| = {q12_err.mean():.4f}")
print(f"    max|Δ| = {q12_err.max():.4f}")
check("q 離 1/12 格點 < 0.03", q12_err.mean() < 0.03, f"(mean {q12_err.mean():.4f})")

# 隨機對照
rng = np.random.default_rng(42)
rand_q = rng.uniform(0.5, 1.1, 36)
rand_err = np.abs(rand_q - np.round(rand_q*12)/12)
print(f"    隨機對照 mean|Δ| = {rand_err.mean():.4f}")
check("q 格點誤差 << 隨機", q12_err.mean() < rand_err.mean()*0.5, 
      f"({q12_err.mean():.4f} vs {rand_err.mean():.4f})")

# --- [4] m 同 44/88 關係 ---
print(f"\n[5] m 同 K_Chain:")
print(f"    m ∈ [6, 13]")
print(f"    44/4 = 11, 88/8 = 11")
print(f"    m=11 出現幾次? {list(m).count(11)}")
print(f"    m=12 出現? {list(m).count(12)}")
print(f"    m=8? {list(m).count(8)}")
# m 平均
print(f"    mean m = {m.mean():.2f}")
print(f"    mean q = {q.mean():.4f}")
print(f"    mean J* = {J0.mean():.6f}")
print(f"    e^(-2π·mean q) = {math.exp(-2*math.pi*q.mean()):.6f}")

# --- [5] 同 γ 譜 (K_Chain) 比較 ---
print(f"\n[6] q 譜 vs K_Chain γ 譜:")
gammas = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])
# q 譜 (排序)
q_sorted = np.sort(q)
print(f"    q 排序: {np.array2string(q_sorted, precision=3)}")
print(f"    q 間距: {np.array2string(np.diff(q_sorted), precision=3)}")
# 有冇 2 個 cluster?
print(f"    q < 0.6: {np.sum(q < 0.6)}")
print(f"    q < 0.7: {np.sum(q < 0.7)}")
print(f"    q > 0.9: {np.sum(q > 0.9)}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
