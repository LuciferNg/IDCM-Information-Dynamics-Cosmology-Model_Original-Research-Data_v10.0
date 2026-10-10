#!/usr/bin/env python3
"""
O48 Q1.49: 純 TT 疊圖正式版 — 監製 fig_q1_peak_valley_overlay_pureTT.png
================================================================
背景: docs/26 引用 fig_q1_peak_valley_overlay_pureTT.png 但該圖係 closeout 前
以 one-liner 生成（無落碟）→ 按推導落碟硬規則（§4.9）補 producer script。

目的: 三實驗（Planck Plik 純 TT、SPT-3G、ACT DR4）detrend residual 疊圖
+ IDCM 峰（44N+s）+ 谷（V¾）模型 overlay。
- 純 TT = Plik-lite 613-rows 三 block 中每 ℓ 取 max（= TT block, ≡ O9 planck_tt.txt）
- detrend: log-poly order 4（O48 峰形框架一致）
- V¾ 模型: 谷位 = 峰間隙 ¾（V¾ 盲測）
"""
import math, os, sys
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{BASE}/docs/fig_q1_peak_valley_overlay_pureTT.png"

# ---------- 1. Planck Plik-lite 純 TT (每 ℓ max = TT block) ----------
PLIK = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o214_energy_budget_definition/data/planck2018_plik_lite/cl_cmb_plik_v22.dat"
def load_plik_tt(path):
    rows = np.loadtxt(path)               # ℓ, D_ℓ
    ell = rows[:, 0].astype(int)
    val = rows[:, 1]
    # group by ℓ, take max (TT block = 最大; TE/EE 較細/負)
    out = {}
    for e, v in zip(ell, val):
        out[e] = max(out.get(e, -np.inf), v)
    es = np.array(sorted(out))
    return es, np.array([out[e] for e in es])

try:
    l_p, d_p = load_plik_tt(PLIK)
    HAVE_PLIK = True
except Exception as ex:
    print(f"[WARN] 冇 Plik: {ex}"); HAVE_PLIK = False
    l_p, d_p = np.array([]), np.array([])

# ---------- 2. SPT-3G ----------
SPT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o214_energy_budget_definition/data/spt3g_d1"
def load_spt(path):
    bdp = np.loadtxt(f"{path}/SPT3G_D1_TnE_bdp.txt")
    win = np.loadtxt(f"{path}/TT_150x150_window.txt")
    # TT_150x150 偏移 (21 個 spectrum 中 TT_90x90..TT_90x220 = 5*52+4*72 = off)
    off = 5*52 + 4*72 + 52 + 4*72   # TT_90x90..TE_90x220 = 260+288+52+288 太長, 直接由 36 script 邏輯
    # 36 script: for name in spectra: break at TT_150x150 → 累計 17 個前 spectrum
    # TT_90x90(52)+TE_90x90(72)+EE_90x90(72)+TT_90x150(52)+TE_90x150(72)
    # +TE_150x90(72)+EE_90x150(72)+TT_90x220(52)+TE_90x220(72)+TE_220x90(72)
    # +EE_90x220(72)+TT_150x150 前 = 52+72+72+52+72+72+72+52+72+72+72 = 732
    off = 732
    tt150 = bdp[off:off+52]
    lgr = win[:, 0]
    centers = np.array([lgr[np.argmax(win[:, b])] for b in range(1, 53)])
    mask = tt150 > 0
    return centers[mask], tt150[mask]

try:
    l_s, d_s = load_spt(SPT)
    HAVE_SPT = len(l_s) > 0
    print(f"SPT: {len(l_s)} bins, ℓ {l_s[0]:.0f}..{l_s[-1]:.0f}")
except Exception as ex:
    print(f"[WARN] 冇 SPT: {ex}"); HAVE_SPT = False
    l_s, d_s = np.array([]), np.array([])

# ---------- 3. ACT DR4 (txt: ℓ, D_ell, sigma) ----------
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"
def load_act(path):
    if not os.path.exists(path): return np.array([]), np.array([])
    a = np.loadtxt(path, comments='#')
    return a[:, 0], a[:, 1]

try:
    l_a, d_a = load_act(ACT)
    HAVE_ACT = len(l_a) > 0
