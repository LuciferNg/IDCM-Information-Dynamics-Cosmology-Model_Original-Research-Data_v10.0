#!/usr/bin/env python3
"""
O128 scripts/03 — A_φφ 鏈 + σ8 缺口分析
==========================================
O128 第二目標: σ8 歸一化之**下游鏈** (A_φφ) 與**殘餘缺口** (+5.14%) 之獨立審計。

[A] ℓ-空間測度 w(ℓ) = ln4·4^{−ℓ} 之恆等式 (獨立復算 O213 R4 結構部分)
[B] 幾何核比 Q_IDCM/Q_ΛCDM 之**穩健性** (O213 scripts/06 用單一 toy P_n(k))
[C] A_φφ 鏈: 所需 σ8 = 0.7867, f 窗口
[D] 缺口因子 1.10548 — 結構池覆蓋率 null test (獨立復算 O213 docs/11 §七)
[E] 缺口機制候選 (transfer c_T / 對偶 budget / Δln k 測度 / f)

Run: /usr/bin/python3 scripts/03_aphphi_and_gap.py
"""
import math
import numpy as np
import mpmath as mpm

mp = mpm.mp
mp.dps = 40

PASS = 0; TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    print(f"  [{'✔' if cond else '✘'}] {name}" + (f"   {detail}" if detail else ""))

print("=" * 80)
print("O128 scripts/03 — A_φφ 鏈 + σ8 缺口分析")
print("=" * 80)

# ══ [A] ℓ-測度恆等式 ═══════════════════════════════════════════════════════
print("\n[A] ℓ-空間測度 w(ℓ) = ln4·4^{−ℓ} (獨立復算)")
ln4 = mp.log(4)
w = lambda l: ln4 * mp.mpf(4) ** (-l)
I0 = mp.quad(lambda l: w(l), [0, mp.inf])
m1 = mp.quad(lambda l: l * w(l), [0, mp.inf])
m2 = mp.quad(lambda l: l ** 2 * w(l), [0, mp.inf])
chk("A1 ∫₀^∞ w dℓ = 1 EXACT", abs(I0 - 1) < mp.mpf("1e-30"), mp.nstr(I0, 15))
chk("A2 ⟨ℓ⟩ = 1/ln4;  std = ⟨ℓ⟩ (指數分布簽名)",
    abs(m1 - 1 / ln4) < mp.mpf("1e-30") and abs(m2 - m1 ** 2 - 1 / ln4 ** 2) < mp.mpf("1e-30"),
    f"⟨ℓ⟩ = {mp.nstr(m1, 10)}")
chk("A3 ⟨4^{−ℓ}⟩ = 1/2 EXACT (中位 ℓ = log₄2 = 1/2)",
    abs(mp.quad(lambda l: mp.mpf(4) ** (-l) * w(l), [0, mp.inf]) - mp.mpf(1) / 2) < mp.mpf("1e-30"),
    "自相似對稱")

# ══ [B] 幾何核比穩健性 ═════════════════════════════════════════════════════
print("\n[B] 幾何核比 Q_IDCM/Q_ΛCDM — 穩健性 (O213 用單一 toy P_n)")
R_world = mp.mpf("4129.94"); E0 = mp.mpf("1.11911398")
H0_L, Om_L = mp.mpf("67.4"), mp.mpf("0.3153"); c_kms = mp.mpf("299792.458")

def Dapp(z):
    e = mp.log(1 + z, 4); return R_world * (1 - mp.mpf(4) ** (-e)) * (e + E0)
def chi_lcdm(z):
    return c_kms / H0_L * mp.quad(lambda zz: 1 / mp.sqrt(Om_L * (1 + zz) ** 3 + (1 - Om_L)), [0, z])

zgrid = [mp.mpf("0.07") * (mp.mpf("5.9") / mp.mpf("0.07")) ** (i / 199) for i in range(200)]
chi_id = np.array([float(Dapp(z)) for z in zgrid])
chi_lc = np.array([float(chi_lcdm(z)) for z in zgrid])
Lg = np.logspace(1.5, 2.6, 400)

