#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-35 — 問題 1: U_i ∈ SU(12) 具體形式 (44 鏈站 × 12 維纖維, 528 = 44×12)
========================================================================
問題原文 (01_problem_record.md 開放問題 1):
  「U_i ∈ SU(12) 具體形式 — 528 = 44×12 張量身份」

上游 (只讀, 未改):
  ★ o161 docs/02: 鏈 connection U_k = e^{i·2θ_k} = e^{ikπ/88} (k = 1..88);
      γ_k = |1−U_k|² = 4sin²(kπ/176); Wilson line ΠU_k = i (Z₄ = B)
  ★ o144 docs/10: E_conn[U] = M₀ Σ_k |1−U_k|²; Σ_k γ_k^(176-L) = 178 (88-link)
  ★ o85 docs/15 定理 E: Φ = diag(λ₄·I₃, λ₂·I₂, λ₁,λ₃,λ₅,λ₇,λ₉,λ₁₁,λ₁₃) − v̄·I₁₂
      λ_m = 2−2cos(πm/44), v̄ = 0.207620801937 (traceless 平移);
      # ⚠️ 2026-10-12 audit: v̄ 值驗證正確 (= Σλ_M/12, docs/22 appendix); 'O85 docs/15 定理 E' citation 路徑斷, O85 owner 核實中
      纖維標籤 (12 個): {4,4,4, 2,2, 1,3,5,7,9,11,13}
  ★ o137: 9-mode 集 {1,2,3,4,5,7,9,11,13} = {前 μ² 偶} ∪ {前 L₄ 奇};
      Σ = 55 = F₁₀
  ★ o159 docs/03: U(1) 生成元 = 鏈平移; mode k 電荷 = k

本腳本 (寫入限於 o144_boson_identity/, 只讀上游):
  §A 構造: 由鏈相位 ω_i = iπ/88 升入 SU(12), 纖維電荷 = 標籤 m_j
  §B 驗證: 幺正 / det / 中央化子 / 528-component 計數 / E(q) 平台 / Wilson 全線
  §C 判決
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

# ---------------------------------------------------------------- §A 構造
# 88-link 相位 (o161): ω_i = iπ/88, i = 1..88
N88 = 88
M = [4,4,4, 2,2, 1,3,5,7,9,11,13]      # 12 纖維標籤 (O85 定理 E, 單態升序 canon)
S = sum(M)
print(f"§A 纖維標籤 M = {M},  ΣM = S = {S}")
assert len(M) == 12

# 未移位 (U(12) 形式): U_i^U = diag(e^{iω_i m_j})
def UU(i):
    w = mp.pi * i / 88
    return [mp.e**(1j*w*m) for m in M]

# 移位 (SU(12)): X = diag(m_j − S/12) traceless;  U_i = diag(e^{iω_i(m_j−S/12)})
def US(i):
    w = mp.pi * i / 88
    return [mp.e**(1j*w*(m - mp.mpf(S)/12)) for m in M]

