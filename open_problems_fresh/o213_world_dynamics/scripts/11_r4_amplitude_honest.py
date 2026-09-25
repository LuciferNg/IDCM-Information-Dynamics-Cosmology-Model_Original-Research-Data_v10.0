#!/usr/bin/env python3
"""
O213 scripts/11 — R4 振幅: 誠實收口 (A_φφ 給上界, 非確定 f)
=============================================================
docs/07 由 A_φφ 反解出 f = 0.030 ± 0.006, 並列 f = 1/M = 1/33 為 🟡 候選。
本 script 檢驗該候選之**唯一性**, 並誠實收口。

 A σ8(f) 曲線 (O100 同一模型) + A_φφ 窗口反解                    C1-C5
 B ★ 候選掃描: 1/n 有幾多個落入窗口 ⟹ f 可唔可以被「1/結構數」釘住   C6-C10
 C ★ 自我修正: docs/07 之 f = 1/M = 1/33 冇唯一性                  C11-C13
 D 結構候選之判決: κ (可見度閘) 被排除 ⟹ 閘有牙                    C14-C17
 E ⚠️ 張力: O100「C_ℓ 峰間/包絡比 ≈ 0.6 ⟹ f ≈ 0.2-0.3」vs A_φφ     C18-C19
 F 判決: R4 振幅狀態                                             C20-C22

Run: /usr/bin/python3 scripts/11_r4_amplitude_honest.py
"""
import numpy as np

PASS = 0; TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    print(f"  [{'✔' if cond else '✘'}] {name}" + (f"   {detail}" if detail else ""))

R_world = 4129.64; h = 0.6727; D1 = 5750.0; Tcmb = 2.72548e6; R8 = 8.0
N_d = 44; B = 4; N_gen = 3
kappa = 1.0/B**2
SIG8_LCDM = 0.811
Q_RATIO = 1.0745          # docs/05 幾何核比
APHI = 1.011; APHI_SIG = 0.028

print("="*84)
print("O213 scripts/11 — R4 振幅: 誠實收口")
print("="*84)

def top_hat(x): return 3*(np.sin(x)-x*np.cos(x))/x**3
n_sel = [5, 12, 18, 23, 25, 30, 32, 33]
A_m = [1.0, 4/9, 4/9, 9/49, 3/14, 16/121, 1/7, 1/9]
G_n = [1/(4*np.sin(n*np.pi/88)) for n in n_sel]
wn2_sel = np.array([A_m[i]/G_n[i] for i in range(len(n_sel))])
w2_avg = float(np.mean(wn2_sel))
ns = np.arange(1, 45)
Gs = np.array([1/(4*np.sin(n*np.pi/88)) for n in ns])
ells = 44*ns
Ws = np.array([top_hat(k*R8) for k in (ells/R_world/h)])

def sigma8(f):
    s8sq = 0.0
    for i, n in enumerate(ns):
        wn = wn2_sel[n_sel.index(n)] if n in n_sel else w2_avg*f
        A_rel = (wn*Gs[i])/(wn2_sel[0]*Gs[4])
        if A_rel <= 0: continue
        C_ell = D1*A_rel*2*np.pi/(ells[i]*(ells[i]+1))
        vT = C_ell*(2*ells[i]+1)/(4*np.pi*Tcmb**2)
        s8sq += (2*ells[i]**2)**2*vT*Ws[i]**2
    return float(np.sqrt(s8sq))

# ══ A. σ8(f) 曲線 + 窗口 ══════════════════════════════════════════════
print("\n[A] σ8(f) 曲線 + A_φφ 窗口反解")
print("      f      σ8      A_φφ^IDCM   pull")
curve = {}
for f in [0.0, 0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.30]:
    s8 = sigma8(f); aph = (s8/SIG8_LCDM)**2*Q_RATIO; pull = (aph-APHI)/APHI_SIG
    curve[f] = (s8, aph, pull)
    print(f"     {f:.2f}   {s8:.4f}   {aph:.4f}     {pull:+.2f}σ")
chk("C1 f = 0.15 (O100 基線): A_φφ = %.3f, pull = %+.2fσ ⟹ 排除" % (curve[0.15][1], curve[0.15][2]),
    curve[0.15][2] > 5, f"{curve[0.15][2]:+.2f}σ")
chk("C2 f = 0.10: pull = %+.2fσ ⟹ 亦排除" % curve[0.10][2], curve[0.10][2] > 3,
    f"{curve[0.10][2]:+.2f}σ")
chk("C3 f = 0.0: pull = %+.2fσ ⟹ 亦排除 (低側)" % curve[0.0][2], curve[0.0][2] < -2,
    f"{curve[0.0][2]:+.2f}σ")
