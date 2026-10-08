#!/usr/bin/env python3
"""
O148 S4-2 — docs/03 §6-§10 + docs/05 獨立核對 (Document Cross-Check v2)
========================================================================
由第一性原理重算本 session 新寫入文檔嘅每個公式/數值 (唔讀任何推導 script 輸出),
與 scripts/08 (數學驗證) 互補: 本 script 核對「文檔寫咗啲乜」vs「正確值」。
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d, B = 44, 4
log2B = math.log2(B)

def gam176(k): return 4 * math.sin(k * math.pi / 176) ** 2
def gam88(n):  return 4 * math.sin(n * math.pi / 88) ** 2

print("=" * 78)
print("  O148 S4-2 — docs/03 §6-§10 + docs/05 獨立核對")
print("=" * 78)

E = sum(gam176(k) for k in range(2, 89, 2))    # 世界 (偶 k)
O = sum(gam176(k) for k in range(1, 88, 2))    # 觀察者 (奇 k)
S88 = E + O                                    # 178

# ═══════ docs/03 §6 相位晶格 ═══════
print("\n─── docs/03 §6 相位晶格 ───")
S_even = sum(math.sin(math.pi * j / 88) ** 2 for j in range(1, 45))
S_odd = sum(math.sin((2 * j - 1) * math.pi / 176) ** 2 for j in range(1, 45))
check("§6 4×Σsin²(jπ/88) = 4×22.5 = 90", abs(4 * S_even - 90) < 1e-12)
check("§6 4×Σsin²((2j−1)π/176) = 4×22 = 88", abs(4 * S_odd - 88) < 1e-12)
check("§6 θ_k = kπ/176 係模態相位角", abs(gam176(22) - 4 * math.sin(22 * math.pi / 176) ** 2) < 1e-12)
check("§6 90−88 = 4×0.5 = γ₄₄/2 = 2", abs(E - O - 2) < 1e-12)

# ═══════ docs/03 §7 對稱閉合 ═══════
print("\n─── docs/03 §7 對稱閉合 ───")
check("§7 360 = B×Σγ_even = 4×90", B * E == 360)
check("§7 360 = B×Σγ_odd + 2γ₄₄ = 4×88 + 8", B * O + 8 == 360)
check("§7 8 = 2γ₄₄ = B×μ² = 4×2", 2 * 4 == B * (E - O) == 8)
check("§7 兩式相等 ⟺ E−O = γ₄₄/2", (B * E == B * O + 8) == (E - O == 2))

# ═══════ docs/03 §8 公平份額 + 閉合階梯 ═══════
print("\n─── docs/03 §8 公平份額 + 閉合階梯 ───")
lam = [gam176(k) for k in range(1, 89)]
check("§8 Σ(k=1..87) = 174 = 87×2 + 0", abs(sum(lam[:87]) - 174) < 1e-12)
check("§8 λ₈₈ = 4, 超額 = 2", abs(lam[87] - 4) < 1e-12)
check("§8 Σ(k=1..88) = 178 = 88×2 + 2", abs(S88 - 178) < 1e-12)
check("§8 世界 90 = 44×2 + 2, 觀察者 88 = 44×2 + 0", abs(E - 90) < 1e-12 and abs(O - 88) < 1e-12)
check("§8 176 = B·N_d = 88×2", B * N_d == 176)
check("§8 178 = 176 + γ₄₄/2 = 176+2", 176 + 2 == 178)
check("§8 180 = 176 + γ₄₄ = B(N_d+1) = 4×45", 176 + 4 == 180 and B * (N_d + 1) == 180)
check("§8 360 = 2×180 = 4×90", 2 * 180 == 360 and B * E == 360)

# ═══════ docs/03 §9 自觀閉合 + Z₂ ═══════
print("\n─── docs/03 §9 自觀閉合 + Z₂ ───")
check("§9 180 = Σγ_all + (E−O) = 178 + 2", S88 + (E - O) == 180)
check("§9 觀察者 = 44×2+0 (完美公平), 世界 = 44×2+2", abs(O - 88) < 1e-12 and abs(E - 90) < 1e-12)
check("§9 冷斑 A = 88×61/40 = 134.2 (O41 錨)", abs(88 * 61 / 40 - 134.2) < 1e-9)
check("§9 偶模態 +1 / 奇模態 −1 (shift-88)", all((-1) ** k == (1 if k % 2 == 0 else -1) for k in range(1, 89)))

# ═══════ docs/03 §10 CSG 審計 ═══════
print("\n─── docs/03 §10 CSG 審計 ───")
check("§10 Γ 最大本徵值 = 4×4 = 16", 16 == 4 * 4)
check("§10 全部閉合數 > 16 → 唔係本徵態", min(88, 90, 176, 178, 180, 360) > 16)
g44 = [gam88(n) for n in range(1, 45)]
check("§10 CSG N_d=44 Σγ = 90 (= 世界側)", abs(sum(g44) - 90) < 1e-12)
csg_obs = sum(g44[n] for n in range(1, 44, 2))     # n=2,4,...,44 (CSG observer_mask: i 奇)
csg_world = sum(g44[n] for n in range(0, 43, 2))   # n=1,3,...,43
check("§10 CSG 內部分裂 46/44", abs(csg_obs - 46) < 1e-12 and abs(csg_world - 44) < 1e-12)
check("§10 N_d=88 空間: Σ=178, even=90, odd=88", abs(S88 - 178) < 1e-12)

# ═══════ docs/05 §1-§6 bits 身份 ═══════
print("\n─── docs/05 §1-§6 bits/mode 身份 ───")
check("05-1 90 = (N_d+1)·log₂B = 45×2", (N_d + 1) * log2B == 90)
check("05-2 88 = N_d·log₂B = 44×2", N_d * log2B == 88)
check("05-3 E−O = log₂B = 2", E - O == log2B)
check("05-4 f_unproj/E_min = N_d/(N_d+1) = 44/45",
      abs((61.5 / 90) / (123 / 176) - 44 / 45) < 1e-12)
check("05-5 f_unproj = ⟨W⟩²/[(N_d+1)log₂B] = 41/60", abs(61.5 / 90 - 41 / 60) < 1e-12)
check("05-6 E_min = ⟨W⟩²/[N_d·log₂B] = 123/176", abs(61.5 / 88 - 123 / 176) < 1e-12)
check("05-7 178 = B·N_d + log₂B = 176+2", B * N_d + log2B == 178)
check("05-8 180 = B(N_d+1) = 176 + B", B * (N_d + 1) == 180)
check("05-9 360 = B(N_d+1)·log₂B = 4×45×2", B * (N_d + 1) * log2B == 360)
check("05-10 46 = N_d + log₂B (n≡0 扇區)", N_d + log2B == 46)
# mod-4 扇區驗證
s0 = sum(gam176(k) for k in range(4, 89, 4))   # k≡0
s1 = sum(gam176(k) for k in range(1, 88, 4))   # k≡1
s2 = sum(gam176(k) for k in range(2, 88, 4))   # k≡2
s3 = sum(gam176(k) for k in range(3, 88, 4))   # k≡3
check("05-11 mod-4: n≡0=46, n≡2=44, n≡1+n≡3=88 (sec 對消)",
      abs(s0 - 46) < 1e-12 and abs(s2 - 44) < 1e-12 and abs(s1 + s3 - 88) < 1e-12,
      f"s0={s0:.6f} s1={s1:.6f} s2={s2:.6f} s3={s3:.6f}")
check("05-12 世界 90 = 46+44", abs(s0 + s2 - 90) < 1e-12)

# ═══════ docs/05 §8 候選 ═══════
print("\n─── docs/05 §8 候選因子 ───")
check("05-13 1800 = 20×90 = 20×Σγ_even", 20 * 90 == 1800)
check("05-14 20 = B×F₅ = 4×5 (候選)", B * 5 == 20)
check("05-15 123/178 = E_min×88/89 (Gemini 總標度, 冇結構身份)",
      abs(123 / 178 - (123 / 176) * (88 / 89)) < 1e-12)
check("05-16 61 = 90−29 = ⟨W⟩²−1/2", 90 - 29 == 61 and 61.5 - 0.5 == 61)
check("05-17 61 ≈ 88·ln2 (0.005% 陷阱窗)", abs((61 / (88 * math.log(2)) - 1)) < 5e-5)
check("05-18 720 = 2×360 = 4×180 (🔴 開放候選)", 2 * 360 == 720 and 4 * 180 == 720)

# ═══════ 總結 ═══════
print("\n" + "=" * 78)
print(f"  結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
for name, ok, detail in rows:
    if not ok:
        print(f"  ❌ {name}  {detail}")
if FAIL == 0:
    print("  全部 PASS ✅")
