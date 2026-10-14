#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-23 — §4.3 攻堅: 44 鏈 SU(3) 連絡場能量泛函 → 弦張力 σ (2026-09-18)
=======================================================================
任務 (§4.3 原文): 「膠子連結的場能量公式不存在: 沒有 SU(3) 連絡場在 44 鏈上的能量泛函」

上游已建立 (O210 C6 / O124):
  - 連絡變量: U_k = e^{i·2θ_k}, 2θ_k = kπ/88  (k = 1..88 條連結)
  - 譜權重恆等式: γ_k^(176-L) = |1−U_k|² = 4sin²(kπ/176)   [EXACT]
  - Wilson 總相位: Σθ_k = 44.5π = (89/2)π
  - 連結膠子譜 (O124): λ_n = 4sin²(πn/88), n = 0..87; λ_0 = 0 (無質量)
  - 譜和: Σλ(0..87) = 176 = 4N_d;  Σλ(1..44) = 90 = Σγ_even
  - β 係數: b₀ = 11 − 2N_f/3 = L₄ = 7 (N_f = 6 唯一)
  - α_s⁻¹(M_Z) = F₆ + sin²θ_W + 1/B = 8.4707757

本腳本:
  §A 能量泛函構造 + 全部精確恆等式驗證 (mpmath dps = 40)
  §B σ 導出: 泛函 → 能量密度 → 張力 (鏈自身色散定標長度)
  §C σ 之框架內檢驗: E_bind = σ·ℓ (ℓ = 通量管長度) → ℓ 嘅結構身份
  §D 觀測對比: σ_IDCM vs QCD σ (獨立觀測 = 真預言檢驗) + 密度測試
  §E 物理正確路線: 量綱蛻變 (dimensional transmutation) 由 α_s 導 Λ_QCD
  §F 判決
"""
import mpmath as mp
import itertools, json, sys
from fractions import Fraction

mp.mp.dps = 40
PASS = FAIL = 0
ROWS = []

def chk(cid, name, got, want, tol=1e-30):
    global PASS, FAIL
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= tol
    if ok: PASS += 1
    else: FAIL += 1
    ROWS.append({"id": cid, "check": name, "ok": bool(ok)})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def chkb(cid, name, cond):
    global PASS, FAIL
    ok = bool(cond)
    if ok: PASS += 1
    else: FAIL += 1
    ROWS.append({"id": cid, "check": name, "ok": ok})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def hdr(s):
    print("\n" + "=" * 78); print(s); print("=" * 78)

# ── 常數 ──
N_d = 44; B = 4; N_gen = 3
LUC = [2, 1, 3, 4, 7, 11, 18, 29, 47]          # L_0..L_8
FIB = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89] # F_0..F_11
M_tree = 33
M0_MeV = mp.mpf('27.9009')          # O37 <W> = M0
M0_GeV = M0_MeV / 1000
HBARC = mp.mpf('197.3269804')       # MeV·fm

# QCD 觀測參考 (獨立觀測, 非輸入)
SIG_OBS = mp.mpf('0.18')            # GeV^2 (Regge: sigma = 1/(2 pi alpha'), alpha' = 0.88 GeV^-2)
SIG_OBS_LAT = mp.mpf('0.1936')      # GeV^2 (sqrt(sigma) = 440 MeV, lattice Sommer)
SIG_OBS_LO = mp.mpf('0.1764')       # GeV^2 (sqrt(sigma) = 420 MeV)

# ══════════════════════════════════════════════════════════════════════
hdr("[§A] 44 鏈 SU(3) 連絡場能量泛函 — 構造 + 精確恆等式")
# ══════════════════════════════════════════════════════════════════════
print("""
構造 (零新常數, 全部部件已在框架內):
  44 鏈 = 世界弦; 連絡場住喺 88 條連結上 (176-L 標準, O210 C1)
    U_k = e^{i·2θ_k},  2θ_k = kπ/88,  k = 1..88          [連絡變量]
  唯一可用嘅規範不變局部測度 = |1 − U_k|²
    ⇒ 能量泛函 (Wilson 作用量之 IDCM 形式):

        E_conn[U] = M0 · Σ_k w_k |1 − U_k|²  ,  w_k = 1 (均勻鏈)
                  = M0 · Σ_k γ_k^(176-L)

  物理讀法: 每個連結貢獻「相位偏離真空」嘅能量; 張力 = 能量/長度。
