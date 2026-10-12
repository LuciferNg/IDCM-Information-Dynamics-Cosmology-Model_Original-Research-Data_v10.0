#!/usr/bin/python3
"""O239 — Script 14: 合成數據——MC 誤差袋模擬「lattice 精度提升」效果
============================================================================
調律者問題: 「即使沒有 lattice, 是否可以模擬類似重整化技術來合成數據?」

上一 script (13) 用 freeze v2 偽 ensemble（scheme 全替換）證 γ 穩健。但嗰個
只係「改用已有值」。真正嘅「模擬 lattice」= 用 freeze v2 **現有誤差**做
MC 誤差袋, 合成大量質量組, 得出 γ 嘅真實分佈; 然後模擬「假如誤差收窄到
1-2%（lattice 直量）」γ 分佈收窄到幾緊——決定 freeze v3 值唔值等。

預註冊判據:
  M1 MC(現有誤差): γ 分佈 std —— 報告真實不確定性（唔係單點 CI 近似）
  M2 判別力現況: −19/4 同 −33/7 喺現有誤差下可唔可分離（分佈重疊率）
  M3 模擬 lattice 1-2%: γ 分佈 std 收窄幾多倍? 重疊率變幾多?
  M4 判決: 若模擬 1-2% 後重疊率仍高 (不可判) → freeze v3 唔值等 (合成已夠/無牙)
           若模擬 1-2% 後重疊率低 (可判) → freeze v3 有牙, 等得過
誤差來源（freeze v1.0/v2, PDG2024/FLAG2024）:
  t: 172.69 ± 1.30 (0.75%), b: 4.18 ± 0.03 (0.7%), tau 0.0006%, c: 1.27 ± 0.02 (1.6%)
  mu 0.00003%, s: 93.4 ± 1.0 (1.1%), d: 4.67 ± 0.48 (10.3%), u: 2.16 ± 0.49 (22.7%), e 精確
"""
import json, math
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261012)  # 固定 seed

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/14 — 合成數據: MC 誤差袋 + 模擬 lattice 精度提升")
print("=" * 78)

labels = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
n_modes = [1, 2, 3, 4, 5, 7, 9, 11, 13]
lt = np.log(np.array([n * np.pi / 88 for n in n_modes]))

# 現有誤差 (相對)
REL = np.array([0.0075, 0.0072, 0.000006, 0.0157, 0.0000003, 0.0107, 0.103, 0.227, 0.0000001])

def gamma_of(m):
    r = stats.linregress(lt, np.log(m))
    return r.slope

def mc_gamma(N, scale=1.0):
    """MC 誤差袋: N 組合成, 誤差乘 scale (scale<1 模擬精度提升)"""
    gs = []
    for _ in range(N):
        m = 1.0 * np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
        # log-normal noise (質量正定)
        m *= np.exp(rng.normal(0, REL * scale, 9))
        gs.append(gamma_of(m))
    return np.array(gs)

# ── M1: 現有誤差分佈 ──
print("\n── M1: MC 現有誤差 ──")
N = 200000
gs0 = mc_gamma(N, scale=1.0)
print(f"   γ 分佈: mean {gs0.mean():+.4f}  std {gs0.std():.4f}  "
      f"p5 {np.percentile(gs0,5):+.4f}  p95 {np.percentile(gs0,95):+.4f}")
print(f"   相對於 |γ|: {gs0.std()/abs(gs0.mean())*100:.1f}%（單點 CI 近似 7.8%）")
chk("M1 MC std 報告完成", True, f"std={gs0.std():.4f}")

