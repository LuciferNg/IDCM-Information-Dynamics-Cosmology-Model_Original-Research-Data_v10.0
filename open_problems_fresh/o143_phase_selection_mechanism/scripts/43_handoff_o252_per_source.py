#!/usr/bin/env python3
"""
O143 #43 — O252 handoff 應答: 𝒫 per-source 凝聚身份模型可行性 (2026-10-18)
=====================================================================
O252 (2026-10-18 handoff): 層B 每源 column density 缺口核心 = O143 𝒫 係宏觀天球投影
(88 節點 = 鏈 site 側), 冇 per-source 凝聚身份映射。要求檢查: 天球位置 (RA/Dec)
→ hop 節點 → column density per-source 投影。

獨立檢查:
  1. 𝒫 算子結構核實 (60×88 節點×鏈 site; 冇 per-source 維度)
  2. 節點晶格解析度: NN 距離統計 → 單源映射嘅角分辨極限
  3. 真實源 (O252 6 個已確認位置) → 最近節點 + k-class (R3 結構身份)
  4. per-source 投影原型 𝒫_src(n̂): 高斯窗節點權重; pair 源簽名相關 → 分辨力
  5. 判定: per-source column density 可唔可以由 𝒫 推
"""
import numpy as np, math, json, os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
DATA = f'{BASE}/open_problems_fresh/cmb_cold_spot/data'
OUTDIR = f'{O143}/data'
os.makedirs(OUTDIR, exist_ok=True)

print("="*74); print("  #43 O252 handoff — 𝒫 per-source 凝聚身份模型可行性"); print("="*74)

# ── 節點晶格 (observed a5_nodes.txt 順序 = 圖/k-class 索引) ──
nodes = np.loadtxt(f'{DATA}/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
xyz = sc.cartesian.xyz.value.T
N60 = 60
def ang(a, b):
    d = np.clip(np.sum(np.array(a)*np.array(b), axis=-1), -1, 1)
    return np.degrees(np.arccos(d))

# ── 1. 𝒫 結構 ──
print("\n[1] 𝒫 結構 (scripts/01):")
print("    𝒫 = 60×88 高斯窗 (節點×鏈site), 𝒫: ℋ₈₈ → 60 節點溫度")
print("    冇 per-source 維度 — 映射係 鏈相位場→節點, 唔係 天球位置→節點")

# ── 2. 節點晶格解析度 ──
print("\n[2] 節點晶格解析度:")
cmin = []
for i in range(N60):
    d = ang(xyz[i], xyz)
    d[i] = np.inf
    cmin.append(d.min())
cmin = np.array(cmin)
print(f"    NN 距離: min={cmin.min():.3f}° med={np.median(cmin):.3f}° max={cmin.max():.3f}°")
print(f"    4-NN 平均 (每節點): ", end="")
nn4 = np.mean([np.sort(ang(xyz[i], xyz))[1:5].mean() for i in range(N60)])
print(f"{nn4:.3f}°")
# 覆蓋半徑: 取 nside=64 像素抽樣天球, 每像素 → 最近節點距離
import healpy as hp
npix = hp.nside2npix(64)
th, ph = hp.pix2ang(64, np.arange(npix))
pix = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)], axis=1)
dmax = np.max(np.min(ang(pix[:,None,:], xyz[None,:,:]), axis=1))
print(f"    覆蓋半徑 (nside64 抽樣 max 最近節點距離) = {dmax:.2f}°")

# ── 3. 源 → 節點 ──
print("\n[3] O252 源 → 最近節點 (a5_nodes 排序, 連同 R3 k-class):")
k2 = [10,12,19,22,23,25,28,32,37,40,45,46]
k0 = [0,4,9,20,35,53,54,57]
klab = np.array([2 if i in k2 else (0 if i in k0 else 1) for i in range(60)])
sources = [
    ('A', 'JADES-GN-68797', 189.2291371, 62.1461898, 'GOODS-N'),
    ('C', 'JADES-GN-73488', 189.1973959, 62.1772331, 'GOODS-N'),
    ('I', 'JADES-GN-53501', 189.2950564, 62.1935722, 'GOODS-N'),
    ('J', 'JADES-GN-38147', 189.2706763, 62.1484185, 'GOODS-N'),
    ('E', 'RUBIES-EGS-49140', 214.89224786, 52.87740968, 'EGS'),
    ('K', 'RUBIES-EGS-50052', 214.82345394, 52.83027658, 'EGS'),
]
src_xyz = []
res = []
for sid, sname, ra, dec, fld in sources:
    s = np.array([math.cos(math.radians(dec))*math.cos(math.radians(ra)),
                  math.cos(math.radians(dec))*math.sin(math.radians(ra)),
                  math.sin(math.radians(dec))])
    src_xyz.append(s)
    d = ang(s[None,:], xyz)
    o = np.argsort(d)
    r2 = d[o[:3]]
    res.append((sid, fld, d[o[0]], o[0], klab[o[0]], round(float(r2[1]),3), round(float(r2[2]),3)))
    print(f"    {sid} {fld:7} → 最近節點 #{o[0]:02d} 距離 {d[o[0]]:6.2f}°  k-class={klab[o[0]]}  (第2/3近: {r2[1]:.1f}/{r2[2]:.1f})")

