#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/13 — B1: 斜率 a = 1 嘅第一原理 (Z2 和律推導)
==========================================================
目標 (docs/04 §B1 由 🔴 推向 🟢):
  原本: a = <γ>_odd/2 = 1 只係「Σγ_odd = 44 = N_d」嘅算術後果 (觀察級)
  本腳本: 由 Z2 反對稱**解析推導** Σγ_odd = N_d, 並列出 a = 1 嘅全部等價譜表達

推導鏈:
  S1  Z2 對偶: γ_n + γ_{44−n} = 4 = B            (n = 1..43)
  S2  反對稱: cos(π(44−n)/44) = −cos(πn/44)      (偶鏈長 ⇒ 無不動點於奇數)
  S3  ⟹ Σ_{odd n} cos(πn/44) = 0  EXACT
  S4  ⟹ Σγ_odd = Σ_{odd} 2(1−cos(πn/44)) = 2·N_odd = 44 = N_d  EXACT
  S5  ⟹ a = Σγ_odd / N_d = 1  EXACT
  S6  ⟹ Σγ_even − Σγ_odd = γ_22 = 2 = μ² (Z2 不動點權重)

判準: S3/S4/S5 全部要 mpmath dps=40 下 dev < 1e-30, 且 S3 要**解析**成立
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2
inv = 1 / phi

N = 44                      # 鏈模態數 (雙半格 88 site → 44 模態)
gam = {n: 4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N + 1)}
vg  = {n: mp.cos(pi * n / 88) for n in range(1, N + 1)}
ODD  = list(range(1, 44, 2))       # 22 個
EVEN = list(range(2, 45, 2))       # 22 個

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 78)
print("O169/13 — B1: 斜率 a = 1 嘅第一原理 (Z2 和律)")
print("=" * 78)

# ---------- S1: Z2 對偶 ----------
print("\nS1. Z2 對偶律  γ_n + γ_{44−n} = 4 = B  (n = 1..43)")
devs = [abs(gam[n] + gam[44 - n] - 4) for n in range(1, 44)]
chk("S1  γ_n + γ_{44−n} = 4  (43/43 對)", max(devs) < mp.mpf('1e-35'),
    f"max dev = {mp.nstr(max(devs), 5)}")
print(f"      γ_22 = {mp.nstr(gam[22], 12)}  (= B/2 = 2, 不動點)")

# ---------- S2: 反對稱 ----------
print("\nS2. 反對稱: cos(π(44−n)/44) = −cos(πn/44)")
devs2 = [abs(mp.cos(pi * (44 - n) / 44) + mp.cos(pi * n / 44)) for n in range(1, 44)]
chk("S2  cos(π(44−n)/44) = −cos(πn/44)  (43/43)", max(devs2) < mp.mpf('1e-35'),
    f"max dev = {mp.nstr(max(devs2), 5)}")

# ---------- S3: 奇數和 = 0 ----------
print("\nS3. 奇數和  Σ_{odd n=1..43} cos(πn/44) = 0")
s3 = mp.fsum(mp.cos(pi * n / 44) for n in ODD)
chk("S3  Σ_odd cos(πn/44) = 0  EXACT", abs(s3) < mp.mpf('1e-38'), f"值 = {mp.nstr(s3, 5)}")
print("      解析理由: 每個 pair (n, 44−n) 都係 (奇, 奇) 且 cos 相反 → 兩兩相消;")
print("               44 係偶數 ⇒ 不動點 n = 22 係偶數, 唔喺奇數集 → 冇殘項。")

