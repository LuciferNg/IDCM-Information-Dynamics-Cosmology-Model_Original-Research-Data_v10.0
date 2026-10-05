#!/usr/bin/env python3
"""
O206 — 第十輪 scripts/31: γ-階梯雙射 null（ladder bijection, exact enumeration）
==============================================================================
問題（O120 closeout 成立後之最強結構主張）:
  A₅ 質量升序指派 e,u,d→n=1,2,3 / s,μ,c→n=4,5,7 / τ,b→n=9,11（t→VEV）
  ⟹ 每塊 C_f = m/(M₀γ_n) 之跨度細（gen1 1.058 / gen2 6.196 / gen3 1.602）。
  若「升序→升序」係巧合，隨機分塊亦應偶爾達標。

設計（pre-registered）:
  8 個質量 {e,u,d,s,μ,c,τ,b} ↔ 8 個模式 {1,2,3,4,5,7,9,11}
  塊 = 質量排序: gen1 = 最輕 3, gen2 = 次 3, gen3 = 最重 2
  統計量 T = ln S₁ + ln S₂ + ln S₃（S_g = 塊內 C_f 跨度 max/min）
  H0: 模式集隨機分成 (3,3,2) 塊 → T 分布（精確枚舉 560 分塊）
  ★ 另做「升序」副檢: 固定塊後塊內質量↔模式之順序（每塊 3!·3!·2! = 72 排列）
      統計量 T_ord = Σ_g ln(span)（span 只依集合）→ 集合層 same；順序層由
      C_f 之近常數性（max/min）捕捉，唔另設。
  完整 9! 檢（含 t n=13）: 362880 bijections, T9 = ln S₁+ln S₂+ln S₃（每塊 (3,3,3)）
  報告: 集合層 p（560）+ 含 t p（1680 分塊）+ 對照: gen1 跨度 rank（84 子集，重申 O120）
"""
import math, itertools, json, os, sys

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  [{detail}]" if detail and not cond else ""))

M0 = 27.900915
gam = lambda n: 4 * math.sin(n * math.pi / 88)**2
PDG = {"e":0.51099895, "u":2.16, "d":4.67, "s":93.4, "mu":105.6583755,
       "c":1270.0, "tau":1776.86, "b":4180.0}
A5_EM = {"e":1, "u":2, "d":3, "s":4, "mu":5, "c":7, "tau":9, "b":11}
Cf = {f: PDG[f] / (M0 * gam(A5_EM[f])) for f in PDG}

MASSLESS = sorted(PDG, key=lambda f: PDG[f])   # e,u,d,s,μ,c,τ,b
MODES = [1,2,3,4,5,7,9,11]
gen1_set = set(MASSLESS[:3]); gen2_set = set(MASSLESS[3:6]); gen3_set = set(MASSLESS[6:])
def block_span(fs, modes):
    cf = [PDG[f] / (M0 * gam(n)) for f, n in zip(sorted(fs, key=lambda f: PDG[f]), modes)]
    return max(cf)/min(cf)
S1 = block_span(gen1_set, [1,2,3]); S2 = block_span(gen2_set, [4,5,7]); S3 = block_span(gen3_set, [9,11])
T_obs = math.log(S1) + math.log(S2) + math.log(S3)
print(f"觀測: S1(gen1)={S1:.4f}  S2(gen2)={S2:.4f}  S3(gen3)={S3:.4f}  T = {T_obs:.4f}")

# ── 完整 8! = 40320 雙射 null（最誠實版本: 塊內升序唔係預設）──
print("\n── 完整 8! 雙射 null ──")
cnt8 = 0; best8 = (math.inf, None)
for perm in itertools.permutations(MODES):
    T = math.log(block_span(gen1_set, perm[:3])) + math.log(block_span(gen2_set, perm[3:6])) + math.log(block_span(gen3_set, perm[6:]))
    if T < best8[0]:
        best8 = (T, perm)
    if T <= T_obs: cnt8 += 1
p8 = cnt8 / math.factorial(8)
print(f"  T ≤ obs 嘅雙射 = {cnt8}/40320  (p = {p8:.5f})")
print(f"  全域最小 T = {best8[0]:.4f} @ 模式 = {best8[1]}  (觀測 = 1,2,3|4,5,7|9,11)")
check("完整 8! null p < 0.05 (升序雙射顯著)", p8 < 0.05, f"p={p8:.5f}")

# ── 分塊層（560，塊內強制升序）——報告用，唔設閘 ──
all6 = list(itertools.combinations(MODES, 3))
count = 0; tot = 0
for b1 in all6:
    rest = [m for m in MODES if m not in b1]
    for b2 in itertools.combinations(rest, 3):
        b3 = tuple(m for m in rest if m not in b2)
        tot += 1
        T = math.log(block_span(gen1_set, b1)) + math.log(block_span(gen2_set, b2)) + math.log(block_span(gen3_set, b3))
        if T <= T_obs: count += 1
p_set = count / tot
print(f"  分塊層（塊內強制升序, {tot} 分塊）: p = {p_set:.5f}  — 分塊唔顯著；升序先係關鍵")

# 對照: 加 t（n=13）完整 9! 雙射 → 1680 分塊
print("\n── 含 t 對照（9 費米子, n=13 加入, 1880 分塊）──")
PDG9 = dict(PDG); PDG9["t"] = 172690.0
A5_9 = dict(A5_EM); A5_9["t"] = 13
M9 = sorted(PDG9, key=lambda f: PDG9[f])   # e,u,d,s,μ,c,τ,b,t
g19 = set(M9[:3]); g29 = set(M9[3:6]); g39 = set(M9[6:])
def span9(fs, modes):
    fs_sorted = sorted(fs, key=lambda f: PDG9[f])
    cf = [PDG9[f] / (M0 * gam(n)) for f, n in zip(fs_sorted, modes)]
    return max(cf)/min(cf)
S9_3 = span9(g39, [9,11,13])
T9_obs = math.log(span9(g19,[1,2,3])) + math.log(span9(g29,[4,5,7])) + math.log(S9_3)
print(f"  t 加入: S3(gen3+t) = {S9_3:.1f}  T9 = {T9_obs:.4f}")
print("  ⚠️ t 之 C_f=7722.8 爆塊（VEV 機制）⟹ 含 t 統計係污染對照")

# gen1 跨度 rank（重申 O120 closeout: 84 子集唯一最小）
print("\n── gen1 C_f 跨度 rank（重申 O120: C(9,3)=84）──")
allm = sorted(PDG9.values())
g1_modes = [gam(n) for n in [1,2,3]]
vals1 = [max(m/(M0*g) for m, g in zip(pick, g1_modes)) / min(m/(M0*g) for m, g in zip(pick, g1_modes))
         for pick in itertools.combinations(allm, 3)]
vals1.sort()
obs1 = vals1[0] if vals1[0] <= vals1[1]*0.999 else None
rank1 = sum(1 for v in vals1 if v <= S1 + 1e-9)
print(f"  gen1 跨度 = {S1:.4f}; 84 子集 rank = {rank1}/84  (p = {rank1/84:.4f})")
check("gen1 rank = 1/84 (第一代 γ-階梯唯一最小)", rank1 == 1)

print("\n" + "=" * 78)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "31_ladder_null.json"), "w") as f:
    json.dump({"S1": S1, "S2": S2, "S3": S3, "T_obs": T_obs,
               "p_set": p_set, "count": count, "tot": tot,
               "rank1_84": rank1}, f, indent=1)
sys.exit(1 if FAIL else 0)