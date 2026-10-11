#!/usr/bin/python3
"""O239 — Script 11: 全譜 θ-冪律（88 點 β 收窄）+ 903 合成全掃描
============================================================================
「繼續推」兩條線:
  A) β 收窄: 用 scripts/05 嘅 88 全模態 |dm|（唔係 9 點）
     檢定 ln|dm| vs ln θ 全譜冪律——R² 同 slope CI（88 點 stderr ≪ 9 點）
     ⟹ β = −19/(4φ²) = −1.8143 嘅 CI 判定（9 點時 CI 太闊不可判）
  B) 903 合成全掃描: 全部組合 η_a+η_b 對層 ℓ 階梯嘅誤差收斂率分佈——
     population 收斂比（唔係樣本）; 「cot 積對層階梯嘅 Diophantine 表徵」

材料:
  data/05_spectral_signature.json: dm_all (88), gamma_all (88) — scripts/05 產出
  O206 o206_lib: 需要確認 dm_all 係咪同 O206 嘅 9 值一致（sanity, 見 H5)

預註冊判據:
  A1 88 點 ln|dm| vs ln θ 冪律 R²>0.98（全譜, 唔只 9 模態）
  A2 slope β_88 CI95: −19/(4φ²) = −1.81434 落唔落喺 CI（9 點時兩者都喺, 88 點應判）
  A3 全譜 β_88 同 9 點 β_9 一致（< 5%）
  B1 903 對合成誤差尾部收斂比 population 中位 < 0.5（FSR 升層全域有效）
  B2 收斂比分佈有冇結構: 唔可以全數都好近 0.25（=狄利克雷型臨界?）——
     只報告分佈（中位/四分位/極端值）
"""
import json, math
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/11 — 全譜 θ-冪律 β 收窄 + 903 合成全掃描")
print("=" * 78)

D = json.load(open("data/05_spectral_signature.json"))
dm88 = np.abs(np.array(D["dm_all"]))      # |dm| 88 值
th88 = np.array([n*np.pi/88 for n in range(1, 89)])
lt, ld = np.log(th88), np.log(dm88)

# sanity: 同 O206 9 值一致（n=1..13 模態）
try:
    O = json.load(open("data/09_o206_inputs.json"))
    dm9_from_206 = np.array(O["dm9"])
    idx_9 = [n-1 for n, _ in O["PAIR"]]   # A5_MODES=[1,2,3,4,5,7,9,11,13] → 0-based
    devs = np.abs(dm88[idx_9] - dm9_from_206)/dm9_from_206
    print(f"\n   sanity: 88 全譜 |dm| 同 O206 9 值 max dev = {devs.max():.2e}")
    chk("S0 88 全譜 |dm| 同 O206 一致", devs.max() < 1e-8, f"max dev {devs.max():.1e}")
except Exception as e:
    print(f"   sanity 讀取失敗: {e}")

# ── A1: 全譜冪律 ──
print("\n── A1: 88 點 ln|dm| vs ln θ 全譜冪律 ──")
r_a = stats.linregress(lt, ld)
print(f"   88 點: R² = {r_a.rvalue**2:.6f}  slope = {r_a.slope:.6f} ± {r_a.stderr:.6f}")
print(f"   9 點:  R² = 0.993307  slope = −1.8146 ± 0.0563")
chk("A1 全譜冪律 R² > 0.98", r_a.rvalue**2 > 0.98, f"R²={r_a.rvalue**2:.4f}")

# ── A2: β CI 判定 ──
print("\n── A2: β_88 CI95 對 −19/(4φ²) 判定 ──")
tcrit88 = 2.0   # t(86, 0.975) ≈ 1.99
beta_pred = -(19/4)/((1+5**0.5)/2)**2
print(f"   β_88 = {r_a.slope:.6f} ± {r_a.stderr:.6f}")
print(f"   CI95 = [{r_a.slope-tcrit88*r_a.stderr:.6f}, {r_a.slope+tcrit88*r_a.stderr:.6f}]")
print(f"   −19/(4φ²) = {beta_pred:.6f}  在 CI? {r_a.slope-tcrit88*r_a.stderr <= beta_pred <= r_a.slope+tcrit88*r_a.stderr}")
# 訊噪比: 88 點 stderr 比 9 點細幾多
print(f"   stderr 比: 9 點/88 點 = {0.0563/r_a.stderr:.1f}× (√(88/9)≈3.1 理論)")
chk("A2a β_88 CI 半寬 < 3%（夠窄判身份）", tcrit88*r_a.stderr/abs(r_a.slope) < 0.03,
    f"半寬 {tcrit88*r_a.stderr/abs(r_a.slope)*100:.2f}%")
