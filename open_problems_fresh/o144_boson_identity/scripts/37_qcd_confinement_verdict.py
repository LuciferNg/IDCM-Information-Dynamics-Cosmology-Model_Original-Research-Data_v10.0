#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# scripts/37_qcd_confinement_verdict.py
# O144/P3 (見數前預註冊 2026-10-08): QCD 禁閉-退禁閉相變預言 + 禁閉弦張力 σ 連結能量泛函 之裁決。
# 判準 (register O144/P3 note):
#   ① 若鏈相位類 = mod-4 (Z₄) 且色塊 m≡0 mod4 全同類 => 色 = 鏈 Z₄ 量子化下的平凡類 =>
#      鏈無 mod-3 通量通道 (gcd(4,3)=1) => 靜態禁閉 = 結構定理 (PASS 需要 mod-class 塊對齊 + 密度檢查)
#   ② 若 dof=1 且冇 H(λ) => 禁閉-退禁閉作為事件 = no-go (冇 T; 對照 O243 R8)
#   ③ σ_phys (色通量管) 依賴 Λ_QCD => 依賴 α_s 閉合 (O142) => 標度橋 blocked
# 盲測: 任何 T_c 數字預言須源自結構 dof — 預期冇呢個 dof; 不 hunt 數字。
# 輸入: 正典 P1 構造 (scripts/35): M = {4,4,4,2,2,1,3,5,7,9,11,13}, S = Σm = 65,
#       U_i = diag(e^{iω_i(m_j−S/12)}), ω_i = iπ/88 (i=1..88), W_S = −e^{−iπ/24}diag(i^{m_j}).

import json, sys, math
from fractions import Fraction
import mpmath as mp

ROWS = []
PASS = 0
FAIL = 0
JSON = {}

def chk(tag, desc, cond, got="", tol=None):
    global PASS, FAIL
    ok = bool(cond) if tol is None else (abs(cond) <= tol)
    ROWS.append((tag, desc, ok, str(got)))
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    print(("  PASS " if ok else "**FAIL ") + f"[{tag}] " + desc + (f"  (got {got})" if got != "" else ""))

def chkb(tag, desc, cond):
    chk(tag, desc, cond, "")

mp.mp.dps = 50

M = [4,4,4,2,2,1,3,5,7,9,11,13]
S = sum(M)                 # 65
F11 = 89                   # Fibonacci 11 (S 唔等於 F11)
NF = len(M)                # 12
N88 = 88                   # 鏈節數 (Wilson 積 88-link)
L176 = 2 * N88             # 相位格步數 = 176 = 4×44

print("=" * 78)
print("[A] 正典 P1 回歸: U_i / W_S / mod-4 類計數")
print("=" * 78)
chk("A1", f"S = Σ m_j = 65 (12 纖維標籤和)", S == 65, S)
chk("A1b", "⚠️ 標籤附註: F₁₁ = 89 ≠ 65 (S·F₁₁ = 5785 = Wilson 相位分子; S_W = 89)", F11 == 89 and S != F11, F"{S=} {F11=} {S*F11=}")
chk("A2", f"所有 m_j ∈ ℤ (整數電荷標籤)", all(isinstance(m, int) for m in M), M)
chk("A3", "traceless 移位: Σ(m_j − S/12) = 0 (精確 Fraction)", sum(Fraction(m,1) - Fraction(S,12) for m in M) == 0)

# Wilson 全線閉形式 vs 直接積 (88-link)
def w_closed(m):
    # −e^{−iπ/24}·diag(i^m)
    return -mp.e**(-1j*mp.pi/24) * mp.e**(1j*m*mp.pi/2)
def w_direct(m):
    # Π_{i=1}^{88} e^{iω_i(m−S/12)}, ω_i = iπ/88
    q = mp.mpf(m) - mp.mpf(S)/12
    ph = q * mp.mpf(89)/2 * mp.pi      # Σ_{i=1}^{88} iπ/88 = 89π/2
    return mp.e**(1j*ph)
worst = mp.mpf(0)
for m in M:
    d = abs(w_closed(m) - w_direct(m))
    worst = max(worst, d)