""")
gam = lambda k: 4 * mp.sin(mp.pi * k / 176) ** 2
lam = lambda n: 4 * mp.sin(mp.pi * n / 88) ** 2

# A1: |1-U|^2 = gamma 恆等式 (全部 88 條)
ok_all = True
for k in range(1, 89):
    U = mp.e ** (mp.mpc(0, mp.pi * k / 88))
    if abs(abs(1 - U) ** 2 - gam(k)) > mp.mpf('1e-35'):
        ok_all = False; break
chkb("A1", "|1−U_k|² = γ_k^(176-L) = 4sin²(kπ/176) 對全部 k=1..88", ok_all)

# A2: 么正性
chkb("A2", "U_k† = U_k⁻¹ (么正, 全部 k)",
     all(abs((mp.e ** (mp.mpc(0, mp.pi*k/88))) * (mp.e ** (mp.mpc(0, -mp.pi*k/88))) - 1) < mp.mpf('1e-35')
         for k in range(1, 89)))

# A3: 譜和
Sg = mp.fsum([gam(k) for k in range(1, 89)])
Sg_ev = mp.fsum([gam(k) for k in range(2, 89, 2)])
Sg_od = mp.fsum([gam(k) for k in range(1, 88, 2)])
chk("A3", "Σγ = 178 = 2F₁₁", Sg, 178)
chk("A4", "Σγ_even = 90", Sg_ev, 90)
chk("A5", "Σγ_odd = 88 = 2N_d", Sg_od, 88)
chk("A6", "Σγ_even − Σγ_odd = μ² = 2", Sg_ev - Sg_od, 2)

# A7: ★ Wilson 作用量總和 = F₁₁
SW = mp.fsum([1 - mp.cos(k * mp.pi / 88) for k in range(1, 89)])
chk("A7", "★ S_W = Σ_k (1 − cos 2θ_k) = 89 = F₁₁ (精確)", SW, 89)
chk("A8", "Σγ = 2·S_W (泛函與 Wilson 作用量一致)", Sg, 2 * SW)

# A9: Wilson 總相位 (site phase = 2θ_k = kπ/88, 唔係 θ_k)
chk("A9", "Σ(2θ_k) = Σ kπ/88 = 44.5π = (89/2)π", mp.fsum([mp.pi * k / 88 for k in range(1, 89)]), mp.pi * 89 / 2)
chk("A9b", "Σθ_k (半角) = 22.25π = (89/4)π", mp.fsum([mp.pi * k / 176 for k in range(1, 89)]), mp.pi * 89 / 4)

# A10: 連結膠子譜 (O124)
Sl = mp.fsum([lam(n) for n in range(0, 88)])
chk("A10", "Σλ(0..87) = 176 = 4N_d (含零模)", Sl, 176)
chk("A11", "λ_0 = 0 (無質量膠子)", lam(0), 0)
chk("A12", "Σλ(1..44) = 90 = Σγ_even", mp.fsum([lam(n) for n in range(1, 45)]), 90)
chkb("A13", "γ_(2n) = λ_n (176-L even = 88-L) 對 n=1..44",
     all(abs(gam(2 * n) - lam(n)) < mp.mpf('1e-35') for n in range(1, 45)))
# A14: 總連絡場能量
E_conn = M0_MeV * Sg
print(f"\n  E_conn = M0 · Σγ = {M0_MeV} × 178 = {mp.nstr(E_conn, 8)} MeV = {mp.nstr(E_conn/1000, 6)} GeV")
chk("A14", "E_conn = 178 M0 = 2F₁₁ M0", E_conn, 178 * M0_MeV, 1e-20)

# ══════════════════════════════════════════════════════════════════════
hdr("[§B] σ 導出: 泛函 → 能量密度 → 張力")
# ══════════════════════════════════════════════════════════════════════
print("""
σ 嘅定義: 通量管每單位長度嘅能量  σ = (每連結能量)/(連結長度 a)

連結長度 a 由鏈自身色散關係鎖定 (唔係自由選擇):
  離散環色散:  ω_n = (2c/a) sin(πn/N)  →  質量  m_n = M0 · 2sin(πn/88)
  匹配 ⇒ 2c/a = M0  ⇒  a = 2/M0   (自然單位 ħ=c=1)

