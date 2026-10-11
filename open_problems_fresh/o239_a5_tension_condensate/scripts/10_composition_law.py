#!/usr/bin/python3
"""O239 — Script 10: 合成律誤差衰減律（O140 「FSR 升層」回答之可證偽檢定）
============================================================================
O140 docs/02 §236-243: 「加速合成 η_a+η_b 唔在階梯上」🔴 開放;
  FSR 回答: 合成提升到更精細尺度層 ℓ 實現 (層 ℓ 階梯更密)
O140 fsr_to_sr.json note: 「ell→∞: Δv~4^{−2l}, proj_err→0, η連續→SL(2,R)」
O140 docs/14 (collective_boost): 「快度 ℝ 加法喺多粒子層面精確成立 (無中間投影時)」
  physical_space = rapidity ℝ (rung = measurement display)

本 script 檢定（判據預註冊）:
  L1 階梯密度: 層 ℓ 階梯（N_ℓ=44·4^ℓ 模態）嘅最小可辨間距隨 ℓ 係咪 ~4^{−ℓ}
     （幾何預期）定 ~4^{−2ℓ}（O140 fsr note 嘅 Δv 聲稱）?
  L2 ★合成誤差收斂: 對固定合成 η_a+η_b, min distance 到層 ℓ 階梯 d_ℓ
     隨 ℓ 嘅衰減: 若 d_ℓ ~ 4^{−ℓ} = 「升層實現」有效（誤差隨階梯密度收斂）;
     若 d_ℓ 唔衰減 = FSR 升層回答失敗（合成誤差鎖死）;
     若 d_ℓ ~ 4^{−2ℓ} = O140 fsr note 嘅 Δv 預言級收斂
  L3 覆蓋條件: η_a+η_b ≤ max η_ℓ（階梯最大 rapidity）先有正式答案——
     記錄需要嘅最小 ℓ*（合成超出階梯範圍時, FSR 回答要求更高層）
  L4 判決: 合成律「唔封閉」係咪可以 re-frame 做「display-layer 現象」
     （物理空間 = η ℝ, 階梯 = rung display, O140 docs/14）?
     依據: L2 收斂成立 ⟹ 離散階梯只係顯示網格, 合成喺 ℝ 精確（同 collective）;
            L2 唔成立 ⟹ 離散結構係物理, κ-Poincaré 型非封閉係真
"""
import mpmath as mp
mp.mp.dps = 30
import json, itertools, math

N = 44

def eta_ladder(ell):
    """層 ℓ 階梯: η_k = ln cot(kπ/(176·4^ℓ)), k=1..N_ℓ"""
    Nl = N * 4**ell
    return [mp.log(mp.cot(mp.mpf(k) * mp.pi / (176 * 4**ell))) for k in range(1, Nl + 1)]

# L0 階梯密度測量
print("=" * 78)
print("O239 scripts/10 — 合成律誤差衰減律（O140 FSR 升層回答檢定）")
print("=" * 78)
P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

# ── L1: 階梯間距隨 ℓ ──
print("\n── L1: 階梯最小/最大間距隨 ℓ ──")
spac = {}
for ell in range(0, 8):
    lad = sorted(eta_ladder(ell))
    mins = min(lad[i+1]-lad[i] for i in range(len(lad)-1))
    maxs = max(lad[i+1]-lad[i] for i in range(len(lad)-1))
    spac[ell] = (float(mins), float(maxs))
    if ell <= 4:
        print(f"   ℓ={ell}: N={N*4**ell:<5} 間距 min={float(mins):.3e} max={float(maxs):.3f}")
# 間距比: ℓ 每 +1, min spacing 係咪 ~×4 細（spac[2]/spac[1] = 0.25）
r = spac[2][0]/spac[1][0]
print(f"   min-spacing 比 (ℓ=2→1): {r:.4f}  (4^{{-1}} = 0.25 預期)")
chk("L1 階梯最小間距隨 ℓ 收窄 ~4^{−ℓ}", abs(r-0.25) < 0.02, f"r={r:.4f}")

# ── L2: 合成誤差收斂 ──
print("\n── L2: 固定合成 η_a+η_b 對層 ℓ 階梯嘅 min distance ──")
# 用 4 個代表合成: (1,1) 超高能, (1,22) 中, (3,7) 中低, (10,20) 低
samples = [(1, 1), (1, 22), (3, 7), (10, 20)]
eta0 = {n: mp.log(mp.cot(mp.mpf(n)*mp.pi/176)) for n in range(1, N)}
print(f"   {'合成':<10} " + "".join(f"d_ℓ={ell}          " for ell in range(0, 6)))
conv = {}
for a, b in samples:
    s = eta0[a] + eta0[b]
    ds = []
    for ell in range(0, 8):
        lad = sorted(eta_ladder(ell))
        dmin = min(abs(s - e) for e in lad)
        ds.append(float(dmin))
    conv[(a, b)] = ds
    print(f"   η_{a}+η_{b}   " + " ".join(f"{d:.2e}" for d in ds[:6]))
