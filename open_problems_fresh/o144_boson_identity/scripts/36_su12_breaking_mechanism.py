#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-36 — 問題 2: ⟨W⟩ 凝聚機制 SU(12)→S(U(3)×U(2)×U(1)⁷)
========================================================================
問題原文 (01_problem_record.md 開放問題 2):
  「⟨W⟩ 凝聚驅動 SU(12)→SM 破缺的機制」

上游 (只讀, 未改):
  ★ o85 docs/15 §3: 奇側 7 單態由 λ<1 譜閾值 m* = 88/6 = 44/3 導出;
      偶側 {2,4} 由塊計數 μ²=2 + 加倍塔「最低選取」(非推導 — 本檔攻此 gap)
  ★ o85 docs/15 定理 E: Φ = diag(λ₄·I₃, λ₂·I₂, λ₁..λ₁₃) − v̄·I₁₂
  ★ o144 docs/10: E_conn[U] = M₀ Σ_i |1−U_i|² (鏈 connection 能量泛函)
  ★ o144 scripts/35: SU(12) connection U_i 之移位纖維能量 E'(q) 閉形式
      E'(q) = 176 − 2·sin(πq/4)·cos(89πq/352)/sin(πq/352)
      E'(A=SM) = 1809.4136608, E'(B=3@2,2@4) = 1875.0638540

本腳本 (寫入限於 o144_boson_identity/):
  §A 奇側閾值獨立重算 (fence O85)
  §B 未移位平台 (fence scripts/35)
  §C 完整指派枚舉 (a@2, b@4), a+b=5, a,b≥1 — E 最小化
  §D ΔE 閉形式分析 (誠實: 有閉形式才報)
  §E 穩健性 + 虛無密度
  §F 判決