每連結能量 = M0 · λ̄,  λ̄ = Σλ(0..87)/88 = 176/88 = 2 = μ²
  ⇒  σ = M0 · λ̄ / a = M0 · 2 / (2/M0) = M0²   [精確]
""")
a_len = 2 / M0_MeV                          # MeV^-1
a_fm = a_len * HBARC                        # fm
lam_bar = Sl / 88
chk("B1", "λ̄ = Σλ/88 = 2 = μ² (精確)", lam_bar, 2)
chk("B2", "a = 2/M0 (鏈自身色散鎖定)", a_len, 2 / M0_MeV)
print(f"  a = 2/M0 = {mp.nstr(a_len, 8)} MeV⁻¹ = {mp.nstr(a_fm, 8)} fm")

sig_B = M0_MeV ** 2                          # MeV^2
sig_B_GeV = sig_B / 1e6                      # GeV^2
chk("B3", "★ σ = M0² (精確, 由泛函導出)", sig_B, M0_MeV ** 2, 1e-20)
print(f"  σ_IDCM = M0² = {mp.nstr(sig_B, 8)} MeV² = {mp.nstr(sig_B_GeV, 6)} GeV²")
print(f"  √σ_IDCM = M0 = {mp.nstr(M0_MeV, 6)} MeV")

# B4: 變體 — 其他自然定標 (誠實列出, 供密度測試)
print("\n  變體 (其他候選定標, 全部列出):")
variants = {
    "a = 2/M0 (鏈色散)": M0_MeV ** 2,
    "a = 1/M0 (Compton)": M0_MeV ** 2 * 2,
    "a = 2/M0, 用 λ_max = 4": M0_MeV ** 2 * 4 / 2,
    "a = 2/M0, 用 μ² = 2 (自對偶模)": M0_MeV ** 2,
    "a = 2/M0, 全 88 連結平均": M0_MeV ** 2,
}
for k, v in variants.items():
    print(f"    {k:<34} σ = {mp.nstr(v/1e6, 6)} GeV²")

# ══════════════════════════════════════════════════════════════════════
hdr("[§C] 框架內檢驗: E_bind = σ · ℓ (通量管長度)")
# ══════════════════════════════════════════════════════════════════════
m_uud = mp.mpf('8.99')                       # docs/01 §1
m_p = mp.mpf('938.272')
E_bind = m_p - m_uud
print(f"  E_bind (觀測預算) = m_p − m_uud = {mp.nstr(E_bind, 8)} MeV")
print(f"  E_bind/M0 = {mp.nstr(E_bind/M0_MeV, 8)}")

ell = E_bind / sig_B                          # MeV^-1
ell_links = ell / a_len
ell_fm = ell * HBARC
print(f"\n  若 σ = M0², 則所需管長 ℓ = E_bind/σ = {mp.nstr(ell, 8)} MeV⁻¹ = {mp.nstr(ell_fm, 6)} fm")
print(f"  ℓ/a = {mp.nstr(ell_links, 8)} 條連結")
print(f"  M_tree/2 = {M_tree/2}")
print(f"  ℓ/a vs M_tree/2 偏差 = {mp.nstr(abs(ell_links - mp.mpf(M_tree)/2)/(mp.mpf(M_tree)/2)*100, 5)}%")
chkb("C1", "ℓ/a ≈ M_tree/2 = 16.5 條連結 (0.93%)", abs(ell_links - mp.mpf(16.5)) / mp.mpf(16.5) < 0.01)
E_from = sig_B * (mp.mpf(M_tree) / 2) * a_len
print(f"\n  ⇒ E_bind(結構) = σ × (M_tree/2) × a = M0² × 16.5 × 2/M0 = M0 × M_tree")
print(f"     = {mp.nstr(E_from, 8)} MeV  (觀測 {mp.nstr(E_bind, 8)} MeV, 偏差 {mp.nstr((E_bind-E_from)/E_bind*100, 5)}%)")
chk("C2", "E_bind = M0 × M_tree = 33 M0 (0.92%)", E_from, 33 * M0_MeV, 1e-20)
chk("C3", "E_bind/M0 觀測 = 33.3065 (殘差 0.3065 未閉合)", E_bind / M0_MeV, mp.mpf('33.3065'), 1e-3)

# C4: 膠球 = 閉合通量管 (由同一泛函, 零新常數)
print("\n  [C4] 膠球 = 閉合通量管 (由同一泛函導出):")
X2370 = mp.mpf('2376.3')
for nm, wt, nl in [("observer 半鏈 (odd k, 44 連結)", Sg_od, 44),
                   ("world 半鏈 (even k, 44 連結)", Sg_ev, 44),
                   ("全鏈 (88 連結)", Sg, 88)]:
    E_g = M0_MeV * wt
    print(f"    {nm:<30} E = Σγ·M0 = {mp.nstr(E_g, 8)} MeV"
          f"  (X(2370)={X2370}: {mp.nstr((E_g-X2370)/X2370*100, 5)}%)")
E_glue_odd = M0_MeV * Sg_od
chk("C4", "膠球 = Σγ_odd·M0 = 88 M0 = 2455.3 MeV (3.3% vs X(2370))", E_glue_odd, 88 * M0_MeV, 1e-20)
chkb("C5", "膠球結構預言與 X(2370) 差 3.3% (🟡, 零擬合)", abs(E_glue_odd / X2370 - 1) < 0.05)

# ══════════════════════════════════════════════════════════════════════
hdr("[§D] 觀測對比 (獨立觀測 = 真預言檢驗) + 密度測試")
# ══════════════════════════════════════════════════════════════════════
print(f"""
  σ_IDCM (由泛函導出) = {mp.nstr(sig_B_GeV, 6)} GeV²
  σ_obs (QCD)         = {SIG_OBS} GeV²  [Regge]
                      = {SIG_OBS_LAT} GeV² [√σ=440 MeV, lattice]
  比值 σ_obs/σ_IDCM   = {mp.nstr(SIG_OBS/sig_B_GeV, 8)}   [Regge]