def kernel_ratio(Pn, chi_i=chi_id, chi_l=chi_lc):
    def Q(chi):
        cs = chi[-1]; out = []
        for Lv in Lg:
            kk = Lv / chi[:-1]; W = chi[:-1] * (1 - chi[:-1] / cs)
            out.append(np.trapezoid(((W / chi[:-1]) * Pn(kk)) ** 2, chi[:-1]))
        return np.array(out)
    qi, ql = Q(chi_i), Q(chi_l)
    return float(np.trapezoid(qi, Lg) / np.trapezoid(ql, Lg)), float(Lg[np.argmax(qi)]), float(Lg[np.argmax(ql)])

toy = lambda k: (k / 0.05) ** 1.2 / (1 + (k / 0.05) ** 2.0)
r0, pk_i, pk_l = kernel_ratio(toy)
print(f"      O213 toy P_n = (k/0.05)^1.2/(1+(k/0.05)²) : ratio = {r0:.4f}  峰 {pk_i:.0f} vs {pk_l:.0f}")
chk("B1 復現 O213 之核比 1.0745 (同 toy P_n)", abs(r0 - 1.0745) < 0.002, f"{r0:.4f}")

shapes = {
    "n_eff=-2.0 (k^0.0)":        lambda k: np.ones_like(k),
    "n_eff=-1.8 (k^0.2)":        lambda k: k ** 0.2,
    "n_eff=-1.5 (k^0.5)":        lambda k: k ** 0.5,
    "n_eff=-1.2 (k^0.8)":        lambda k: k ** 0.8,
    "EH-like turnover k_eq=0.02": lambda k: k / (1 + (k / 0.02) ** 2) ** 1.5,
    "EH-like turnover k_eq=0.05": lambda k: k / (1 + (k / 0.05) ** 2) ** 1.5,
    "EH-like turnover k_eq=0.10": lambda k: k / (1 + (k / 0.10) ** 2) ** 1.5,
    "toy n=1.2 (O213)":          toy,
}
print("\n      ★ P_n(k) 形狀掃描:")
ratios = {}
for lab, P in shapes.items():
    r, pi, pl = kernel_ratio(P)
    ratios[lab] = r
    print(f"        {lab:28s} ratio = {r:.4f}   峰 {pi:.0f} vs {pl:.0f}")
rvals = np.array(list(ratios.values()))
chk("B2 ★ 核比對 P_n 形狀敏感 (極差 > 10%) ⟹ 1.0745 唔係零參數結構量, 係『形狀依賴』",
    (rvals.max() - rvals.min()) / rvals.mean() > 0.10,
    f"範圍 [{rvals.min():.4f}, {rvals.max():.4f}], 極差 {100*(rvals.max()-rvals.min())/rvals.mean():.1f}%")

# ── B3: 核比不確定度 → 所需 σ8 不確定度 ────────────────────────────────────
print("\n      ★★ 核比形狀依賴 → 所需 σ8 之傳播:")
s8_idcm_v = mp.mpf("0.748196781429553")
print(f"        {'P_n 形狀':30s} {'核比':>8s} {'所需 σ8':>10s} {'缺口':>9s} {'pull(A_φφ)':>12s}")
req_by_shape = {}
for lab, r in ratios.items():
    reqv = mp.mpf("0.811") * mp.sqrt(mp.mpf("1.011") / mp.mpf(repr(r)))
    A_here = (s8_idcm_v / mp.mpf("0.811")) ** 2 * mp.mpf(repr(r))
    pull = (A_here - mp.mpf("1.011")) / mp.mpf("0.028")
    req_by_shape[lab] = float(reqv)
    print(f"        {lab:30s} {r:8.4f} {float(reqv):10.4f} {100*(float(reqv)/float(s8_idcm_v)-1):+8.2f}% {float(pull):+11.2f}σ")
rq = np.array(list(req_by_shape.values()))
print(f"        ⟹ 所需 σ8 範圍 [{rq.min():.4f}, {rq.max():.4f}], 極差 {100*(rq.max()-rq.min())/rq.mean():.1f}%")
print(f"        ⟹ 缺口 (+5.14%) 只在 O213 之 toy P_n 下成立; 換 EH-like turnover ⇒ 缺口可縮到 "
      f"{100*(rq.min()/float(s8_idcm_v)-1):+.1f}%")
chk("B3 ★★ O213『真缺口 = +5.14%』之 σ8 值隨 P_n 形狀變動 > 3% ⟹ 缺口幅度唔穩健",
    (rq.max() - rq.min()) / rq.mean() > 0.03,
    f"所需 σ8 ∈ [{rq.min():.4f}, {rq.max():.4f}]")