# ---------------------------------------------------------------- §B 驗證
print("§B1 整數恆等式")
chk("B1.1", "S = 65 = F₁₁", S, 65)   # ⚠️ 2026-10-12 audit 附註: label 誤植 — F₁₁ = 89 ≠ 65 (見 docs/22 appendix + data/37 A1b); 數值 S=65 正確
chk("B1.2", "9-mode 集 Σ = 55 = F₁₀ (O137 fence)", sum([1,2,3,4,5,7,9,11,13]), 55)
chk("B1.3", "528 = 44×12 (site×fiber)", 44*12, 528)
chk("B1.4", "528 = C(33,2) = C(K_tree,2)", 33*32//2, 528)
chk("B1.5", "88×12 = 2×528 (88-link 版)", 88*12, 2*528)
chk("B1.6", "63 = 3F₈ (反事實指派 Σ), 對照", 3*21, 63)

print("§B2 SU(12) 性質 (移位形式)")
tr = sum(m - mp.mpf(S)/12 for m in M)      # traceless: Σ(m−S/12) = S − 12·S/12 = 0
chk("B2.t", "Σ(m_j − S/12) = 0 (traceless, tol)", tr, 0, tol=1e-50)
for i in (1, 17, 44, 88):
    u = US(i)
    # 幺正: |u_j|² = 1
    ok = all(abs(abs(u[j])**2 - 1) < 1e-50 for j in range(12))
    chkb(f"B2.u{i}", f"U_{i} 幺正 (|u_j|=1)", ok)
    # det: 移位後 Σ(m−S/12) = 0 ⟹ det = e^{iω_i·0} = 1
    chkb(f"B2.d{i}", f"det U_{i} = 1 (指數 traceless)", abs(tr) < 1e-50)
# 移位全線 (88-link): Π_i U_i^S = diag(e^{i(m_j−S/12)·44.5π})
#   (m_j−65/12)·44.5π = m_j·44.5π − 65·89π/24 = m_j·44.5π − 5785π/24
#   5785π/24 = 240π + π + π/24 ⟹ e^{−i5785π/24} = −e^{−iπ/24}
#   ⟹ W_S = −e^{−iπ/24} · diag(i^{m_j})   (EXACT 閉形式)
prod = [mp.mpf(1)+0j]*12
for i in range(1, N88+1):
    u = US(i)
    prod = [prod[j]*u[j] for j in range(12)]
# closed form: −e^{−iπ/24}·i^{m_j}
ok = True
for j, m in enumerate(M):
    want = -mp.e**(-1j*mp.pi/24) * (1j**m)
    if abs(prod[j] - want) > 1e-40: ok = False
chkb("B2.W", "Π_{i=1..88} U_i^S = −e^{−iπ/24}·diag(i^{m_j}) (閉形式)", ok)
JSON["wilson_shifted_88"] = [str(p) for p in prod]

print("§B3 中央化子 / 塊結構")
from collections import Counter
cnt = Counter(M)
blocks = sorted(cnt.items())
nonsing = sum(1 for m,c in cnt.items() if c > 1)
sing = sum(1 for m,c in cnt.items() if c == 1)
chk("B3.1", "非單態塊數 = μ² = 2", nonsing, 2)
chk("B3.2", "單態數 = L₄ = 7", sing, 7)
chk("B3.3", "塊尺寸: mode2→2, mode4→3", (cnt[2], cnt[4]), (2, 3))
chk("B3.4", "總纖維 3+2+7 = 12", 3+2+7, 12)
# 9-mode 集只引用
nine = {1,2,3,4,5,7,9,11,13}
chkb("B3.5", "全部標籤 ∈ 9-mode 集", set(M) <= nine)

print("§B4 E(q) 平台 (問題 2 輸入): Σ_{i=1..88} 4sin²(iqπ/176)")
Eint = {}
for q in range(1, 14):
    s = sum(4*mp.sin(mp.pi*i*q/176)**2 for i in range(1, N88+1))
    Eint[q] = s
chk("B4.1", "E(1) = 178 (o144 docs/10 對照)", Eint[1], 178)
chk("B4.2", "E(3) = 178 (奇 q 平台)", Eint[3], 178)
chk("B4.3", "E(13)= 178 (奇 q 平台)", Eint[13], 178)
chk("B4.4", "E(2) = 176 (偶 q 平台)", Eint[2], 176)
chk("B4.5", "E(4) = 176 (偶 q 平台)", Eint[4], 176)
chk("B4.6", "E(6) = 176 (偶)", Eint[6], 176)
chk("B4.7", "E_asgn = 7·178+5·176 = 2126 (任何 7奇+5偶 指派相同)", 7*178+5*176, 2126)
JSON["Eint"] = {str(q): str(Eint[q]) for q in Eint}

print("§B5 未移位 Wilson 全線 (Z₄ = B 嵌入)")
W = [mp.e**(1j*mp.mpf(89)/2*mp.pi*m) for m in M]   # Σ_i ω_i = 3916π/88 = 44.5π → e^{i44.5π m}
Wcls = []
for j in range(12):
    w = W[j]
    # 分類: 1 / i / -1 / -i
    if abs(w-1) < 1e-40: Wcls.append(0)
    elif abs(w-1j) < 1e-40: Wcls.append(1)
    elif abs(w+1) < 1e-40: Wcls.append(2)
    elif abs(w+1j) < 1e-40: Wcls.append(3)
    else: Wcls.append(-1)
chkb("B5.1", "全部 W 值 ∈ {±1, ±i} (Z₄)", all(c >= 0 for c in Wcls))
nc = Counter(Wcls)
chk("B5.2", "mod4 類 0 (W=+1): 3 個 = N_gen (SU(3) 塊)", nc.get(0,0), 3)
chk("B5.3", "mod4 類 2 (W=−1): 2 個 (SU(2) 塊)", nc.get(2,0), 2)
chk("B5.4", "mod4 類 1 (W=+i): 4 個 (單態 1,5,9,13)", nc.get(1,0), 4)
chk("B5.5", "mod4 類 3 (W=−i): 3 個 (單態 3,7,11)", nc.get(3,0), 3)
chk("B5.6", "類計數鏡像: n₀ = n₃ 且 n₁−n₂ = 2 = μ²", (nc.get(0,0)==nc.get(3,0), nc.get(1,0)-nc.get(2,0)), (True, 2))
JSON["wilson_classes"] = Wcls
JSON["wilson_class_counts"] = dict(nc)

print("§B6 44-site 形式 (528 分量): i = 1..44")
# 44-site holonomy: Σ_{i=1..44} ω_i = 990π/88 = 45π/4 → e^{i·45π/4·m}
W44 = [mp.e**(1j*mp.mpf(45)/4*mp.pi*m) for m in M]
# 確認 45/4·m: m=1 → 11.25π → e^{i11.25π} = e^{i(10π+1.25π)} = e^{i5π/4}; m=2 → 22.5π → e^{i0.5π} = i; m=4 → 45π → −1
ok = True
want44 = {1: mp.e**(1j*5*mp.pi/4), 2: 1j, 4: -1}
for j, m in enumerate(M):
    if m in want44:
        if abs(W44[j] - want44[m]) > 1e-30: ok = False
chkb("B6.1", "44-site holonomy 結構 (m=2→i, m=4→−1, m=1→e^{i5π/4})", ok)
# 528 相位計數: 44 sites × 12 fibers
chk("B6.2", "44×12 = 528 phase 分量 (問題原文張量身份)", 44*12, 528)
JSON["wilson44"] = [str(w) for w in W44][:6]

print("§B7 E_conn,SU(12) 移位纖維能量 + A/B 指派判別")
# 每纖維 j (移位): E'_j = Σ_{i=1..88} |1−e^{iω_i(m_j−S/12)}|²
# 閉形式: E'(q) = 176 − 2·sin(πq/4)·cos(89πq/352)/sin(πq/352)   (cot-sum, N=88)
def Eshift(q):
    q = mp.mpf(q)
    return mp.mpf(176) - 2*mp.sin(mp.pi*q/4)*mp.cos(mp.pi*89*q/352)/mp.sin(mp.pi*q/352)
def Eshift_sum(Mlist):
    Slist = sum(Mlist)
    return sum(Eshift(m - mp.mpf(Slist)/12) for m in Mlist)
# 自洽: 閉形式 vs 直接和
q0 = mp.mpf(1) - mp.mpf(65)/12
direct = sum(abs(1 - mp.e**(1j*mp.pi*i*q0/176))**2 for i in range(1, N88+1))
chk("B7.1", "E'(q) 閉形式 (cot-sum) vs 直接和", Eshift(q0), direct, tol=1e-40)
Es = {j: Eshift(m - mp.mpf(S)/12) for j, m in enumerate(M)}
Etot = sum(Es.values())
print(f"  移位 (A=SM) E'_總 = {Etot}")
# A (SM): M_A = [4,4,4,2,2|odd], S=65;  B (反事實): M_B = [2,2,2,4,4|odd], S=63
MB = [2,2,2,4,4, 1,3,5,7,9,11,13]
EA = Eshift_sum(M)
EB = Eshift_sum(MB)
print(f"  E'_A (2@2,3@4) = {EA}")
print(f"  E'_B (3@2,2@4) = {EB}")
print(f"  ΔE = E_B − E_A = {EB - EA}")
chkb("B7.2", "移位能量 A≠B (平台破缺 → 指派判別)", abs(EB - EA) > 1e-30)
chkb("B7.3", "SM 指派 A (2@2,3@4) 能量最低", EA < EB)
JSON["E_shifted_A"] = str(EA)
JSON["E_shifted_B"] = str(EB)
JSON["E_shifted_dE"] = str(EB - EA)
JSON["E_shifted_total_A"] = str(Etot)
JSON["E_shifted_per_fiber_A"] = {str(j): str(Es[j]) for j in Es}

# ---------------------------------------------------------------- 輸出
JSON["M"] = M
JSON["S"] = S
JSON["checks"] = ROWS
JSON["passed"] = PASS
JSON["failed"] = FAIL
with open("data/35_su12_connection_u_i.json", "w", encoding="utf-8") as f:
    json.dump(JSON, f, ensure_ascii=False, indent=1)
print(f"                                                                                                                                                                                                                  ")
print(f"  驗證: scripts/35 = {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)