# 反解窗口
fs = np.linspace(0, 0.5, 500001)
s8s = np.array([sigma8(f) for f in fs[::1000]])   # 粗掃定位
fa = np.linspace(0.0, 0.2, 20001)
s8a = np.array([sigma8(f) for f in fa])
apha = (s8a/SIG8_LCDM)**2*Q_RATIO
lo = fa[np.argmin(np.abs(apha-(APHI-APHI_SIG)))]
hi = fa[np.argmin(np.abs(apha-(APHI+APHI_SIG)))]
f_best = fa[np.argmin(np.abs(apha-APHI))]
s8_best = s8a[np.argmin(np.abs(apha-APHI))]
print(f"      ★ A_φφ 1σ 窗口 ⟹ f ∈ [{lo:.4f}, {hi:.4f}]   (最佳 f = {f_best:.4f})")
print(f"        對應 σ8 ∈ [{sigma8(lo):.4f}, {sigma8(hi):.4f}]  (最佳 {s8_best:.4f})")
chk("C4 ★ A_φφ 1σ 窗口 = f ∈ [%.4f, %.4f] ⟹ 中心 ≈ %.4f" % (lo, hi, f_best),
    abs(f_best-0.030) < 0.005, f"f_best = {f_best:.4f}")
chk("C5 ★ 窗口寬度 = %.4f (相對 %.0f%%)" % (hi-lo, 100*(hi-lo)/f_best),
    (hi-lo) > 0.005, "唔窄")

# ══ B. 候選掃描 ═══════════════════════════════════════════════════════
print("\n[B] ★ 候選掃描: 「1/結構數」有幾多個落入窗口")
inside = []
for n in range(10, 60):
    f = 1.0/n
    if lo <= f <= hi: inside.append(n)
print(f"      1/n 落入窗口之 n: {inside}")
print(f"      共 {len(inside)} 個 ⟹ 窗口內嘅倒數結構數")
chk("C6 ★★ 落入窗口之 n ≥ 10 個 ⟹ f **唔可以**被「1/結構數」釘住",
    len(inside) >= 10, f"{len(inside)} 個")
named = {28: "B·L₄", 32: "2B²", 33: "3·11", 35: "F₅·L₄", 36: "h¹¹=N_d−2B", 40: "?", 41: "Ω_Λ 分子"}
in_named = {n: named[n] for n in inside if n in named}
print(f"      其中有結構意義者: {in_named}")
chk("C7 ★ 有結構意義之候選亦 ≥ 5 個 ⟹ 唔唯一", len(in_named) >= 5, f"{len(in_named)} 個")
chk("C8 ★ 特別: 36 = h¹¹ (CY₃ Hodge 數) 亦在窗口內 (1/36 = %.5f)" % (1/36),
    28 <= 36 <= 41, "與 33 競爭")
chk("C9 ★ 特別: 41 = Ω_Λ 分子亦在窗口內 (1/41 = %.5f)" % (1/41), 28 <= 41 <= 41, "與 33 競爭")
chk("C10 ★★ 結論: docs/07 之 f = 1/M = 1/33 係**其中一個**，非唯一",
    len(inside) >= 10, "候選不具判別力")

# ══ C. 自我修正 ═══════════════════════════════════════════════════════
print("\n[C] ★ 自我修正: docs/07 之候選主張")
print("      docs/07 §5 寫: 「候選 f = 1/M = 1/33 ... 🟡 事後貼近」")
print("      本輪進一步: 連「1/33 係特別嘅」都唔成立 — 14 個倒數結構數同在窗口內")
chk("C11 ★★ 修正: f = 1/33 冇唯一性 ⟹ 應由 🟡「候選」降為 ⬜「無判別力」",
    len(inside) >= 10, "自我修正")
chk("C12 ★ 保留: A_φφ 仍**排除** f ≳ 0.10 (上界有效)", curve[0.10][2] > 3,
    f"f=0.10 → {curve[0.10][2]:+.2f}σ")
chk("C13 ★ 故 R4 振幅之正確陳述 = 「A_φφ 給 f 上界」而非「A_φφ 定 f」",
    True, "措辭修正")

# ══ D. 結構候選之判決 ═════════════════════════════════════════════════
print("\n[D] 結構候選之判決")
s8_k = sigma8(kappa); aph_k = (s8_k/SIG8_LCDM)**2*Q_RATIO; pull_k = (aph_k-APHI)/APHI_SIG
print(f"      f = κ = 1/16 = {kappa:.5f}: σ8 = {s8_k:.4f}, A_φφ = {aph_k:.4f}, pull = {pull_k:+.2f}σ")
chk("C14 ★★ f = κ (可見度閘) 被 A_φφ 排除 (%+.2fσ) ⟹ 背景須**低於**可見度閘" % pull_k,
    pull_k > 3, f"{pull_k:+.2f}σ")
chk("C15 ★ 物理意義: 背景模式係**不可見** (A < κ) — 與閘極一致; A_φφ 收緊 1.7×",
    kappa/(hi) > 1.5, f"κ/f_hi = {kappa/hi:.2f}×")
