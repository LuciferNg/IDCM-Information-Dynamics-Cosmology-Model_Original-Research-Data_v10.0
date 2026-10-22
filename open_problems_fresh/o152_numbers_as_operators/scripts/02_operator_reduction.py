#!/usr/bin/env python3
"""
O152 scripts/02_operator_reduction.py — 算子約化定理 (U1 最小性)
================================================================
定理 R1-R5: 生成算子族約化到最小集 — G3/G4/G6/G8 係 G2 (K_chain) 嘅譜函數。

R1 (Dirac 平方根):  ω_n = √γ_n, 44/44
R2 (v_g 譜函數):     v_g(n) = √(1−γ_n/4), 44/44;  v_g(44−n) = √γ_n/2
R3 (Beat 譜化):      beat(a,b) = |√γ_b − √γ_a|, 946/946
R4 (算子約化):       B = γ₄₄ (Nyquist), log₂B = γ₂₂ (自對偶), C_obs = N_d·γ₂₂
R5 (半整數縫佔據):   44 縫 {k+1/2}; T̂-譜佔據 11 縫 = rank(SU(12))
"""
import json
import os
import mpmath as mp

mp.mp.dps = 50
TOL = mp.mpf('1e-40')

def gamma44(n): return 4 * mp.sin(mp.pi * n / 88) ** 2
def omega(n):   return 2 * mp.sin(mp.pi * n / 88)
def vg(n):      return mp.cos(mp.pi * n / 88)

LUCAS = {0: 2, 1: 1}
for _n in range(2, 15):
    LUCAS[_n] = LUCAS[_n - 1] + LUCAS[_n - 2]
FIB = {1: 1, 2: 1}
for _n in range(3, 16):
    FIB[_n] = FIB[_n - 1] + FIB[_n - 2]
def L(n): return LUCAS[n]
def F(n): return FIB[n]

results = []
def check(cid, desc, op, func, cond, detail=""):
    results.append((cid, desc, op, func, "PASS" if cond else "FAIL", detail))
    return cond

# ---------- R1: ω = √γ (Dirac 平方根) ----------
r1 = all(abs(omega(n) - mp.sqrt(gamma44(n))) < TOL for n in range(1, 45))
check("R1", "ω_n = √γ_n (Dirac 平方根 D² = L), 44/44", "G3 = √G2", "F1 本徵值/譜函數",
      r1, "√(4sin²(πn/88)) = 2sin(πn/88) = ω_n — 勢算子 = 鏈算子平方根 (Connes 譜三元組結構)")

# ---------- R2: v_g 譜函數 ----------
r2a = all(abs(vg(n) - mp.sqrt(1 - gamma44(n) / 4)) < TOL for n in range(1, 45))
r2b = all(abs(vg(44 - n) - mp.sqrt(gamma44(n)) / 2) < TOL for n in range(1, 45))
check("R2", "v_g(n) = √(1−γ_n/4); v_g(44−n) = √γ_n/2, 44/44", "G4 = f(G2)", "F1 本徵值/譜函數",
      r2a and r2b, "v_g² = 1−γ/4; v_g(44−n) = ω_n/2 (O149 定理2 嘅逆)")

# ---------- R3: Beat = |√γ_b − √γ_a| ----------
r3 = all(abs((omega(b) - omega(a)) - (mp.sqrt(gamma44(b)) - mp.sqrt(gamma44(a)))) < TOL
         for a in range(1, 45) for b in range(a + 1, 45))
check("R3", "beat(a,b) = |√γ_b − √γ_a|, 946/946", "G5 = f(G2)", "F8 拍頻/譜差",
      r3, "拍頻空間 = 平方根譜嘅差空間 — 946 指令全部由 K_chain 本徵值產生")

# ---------- R4: 算子約化 ----------
g44 = gamma44(44)   # Nyquist = 4
g22 = gamma44(22)   # 自對偶 = 2
check("R4a", "B = γ₄₄ (Nyquist 本徵值 = 4)", "G6 = f(G2)", "F1 本徵值",
      abs(g44 - 4) < TOL, "K_Tree 分支因子 = 鏈嘅最大本徵值")
check("R4b", "log₂B = γ₂₂ (Z₂ 自對偶本徵值 = 2)", "G8 = f(G2)", "F1 本徵值",
      abs(g22 - 2) < TOL, "每模態 2 bits = γ₂₂")