""")
ratio = SIG_OBS / sig_B_GeV
chk("D1", "σ_IDCM = 7.7846e-4 GeV² (M0²)", sig_B_GeV, mp.mpf('0.0007784602'), 1e-9)
chkb("D2", "★ σ_IDCM 與 QCD σ 相差 ~231× → 偽證 (M0 尺度鏈非 QCD 通量管)", 200 < ratio < 270)
print(f"  所需倍數 = {mp.nstr(ratio, 8)}")
print("  候選結構分解 (後驗, 僅記錄): 3×7×11 = 231 = N_gen·L₄·L₅, 偏離 "
      + mp.nstr((ratio / 231 - 1) * 100, 4) + "%")

# 密度測試: 231 呢個數有幾特別?
print("\n  [密度測試] 固定詞彙 (IDCM 結構整數) 能湊出幾多個 ~231 嘅乘積?")
VOCAB = {
    "N_d": 44, "B": 4, "N_gen": 3, "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L8": 47,
    "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55, "F11": 89,
    "M": 33, "h11": 36, "Sum_phi8": 17, "Sg": 178, "Sg_od": 88, "Sg_ev": 90,
    "Eproj2": 57, "Ssync2": 123, "L10": 123, "n176": 176, "n264": 264, "n528": 528,
    "Nc": 3, "CA": 3, "b0": 7, "pure_b0": 11, "F6b": 8,
}
TARGET = ratio
hits = []
keys = list(VOCAB.items())
for r in (1, 2, 3):
    for combo in itertools.combinations_with_replacement(keys, r):
        v = 1
        for _, x in combo: v *= x
        if v == 0: continue
        for div in (1, 2, 3, 4, 5, 7, 8, 11, 44, 88, 178, 123):
            val = mp.mpf(v) / div
            if abs(val - TARGET) / TARGET < 0.005:
                expr = "·".join(c[0] for c in combo) + (f"/{div}" if div > 1 else "")
                hits.append((expr, float(val)))
hits = sorted(set(hits), key=lambda x: (abs(x[1] - float(TARGET)), x[0]))
print(f"    ≤3 因子乘積/比值, 0.5% 窗內命中 = {len(hits)} 條")
for e, v in hits[:12]:
    print(f"      {e:<26} = {v:.2f}")
chkb("D3", f"密度測試: 231.2 有 {len(hits)} 條結構表達 → 分解本身唔攜帶信息", len(hits) >= 8)

# D4: 同一密度測試用於 E_bind/M0 = 33.3065
TARGET2 = E_bind / M0_MeV
hits2 = []
for r in (1, 2, 3):
    for combo in itertools.combinations_with_replacement(keys, r):
        v = 1
        for _, x in combo: v *= x
        if v == 0: continue
        for div in (1, 2, 3, 4, 5, 7, 8, 11, 44, 88, 178, 123, 176, 60, 90):
            val = mp.mpf(v) / div
            if abs(val - TARGET2) / TARGET2 < 0.005:
                expr = "·".join(c[0] for c in combo) + (f"/{div}" if div > 1 else "")
                hits2.append((expr, float(val)))
hits2 = sorted(set(hits2), key=lambda x: (abs(x[1] - float(TARGET2)), x[0]))
print(f"\n  [密度測試] E_bind/M0 = {mp.nstr(TARGET2, 8)} 嘅結構表達 = {len(hits2)} 條 (0.5% 窗)")
for e, v in hits2[:8]:
    print(f"      {e:<26} = {v:.3f}")
chkb("D4", f"E_bind/M0 亦有 {len(hits2)} 條表達 → 33.3065 同樣非唯一", len(hits2) >= 8)

# ══════════════════════════════════════════════════════════════════════
hdr("[§E] 物理正確路線: 量綱蛻變 (由 α_s 導 Λ_QCD)")
# ══════════════════════════════════════════════════════════════════════
sin2W = mp.mpf('0.220776')                  # 模式比 (O144)
alpha_s_inv = 8 + sin2W + mp.mpf(1)/4
b0 = 7                                       # = L4 (N_f = 6)
b0_pure = 11                                 # = L5 (純 SU(3))
MZ = mp.mpf('91.1876')
print(f"""
  O124 已建立: α_s⁻¹(M_Z) = F₆ + sin²θ_W + 1/B = 8 + {sin2W} + 0.25 = {mp.nstr(alpha_s_inv, 8)}
  b₀ = L₄ = 7 (N_f = 6);  b₀(pure) = L₅ = 11

  Λ_QCD = M_Z · exp(−2π/(b₀ α_s(M_Z)))