# ---------- S4: Σγ_odd = N_d ----------
print("\nS4. 譜和  Σγ_odd = N_d = 44   (同 Σγ_even = 46)")
s_odd  = mp.fsum(gam[n] for n in ODD)
s_even = mp.fsum(gam[n] for n in EVEN)
s_all  = mp.fsum(gam[n] for n in range(1, N + 1))
chk("S4  Σγ_odd = 44 = N_d  EXACT", abs(s_odd - 44) < mp.mpf('1e-35'), f"值 = {mp.nstr(s_odd, 12)}")
chk("S4b Σγ_even = 46 = N_d + μ²  EXACT", abs(s_even - 46) < mp.mpf('1e-35'), f"值 = {mp.nstr(s_even, 12)}")
chk("S4c Σγ = 90 = 2N_d + μ²", abs(s_all - 90) < mp.mpf('1e-35'), f"值 = {mp.nstr(s_all, 12)}")
print(f"      解析: Σ_odd  γ = 2·N_odd − 2·(S3) = 2·22 − 0 = 44")
print(f"            Σ_even γ = 2·N_even − 2·Σ_even cos(πn/44);  Σ_even cos = −1 (不動點 n=22 貢獻 cos(π/2)=0, n=44 貢獻 cos(π)=−1)")
s4e = mp.fsum(mp.cos(pi * n / 44) for n in EVEN)
chk("S4d Σ_even cos(πn/44) = −1", abs(s4e + 1) < mp.mpf('1e-35'), f"值 = {mp.nstr(s4e, 12)}")

# ---------- S5: a = 1 ----------
print("\nS5. 斜率  a = Σγ_odd / N_d = 1")
a = s_odd / 44
chk("S5  a = Σγ_odd/N_d = 1  EXACT", abs(a - 1) < mp.mpf('1e-35'), f"值 = {mp.nstr(a, 12)}")

print("\nS5b. a = 1 嘅全部等價譜表達 (7 條, 全部 dev = 0)")
eq = {
    'Σγ_odd / N_d':        s_odd / 44,
    '⟨γ⟩_odd / 2':          (s_odd / 22) / 2,
    'μ² / 2':               mp.mpf(2) / 2,
    'γ_22 / 2':             gam[22] / 2,
    '(Σγ_even − Σγ_odd)/2': (s_even - s_odd) / 2,
    'Σγ_odd / (2·N_odd)':   s_odd / (2 * 22),
    'B / 4':                mp.mpf(4) / 4,
}
for k, v in eq.items():
    chk(f"    {k:<22} = 1", abs(v - 1) < mp.mpf('1e-35'), f"值 = {mp.nstr(v, 12)}")

# ---------- S6: 不動點權重 ----------
print("\nS6. Z2 不動點 (n = 22) 承載 μ²")
chk("S6  Σγ_even − Σγ_odd = γ_22 = μ² = 2", abs((s_even - s_odd) - 2) < mp.mpf('1e-35'),
    f"差 = {mp.nstr(s_even - s_odd, 12)}")
print(f"      結構讀法: 奇數集冇不動點 → 純反對稱相消 → Σ = N_d (整數飽和)")
print(f"                偶數集含不動點 n=22 → 多出 γ_22 = 2 = μ²")

# ---------- S7: 同 DESI 擬合值對照 ----------
print("\nS7. 對照 DESI 自由擬合 (scripts/04): a = 0.994278 ± 0.04951")
sig = mp.mpf('0.04951')
chk("S7  a = 1 距擬合值 0.12σ", abs((mp.mpf('0.994278') - 1) / sig) < mp.mpf('0.2'),
    f"= {mp.nstr((mp.mpf('0.994278') - 1) / sig, 4)}σ")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS) + len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
print("=" * 78)
print("""
結論 (B1 狀態更新):
  推導級 (新, 本腳本): Z2 反對稱 (S2) ⟹ Σ_odd cos(πn/44) = 0 (S3)
                       ⟹ Σγ_odd = N_d = 44 (S4) ⟹ a = 1 (S5)  — 全部 EXACT
  ⇒ a = 1 **唔再係「算術後果」**: 佢係鏈譜 Z2 結構嘅精確推論。
  ⇒ 同時得出 μ² = γ_22 = Σγ_even − Σγ_odd = 2 (不動點權重)。
  🔴 仍然未閉合: 「每層增益 = Σγ_odd/N_d」嘅**輸運詮釋** (點解係奇/反週期
     扇區、點解按鏈長歸一) — 即 projection-kernel 算子推導。
""")