chk("A2b 若 −19/(4φ²) 唔喺 CI → 結構預言否證; 若喺 → 仍唔可宣稱（池 null）",
    r_a.slope-tcrit88*r_a.stderr <= beta_pred <= r_a.slope+tcrit88*r_a.stderr,
    f"β_pred={beta_pred:.6f}")

# ── A3: β_88 vs β_9 ──
# 9 模態重算 β（同 scripts/09 一致）
O9 = json.load(open("data/09_o206_inputs.json"))
th9 = np.array([n*np.pi/88 for n,_ in O9["PAIR"]])
dm9 = np.abs(np.array(O9["dm9"]))
r9 = stats.linregress(np.log(th9), np.log(dm9))
dev_beta = abs(r_a.slope - r9.slope)/abs(r9.slope)
print(f"\n── A3: β_88 vs β_9 ──")
print(f"   β_9 = {r9.slope:.6f}, β_88 = {r_a.slope:.6f}, dev = {dev_beta*100:.2f}%")
chk("A3 全譜/子集 β 一致 (<5%)", dev_beta < 0.05, f"dev={dev_beta:.3%}")

# ═══════════════════════════════════════════════════════════════
# ── B: 903 合成全掃描 ──
print("\n" + "=" * 78)
print("B: 903 對合成全掃描 — 收斂率 population 分佈")
print("=" * 78)
import itertools
import numpy as np

N = 44

def ladder_at_np(ell):
    """層 ℓ 階梯 (float64 numpy, **遞增序**): η_k = ln cot(kπ/(176·4^ell))
    ln cot x = −ln tan x: x 大 → η 細。用 k 由大到細 → η 由細到大 (遞增)。"""
    Nl = N * 4**ell
    k = np.arange(Nl, 0, -1, dtype=np.float64)   # 由大到細
    x = k * np.pi / (176.0 * 4**ell)
    return -np.log(np.tan(x))                    # −ln tan = ln cot, 遞增

# 預計算 ℓ=4..7 階梯（903 對要快）—— 用 searchsorted 最近鄰
lads = {ell: ladder_at_np(ell) for ell in range(4, 8)}
tail_ratios_all = []
d7_all = []
worst_pairs = []
eta0_np = np.log(1.0/np.tan(np.arange(1, N, dtype=np.float64) * np.pi / 176.0))
for a, b in itertools.combinations(range(1, N), 2):
    s = eta0_np[a-1] + eta0_np[b-1]
    ds = []
    for ell in range(4, 8):
        lad = lads[ell]
        j = np.searchsorted(lad, s)
        dmin = np.inf
        if j > 0:
            dmin = min(dmin, abs(s - lad[j-1]))
        if j < len(lad):
            dmin = min(dmin, abs(s - lad[j]))
        ds.append(float(dmin))
    trs = [ds[i+1]/ds[i] for i in range(3) if ds[i] > 0]
    meanr = sum(trs)/len(trs) if trs else float('nan')
    tail_ratios_all.append(meanr)
    d7_all.append(ds[-1])
    if ds[-1] > 1e-3:
        worst_pairs.append((a, b, ds[-1], meanr))

arr = np.array([r for r in tail_ratios_all if not math.isnan(r)])
d7 = np.array(d7_all)
print(f"   903 對尾部收斂比: 中位 {np.median(arr):.4f}  "
      f"Q1 {np.percentile(arr,25):.4f}  Q3 {np.percentile(arr,75):.4f}")
print(f"   尾部比<0.5 比例: {(arr<0.5).mean()*100:.1f}%")
print(f"   d_ℓ=7 殘餘: 中位 {np.median(d7):.2e}  max {d7.max():.2e}")
print(f"   最差殘餘 (a,b,d7,比): {worst_pairs[:3]}")
print(f"   收斂比 min {arr.min():.4f}  max {arr.max():.4f}")
chk("B1 903 對尾部收斂比中位 < 0.5（FSR 升層全域有效）", np.median(arr) < 0.5,
    f"中位 {np.median(arr):.4f}")
chk("B2 殘餘 d_ℓ=7 中位 < 1e-6（升 7 層後誤差可忽略）", np.median(d7) < 1e-6,
    f"d7 中位 {np.median(d7):.1e}")

json.dump({
    "A1_R2_88": r_a.rvalue**2, "A1_slope_88": r_a.slope, "A1_se_88": r_a.stderr,
    "A3_beta9": r9.slope, "A3_dev": dev_beta,
    "B_tail_median": float(np.median(arr)),
    "B_tail_q1": float(np.percentile(arr, 25)),
    "B_tail_q3": float(np.percentile(arr, 75)),
    "B_d7_median": float(np.median(d7)), "B_d7_max": float(d7.max()),
    "B_worst": worst_pairs[:5],
    "verdict": "全譜 β 收窄 + 903 全掃描完成",
}, open("data/11_full_spectrum_composition.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")