# 收斂率: 尾部(ℓ=4..7) 比 d_ℓ/d_{ℓ-1} 平均——分開「早期跳點」同「尾部真收斂」
print("\n   尾部收斂比（ℓ=4→7 平均, 跳點喺早期 ℓ<4 已掠過）:")
tail_ratios = []
for (a, b), ds in conv.items():
    trs = [ds[i+1]/ds[i] for i in range(4, 7) if ds[i] > 0]
    meanr = sum(trs)/len(trs) if trs else float('nan')
    tail_ratios.append((a, b, meanr))
    print(f"   η_{a}+η_{b}: 尾部比 {meanr:.4f}   (0.25=階梯密度收斂, 0.0625=O140 Δv 級)")
ok_tail = all(not math.isnan(r_) and r_ < 0.5 for _, _, r_ in tail_ratios)
chk("L2 合成誤差尾部收斂（全部樣本 ℓ=4..7 平均比 < 0.5）", ok_tail,
    "; ".join(f"η_{a}+η_{b}:{r_:.3f}" for a, b, r_ in tail_ratios))
# 平台檢測: 尾部收斂比 > 0.8 且有非零誤差 = 收斂停滯（平台）
plat = []
for a, b, r_ in tail_ratios:
    ds = conv[(a, b)]
    if ds[-1] > 1e-6 and r_ > 0.8:
        plat.append((a, b, ds[-1]))
print(f"   平台檢測: 尾部比>0.8 且 d_ℓ=7 > 1e-6 → {plat if plat else '冇'}")
chk("L2b 冇收斂停滯平台（尾部比<0.8 或誤差已到 1e-6 級）", len(plat) == 0,
    str(plat) if plat else "all converged")

# ── L3: 覆蓋條件 ──
print("\n── L3: 覆蓋條件（η_sum ≤ max η_ℓ）──")
sums = [eta0[a]+eta0[b] for a, b in samples]
maxsum = max(sums)
for ell in range(0, 8):
    lad = sorted(eta_ladder(ell))
    mx = lad[-1]  # 最大 rapidity = 最細角 (k=1)
    if ell <= 3 or mx >= maxsum:
        print(f"   ℓ={ell}: max η_ℓ = {float(mx):.4f}   (最大合成 {float(maxsum):.4f} "
              f"{'✓覆蓋' if mx >= maxsum else '✗未覆蓋'})")
ell_cover = next(e for e in range(8) if sorted(eta_ladder(e))[-1] >= maxsum)
print(f"   ⟹ 全部樣本合成被覆蓋所需最小 ℓ* = {ell_cover}")
chk("L3 覆蓋條件: ℓ=8 內全部覆蓋", ell_cover < 8, f"ℓ*={ell_cover}")

# ── L4: 判決 ──
print("\n── L4: 判決 ──")
if ok_tail:
    print("   合成誤差尾部收斂 ⟹ FSR「升層實現」回答有效（升層精度以 ~4^{−ℓ} 至更優收斂）:")
    print("   「η_a+η_b 唔在 ℓ=0 階梯上」係低層現象——升高層誤差縮細")
    print("   ⟹ 離散階梯係 rung display; 物理合成空間 = η ℝ（O140 docs/14）")
    print("   ⟹ 合成律「不封閉」= display-layer 現象, 唔係 κ-Poincaré 型物理非封閉")
else:
    print("   合成誤差尾部未收斂/有平台 ⟹ 離散殘餘鎖死:")
    print("   FSR 升層回答只喺部分樣本有效; κ-Poincaré 型非封閉成分存在（O140 開放項維持 🔴）")

json.dump({
    "L1_spacing": {str(k): v for k, v in spac.items()},
    "L2_conv": {f"{a},{b}": ds for (a, b), ds in conv.items()},
    "L3_ell_cover": ell_cover,
    "L4_verdict": "FSR 升層有效" if ok_tail else "FSR 升層局部有效/有平台",
    "note": "L1 spacing 用 sorted 升序: lad[-1] 係最大 η (k=1 最細角)",
}, open("data/10_composition_law.json", "w"), indent=1, ensure_ascii=False)
print("saved data/10_composition_law.json")

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")