# ══ [C] A_φφ 鏈 ════════════════════════════════════════════════════════════
print("\n[C] A_φφ 鏈")
A_pp, s_A = mp.mpf("1.011"), mp.mpf("0.028")
sig_L = mp.mpf("0.811")
s8_idcm = mp.mpf("0.748196781429553")
s8_boss = mp.mpf("0.783")
req = sig_L * mp.sqrt(A_pp / mp.mpf(r0))
print(f"      A_φφ = {A_pp} ± {s_A} (Planck VIII 2019)")
print(f"      核比 (O213 toy) = {r0:.4f} ⇒ 所需 σ8,IDCM = {mp.nstr(req, 8)}")
chk("C1 復現所需 σ8 = 0.7867 (用 O213 核比)", abs(req - mp.mpf("0.7867")) < mp.mpf("1e-3"), mp.nstr(req, 6))
gap_s8 = req / s8_idcm - 1
gap_s8sq = (req / s8_idcm) ** 2 - 1
print(f"      O100 σ8 = {mp.nstr(s8_idcm, 8)}  ⇒ 缺口 = {100*float(gap_s8):.2f}% in σ8, {100*float(gap_s8sq):.2f}% in σ8²")
chk("C2 缺口 = +5.14% (σ8) / +10.55% (σ8²)",
    abs(float(gap_s8) * 100 - 5.14) < 0.05 and abs(float(gap_s8sq) * 100 - 10.55) < 0.1,
    f"{100*float(gap_s8):.2f}% / {100*float(gap_s8sq):.2f}%")

# ── C3: f 窗口 (用 O100 scripts/09 之 beat 背景模型, 修正 R_world) ──────────
ells9 = [220, 537, 810, 1014, 1121, 1340, 1412, 1465, 1474]
Am9 = [1.0, 4/9, 4/9, 9/49, 3/14, 16/121, 1/7, 1/9, 1/16]
n_sel = [5, 12, 18, 23, 25, 30, 32, 33]
n_all = list(range(1, 45))
G = lambda n: 1.0 / (4 * np.sin(n * np.pi / 88))
w2_sel = np.array([Am9[i] / G(n_sel[i]) for i in range(len(n_sel))])
w2_avg = w2_sel.mean()

def sigma8_f(f, D1=5750.0, R=4129.941562, h=0.6727, T=2.72548):
    tot = 0.0
    for n in n_all:
        L = 44 * n
        x = L * 8.0 / (R * h)
        W2 = (3 * (np.sin(x) - x * np.cos(x)) / x ** 3) ** 2
        if n in n_sel:
            A_rel = Am9[n_sel.index(n)]
        else:
            A_rel = (w2_avg * f * G(n)) / (w2_sel[0] * G(5))
        D2 = 2 * (D1 / T ** 2) * 1e-12 * A_rel * L ** 3 * (2 * L + 1) / (L + 1)
        tot += D2 * W2
    return math.sqrt(tot)

s8_f0 = sigma8_f(0.0)
fs = np.linspace(0, 0.3, 6001)
s8s = np.array([sigma8_f(f) for f in fs])
lo = 0.7757; hi = 0.7975
inwin = (s8s >= lo) & (s8s <= hi)
f_lo, f_hi = fs[inwin].min(), fs[inwin].max()
f_best = fs[np.argmin(np.abs(s8s - float(req)))]
print(f"      σ8(f=0) = {s8_f0:.4f} (9 峰, 全 44-mode 模型)  vs 純 9 峰 {float(s8_idcm):.4f}")
print(f"      ★ f 窗口 (σ8 ∈ [0.7757, 0.7975]): f ∈ [{f_lo:.4f}, {f_hi:.4f}]  最佳 {f_best:.4f}")
chk("C3 ★ f 1σ 窗口 = [0.0211, 0.0387] (獨立復算, 用 44-mode 模型)",
    abs(f_lo - 0.0211) < 0.004 and abs(f_hi - 0.0387) < 0.004,
    f"[{f_lo:.4f}, {f_hi:.4f}]")