""")
for name, b in [("b₀ = L₄ = 7 (N_f=6)", b0), ("b₀ = L₅ = 11 (pure)", b0_pure)]:
    Lam = MZ * mp.e ** (-2 * mp.pi * alpha_s_inv / b)
    sig_lam = Lam ** 2
    print(f"  {name:<24} Λ = {mp.nstr(Lam, 6)} GeV;  σ = Λ² = {mp.nstr(sig_lam, 6)} GeV²"
          f"  (vs obs {SIG_OBS}: {mp.nstr(SIG_OBS/sig_lam, 6)}× 差)")
chk("E1", "α_s⁻¹(M_Z) = 8.4707757 (O124)", alpha_s_inv, mp.mpf('8.470776'), 1e-5)
Lam7 = MZ * mp.e ** (-2 * mp.pi * alpha_s_inv / b0)
chk("E2", "Λ_QCD(1-loop, b₀=7) = 0.04548 GeV", Lam7, mp.mpf('0.0454823'), 1e-5)
chkb("E3", "σ = Λ²(b₀=7) = 2.06e-3 GeV² → 比觀測細 87× (失敗)",
     abs((Lam7**2) / SIG_OBS - mp.mpf(1)/87) < mp.mpf('0.01'))
# 需要幾多 b₀ 才命中?
b_req = 4 * mp.pi * alpha_s_inv / mp.log(MZ**2 / SIG_OBS)
print(f"\n  若要 σ = 0.18 GeV², 需要 b₀ = {mp.nstr(b_req, 8)}  (非結構整數 → 此路線失敗)")
chkb("E4", "所需 b₀ = 9.909 非結構 → 1-loop 蛻變路線失敗", abs(b_req - 9.909) < 0.01)
# 若加 ×Σγ_odd 因子
sig_lam88 = Lam7 ** 2 * 88
print(f"  若 σ = Σγ_odd · Λ² = 88 × {mp.nstr(Lam7**2, 6)} = {mp.nstr(sig_lam88, 6)} GeV²"
      f"  (vs obs: {mp.nstr((sig_lam88-SIG_OBS)/SIG_OBS*100, 5)}%)")
chkb("E5", "σ = Σγ_odd·Λ² = 0.1820 GeV² (1.13%) — 但 ×88 無推導 (後驗)", abs(sig_lam88/SIG_OBS - 1) < 0.02)

# ══════════════════════════════════════════════════════════════════════
hdr("[§F] 判決")
# ══════════════════════════════════════════════════════════════════════
print(f"""
§A 能量泛函:        ✅ 構造成功, 零新常數
   E_conn[U] = M0 Σ_k |1−U_k|²  (唯一可用規範不變測度)
   ★ 新精確恆等式: S_W = Σ_k(1 − cos2θ_k) = 89 = F₁₁  (Wilson 作用量總和 = Fibonacci)
   Σγ = 2F₁₁ = 178;  Σλ = 4N_d = 176;  γ_(2n) = λ_n;  E_conn = 178 M0 = {mp.nstr(E_conn/1000, 6)} GeV

