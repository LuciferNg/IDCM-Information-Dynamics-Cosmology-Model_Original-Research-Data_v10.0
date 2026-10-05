#!/usr/bin/env python3
"""
O137 — #1 Round 3d: A₅ 模式集 × 質量排序 × O137 γ_n 框架

背景: O136 docs/19 嘅 A₅ 動差準則 (質量無關, 第一性原理):
  奇 n: 首個非零奇動差 l=15  ⟹ n ≤ 13 (奇) → 7 模式
  偶 n: 首個非零偶動差 l=6   ⟹ n ≤ 4 (偶)  → 2 模式
  合計 9 模式 = {1,2,3,4,5,7,9,11,13} = 3 輕子 + 6 夸克

測試: 若呢 9 模式【按質量升序】配對, O137 公式 m = M₀γ_n·C_f 嘅 C_f 有無結構?
"""
import numpy as np
from math import sin, pi

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2

MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]

# ---- A₅ 集驗證 ----
odd_le13  = [n for n in range(1,14) if n%2==1]
even_le4  = [n for n in range(2,5) if n%2==0]
print(f"奇 n ≤ 13: {odd_le13} ({len(odd_le13)} 個 = L₄=7)")
print(f"偶 n ≤ 4 : {even_le4} ({len(even_le4)} 個 = 2)")
print(f"合計: {sorted(odd_le13+even_le4)}  = A₅ 集? {sorted(odd_le13+even_le4)==A5}")

# ---- 質量升序配對 ----
order = sorted(MASS, key=lambda p: MASS[p])
print(f"\n質量升序: {[(p, MASS[p]) for p in order]}")
print(f"模式升序: {A5}")

print("\n" + "="*76)
print("A₅ 模式集 × 質量升序配對: m = M₀·γ_n·C_f")
print("="*76)
print(f"{'粒子':>5} {'n':>3} {'γ_n':>10} {'M₀γ_n':>10} {'m_obs':>10} {'C_f 反解':>10}  {'世代':>4}")
rows = []
gen_map = {'e':1,'u':1,'d':1,'s':2,'mu':2,'c':2,'tau':3,'b':3,'t':3}
for p, n in zip(order, A5):
    g = gamma_n(n); mg = M0*g; C = MASS[p]/mg
    rows.append((p,n,g,mg,MASS[p],C))
    print(f"{p:>5} {n:>3} {g:>10.6f} {mg:>10.4f} {MASS[p]:>10.4f} {C:>10.4f}  {gen_map[p]:>4}")

print("\n--- 世代內 C_f 一致性 ---")
for gen in [1,2,3]:
    ps = [r for r in rows if gen_map[r[0]]==gen]
    Cs = [r[5] for r in ps]
    print(f"Gen{gen}: C_f = {[round(c,3) for c in Cs]}  跨度 {max(Cs)/min(Cs):.3f}×  "
          f"mean={np.mean(Cs):.3f} std/mean={np.std(Cs)/np.mean(Cs)*100:.2f}%")

print("\n--- 全部 9 粒子 C_f 跨度 ---")
allC = [r[5] for r in rows]
print(f"C_f 範圍 [{min(allC):.3f}, {max(allC):.3f}]  跨度 {max(allC)/min(allC):.1f}×")

# ---- ★ 第一代: C_f ≈ 3.6 = L₆/F₅ ? ----
print("\n" + "="*76)
print("★ 第一代測試: C_f = 3.6 = L₆/F₅ (O54 電子因子) 統一?")
print("="*76)
C36 = 18/5
print(f"\n{'粒子':>5} {'n':>3} {'m_pred = M₀γ_n×3.6':>20} {'m_obs':>10} {'Δ%':>8}")
devs = []
for p,n,g,mg,m,C in rows[:3]:
    mp = mg*C36; dev = (mp-m)/m*100; devs.append(abs(dev))
    print(f"{p:>5} {n:>3} {mp:>20.4f} {m:>10.4f} {dev:>+8.2f}")
print(f"\n第一代 RMS 偏差 = {np.sqrt(np.mean(np.square(devs))):.2f}%")

# ---- ★★ m ∝ n² 測試 (第一代) ----
print("\n" + "="*76)
print("★ m ∝ n² 測試 (γ_n ≈ (nπ/44)² for small n)")
print("="*76)
print(f"\n{'粒子':>5} {'n':>3} {'n²':>4} {'m_obs':>10} {'m/n²':>10}")
r2 = []
for p,n,g,mg,m,C in rows[:3]:
    print(f"{p:>5} {n:>3} {n*n:>4} {m:>10.4f} {m/(n*n):>10.4f}")
    r2.append(m/(n*n))
print(f"\nm/n² 跨度: {max(r2)/min(r2):.4f}×  ({min(r2):.4f} → {max(r2):.4f})")
print(f"觀測比 m_e:m_u:m_d = {MASS['e']:.4f} : {MASS['u']:.4f} : {MASS['d']:.4f}")
print(f"              = 1 : {MASS['u']/MASS['e']:.4f} : {MASS['d']/MASS['e']:.4f}")
print(f"n² 預言        = 1 : 4 : 9")
print(f"偏差: u {(MASS['u']/MASS['e']/4-1)*100:+.2f}%,  d {(MASS['d']/MASS['e']/9-1)*100:+.2f}%")

# ---- null test: 隨機質量能否給出同樣緊嘅 m/γ 常數? ----
print("\n" + "="*76)
print("null test: 隨機第一代質量 → m/γ_n 常數性")
print("="*76)
rng = np.random.default_rng(20260830)
g3 = [gamma_n(1), gamma_n(2), gamma_n(3)]
obs_spread = max(r2)/min(r2)
cnt = 0; N = 20000
for _ in range(N):
    ms = 10**rng.uniform(np.log10(0.3), np.log10(8.0), 3)
    rr = [ms[i]/g3[i] for i in range(3)]
    if max(rr)/min(rr) <= obs_spread: cnt += 1
print(f"觀測 m/γ 跨度 = {obs_spread:.4f}")
print(f"null (20000 隨機質量三元組, log-uniform [0.3,8]): P(跨度 ≤ 觀測) = {cnt/N:.4f}")
print(f"⟹ {'🟢 顯著' if cnt/N < 0.05 else '🔴 唔顯著 (密度效應可解釋)'}")

# ---- 世代比測試: C_f 世代結構 ----
print("\n" + "="*76)
print("世代比測試: m/γ_n 跨世代")
print("="*76)
print(f"{'世代':>5} {'C_f mean':>10} {'vs Gen1':>10}")
c1 = np.mean([r[5] for r in rows if gen_map[r[0]]==1])
for gen in [1,2,3]:
    cm = np.mean([r[5] for r in rows if gen_map[r[0]]==gen])
    print(f"{gen:>5} {cm:>10.4f} {cm/c1:>10.3f}")
print(f"\nIDCM 結構常數候選: 44=N_d, 123=L₁₀, 88, 36=h11, 61.5=E_proj, 90")
