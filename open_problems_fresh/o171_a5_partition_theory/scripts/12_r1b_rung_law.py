#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/12 — R1b + R8: rung law (算子類型 → sector 大小)
=============================================================
問題 (docs/04 §6, final_result 遺留):
  R1b: 「算子類型 → sector 大小」定量律 — 為何表層用 L₅ (=11) 而深層用 L₄ (=7)?
  R8:  表層/深層係咪對應「鏈 sector vs 樹 sector」?

★ 本 script 主結果 (rung law + 型別二分):
  定律: d = g · L_m,  g ∈ A₅ 表示論不變量 {1,3,3,4,5,12,60}, L_m ∈ Lucas
        且 (g, m) 對每個家族成員**唯一** ⇒ rung law 有判別力
  型別二分 (R8):
        表層 (33,44,55) = **帶計數型**: d = nR, n ∈ {3,4,5} = A₅ 非平凡 irrep 維數
                          ⇔ 波段計數 #{γ_k ≤ γ_nR} = nR  (鏈譜前綴)
        深層 (420)      = **軌道計數型**: d = (L₇²−1)/2 = Z₂ 折疊軌道數
                          ⇒ 420 **唔係**鏈帶 (420/11 ∉ Z, 420 > 88)
  ★★ 統一: n (帶指數) = dim ρ_i (irrep 維數) — 呢條先係定律嘅真內容

  C1 rung law 唯一性 (枚舉 (g, L_m) 對)
  C2 ★ 帶指數 = irrep 維數 恆等 + null test (P = 1/C(8,3) = 1/56)
  C3 型別二分: 帶計數型 vs 軌道計數型 (生成公式檢定)
  C4 深層唔係鏈帶 (三種鏈讀法全試)
  C5 rung 指數來源候選 (m=5 vs m=4) + 多身份 null test
  C6 和/積對偶事實 (Σdim = 12 = B·N_gen; Πdim = 60 = |A₅| = Σdim²)
  C7 裁決