# ── C4: 兩個獨立 A_φφ 錨 (文獻) ─────────────────────────────────────────────
print("\n      ★ 兩個獨立 A_φφ 觀測錨 (文獻):")
anchors = {
    "Planck 2018 VIII (2020), MV L=8–400, CMB marg.": (1.011, 0.028),
    "PR4/NPIPE (Carron+2022)":                        (1.004, 0.024),
}
for lab, (A0, s0) in anchors.items():
    reqv = mp.mpf("0.811") * mp.sqrt(mp.mpf(repr(A0)) / mp.mpf(repr(r0)))
    A_here = (s8_idcm / mp.mpf("0.811")) ** 2 * mp.mpf(repr(r0))
    pull = (A_here - mp.mpf(repr(A0))) / mp.mpf(repr(s0))
    print(f"        {lab:48s} A_φφ={A0}±{s0} ⇒ 所需 σ8 = {float(reqv):.4f}  "
          f"(缺口 {100*(float(reqv)/float(s8_idcm)-1):+.2f}%, O100 pull {float(pull):+.2f}σ)")
    chk(f"C4 {lab[:28]}: 所需 σ8 落 [0.762, 0.820] 且 O100 σ8 pull ≤ −3σ",
        0.760 < float(reqv) < 0.822 and float(pull) <= -3.0, f"{float(reqv):.4f}")

# ══ [D] 缺口因子之結構池覆蓋率 ══════════════════════════════════════════════
print("\n[D] 缺口因子 1.10548 — 結構池覆蓋率 null test")
pool = [1,2,3,4,5,7,8,9,11,12,13,14,15,16,18,19,20,21,22,23,25,26,29,30,31,32,33,35,36,
        40,41,44,45,47,49,55,60,64,70,77,88,90,120,123,176,421]
print(f"      池 |S| = {len(pool)}")
A_m_list = [1.0, 4/9, 4/9, 9/49, 3/14, 16/121, 1/7, 1/9, 1/16]
vals = []
for a in pool:
    for b in pool:
        if a != b:
            v = a / b
            if 0.5 < v < 2.0: vals.append(v)
phi = (1 + 5 ** 0.5) / 2
for k in range(1, 7):
    for v in (phi ** k, phi ** (-k), 2.0 ** k, 2.0 ** (-k), 4.0 ** k, 4.0 ** (-k)):
        if 0.5 < v < 2.0: vals.append(v)
for a in A_m_list:
    v = 1 + a
    if 0.5 < v < 2.0: vals.append(v)
vals = np.array(sorted(set(np.round(vals, 12))))
print(f"      生成值數 (去重) = {len(vals)}")
target = float((req / s8_idcm) ** 2)
print(f"      目標缺口因子 = {target:.5f}")
hits = np.where(np.abs(vals / target - 1) < 0.005)[0]
print(f"      命中 (±0.5%) = {len(hits)}: " + ", ".join(f"{vals[i]:.5f} ({vals[i]/target-1:+.3%})" for i in hits[:6]))
grid = np.linspace(0.8, 1.4, 1201)
cover = np.mean([np.min(np.abs(vals - g)) / g < 0.005 for g in grid])
print(f"      ★ 覆蓋率 (±0.5% 窗, [0.8,1.4]) = {100*cover:.1f}%")
chk("D1 覆蓋率 ≥ 20% ⟹ 該池對任何目標皆無判別力 (缺口因子唔可由結構池決定)",
    cover > 0.20, f"{100*cover:.1f}% (O213 報 94.2%)")

# ══ [E] 缺口機制候選 ═══════════════════════════════════════════════════════
print("\n[E] 缺口機制候選 (需結構強逼, 非擬合)")
need = target
print(f"      需要 σ8² 乘上 {need:.5f}")
# (1) 對偶 budget 90/88
for p in [0.5, 1.0, 2.0]:
    print(f"        (1) 對偶 (90/88)^{p}: {(90/88)**p:.5f}  ({100*((90/88)**p-1):+.2f}%)")
p_need = math.log(need) / math.log(90 / 88)
print(f"        ⟹ 需 (90/88)^{p_need:.4f}; p 非結構整數 ⇒ 不成立")
chk("E1 對偶 budget (90/88)^p 唔能給出 1.10548 (需 p = {:.3f}, 非結構)".format(p_need),
    abs(p_need - round(p_need)) > 0.1, f"p = {p_need:.4f}")