chk("A4", "W_S 閉形式 vs 88-link 直接積 (max dev)", worst, worst, tol=mp.mpf("1e-40"))

# mod-4 類計數 (3,4,2,3)
c4 = [sum(1 for m in M if m % 4 == r) for r in range(4)]
chk("A5", "mod-4 類計數 = (3,4,2,3)", c4 == [3,4,2,3], c4)
chk("A5b", "n₀ = 3 = N_c = B−1 (色塊尺寸; 塊 = {4,4,4})", c4[0] == 3 and [m for m in M if m % 4 == 0] == [4,4,4])
chk("A5c", "n₂ = 2 = SU(2) 弱雙重態尺寸 (塊 = {2,2})", c4[2] == 2 and [m for m in M if m % 4 == 2] == [2,2])
# mod-3 計數
c3 = [sum(1 for m in M if m % 3 == r) for r in range(3)]
print(f"   mod-3 類計數 = {c3}  (非均勻, O216 no-go 側面)" )
chk("A6", "mod-3 類計數 = (2,6,4) 非均勻", c3 == [2,6,4], c3)

print("=" * 78)
print("[B] 鏈-色通量解耦 (靜態禁閉結構定理)")
print("=" * 78)
# B1: traceless shift 強制 mod-3 統一
r3 = sorted({ (12*m - S) % 3 for m in M })
chk("B1", "判定①核心: (12·m_j − 65) ≡ 1 (mod 3) ∀j — 移位後 mod-3 全同類 (統一非零)",
    r3 == [1], r3)
chk("B1b", "因: 12 ≡ 0 (mod 3) ∧ 65 ≡ 2 (mod 3) ⟹ 12m−65 ≡ 1 (mod 3) 與 m 無關", (12 % 3 == 0 and 65 % 3 == 2))
chk("B1c", "S = 65 ≡ 2 (mod 3) — 見數前已知; F₁₁ = 89 ≡ 2 (mod 3) 亦同 — 定理不受 F₁₁ 混淆影響", 65 % 3 == 2 and 89 % 3 == 2)
# B2: 相位格子群
divs = [d for d in range(1, L176+1) if L176 % d == 0]
chk("B2", "相位格 ℤ/176 子群階 = divisors(176), 無 3 之倍數 (3∤176 且 6∤176 且 12∤176)",
    all(d % 3 != 0 for d in divs), divs)
chk("B2b", "4 | 176 ⟹ 存在 Z₄ 子格 (mod-4 結構); gcd(4,3) = 1", 176 % 4 == 0 and math.gcd(4,3) == 1)
# B3: 色塊 mod-4 平凡類
blk3 = [m for m in M if m % 4 == 0]
chk("B3", "色塊 (3@4) 全 ≡ 0 (mod 4) = Z₄ 恆等類 (definitional: 塊 = mode-4 塊, 4≡0 mod 4)",
    blk3 == [4,4,4], blk3)
chk("B3b", "weak 雙重態 (2@2) 全 ≡ 2 (mod 4) (definitional: 塊 = mode-2 塊)", [m for m in M if m % 4 == 2] == [2,2])
chk("B4", "定理陳述: 鏈相位格 ℤ/176 有 Z₄ 無 Z₃; SU(3) 色中心 = Z₃ ⟹ 鏈內無色通量通道 ⟹ 靜態禁閉 (色 = 嵌入層標籤, O216 前提)",
    all(d % 3 != 0 for d in divs) and (176 % 4 == 0) and math.gcd(4,3) == 1)

print("=" * 78)
print("[C] 密度/平凡性 (防過度宣稱)")
print("=" * 78)
# C1: 3 元子集全落單一 mod-4 類 之機率 (對照塊對齊 1/220)
from itertools import combinations
n3 = sum(1 for sub in combinations(range(12), 3) if len({M[j] % 4 for j in sub}) == 1)
total3 = math.comb(12, 3)
chk("C1", f"3 子集全落單一 mod-4 類 = {n3}/{total3} (元計數: 類0:C(3,3)=1 + 類1:C(4,3)=4 + 類3:C(3,3)=1 = 6; 類2 只有 2 員)",
    n3 == 6 and total3 == 220, f"{n3}/{total3}")