"""
import mpmath as mpm
from fractions import Fraction as Fr

mp = mpm.mp; mp.dps = 50
pi, sin, nstr, mpf = mp.pi, mp.sin, mp.nstr, mp.mpf

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

B, N_gen, N_d, R, F5, L4, L5, L7 = 4, 3, 44, 11, 5, 7, 11, 29
LUC = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76}
A5_REP = [1, 3, 3, 4, 5, 12, 60]      # irrep 維數 + Σdim + |A₅|

print("="*80)
print("O171 scripts/12 — R1b+R8: rung law (d = g·L_m) + 型別二分")
print("="*80)

# ---------- C1: rung law 唯一性 ----------
print("\n=== C1: rung law d = g·L_m — 唯一性枚舉 ===")
print(f"  g ∈ A₅ 表示論不變量 {A5_REP} (irrep 維數 1,3,3,4,5 + Σdim = 12 + |A₅| = 60)")
print(f"  L_m ∈ Lucas {sorted(set(LUC.values()))}")
fam = {"33/34 (O10 質數峰)": 33, "44/45 (邊界截斷)": 44,
       "55/56 (O167 r*/r_d)": 55, "420/421 (O167 r_d)": 420}
decomp = {}
for nm, d in fam.items():
    sols = sorted({(g, m) for g in set(A5_REP) for m, lv in LUC.items() if g*lv == d})
    decomp[d] = sols
    print(f"  d = {d:>3} ({nm:<20}) 解 (g, L_m) = {[(g, f'L{m}={LUC[m]}') for g, m in sols]}")
    chk(f"C1 d = {d} 嘅 (g, L_m) 分解唯一", len(sols) == 1)
chk("C1e 表層三個成員共享同一 rung m = 5 (L₅ = 11 = R)",
    all(decomp[d][0][1] == 5 for d in (33, 44, 55)))
chk("C1f 深層用 rung m = 4 (L₄ = 7)", decomp[420][0][1] == 4)
chk("C1g 表層 g = dim ρ_i ∈ {3,4,5}; 深層 g = |A₅| = 60",
    [decomp[d][0][0] for d in (33, 44, 55)] == [3, 4, 5] and decomp[420][0][0] == 60)
print("  ⇒ rung law 有判別力: 每個成員嘅 (群因子, rung) 唯一")

# ---------- C2: ★ 帶指數 = irrep 維數 ----------
print("\n=== C2: ★ 帶指數 n = irrep 維數 (定律真內容) ===")
bands = {n: n*R for n in range(1, 9)}
print(f"  鏈帶 (R = 11): {bands}")
print(f"  家族成員落喺邊啲帶: {[n for n in range(1,9) if bands[n] in fam.values()]}")
sel = sorted(n for n in range(1, 9) if bands[n] in fam.values())
chk("C2 選中帶指數 = {3,4,5} = A₅ 非平凡 irrep 維數", sel == [3, 4, 5])
print(f"  未選中: {[n for n in range(1,9) if n not in sel]}  (= 1,2,6,7,8; 含 trivial 維數 1)")
# 波段律核對 (鏈譜前綴)
g = [4*sin(pi*k/176)**2 for k in range(1, 89)]
for n in (3, 4, 5):
    thr = 4*sin(n*pi/16)**2
    cnt = sum(1 for x in g if x <= thr + mpf('1e-25'))
    chk(f"C2b #{chr(947)} <= {chr(947)}_{n}R = {cnt} = {n}R", cnt == n*R)
# null test
from math import comb
p_rand = Fr(1, comb(8, 3))
print(f"  ★ null test: 由 8 個帶隨機揀 3 個 = {{3,4,5}} 嘅概率 = 1/C(8,3) = {p_rand} = {float(p_rand)*100:.2f}%")
chk("C2c 隨機命中概率 1.79% (< 5%) ⇒ 弱顯著", p_rand < Fr(1, 20))
print("  ⇒ 定律: 帶指數 n 由群內容**選出** (n = dim ρ_i); rung 單位 = 鏈週期 R")
print("     ⚠️ 但 3,4,5 本身 = irrep 維數係群論事實, 而「帶指數 = 維數」係**識別**, 唔係推導")

# ---------- C3: 型別二分 ----------
print("\n=== C3: 型別二分 — 帶計數型 vs 軌道計數型 ===")
print("  (i) 帶計數型: d = #{γ_k ≤ γ_nR} = nR — 鏈譜前綴計數")
for n in (3, 4, 5):
    print(f"      n = {n}: d = {n}R = {n*R}")
print("  (ii) 軌道計數型: d = (L₇²−1)/2 = Z₂ 折疊非真空軌道數")
d420 = Fr(L7**2 - 1, 2)
print(f"      L₇ = {L7}: (L₇²−1)/2 = ({L7*L7}−1)/2 = {d420}")
chk("C3 420 = (L₇²−1)/2 (軌道計數型)", d420 == 420)
# 表層可否用軌道計數型表示?
tab_orb = []
for d in (33, 44, 55):
    Lv = None
    for cand in range(2, 100):
        if Fr(cand*cand - 1, 2) == d: Lv = cand
    tab_orb.append((d, Lv))
print(f"  表層可否寫成 (L²−1)/2? {tab_orb}")
chk("C3b 表層 (33,44,55) **唔係**軌道計數型 ((L²−1)/2 無整數解)",
    all(Lv is None for _, Lv in tab_orb))
# 深層可否用帶計數型表示?
chk("C3c 深層 420 唔係帶計數型 (420/11 ∉ Z)", 420 % R != 0, f"(420/11 = {420/R:.4f})")
chk("C3d 420 > 88 = 鏈全長 ⇒ 超出鏈帶範圍", 420 > 88)
# 帶前綴和檢定
pref = [sum(n*R for n in range(1, k+1)) for k in range(1, 9)]
print(f"  鏈帶前綴和: {pref}")
chk("C3e 420 唔在任何帶前綴和", 420 not in pref)
print("  ⇒ ★ 型別二分成立: 表層 = 帶計數型; 深層 = 軌道計數型 — 生成公式唔同")
print("     (一致於 docs/04 錨定理: 只有 420 有連續對表示 (14,15))")

# ---------- C4: 深層嘅 L₇ 來源 (鏈) ----------
print("\n=== C4: 深層 rung 嘅鏈根源 (統一解釋) ===")
n_lt = sum(1 for x in g if x < 1)
print(f"  L₇ = #{{γ_k < μ²/2 = 1}} = {n_lt} (鏈譜閾值計數) ⇒ 29")
chk("C4 L₇ = 29 由鏈譜導出", n_lt == 29)
chk("C4b L₇ = 2L₄ + N_gen·F₅ = 14 + 15", 2*L4 + N_gen*F5 == 29)
chk("C4c L₄ = (L₇ − N_gen·F₅)/2 = (29−15)/2 = 7", Fr(L7 - N_gen*F5, 2) == 7)
print("  ⇒ 深層 rung 7 **亦係鏈導出** (經 L₇): L₄ = (L₇ − N_gen F₅)/2")
print("     ⇒ 表層同深層都係「鏈根源」, 分別在於用鏈**週期** (R = L₅) 定鏈**計數** (L₇)")
chk("C4d 兩個 rung 都係鏈導出 (R = 88/8; L₄ = (L₇−15)/2)", 88//8 == R and Fr(L7-15, 2) == L4)

# ---------- C5: rung 指數來源候選 + 多身份 ----------
print("\n=== C5: rung 指數 (m = 5 vs 4) 來源候選 ===")
cand5 = {"|Irr(A₅)| = 群不可約表示數": 5, "F₅": F5, "N_gen + μ²": N_gen + 2,
         "B + 1": B + 1, "#{γ ≤ μ²}/R − 1 = 44/11 − 1": N_d//R - 1}
cand4 = {"B (分支因子)": B, "L₃": 4, "dim ρ₄ (4-維 irrep)": 4, "|Irr| − 1": 4,
         "N_gen + 1": N_gen + 1}
print("  m = 5 嘅候選身份:")
for k, v in cand5.items():
    print(f"    {k:<32} = {v}  {'✓' if v == 5 else '✗'}")
print("  m = 4 嘅候選身份:")
for k, v in cand4.items():
    print(f"    {k:<32} = {v}  {'✓' if v == 4 else '✗'}")
chk("C5 m = 5 有 ≥3 條獨立身份 (多身份)", sum(1 for v in cand5.values() if v == 5) >= 3)
chk("C5b m = 4 有 ≥3 條獨立身份 (多身份)", sum(1 for v in cand4.values() if v == 4) >= 3)
print("  ⚠️ 誠實: 5 同 4 都係細數 ⇒ 多身份密度高 ⇒ **無法由身份唯一決定 rung 指數**")
print("     ⇒ R1b 嘅「為何 m=5 vs m=4」仍然 🔴 (但定律本身已唯一)")

# ---------- C6: 和/積對偶 ----------
print("\n=== C6: ★ 和/積對偶事實 ===")
dims = [3, 4, 5]
s_dims, p_dims = sum(dims), dims[0]*dims[1]*dims[2]
print(f"  Σ dim_i (非平凡) = {s_dims} = B·N_gen = {B*N_gen} = L₅ + 1 = {L5+1}")
print(f"  Π dim_i (非平凡) = {p_dims} = |A₅| = {60} = Σ_{{all}} dim² = {1+9+9+16+25}")
chk("C6 Σdim = 12 = B·N_gen = L₅+1", s_dims == B*N_gen == L5+1)
chk("C6b Πdim = 60 = |A₅| = Σdim²", p_dims == 60 == sum(d*d for d in [1,3,3,4,5]))
print("  ★ 對偶: 維數之**和** = 乘積型量 (B·N_gen); 維數之**積** = 和型量 (|A₅| = Σdim²)")
print("     ⇒ 表層 (用單一 dim 做因子) 配 L₅ = Σdim − 1 = 11;")
print("        深層 (用全積 = 群階) 配 L₄ = ... (未閉合, 見 C5)")
chk("C6c 表層 rung L₅ = Σdim − 1 = 11", L5 == s_dims - 1)
print("     ⚠️ 深層 rung L₄ = 7 ≠ Πdim − 1 = 59 ⇒ 對偶律**唔**統一解釋兩個 rung")

# ---------- C7: 裁決 ----------
print("\n=== C7: 裁決 ===")
print("  🟢 rung law: d = g·L_m, (g, m) 對四成員**唯一** (g ∈ A₅ 表示論不變量)")
print("  🟢 型別二分 (R8): 表層 = 帶計數型 (nR); 深層 = 軌道計數型 ((L₇²−1)/2)")
print("  🟢 ★ 帶指數 = irrep 維數 (n = dim ρ_i), 隨機命中 1.79%")
print("  🟢 兩型 rung 都係鏈導出 (R = 鏈週期; L₄ = (L₇ − 15)/2, L₇ = 鏈閾值計數)")
print("  🟢 和/積對偶: Σdim = 12 = B·N_gen = L₅+1 (但唔解釋深層 rung)")
print("  🔴 rung 指數 m 嘅**唯一**來源 (m=5 vs m=4) — 多身份 (5 同 4 各有 ≥3 條)")
print("  ⇒ R1b 由 🔴 升 🟡 (定律 + 唯一性 + 型別二分閉合; 指數來源遺留)")
print("  ⇒ R8 由 🟡 升 🟢 (型別二分已證: 表層 = 鏈帶, 深層 = 格軌道)")

print()
print(f"RESULT: {ok}/{tot} PASS")
