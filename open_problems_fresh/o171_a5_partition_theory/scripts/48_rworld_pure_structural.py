"""
O171 攻堅 48: R_world 純結構鎖定 — 可能定不可能?
=================================================================
用戶問: 「是否不能純結構鎖定?」

分三層回答:
  1. 維度論證 (O201 ⑨): R_world 有量綱 (Mpc), 結構數無量綱
     → 冇長度單位錨, 結構上不可能
  2. 更大範圍純結構掃描: 完整 IDCM 結構數庫 × 基本算子
     → 有冇意外命中? (過陷阱窗 + 避 tautology)
  3. 長度錨候選: λ_sync (循環) / l_P (物理) / r_d (觀測) / r_s (循環)
     → 判決: 邊種「純結構」可行, 邊種唔可能
"""
import mpmath as mp
mp.mp.dps = 30

c = mp.mpf('299792.458')
omega = mp.mpf('72.59')
R = c / omega  # 4129.9416 精確值

print("=" * 74)
print("1. 維度論證 (O201 ⑨) — 有量綱 vs 無量綱")
print("=" * 74)
print("""
  R_world = 4129.94 Mpc  ← 有量綱 (長度)
  結構數 (44, 88, 90, 178, 420, 421, L₄=7, L₅=11, L₇=29, A₅=60...)  ← 無量綱

  譜泛函 (γ_n = 4sin²(πn/176), Σγ, beat(i,j)...) 全部無量綱
  → 任何「無量綱結構數嘅代數組合」結果仍然無量綱
  → 結構上唔可能等於一個「有量綱嘅長度」
  → 除非乘一個「長度單位」L_unit:
       R_world = (結構數組合) × L_unit

  ★ 問題變成: L_unit 係咩?
     候選:
       a. λ_sync = L_ring/88 = πR/44  ← 循環! (定義就用咗 R)
       b. r_s = λ_sync/2 = πR/88      ← 循環! (一樣)
       c. l_P (Planck 長度)            ← 物理常數, 唔係結構數
       d. r_d (drag 聲學視界)          ← 觀測量!
       e. T_CMB 相關                    ← 觀測

  → 「純結構鎖定」冇可能: 結構數組合永遠無量綱,
     R_world 需要長度錨, 而所有長度錨都係 (循環/物理/觀測)
""")

print("=" * 74)
print("2. 更大範圍純結構掃描 (確認冇意外命中)")
print("=" * 74)
S = {
    "33": 33, "34": 34, "44": 44, "45": 45, "55": 55, "56": 56,
    "420": 420, "421": 421,
    "L2": 3, "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29,
    "L8": 47, "L9": 76, "L10": 123,
    "F4": 3, "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F10": 55,
    "88": 88, "90": 90, "176": 176, "178": 178, "264": 264,
    "946": 946, "60": 60, "12": 12, "15": 15, "16": 16,
}
print(f"  結構數庫: {len(S)} 個")
# 掃描: R/(a) 商, R/(a±b), R/(a*b), R*a, R*a/b
hits = []
vals = sorted(set(S.values()))
for a in vals:
    if a == 0:
        continue
    # 單數: R/a, R*a
    for label, v in [("R/a", R/a), ("R*a", R*a)]:
        d = abs(v - round(v))
        if d < 1e-2 and v != 0:  # 放寬到 1e-2 睇有冇「接近整數」
            hits.append((float(d/round(v)*100), f"{label} (a={a}) = {mp.nstr(v,7)} ≈ {round(v)}"))
for i, a in enumerate(vals):
    if a == 0:
        continue
    for j, b in enumerate(vals):
        if j <= i or b == 0:
            continue
        for label, v in [("R/(a+b)", R/(a+b)), ("R/(a-b)", R/(a-b) if a != b else None),
                         ("R/(a*b)", R/(a*b)), ("R*a/b", R*a/b), ("R*b/a", R*b/a)]:
            if v is None or v == 0:
                continue
            d = abs(v - round(v))
            if d < 1e-2:
                hits.append((float(d/round(v)*100), f"{label} (a={a},b={b}) = {mp.nstr(v,7)} ≈ {round(v)}"))
hits.sort()
print(f"  接近整數命中 (dev < 1e-2): {len(hits)}")
for dev, desc in hits[:15]:
    trap = " ⚠️陷阱窗" if 1e-3 < dev < 0.1 else ""
    print(f"    {dev:.5f}%: {desc}{trap}")
if not hits:
    print("    (冇)")

print()
print("=" * 74)
print("3. 長度錨候選分析")
print("=" * 74)
lam_sync = mp.pi * R / 44
r_s = lam_sync / 2
print(f"  a. λ_sync = L_ring/88 = πR/44 = {mp.nstr(lam_sync, 6)} Mpc — 循環 (定義用 R)")
print(f"  b. r_s = λ_sync/2 = πR/88 = {mp.nstr(r_s, 6)} Mpc — 循環")
print(f"  c. l_P = 1.616e-35 m — 物理常數 (唔係結構數)")
R_lP = R * mp.mpf('3.0856775814913673e22') / mp.mpf('1.616255e-35')
print(f"     R_world/l_P = {mp.nstr(R_lP, 5)} — 冇結構")
print(f"  d. r_d = 147.09 Mpc — 觀測 (Planck)")
F = mp.mpf(88) * 421 / (420 * mp.pi)
print(f"     R_world/r_d = 88×421/(420π) = {mp.nstr(F, 6)} ← 唯一非循環純結構比!")

print()
print("=" * 74)
print("4. 判決")
print("=" * 74)
print(f"""
  🔴 「純結構直接鎖定」— 結構上不可能:
     有量綱 R_world 需要長度錨, 結構數組合無量綱 (O201 ⑨)
     → 冇「無量綱結構數 → 有量綱長度」嘅數學通道

  🟡 「純結構比鎖定」— 已經成立:
     R_world/r_d = 88×421/(420π) = 28.078 (純結構比)
     → 但呢個需要 r_d 做絕對尺度錨 (觀測量)

  🔴 循環錨 (λ_sync, r_s) 唔算: 定義就用咗 R

  ★ 結論: R_world = 4129.94 Mpc 嘅絕對尺度必須來自:
       (a) 觀測錨 (r_d, η_B, T_CMB, ω_cmb) — 三重鎖定已成立
       (b) 物理常數長度 (l_P) — 但 R/l_P 冇結構身份
     → 「純結構」+「絕對尺度」兩者不可兼得
     → 正確表述: R_world 唔係自由參數 (三重鎖定),
       但唔係「純結構導出量」(冇純結構長度單位)

  🟢 可證偽預言: 如果未來搵到 R/l_P 有結構身份
     → 純結構鎖定重生 (但 l_P 本身係物理輸入)
""")
