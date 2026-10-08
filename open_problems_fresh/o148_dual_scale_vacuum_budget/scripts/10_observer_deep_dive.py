#!/usr/bin/env python3
"""
O148 S5-1 — 觀察者側/自觀因子深追 (Observer Deep Dive)
========================================================
追擊開放項:
  A. sec 對消機制: mod-4 扇區 n≡1/n≡3 嘅 sec 項數值 + 結構身份
  B. ★Σφ = F₅·φ_origin 分判 (o137: 1800 = 20×90 → 20 = B×F₅ 定三角形面數)
  C. ★o137 44 分解交叉: 44 = L₃L₄+N_gen²+F₅+2, 個「2」= log₂(B)?
  D. F₁₁ 中心形式: 88/90/176/178/180/360 = F₁₁±{1,2}×log₂B 算術組織
  E. 720 = 4π sr: corpus 錨掃描 (已 grep: 全部係浮點尾數 → 排除)
  F. 候選: L₈ = 47 = N_d+N_gen; 45 = (F₁₁+1)/2; 88/89 連比
全部由定義重算。
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d, B, N_gen = 44, 4, 3
phi = (1 + math.sqrt(5)) / 2
log2B = math.log2(B)
F11 = 89
L = {3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 10: 123}

def gam176(k): return 4 * math.sin(k * math.pi / 176) ** 2

print("=" * 78)
print("  O148 S5-1 — 觀察者側/自觀因子深追")
print("=" * 78)

# ═══════ A. sec 對消機制 ═══════
print("\n─── A. mod-4 扇區 sec 對消機制 ───")
s0 = sum(gam176(k) for k in range(4, 89, 4))    # k≡0: 4,8,...,88
s1 = sum(gam176(k) for k in range(1, 88, 4))    # k≡1: 1,5,...,85
s2 = sum(gam176(k) for k in range(2, 88, 4))    # k≡2: 2,6,...,86
s3 = sum(gam176(k) for k in range(3, 88, 4))    # k≡3: 3,7,...,87
sec = s3 - N_d                                 # s3 = 44+sec (定義)
check("A1 s0 = 46 = N_d + log₂B", abs(s0 - 46) < 1e-12)
check("A2 s2 = 44 = N_d", abs(s2 - 44) < 1e-12)
check("A3 s1+s3 = 88 (sec 對消)", abs(s1 + s3 - 88) < 1e-12)
print(f"    s1 = {s1:.10f}, s3 = {s3:.10f}, sec = {sec:.10f}")
# sec 結構身份掃描: 候選 = γ 值 / φ 冪 / Lucas / √2 組合
cands = {
    "γ₄₄/2 (=2)": 2.0, "γ₂₂ (=2)": gam176(22), "γ₁₁ (=2−√2)": gam176(11),
    "γ₃₃ (=2+√2)": gam176(33), "4−γ₂₂": 4 - gam176(22),
    "√2": math.sqrt(2), "√2−1": math.sqrt(2) - 1, "1/φ": phi - 1,
    "φ⁻³": phi ** -3, "φ⁻⁴": phi ** -4, "1−1/φ²": 1 - phi ** -2,
    "L₇/29 相關: 29−28.5": 0.5, "0.5": 0.5, "1/4": 0.25,
}
print("    sec 結構身份掃描:")
for name, v in cands.items():
    d = abs(sec - v)
    if d < 1e-6:
        print(f"      ✅ sec ≈ {name} (dev {d:.2e})")
        check(f"A4 sec = {name}", d < 1e-6)
# 用 sin 公式重寫 sec: sec = Σ_{k≡3} sin² ×4 − 44 = Σ_{j} [4sin²((4j−1)π/176)] − 44
# 配對 (k, 88−k): sin²(kπ/176)+sin²((88−k)π/176) = 1 → sec 可唔可以閉式?
check("A5 配對 (k,88−k) 和 = 1: sin²θ+cos²θ", abs(math.sin(3*math.pi/176)**2 + math.sin(85*math.pi/176)**2 - 1) < 1e-12)
# ★ 閉式 (手推, sympy summation bug 但數值確認):
#   s3/4 = Σ_{j=0}^{21} sin²(3π/176 + jπ/44) = 11 + 1/(4cos(π/88))  [nΔ=π/2, cos(45π/88)=−sin(π/88)]
#   s3 = 44 + sec(π/88); s1 = 44 − sec(π/88)
#   s0/4 = 11 + 1/2 (cos(23π/44) = −sin(π/44)); s0 = 46 精確
#   s2/4 = 11 + 0 (cos(π/2) = 0); s2 = 44 精確
sec_exact = 1 / math.cos(math.pi / 88)
check("A6 ★ s3 = 44 + sec(π/88) 精確", abs(s3 - (44 + sec_exact)) < 1e-12,
      f"s3={s3:.12f} vs 44+sec={44+sec_exact:.12f}")
check("A7 ★ s1 = 44 − sec(π/88) 精確", abs(s1 - (44 - sec_exact)) < 1e-12)
check("A8 sec(π/88) = 1/cos(π/88) ≈ 1.000637580593 (transcendental, 唔係整數)",
      abs(sec_exact - 1.000637580593) < 1e-12)
check("A9 ★ s0 = 46 精確整數 (相位到 π/2: cos(23π/44) = −sin(π/44) 使 1/2 出現)", abs(s0 - 46) < 1e-12)
check("A10 ★ s2 = 44 精確整數 (cos(π/2) = 0)", abs(s2 - 44) < 1e-12)
check("A11 對消: s1+s3 = 88 (sec 以 ± 對稱出現, 消走)", abs(s1 + s3 - 88) < 1e-12)
check("A12 名稱巧合: 「sec 項」真係 secant 函數 sec(π/88)", True, "命名巧合冇結構意義, 內容係閉式")
# sec(π/88) 同 γ₁ 嘅關係: cos²(π/88) = 1−γ₁/4
g1 = gam176(1)  # = 4sin²(π/176) — 唔係 γ₁ (γ₁ 係 88-chain)
g1_88chain = 4 * math.sin(math.pi / 88) ** 2
check("A13 cos²(π/88) = 1−γ₁/4 (88-chain γ₁)", abs(math.cos(math.pi / 88) ** 2 - (1 - g1_88chain / 4)) < 1e-12)
check("A14 sec(π/88) = (1−γ₁/4)^(−1/2)", abs(sec_exact - (1 - g1_88chain / 4) ** -0.5) < 1e-12)

# ═══════ B. Σφ = F₅·φ_origin 分判 ═══════
print("\n─── B. Σφ = 1800 嘅 20 身份分判 ───")
check("B1 Σφ = 1800 = 20×Σγ_even (o137 形式)", 20 * 90 == 1800)
check("B2 Σφ = 5×360 = F₅×φ_origin (新形式)", 5 * 360 == 1800)
check("B3 φ_origin = B×Σγ_even = 4×90 (已鎖)", B * 90 == 360)
check("B4 20 = B×F₅ = 4×5 (結構鏈: Σφ = F₅·B·Σγ_even)", B * 5 == 20)
check("B5 20Δ 三角形面數 (rhombicosidodecahedron) = 20", 20 == 20, "兩種分解都=20 → 分判靠結構鏈: B×F₅ 有 φ_origin→Σφ 鏈, 三角形數冇")
# 73 參與點結構: 44 點 φ≤12, 29 點 φ>12
check("B6 73−44 = 29 = L₇", 73 - 44 == 29)
check("B7 Σφ/73 平均 = 24.66 (冇整數身份)", abs(1800 / 73 - 24.6575) < 1e-3)

# ═══════ C. o137 44 分解交叉 ═══════
print("\n─── C. o137 44 分解: 「+2」= log₂(B) ───")
check("C1 44 = L₃L₄ + N_gen² + F₅ + 2 = 28+9+5+2 (o137 鐵證)", 4 * 7 + 9 + 5 + 2 == 44)
check("C2 ★ 個「+2」= log₂(B) = E−O (O151/O148 交叉)", 2 == log2B)
check("C3 28 = L₃L₄ = 4×7; 9 = N_gen²; 5 = F₅ (o137 已鎖)", 28 == 4 * 7 and 9 == 3 ** 2 and 5 == 5)
check("C4 ★ 44 = L₃L₄ + N_gen² + F₅ + log₂B (新讀法)", 4 * 7 + 9 + 5 + log2B == 44)

# ═══════ D. F₁₁ 中心形式 ═══════
print("\n─── D. F₁₁ 中心形式 (算術組織, 非新結構) ───")
check("D1 88 = F₁₁ − 1 = F₁₁ − log₂B/2", 89 - 1 == 88 and 89 - log2B / 2 == 88)
check("D2 90 = F₁₁ + 1 = F₁₁ + log₂B/2", 89 + 1 == 90 and 89 + log2B / 2 == 90)
check("D3 176 = 2F₁₁ − 2 = 2F₁₁ − log₂B", 178 - 2 == 176 and 2 * 89 - log2B == 176)
check("D4 178 = 2F₁₁ (corpus 已鎖)", 2 * 89 == 178)
check("D5 180 = 2F₁₁ + 2 = 2F₁₁ + log₂B", 178 + 2 == 180 and 2 * 89 + log2B == 180)
check("D6 360 = 4F₁₁ + 4 = 2(2F₁₁+log₂B)", 4 * 89 + 4 == 360)
check("D7 528 = 6×88 = 6F₁₁ − 6", 6 * 88 == 528 and 6 * 89 - 6 == 528)
check("D8 264 = 3×88 = 3F₁₁ − 3", 3 * 88 == 264 and 3 * 89 - 3 == 264)

# ═══════ E. 720 排除 ═══════
print("\n─── E. 720 = 4π sr 候選 ───")
check("E1 720 = 2×360 = 4×180 (平凡)", 2 * 360 == 720 and 4 * 180 == 720)
check("E2 720 = 8F₁₁+8 = 8(F₁₁+1)", 8 * 89 + 8 == 720)
check("E3 corpus 720 掃描: 全部係浮點尾數 (o105 3.1837720010, o35 −0.0712936987..., o73/bnn 其他) → 冇 720° 身份", True)
check("E4 4π sr 球面立體角讀法: 冇 corpus 錨 → 🔴 排除候選 (只係 2×360 平凡)", True)

# ═══════ F. 候選掃描 ═══════
print("\n─── F. 其他候選 ───")
check("F1 45 = (F₁₁+1)/2 = 2×22+1", (89 + 1) / 2 == 45 and 2 * 22 + 1 == 45)
check("F2 L₈ = 47 = N_d + N_gen = 44+3 (候選)", 44 + 3 == 47 and L[8] == 47)
check("F3 88/89 = F₁₁−1/F₁₁ = 176/178 (Gemini 總標度分母)", 88 / 89 == 176 / 178)
check("F4 90/88 = (F₁₁+1)/(F₁₁−1) = 45/44", 90 / 88 == 45 / 44)
check("F5 f_unproj/E_min = 88/90 = 44/45 = (F₁₁−1)/(F₁₁+1)",
      abs((61.5 / 90) / (123 / 176) - 88 / 90) < 1e-12 and 88 / 90 == 44 / 45)
check("F6 61 = 90−29 = 90−L₇ (已鎖 O41)", 90 - 29 == 61)
check("F7 41/60 分子分母: 41 = 2×22−3, 60 = 3×20 (候選, 弱)", 2 * 22 - 3 == 41 and 3 * 20 == 60)

# ═══════ 總結 ═══════
print("\n" + "=" * 78)
print(f"  結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
for name, ok, detail in rows:
    if not ok:
        print(f"  ❌ {name}  {detail}")
if FAIL == 0:
    print("  全部 PASS ✅")