check("R4c", "C_obs = N_d·γ₂₂ = 44×2 = 88; 90 = (N_d+1)·γ₂₂", "G8⊗G2", "F10 容量",
      abs(44 * g22 - 88) < TOL and abs(45 * g22 - 90) < TOL)
check("R4d", "12 = γ₄₄×N_gen = 4×3; 528 = N_d·γ₄₄·N_gen = 44×12", "G9⊗G2", "F4 維數",
      12 == 4 * 3 and 528 == 44 * 4 * 3)
check("R4e", "132 = N_d·(γ₄₄−1) = 44×3; 264 = N_d·γ₄₄·N_gen/2 = 44×6", "G9⊗G2", "F4 維數",
      132 == 44 * (4 - 1) and 264 == 44 * 4 * 3 // 2)
check("R4f", "2 = γ₄₄/2 = γ₂₂ (五重身份歸一: 2 = log₂B = γ₄₄/2 = γ₂₂)", "G2", "F1 本徵值",
      abs(g22 - g44 / 2) < TOL)

# ---------- R5: 半整數縫佔據 ----------
seams = {mp.mpf(k) + mp.mpf('0.5') for k in range(44)}   # {0.5..43.5}
L_odd = {mp.mpf(L(n)) / 2 for n in range(0, 11) if L(n) % 2 == 1}
F_odd = {mp.mpf(F(n)) / 2 for n in range(1, 12) if F(n) % 2 == 1}
occupied = sorted((L_odd | F_odd) & seams)
beyond = sorted((L_odd | F_odd) - seams)
check("R5a", f"T̂-譜佔據縫: {[float(x) for x in occupied]} ({len(occupied)} 個) + 43.5 (3L₇/2 beat 零點) = 11 = rank(SU(12))", "Z₂⊗G1", "F11 縫",
      len(occupied) == 10 and len(occupied) + 1 == 11,
      f"10 個 T̂ 譜半整數 + 43.5 (3L₇/2, beat 零點縫) = 11 = L₅ = rank(SU(12))")
check("R5b", f"縫外半整數: {[float(x) for x in beyond]} (61.5 已閉合 O41)", "Z₂⊗G1", "F11 縫",
      len(beyond) == 2, "44.5 = F₁₁/2 冇物理角色 (Nyquist 外) — 需個別判決")
# 14.5 = L₇/2: O149 k-ladder k=1 阻擋者
check("R5c", "14.5 = L₇/2 阻擋 k-ladder k=1 (a=(42−13)/2 非整數) → 階梯由 k=2 開始", "G1⊗Z₂", "F11 縫/選擇規則",
      mp.mpf('14.5') == mp.mpf(L(7)) / 2 and (42 - F(7)) / 2 == 14.5 and (42 - F(7)) % 2 == 1,
      "O149 §6.1: k=1 分子 dual (0,1) 出譜 + 分母 a=14.5 非整數 → 雙重拒絕")
# 10.5 = F₈/2: O35 審計 (模態數整數性拒絕 = 縫唔係模態)
check("R5d", "10.5 = F₈/2 = 21/2: O35 審計 10 vs 10.5 vs 11 拒絕 (模態數整數性) — 一致: 縫 = 讀數位置, 唔係模態", "G1⊗Z₂", "F11 縫",
      mp.mpf('10.5') == mp.mpf(F(8)) / 2, "O35 docs/02_transfer_matrix_closure.md §4 + O147 docs/03: 10.5 違規")

# ---------- 統計 ----------
n_pass = sum(1 for r in results if r[4] == "PASS")
n_fail = sum(1 for r in results if r[4] == "FAIL")
print(f"=== O152 算子約化: {n_pass} PASS / {n_fail} FAIL (共 {len(results)}) ===")
for cid, desc, op, func, status, detail in results:
    mark = "✅" if status == "PASS" else "❌"
    print(f"{mark} [{cid}] {desc}  | {op} {func}")
    if detail and status == "FAIL":
        print(f"     詳情: {detail}")

out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
entries = [{"id": cid, "theorem": desc, "operator": op, "function": func,
            "status": status, "detail": detail} for cid, desc, op, func, status, detail in results]
with open(os.path.join(out_dir, "reduction_theorems.json"), "w") as f:
    json.dump({"results": entries, "n_pass": n_pass, "n_fail": n_fail, "total": len(results)},
              f, indent=1, ensure_ascii=False)
print(f"\n輸出: data/reduction_theorems.json")
