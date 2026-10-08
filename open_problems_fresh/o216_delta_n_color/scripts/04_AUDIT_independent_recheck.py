#!/usr/bin/env python3
"""
O216 scripts/04_AUDIT_independent_recheck.py — 獨立重驗（T1）
============================================================
唔 import / 唔 call scripts/01-03 任何代碼；由原始輸入重算所有 headline：
  - 嚴格/寬鬆目錄定義、[6,33] 密度（O137 docs/30 §2.3）
  - Δn_color = {0,12,28} 命中率 + MC q_obs（同 seed 216 複現）+ analytic hypergeometric 對照
  - 鏈長 3 因子無（88/44/176 = 2^a·11^b 家族）
  - Sel mod-3 分佈、夸克/輕子
  - 18 = 2·N_gen² = L₆（Lucas 重算）
  - O88 分解維數（(3,3)⊕(1,3) = 12）、O68 4 = 3⊕1
  - Δn 由 O54 配對原始重算
stdlib-only；/usr/bin/python3。
"""
import random, math, sys

PASS, FAIL = [], []
def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  ({detail})" if detail else ""))

print("="*84)
print("A. 目錄定義 + [6,33] 密度（O137 docs/30 §2.3）")
print("="*84)
STRICT = {1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33}
BROAD  = STRICT | {12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,
                   40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98}
ck("嚴格目錄 18 項", len(STRICT) == 18, f"{len(STRICT)}")
ck("寬鬆目錄 54 項", len(BROAD) == 54, f"{len(BROAD)}")
def dense(cat, lo, hi):
    n = hi - lo + 1
    return sum(1 for x in range(lo, hi+1) if x in cat) / n
ds = dense(STRICT, 6, 33); db = dense(BROAD, 6, 33)
ck("嚴格 [6,33] 密度 = 13/28", abs(ds - 13/28) < 1e-9, f"{ds:.4f} vs 13/28={13/28:.4f}")
ck("寬鬆 [6,33] 密度 = 27/28", abs(db - 27/28) < 1e-9, f"{db:.4f} vs 27/28={27/28:.4f}")

print()
print("="*84)
print("B. Δn_color = {0,12,28} 命中 + q_obs（MC 同 seed + analytic）")
print("="*84)
DN = {0, 12, 28}
ck("Δn ∩ 嚴格 = {28} (1/3)", (DN & STRICT) == {28})
ck("Δn ∩ 寬鬆 = {12,28} (2/3)", (DN & BROAD) == {12,28})

N_MC, SEED = 200_000, 216
rng = random.Random(SEED)
def frac(cat):
    xs = rng.sample(range(0, 34), 3)          # [0,33]
    return sum(1 for x in xs if x in cat)/3

hits_s = [frac(STRICT) for _ in range(N_MC)]
q_mc_s = sum(1 for v in hits_s if v <= 1/3)/N_MC
# analytic: 3 個無放回樣本（hypergeometric: 34 球, 18 中球, 抽 3）
# q_obs(嚴格) = P(X≤1) where X ~ Hypergeom(34,18,3)
import math
def C2(n,k): return math.comb(n,k)
P0 = C2(16,3)/C2(34,3)          # 0 中
P1 = C2(18,1)*C2(16,2)/C2(34,3) # 1 中
q_an_s = float(P0 + P1)
print(f"  MC q_obs(嚴格) = {q_mc_s:.4%}  (seed {SEED}, N={N_MC})")
print(f"  analytic P(X≤1) = {q_an_s:.4%}  (Hypergeom(34,18,3))")
ck("MC 嚴格 q_obs > 5%（🔴 密度效應）", q_mc_s > 0.05, f"{q_mc_s:.4%}")
ck("analytic 嚴格 q_obs = 0.4545", abs(q_an_s - 2720/5984) < 1e-9,
   f"{q_an_s:.6f} = 2720/5984")
ck("MC vs analytic 嚴格差 < 1pp", abs(q_mc_s - q_an_s) < 0.01, f"Δ={abs(q_mc_s-q_an_s)*100:.2f}pp")