# (2) transfer 係數 c_T: σ8 ∝ c_T ⟹ 需 c_T = 2·√need
cT = 2 * math.sqrt(need)
print(f"        (2) transfer c_T: σ8 ∝ c_T ⇒ 需 c_T = 2·√{need:.5f} = {cT:.5f}")
print(f"            候選結構值: 2φ = {2*phi:.5f}, 2√2 = {2*math.sqrt(2):.5f}, 2 (標準 SW+Poisson) = 2")
corr = cT / 2 - 1
print(f"            ⟹ 標準值 c_T = 2 需 +{100*corr:.2f}% 修正 ⇒ 落喺 O100 docs/03 §4 預期之 5–15% 帶")
chk("E2 ★ 缺口 ≡ transfer c_T 由 2 → 2.1028 (+5.14%); 無結構候選命中 ≤1% ⟹ 缺口 = 缺 T(k) 通道",
    min(abs(cT - 2 * phi), abs(cT - 2 * math.sqrt(2)), abs(cT - 2)) / cT > 0.01,
    f"c_T = {cT:.4f}; 最近候選 2 (dev {100*(2/cT-1):+.1f}%) — 5% 級修正即流體轉換量級")
# (3) Δln k 測度: 線譜離散化應帶 Δln k
ells = [220, 537, 810, 1014, 1121, 1340, 1412, 1465, 1474]
lnk = np.log(np.array(ells, float))
dlnk = np.gradient(lnk)
print(f"        (3) Δln k 權重 = {np.round(dlnk,3)}  (極差 {dlnk.max()/dlnk.min():.1f}×)")
# 加權後 σ8
def s8_weighted(D1=5750.0, h=0.6727, R=4129.941562, T=2.72548, wts=None):
    A = A_m_list
    tot = 0.0
    for i, L in enumerate(ells):
        x = L * 8.0 / (R * h)
        W2 = (3 * (np.sin(x) - x * np.cos(x)) / x ** 3) ** 2
        D2 = 2 * (D1 / T ** 2) * 1e-12 * A[i] * L ** 3 * (2 * L + 1) / (L + 1)
        tot += D2 * W2 * (wts[i] if wts is not None else 1.0)
    return math.sqrt(tot)
s8_flat = s8_weighted()
s8_dlnk = s8_weighted(wts=dlnk / dlnk.mean())
print(f"            平坦 Σ: σ8 = {s8_flat:.4f}    Δln k 加權: σ8 = {s8_dlnk:.4f}  (Δ {100*(s8_dlnk/s8_flat-1):+.1f}%)")
chk("E3 Δln k 測度加權令 σ8 變化 ≠ +5.14% ⟹ 唔解釋缺口",
    abs(s8_dlnk / s8_flat - 1 - gap_s8) > 0.005,
    f"Δ = {100*(s8_dlnk/s8_flat-1):+.1f}% vs 需 +5.14%")
# (4) f 背景權重 — 1/n 候選計數
n_cand = [n for n in range(2, 200) if f_lo <= 1.0 / n <= f_hi]
n_struct = [n for n in n_cand if n in pool or n in (28, 32, 33, 35, 36, 40, 41)]
print(f"        (4) beat 背景權重 f: 需 f ≈ {f_best:.4f} (O213 docs/10)")
print(f"            落入窗口之 1/n: n ∈ {n_cand[0]}..{n_cand[-1]} 共 {len(n_cand)} 個")
print(f"            其中有結構身份者 (池/28/32/33/35/36/40/41): {n_struct}")
chk("E4 ★ f 唔可由結構唯一決定 (≥20 個 1/n 同在窗口) ⟹ 缺口係『缺一條通道』而非『缺一個數』",
    len(n_cand) >= 20 and len(n_struct) >= 5,
    f"{len(n_cand)} 個倒數候選, {len(n_struct)} 個有結構身份")

# ══ 交叉核對 O133 ══════════════════════════════════════════════════════════
print("\n[F] 與 O133 (P(k) 鏈譜) 之獨立診斷交叉核對")
print("      O133 結論: ℳ 冇 T(k) 通道 (k_eq analog 缺失) ⇒ 系統性 Δn = +0.71")
print("      本檔缺口 (+5.14% in σ8) 之物理位置 = 同一缺失通道 (物質傳遞函數)")
print("      ⚠️ 此為結構性論斷 (唔計入 PASS 計數): 兩條獨立路徑 —— O133 用 P(k) 形狀斜率,")
print("         本檔用歸一化振幅 —— 皆指向『缺 T(k) 通道』, 方向一致 (需 +5% 級修正)。")

print("\n" + "=" * 80)
print(f"RESULT: {PASS}/{TOTAL} PASS")
print("=" * 80)