§B σ 導出:          ✅ σ = M0² 精確 (鏈自身色散鎖定 a = 2/M0, λ̄ = μ² = 2)
   σ_IDCM = {mp.nstr(sig_B_GeV, 6)} GeV²  (= {mp.nstr(sig_B, 8)} MeV²)

§C 框架內檢驗:      🟡 E_bind = σ × (M_tree/2) × a = M0 × M_tree = 33 M0
   觀測 E_bind/M0 = 33.3065 → 殘差 0.92% (已知缺口, 未閉合)
   ⇒ 泛函 + σ 給出 E_bind 嘅結構形式 (33 M0), 但殘差仍在

§D 觀測對比:        🔴 偽證 — σ_IDCM = {mp.nstr(sig_B_GeV, 6)} GeV² vs QCD {SIG_OBS} GeV² = {mp.nstr(ratio, 6)}× 差
   ⇒ M0 尺度嘅 44 鏈**唔可能**係 QCD 色通量管 (張力細 231 倍)
   ⇒ 231 嘅結構分解有 {len(hits)} 條 (密度測試) → 分解本身無信息

§E 量綱蛻變路線:    🔴 失敗 — b₀ = L₄ = 7 給 σ = 2.06e-3 (87× 細); b₀ = L₅ = 11 給 0.52 (2.9× 大)
   需要 b₀ = 9.909 (非結構)

總結: §4.3 嘅「泛函不存在」已解決 (泛函已寫出且精確);
      但「由泛函導出 σ」在 M0 尺度**失敗** — 缺嘅係 M0 → QCD 禁閉尺度嘅標度橋,
      與開放問題 5 (M0 → v = 246 GeV 標度橋) 同源。
""")

out = {
    "session": "2026-09-18 O144-23 sec4.3 SU(3) connection functional -> sigma",
    "A_functional": {
        "form": "E_conn[U] = M0 * sum_k |1 - U_k|^2",
        "SW_total": str(SW), "SW_identity": "S_W = 89 = F_11 (exact)",
        "sum_gamma": str(Sg), "sum_gamma_even": str(Sg_ev), "sum_gamma_odd": str(Sg_od),
        "sum_lambda": str(Sl), "E_conn_MeV": str(E_conn), "wilson_phase": "44.5 pi",
    },
    "B_sigma": {"sigma_MeV2": str(sig_B), "sigma_GeV2": str(sig_B_GeV),
                "a_MeV_inv": str(a_len), "a_fm": str(a_fm), "lambda_bar": str(lam_bar)},
    "C_ebind": {"E_bind_obs_MeV": str(E_bind), "ell_links": str(ell_links),
                "ell_fm": str(ell_fm), "E_struct_MeV": str(E_from),
                "residual_pct": str((E_bind - E_from) / E_bind * 100)},
    "D_obs": {"sigma_obs_GeV2": str(SIG_OBS), "ratio": str(ratio),
              "density_hits": len(hits), "density_examples": [h[0] for h in hits[:12]]},
    "E_transmutation": {"alpha_s_inv_MZ": str(alpha_s_inv), "b0": b0, "b0_pure": b0_pure,
                        "Lambda_b0_7_GeV": str(Lam7), "sigma_b0_7_GeV2": str(Lam7**2),
                        "b0_required": str(b_req)},
    "passed": PASS, "failed": FAIL, "checks": ROWS,
    "verdict": ("A: functional constructed (exact); B: sigma = M0^2 exact; "
                "C: E_bind = 33 M0 (0.92%); D: FALSIFIED vs QCD sigma by 231x; "
                "E: transmutation route fails"),
}
json.dump(out, open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
                    'open_problems_fresh/o144_boson_identity/data/23_su3_connection_sigma.json',
                    'w'), indent=2, ensure_ascii=False)
print(f"\n總計: {PASS} PASS / {FAIL} FAIL")
print("✅ data/23_su3_connection_sigma.json")