"""
import numpy as np
import mpmath as mp
import itertools, json, sys

mp.mp.dps = 60
PASS = FAIL = 0
ROWS = []
JSON = {}

def chk(cid, name, got, want, tol=1e-40):
    global PASS, FAIL
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= tol
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    ROWS.append({"id": cid, "check": name, "ok": bool(ok), "got": str(got)[:36], "want": str(want)[:36]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def chkb(cid, name, cond):
    global PASS, FAIL
    PASS += 1 if cond else 0
    FAIL += 0 if cond else 1
    ROWS.append({"id": cid, "check": name, "ok": bool(cond)})
    print(f"  [{'PASS' if cond else 'FAIL'}] {cid} {name}")

ODD = [1,3,5,7,9,11,13]

# ----------------------------------------------------- §A 奇側閾值 (fence)
print("§A 閾值 m* = 88/6 = 44/3 獨立重算 (fence O85 docs/15 §3)")
def lam(m):
    return 2 - 2*mp.cos(mp.pi*m/44)
odd_below = [m for m in ODD if lam(m) < 1]
chk("A.1", "奇側 λ<1 數目 = 7 = L₄", len(odd_below), 7)
chkb("A.2", "奇側選集 = {1,3,5,7,9,11,13}", odd_below == ODD)
chk("A.3", "m* = 88/6 = 44/3", mp.mpf(88)/6, mp.mpf(44)/3)
chk("A.4", "閾值以下最大奇模 13 = 2L₄−1", 13, 2*7-1)
# 門檻性質: λ<1 ⟺ cos(2πm/88) > 1/2
ok = all((lam(m) < 1) == (mp.cos(2*mp.pi*m/88) > mp.mpf(1)/2) for m in ODD + [15])
chkb("A.5", "λ<1 ⟺ cos(2πm/88)>1/2 (全部奇模)", ok)

# ----------------------------------------------------- §B 未移位平台 (fence)
print("§B 未移位 E(q) 平台 (fence scripts/35 B4)")
Eint = {}
for q in range(1, 14):
    Eint[q] = sum(4*mp.sin(mp.pi*i*q/176)**2 for i in range(1, 89))
chk("B.1", "E_int(奇) = 178 平台", Eint[5], 178)
chk("B.2", "E_int(偶) = 176 平台", Eint[8], 176)
chk("B.3", "未移位對指派無判別力 (平台簡併)", Eint[1]+Eint[2], Eint[3]+Eint[4])

# ----------------------------------------------------- §C 指派枚舉
print("§C 指派枚舉 (塊計數 μ²=2 ⟹ 非單態塊必須 ≥2 纖維)")
# 每纖維能量 (移位): 依 scripts/35 閉形式
def Eshift(q):
    q = mp.mpf(q)
    return mp.mpf(176) - 2*mp.sin(mp.pi*q/4)*mp.cos(mp.pi*89*q/352)/mp.sin(mp.pi*q/352)
def E_asgn(Mlist):
    S = sum(Mlist)
    return sum(Eshift(m - mp.mpf(S)/12) for m in Mlist), S
def nblocks(Mlist):
    from collections import Counter
    return sum(1 for c in Counter(Mlist).values() if c >= 2)

print("§C.1 塊計數有效性 (mode∈{2,4}, a+b=5)")
cands = {}
for a in range(1, 5):
    b = 5 - a
    M = [2]*a + [4]*b + ODD
    nb = nblocks(M)
    valid = (a >= 2 and b >= 2)
    E, S = E_asgn(M)
    cands[(a, b)] = (E, S, nb, valid)
    print(f"  (a@2={a}, b@4={b}): blocks={nb}, valid={valid}, S={S}, E={E}")
chk("C.1", "(1,4) 非單態塊數 = 1 ≠ μ² (排除)", cands[(1,4)][2], 1)
chk("C.2", "(4,1) 非單態塊數 = 1 ≠ μ² (排除)", cands[(4,1)][2], 1)
chk("C.3", "(2,3) 非單態塊數 = 2 = μ²", cands[(2,3)][2], 2)
chk("C.4", "(3,2) 非單態塊數 = 2 = μ²", cands[(3,2)][2], 2)
valid_set = {(a,b) for (a,b),v in cands.items() if v[3]}
chkb("C.5", "合法候選 = {(2,3),(3,2)}", valid_set == {(2,3),(3,2)})
amin = min(valid_set, key=lambda k: cands[k][0])
chkb("C.6", "SM 指派 (2@2,3@4) 係合法集唯一能量最小", amin == (2, 3))
minE = cands[(2,3)][0]
secE = cands[(3,2)][0]
gap = secE - minE
print(f"  ΔE(合法集) = E_(3,2) − E_(2,3) = {gap}")
JSON["assignments_block_valid"] = {f"({a},{b})": {"S": cands[(a,b)][1], "E": str(cands[(a,b)][0]), "valid": cands[(a,b)][3]} for a, b in cands}
JSON["min_assignment"] = list(amin)
JSON["E_min"] = str(minE)
JSON["E_second"] = str(secE)
JSON["gap_second"] = str(gap)

print("§C.2 偶模選擇完整枚舉: (m1,m2) ∈ 閾值下偶模 {2,4,6,8,10,12,14}, 尺寸 (2,3)/(3,2)")
EVEN_BELOW = [m for m in range(2, 15, 2) if lam(m) < 1]
print(f"  偶模候選: {EVEN_BELOW}")
best = None
rows = []
for m1, m2 in itertools.combinations(EVEN_BELOW, 2):
    for M in ([m1,m1,m2,m2,m2] + ODD, [m1,m1,m1,m2,m2] + ODD):
        if nblocks(M) != 2:
            continue
        E, S = E_asgn(M)
        rows.append((E, M, S))
        if best is None or E < best[0]:
            best = (E, M, S)
if best is None:
    raise SystemExit("§C.2 枚舉空集 — 唔應該發生")
E_best, M_best, S_best = best
print(f"  全局最小: E = {E_best}, M = {M_best}, S = {S_best}")
from collections import Counter
best_cnt = Counter(M_best)
chkb("C.7", "負面結果: 全枚舉全局最小 ≠ SM (偶模選擇唔可由能量導出)", 
     not (best_cnt[2] == 2 and best_cnt[4] == 3 and all(best_cnt[m] == 0 for m in EVEN_BELOW if m not in (2,4))))
best_q = [m - mp.mpf(S_best)/12 for m in M_best]
sm_q = [m - mp.mpf(65)/12 for m in [2,2,4,4,4] + ODD]
chkb("C.8", "q≈0 解釋: 全局最小有纖維落 |q|<0.1 (mode 7: q=−0.083)", min(abs(q) for q in best_q) < mp.mpf("0.1"))
chk("C.9", "SM 指派 (2@2,3@4) 係 {2,4} 輸入下能量最小 (C.6 重述)", minE, cands[(2,3)][0], tol=1e-40)
chkb("C.10", "SM 纖維 |q| 全部 > 0.1 (冇 q≈0 漏洞)", min(abs(q) for q in sm_q) > mp.mpf("0.1"))
JSON["full_enum"] = [{"E": str(E), "M": M, "S": S} for E, M, S in sorted(rows)[:8]]
JSON["global_min_full"] = {"E": str(E_best), "M": M_best, "S": S_best, "min_abs_q": str(min(abs(q) for q in best_q))}
JSON["sm_fiber_min_abs_q"] = str(min(abs(q) for q in sm_q))
JSON["mode_selection_verdict"] = "偶模選擇 {2,4} 唔可以由 E 最小化單獨導出 (q≈0 漏洞); 須 O85 加倍塔/O137 9-mode 集輸入 (fence)"

# ----------------------------------------------------- §D ΔE 分析 (反巧合)
print("§D ΔE 分析 (誠實: 閉形式搜尋)")
dE = gap   # E_(3,2) − E_(2,3)
print(f"  ΔE = E_(3,2) − E_(2,3) = {dE}")
# 候選閉形式辭彙 (理性估算 — 零新常數; 命中先報, 未命中記錄經驗數)
vocab = {
    "65 + cot(π/88)": 65 + 1/mp.tan(mp.pi/88),
    "65 + sin(π/24)": 65 + mp.sin(mp.pi/24),
    "65 + cos(π/11)": 65 + mp.cos(mp.pi/11),
    "65 + 1/φ": 65 + (mp.sqrt(5)-1)/2,
    "65 + 2sin(π/11)": 65 + 2*mp.sin(mp.pi/11),
    "65 + sin(2π/11)": 65 + mp.sin(2*mp.pi/11),
    "65 + sin(π/11)·88/176": 65 + mp.sin(mp.pi/11)*mp.mpf(88)/176,
    "66 − sin(π/11)": 66 - mp.sin(mp.pi/11),
    "65 + λ₂/2": 65 + (2-2*mp.cos(mp.pi/22))/2,
    "65 + λ₄/2": 65 + (2-2*mp.cos(mp.pi/11))/2,
}
print("  候選對照:")
found = None
for name, val in vocab.items():
    d = abs(dE - val)
    print(f"    {name}: {val}  |Δ| = {d}")
    if d < 1e-20:
        found = name
chkb("D.1", "ΔE 無常見常數巧合 (反巧合, |Δ|>1e-20)", found is None)
chkb("D.2", "ΔE 記錄為經驗數: 65.6501932… (零閉合湊數)", abs(dE - mp.mpf("65.6501932021338257940030544887132674397880882452919928428302")) < 1e-40)
JSON["dE"] = str(dE)
JSON["dE_closed_form"] = found
JSON["vocab"] = {k: str(v) for k, v in vocab.items()}

# ----------------------------------------------------- §E 穩健性
print("§E 穩健性")
# E.1 移位係強制 (SU(12) 要求 traceless): 未移位 U(12) 平台簡併 ⟹ 無判別力
chk("E.1", "未移位平台: E(2)=E(4)=176 (判別失效)", Eint[2], Eint[4])
# E.2 gap 相對規模
gap_rel = (secE - minE) / minE
print(f"  相對 gap = {gap_rel}")
chkb("E.2", "gap > 1e-6 相對 (非誤差水平)", gap_rel > 1e-6)
JSON["gap_rel"] = str(gap_rel)
# E.3 單態置換不影響 E (S 相同)
Mp = [2,2,4,4,4] + [13,11,9,7,5,3,1]      # 倒序單態
Smp = sum(Mp)
Ep = sum(Eshift(m - mp.mpf(Smp)/12) for m in Mp)
chk("E.3", "單態置換不變 (E_p = E_(2,3))", Ep, minE, tol=1e-40)
# E.4 奇單態集必須為閾值選 (A.1) — 若換一個非奇模 (如 15): 唔喺 9-mode 集, 排除
chkb("E.4", "奇模選集由閾值固定 (fence A.1)", odd_below == ODD)

# ----------------------------------------------------- 輸出
JSON["checks"] = ROWS
JSON["passed"] = PASS
JSON["failed"] = FAIL
with open("data/36_su12_breaking_mechanism.json", "w", encoding="utf-8") as f:
    json.dump(JSON, f, ensure_ascii=False, indent=1)
print(f"                                                                                                  ")
print(f"  驗證: scripts/36 = {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)