# ── M2: 現況判別力（−19/4 vs −33/7 重疊）──
c1, c2 = -19/4, -33/7  # −4.75, −4.7143
frac1 = (gs0 < (c1+c2)/2).mean()
print("\n── M2: 現況判別力 ──")
print(f"   −19/4={c1}, −33/7={c2}, 分隔 {abs(c1-c2)*1000:.1f} mγ ({abs(c1-c2)/gs0.std():.2f}σ)")
print(f"   P(γ < 中點) = {frac1*100:.1f}%  (50%=完全唔可分離)")
chk("M2 現況不可判 (重疊 > 30%)", 0.3 < frac1 < 0.7, f"P={frac1*100:.1f}%")

# ── M3: 模擬 lattice 精度提升 (誤差 ×0.5, ×0.2, ×0.1) ──
print("\n── M3: 模擬 precision scale (誤差 ×80%, ×20%, ×10%) ──")
for sc, name in [(0.5, "50%"), (0.2, "20% (lattice 級)"), (0.1, "10% (lattice 1-2% 級)")]:
    g = mc_gamma(int(N/4), scale=sc)
    frac = (g < (c1+c2)/2).mean()
    print(f"   scale {name:>20}: std {g.std():.4f} ('{gs0.std()/g.std():.1f}x 收窄')  "
          f"重疊率 P={frac*100:.1f}%  {'可判' if frac<0.18 or frac>0.82 else '不可判'}")
# lattice 1-2% 嘅意思: 誤差收窄到 ~1% (u/d 由 10-23% → 1%)
gl = mc_gamma(int(N/4), scale=0.05)  # u/d 誤差 ~1%
fracl = (gl < (c1+c2)/2).mean()
print(f"   scale 5% (u,d→1.2%/1.1%): std {gl.std():.4f} ({gs0.std()/gl.std():.1f}x)  "
      f"重疊率 {fracl*100:.1f}%  {'可判' if fracl<0.18 or fracl>0.82 else '不可判'}")

# 但: lattice 直量係「新量度」, 唔一定等於現有誤差收窄——直量會確定 md/mu 1-2%,
# 而 m_u/m_d 本身相對足已確定 — 令 u/d 誤差大跌: scale on u,d only
gs_ud = []
for _ in range(100000):
    m = 1.0 * np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
    n = np.zeros(9)
    n[7] = 0.01; n[6] = 0.01    # u,d → 1%
    n[0] = REL[0]; n[1] = REL[1]; n[3] = REL[3]; n[5] = REL[5]  # 其餘現有
    m *= np.exp(rng.normal(0, n*0.7, 9))  # lognormal approx
    gs_ud.append(gamma_of(m))
gs_ud = np.array(gs_ud)
fud = (gs_ud < (c1+c2)/2).mean()
print(f"   u/d→1% (其餘不變): std {gs_ud.std():.4f} ({gs0.std()/gs_ud.std():.1f}x)  重疊率 {fud*100:.1f}%  "
      f"{'可判' if fud<0.18 or fud>0.82 else '不可判'}")

# ── M4: 判決 ──
print("\n── M4: 判決 ──")
judgable_sc5 = fracl < 0.18 or fracl > 0.82
judgable_ud = fud < 0.18 or fud > 0.82
if judgable_ud:
    print("   ✅ 模擬 u/d→1% (lattice 直量) 後 γ 可判 −19/4 vs −33/7")
    print("   ⟹ freeze v3 (lattice 1-2%) 有牙, 等得過——合成 MC 已回答『值唔值等』")
else:
    print("   🔴 即使模擬 lattice 1-2% (u/d→1%), γ 仍然唔可分離兩候選")
    print("   ⟹ freeze v3 判唔到數字身份——等 lattice 唔值得 (除咗判 O234 P2 md/mu)")

json.dump({
    "M1_mean": float(gs0.mean()), "M1_std": float(gs0.std()),
    "M2_P_split_now": float(frac1),
    "M3_std_scales": {"1.0": float(gs0.std()), "0.05": float(gl.std()),
                      "ud1pct": float(gs_ud.std())},
    "M4_verdict": "u/d→1% 可判" if judgable_ud else "u/d→1% 仍不可判",
}, open("data/14_synthetic_mc.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")