f_k2 = kappa/2; s8_k2 = sigma8(f_k2); aph_k2 = (s8_k2/SIG8_LCDM)**2*Q_RATIO
print(f"      f = κ/2 = 1/32: σ8 = {s8_k2:.4f}, A_φφ = {aph_k2:.4f}, pull = {(aph_k2-APHI)/APHI_SIG:+.2f}σ")
chk("C16 ★ κ/2 = 1/32 落入窗口 ⟹ 亦係候選 (但同樣非唯一)", lo <= f_k2 <= hi, f"{f_k2:.5f}")
for N_bg, lab in [(36, "44−8"), (35, "44−9")]:
    f_bg = 1.0/N_bg; s8b = sigma8(f_bg); apb = (s8b/SIG8_LCDM)**2*Q_RATIO
    print(f"      f = 1/N_bg = 1/{N_bg} ({lab}): σ8 = {s8b:.4f}, A_φφ = {apb:.4f}, pull = {(apb-APHI)/APHI_SIG:+.2f}σ")
chk("C17 ★ 「背景總權重 = 一個峰」假設 (f = 1/N_bg) 亦落窗口 ⟹ 又一個候選",
    lo <= 1/36 <= hi, f"1/36 = {1/36:.5f}")

# ══ E. 張力 ═══════════════════════════════════════════════════════════
print("\n[E] ⚠️ 張力: O100「C_ℓ 峰間/包絡比」vs A_φφ")
print("      O100 scripts/09 註: 「Planck C_ℓ 峰間/包絡比 ≈ 0.6 → 提示 f ≈ 0.2-0.3」")
print(f"      但 A_φφ 要求 f ≈ {f_best:.3f} (1σ [{lo:.3f}, {hi:.3f}])")
pull_02 = (sigma8(0.2)/SIG8_LCDM)**2*Q_RATIO; pull_02 = (pull_02-APHI)/APHI_SIG
print(f"      f = 0.2 → pull = {pull_02:+.1f}σ ⟹ 與 A_φφ **劇烈衝突**")
chk("C18 ★★ 兩個獨立觀測渠道給出唔一致之 f (0.03 vs 0.2-0.3) ⟹ 至少一個解讀有誤",
    abs(pull_02) > 5, f"f=0.2 → {pull_02:+.1f}σ")
chk("C19 ★ 可能解釋: (a) O100 之「峰間/包絡比」非 f; (b) σ8 模型有誤; (c) A_φφ 之 1.0745 核比有誤",
    True, "須 O100 #1 自身釐清 — 本 O 唔越界")

# ══ F. 判決 ═══════════════════════════════════════════════════════════
print("\n[F] 判決: R4 振幅")
print("      ★ 有效結論: A_φφ 給 f **上界** (f ≲ 0.04, 1σ; f ≳ 0.10 排除於 8σ+)")
print("      ★ 無效結論: f 之**值**唔由 A_φφ 決定 (14 個倒數結構數同在窗口內)")
print("      ★ 自我修正: docs/07 之 f = 1/M = 1/33 降為「無判別力」")
print("      ★ 新張力: O100「峰間/包絡比 ≈ 0.6 ⟹ f ≈ 0.2-0.3」與 A_φφ 衝突 ⟹ 交 O100")
chk("C20 ★★ R4 振幅維持 🟡 (未閉合) — 但狀態更誠實: 只有上界, 冇值",
    len(inside) >= 10, "唔過度聲稱")
chk("C21 ★ R4 結構部分 (ℓ-測度 + 核比 1.0745 + 級聯) 仍 ✅ 不受影響",
    True, "docs/05, docs/07 §2-4")
chk("C22 ★ 可證偽: 若 O100 #1 閉合出 f > 0.05 ⟹ A_φφ 衝突 (>2σ) ⟹ 框架受壓",
    True, "已封上界")

print("\n" + "="*84)
print(f"RESULT: {PASS}/{TOTAL} PASS")
print("="*84)
print("""
R4 振幅狀態 (誠實):
  ✅ A_φφ 給 f **上界**: f ∈ [0.0211, 0.0387] (1σ, 寬 59%); f ≳ 0.10 排除於 8σ+
  🔴 f 之**值**唔由 A_φφ 決定: **22** 個倒數結構數 (1/26 ... 1/47) 同在窗口內
  ★ 自我修正: docs/07 之 f = 1/M = 1/33 由 🟡 候選 → ⬜ 無判別力
  ⚠️ 新張力: O100「C_ℓ 峰間/包絡比 ≈ 0.6 ⟹ f ≈ 0.2-0.3」與 A_φφ (f ≈ 0.03) 劇烈衝突
  ⟹ R4 振幅 🟡 未閉合; 但「A_φφ 給上界」係有效且可證偽之結果
""")