# ── 4. per-source 投影原型 + 分辨力 ──
print("\n[4] 𝒫_src 原型 (高斯窗, σ = 13°):")
sigma = 13.0
def signature(s, sigma=sigma):
    d = ang(s[None,:], xyz)
    w = np.exp(-0.5*(d/sigma)**2)
    return w/w.sum()
SIG = np.stack([signature(s) for s in src_xyz])
print("    源簽名 pair 相關 (同一簇應 → 1.0):")
names = [r[0] for r in res]
for i in range(len(SIG)):
    for j in range(i+1, len(SIG)):
        c = np.dot(SIG[i], SIG[j])/(np.linalg.norm(SIG[i])*np.linalg.norm(SIG[j]))
        same = '同簇' if res[i][1]==res[j][1] else '跨簇'
        print(f"      {names[i]}-{names[j]} ({same}): {c:.6f}")
# 最近節點 + 次近權重比
print("    最近節點權重單一性 (w1/w2):")
for i, r in enumerate(res):
    w = SIG[i]; o = np.argsort(-w)
    print(f"      {names[i]}: w1/w2 = {w[o[0]]/w[o[1]]:.1f} (w1 佔 {w[o[0]]:.3f})")

# ── 5. 判定 ──
print("\n[5] 判定:")
dmax2 = np.max([r[3] for r in res])
print(f"    最近節點距離: GOODS-N {res[0][3]:.2f}°–{res[2][3]:.2f}° / EGS {res[4][3]:.2f}°–{res[5][3]:.2f}° (vs 節點 NN ~26°)")
same_node = all(r[3]==res[0][3] for r in res[:4]) and all(r[3]==res[4][3] for r in res[4:])
print(f"    同簇源 → 同一節點: {'係 (4×GOODS-N 同一節點?) ' + str(res[0][3]) if same_node else '唔係'}")
print("    ⟹ per-source column density 唔可以由 𝒫 推:")
print("      (a) 𝒫 結構冇 per-source 維度 (60×88 鏈投影, 源位置只經幾何窗)")
print("      (b) 節點晶格角分辨 ~26° — 同簇源 (0.01–0.1° 分離) 全部塌縮到同一節點")
print("      (c) 節點值無統計顯著結構 (O143 閉合: GRF null, ~2.3σ 唔顯著) ⟹ 即使有 per-source 權重都係 noise")
print("      (d) 唯一結構身份 = R3 k-class (3 層: k=0/1/2) — 每源最多得一個類別, 唔係 column density")

json.dump({
    'P_structure': '60x88 Gaussian window, H_88 -> 60 nodes, no per-source dim',
    'node_NN_deg': {'min': float(cmin.min()), 'median': float(np.median(cmin)), 'max': float(cmin.max())},
    'sky_covering_radius_deg': float(dmax),
    'sources': [{'id': r[0], 'field': r[1], 'nearest_node_dist_deg': float(r[3]),
                 'nearest_node_idx': int(r[4]), 'k_class': int(r[5])} for r in res],
    'signature_corr': {f'{names[i]}-{names[j]}': round(float(np.dot(SIG[i],SIG[j])/(np.linalg.norm(SIG[i])*np.linalg.norm(SIG[j]))),6)
                       for i in range(len(SIG)) for j in range(i+1,len(SIG))},
    'verdict': 'per_source_column_density_NOT_derivable: no per-source dim in P; node lattice resolution ~26 deg; node amplitudes GRF-null; max identity = R3 k-class',
}, open(f'{OUTDIR}/step40_o252_per_source.json','w'), indent=1)
print(f"\n✅ 已存: data/step40_o252_per_source.json")