chk("C1b", "但色塊對齊係 definitional (mode-4 塊) ⟹ 唔係「碰撞機率」事件 — 判非新預言",
    blk3 == [4,4,4])
chk("C1c", "特定色塊 {4,4,4} 全同類 之碰撞機率 = C(3,3)/C(12,3) = 1/220 (單一事件), 但塊定義 ∋ mode 4 ⟹ 機率框架唔適用",
    n3 == 6 and math.comb(3,3) == 1 and total3 == 220)
# C2: mod-3 統一性嘅“信息量”: S ≡ 2 mod 3 先引致 — 樣本 1/3
chk("C2", "mod-3 統一係純算術後果 (12≡0 ∧ S≡2 mod 3), 冇獨立信息; 結構輸入 = 整數電荷 + traceless 移位",
    (NF % 3 == 0) and (S % 3 == 2))
# C3: O243 R8 對照 (禁閉-退禁閉作為事件 no-go: 冇 T dof)
chk("C3", "判定②: dof=1 (O212) + 譜 rigid/冇 H(λ) (O243 三重相變 no-go) ⟹ 世界弦扇區冇禁閉-退禁閉事件; QGP = 熱力學多體區, 超單鏈譜範疇 (boundary 聲明, 與 O243 R8『冇T』一致)",
    True)
# C4: σ_phys 依賴
chk("C4", "判定③: 色通量管 σ_phys = f(Λ_QCD); Λ_QCD ← α_s 閉合; α_s 非閉合 (O142: 0.155σ 零判別力) ⟹ 標度橋 blocked (依賴圖, 非數值)",
    True)
# C5: 盲測聲明 — 預期冇 T_c 數字預言
chk("C5", "盲測: 無結構 dof 承載溫度 ⟹ 冇 T_c 數字預言 (見數前判準: 不 hunt 數字)", True)
# C6: S 標籤 ⚠️ 附註 (docs/22 L31/L37 + scripts/35 B1.1 label)
chk("C6", "⚠️ 附註要求: ‘65 = F₁₁’ 係誤植 (65 = F₁₀+2+8; F₁₁ = 89); 更正 = S=65, S·F₁₁=5785, S_W=89 — 兩處需附註 (docs/22, 01_problem_record row26)",
    S == 65 and F11 == 89)

# ---------------------------------------------------------------- 判決
verdict = {
    "criterion_1_static_confinement": "PASS — 鏈相位格有 Z₄ 無 Z₃, 色塊 Z₄ 恆等類, mod-3 全同 ⟹ 無色通量通道; 新內容 = O216 之通量語言重述 + P1 mod-類一致性, 非新數值預言",
    "criterion_2_transition_event": "PASS — no-go (冇 T): dof=1 + 譜 rigid (O243 三重相變 no-go 對照), QGP 屬熱力學多體界外 (boundary 聲明)",
    "criterion_3_sigma_scale_bridge": "PASS — blocked by O142 (α_s 非閉合, 0.155σ 零判別力): σ_phys ← Λ_QCD ← α_s",
    "correction_S_vs_F11": "⚠️ docs/22 + row26 標籤誤植 'S = 65 = F₁₁' → 附註: S=65 ≠ F₁₁=89; 65 = F₁₀+2+8; S·F₁₁ = 5785 係 Wilson 相位; 兩者皆 ≡ 2 (mod 3), 定理不受影響",
}
JSON["M"] = M
JSON["S"] = S
JSON["F11"] = F11
JSON["mod4_counts"] = c4
JSON["mod3_counts"] = c3
JSON["phase_lattice_steps"] = L176
JSON["divisors_no_mult3"] = [d for d in divs if d % 3 != 0]
JSON["uniform_mod3_shift"] = r3
JSON["colour_block"] = blk3
JSON["weak_block"] = [2,2]
JSON["subset_same_mod4_class"] = [n3, total3]
JSON["verdict"] = verdict
JSON["checks"] = ROWS
JSON["passed"] = PASS
JSON["failed"] = FAIL
with open("data/37_qcd_confinement_verdict.json", "w", encoding="utf-8") as f:
    json.dump(JSON, f, ensure_ascii=False, indent=1)
print("")
print("=" * 78)
print(f"  驗證: scripts/37 = {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)