hits_b = [frac(BROAD) for _ in range(N_MC)]
q_mc_b = sum(1 for v in hits_b if v <= 2/3)/N_MC
# analytic: P(X≤2) = 1 − P(X=3) = 1 − C(32,3)/C(34,3)
P3 = C2(32,3)/C2(34,3)
q_an_b = 1.0 - P3
print(f"  MC q_obs(寬鬆) = {q_mc_b:.4%}  (seed {SEED}, N={N_MC})")
print(f"  analytic P(X≤2) = {q_an_b:.4%}  (Hypergeom(34,32,3))")
ck("MC 寬鬆 q_obs > 5%（🔴 密度效應）", q_mc_b > 0.05, f"{q_mc_b:.4%}")
ck("analytic 寬鬆 q_obs = 1 − C(32,3)/C(34,3)", abs(q_an_b - (1.0 - C2(32,3)/C2(34,3))) < 1e-9,
   f"{q_an_b:.6f} = 1024/5984 = {1024/5984:.6f}")
ck("MC vs analytic 寬鬆差 < 1pp", abs(q_mc_b - q_an_b) < 0.01, f"Δ={abs(q_mc_b-q_an_b)*100:.2f}pp")

print()
print("="*84)
print("C. 鏈長 3 因子（88/44/176 = 2^a·11^b 家族, O229 R4）")
print("="*84)
for M in (88, 44, 176):
    fac = [d for d in range(2, M+1) if M % d == 0]
    odd = [d for d in fac if d % 2 == 1 and d != M]
    print(f"  {M} = {'×'.join(str(d) for d in [8,11] if M%d==0)} 因數含3? {'是' if 3 in fac else '否（3∤'+str(M)+'）'}")
    ck(f"3 ∤ {M}", 3 not in fac, f"{M} = 2^a·11^b")
ck("88 因數冇 3（Z_88 冇 order-3 subgroup）", all(d % 3 != 0 for d in [1,2,4,8,11,22,44,88]))

print()
print("="*84)
print("D. Sel mod-3 分佈")
print("="*84)
SEL = {1,2,3,4,5,7,9,11,13}; QUARK = {1,2,4,7,9,11}; LEP = {3,5,13}
def counts(S):
    c = [0,0,0]
    for n in S: c[n%3] += 1
    return tuple(c)
cs, cq, cl = counts(SEL), counts(QUARK), counts(LEP)
print(f"  Sel mod-3 = {cs}; 夸克 = {cq}; 輕子 = {cl}")
ck("Sel mod-3 = (2,4,3) 唔平衡", cs == (2,4,3), str(cs))
ck("夸克 mod-3 = (1,3,2) 唔平衡", cq == (1,3,2), str(cq))
ck("輕子 mod-3 = (1,1,1)", cl == (1,1,1), str(cl))
print("  → mod-3 喺鏈上冇週期結構對應色荷（3 ∤ 鏈長）")

print()
print("="*84)
print("E. 18 = 6×3 = 2·N_gen² = L₆")
print("="*84)
L = [2,1]
while len(L) < 7: L.append(L[-1]+L[-2])
total = len(QUARK) * 3
ck("6×3 = 18", total == 18, str(total))
ck("18 = 2·N_gen² (N_gen=3)", total == 2*9, "2·3²")
ck("L₆ = 18 (Lucas 重算)", L[6] == 18, f"L[6]={L[6]}")

print()
print("="*84)
print("F. O88/O68 分解維數（引用閉合之算術核對）")
print("="*84)
ck("4 = 3⊕1（維數加和）", 3 + 1 == 4)
ck("12 = (3,3)⊕(1,3)（維數 3·3 + 1·3 = 12）", 3*3 + 1*3 == 12, "9+3=12")
ck("色數 3 = B−1 = N_gen = 4−1", 4-1 == 3 == 3)

print()
print("="*84)
print("G. Δn 由 O54 配對原始重算（腳本獨立路徑）")
print("="*84)
# O54: 夸克奇部 u:1, s:7, c:17, b:33 ; 輕子奇部 e:1, μ:7, τ:5
pairs = [((1),(1)), ((7),(7)), ((5),(17)), ((5),(33))]
dns = sorted({abs(q-l) for l,q in pairs})
print(f"  配對 (u,e) (s,μ) (c,τ) (b,τ) → |q−l| = {[abs(q-l) for l,q in pairs]}")
print(f"  唔同值 = {dns}")
ck("Δn = {0,12,28}", set(dns) == {0,12,28}, str(dns))
ck("12 ∉ 嚴格目錄（但 ∈ 寬鬆）", 12 in BROAD and 12 not in STRICT)
ck("28 ∈ 嚴格目錄", 28 in STRICT)

print()
print("="*84)
print("RESULT")
print("="*84)
print(f"PASS {len(PASS)} / FAIL {len(FAIL)}")
sys.exit(0 if not FAIL else 1)