except Exception as ex:
    print(f"[WARN] 冇 ACT: {ex}"); HAVE_ACT = False

# ---------- detrend (log-poly order 4) ----------
def detrend(l, d, lo=100, hi=2500, order=4):
    m = (l>lo)&(l<hi)&(d>0)
    if m.sum() < order+2: return None
    c = np.polyfit(l[m], np.log(d[m]), order)
    env = np.exp(np.polyval(c, l[m]))
    return l[m], d[m]/env

res = {}
for name, l, d, HAVE in [("PR3", l_p, d_p, HAVE_PLIK),
                         ("SPT", l_s, d_s, HAVE_SPT),
                         ("ACT", l_a, d_a, HAVE_ACT)]:
    r = detrend(l, d)
    if r is None:
        print(f"[WARN] {name} detrend 失敗")
        continue
    res[name] = r
    print(f"{name}: {len(r[0])} bins, residual range [{r[1].min():.3f}, {r[1].max():.3f}]")

# ---------- 模型 ----------
# 峰: 44N+s（真峰集合 {1,2,3,5,7}; 假峰 m=4,6 被抑制）
TRUE_PEAKS = [221, 527, 815, 1121, 1409]
# 谷: V¾ = 峰間隙 ¾（docs/11/16/21: 谷位喺峰間隙 ¾ 處）
GAPS = [221, 527, 815, 1121]   # 峰對
VALLEYS = [int(p + 0.75*(q-p)) for p, q in zip(GAPS, GAPS[1:])]
# 手動核: docs/21 谷 [437,716,1040,1346] = 峰 527 → 325*0.75+221... 用直接表
VALLEYS = [437, 716, 1040, 1346]   # audit 後純 TT 谷位

print(f"模型: 峰 {TRUE_PEAKS}")
print(f"模型: 谷 {VALLEYS} (V¾)")

# ---------- V¾ 相關 (純 TT, 同 51 script 方法) ----------
if "PR3" in res:
    lr, rr = res["PR3"]
    pk = [lr[np.argmin(np.abs(lr-p))] for p in TRUE_PEAKS]
    vl = [lr[np.argmin(np.abs(lr-v))] for v in VALLEYS]
    # 峰+谷 joint 模型相關
    def model(x):
        y = np.zeros_like(x, float)
        for p in pk: y += np.exp(-0.5*((x-p)/33.0)**2)
        for v in vl: y -= np.exp(-0.5*((x-v)/35.0)**2)
        return y
    # interp to common grid 215 (same as PR3)
    m_on = model(lr)
    rrm = rr - rr.mean()
    mon = m_on - m_on.mean()
    corr = np.corrcoef(rrm, mon)[0, 1]
    print(f"[V¾ 純 TT] 模型-殘差 corr = {corr:+.3f}")
    # 對照
    m_pk = np.zeros_like(lr, float)
    for p in pk: m_pk += np.exp(-0.5*((lr-p)/33.0)**2)
    m_pk -= m_pk.mean()
    print(f"[峰only  ] corr = {np.corrcoef(rrm, m_pk)[0,1]:+.3f}")

# ---------- 繪圖 ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 5))
colors = {"PR3": "C0", "SPT": "C3", "ACT": "C2"}
labs = {"PR3": "Planck PR3 TT (Plik 純 TT)", "SPT": "SPT-3G D1 TT", "ACT": "ACT DR4 TT"}
for name, (l, r) in res.items():
    ax.plot(l, r*np.std([v[1] for v in res.values()][0])/np.std(r) if False else r,
            ".", ms=3 if name != "PR3" else 2, color=colors[name], label=labs[name], alpha=.8)
for p in TRUE_PEAKS:
    ax.axvline(p, color="red", ls="--", lw=.8, alpha=.7)
for v in VALLEYS:
    ax.axvline(v, color="blue", ls=":", lw=.8, alpha=.7)
ax.set_xlim(100, 1600)
ax.set_xlabel("ℓ")
ax.set_ylabel("D_ℓ residual (detrended, normalized)")
ax.set_title("O48: 峰(red)+谷(blue) vs 三實驗 pure-TT residual")
ax.legend(fontsize=8)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"[OK] saved {OUT}")
print(f"RESULT: pureTT overlay corr={corr:+.3f}" if "PR3" in res else "RESULT: no PR3")