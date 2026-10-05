#!/usr/bin/env python3
"""
O137 — A₅ 集獨立驗證 (Part 3): 座標系修正 + 正確軸重驗

★ Part 3 發現:
  a5_nodes.txt 存 ICRS (RA,Dec), node 0 = 冷斑 (Gal 209,−57) → ICRS (48.2999,−20.4373)
  O136 script 33 用 cold = (l,b)=(209,−57) 直接當同座標系 ⟹ 軸錯 (偏 13.48°)

本 script: 用正確軸 (node 0) 重算動差 + 模式選擇, 對比 docs/19
"""
import numpy as np, math
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
raw = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(raw[:,0]), np.radians(raw[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V,axis=1,keepdims=True)
N = len(V)

# 冷斑 ICRS
from astropy.coordinates import SkyCoord, Galactic
import astropy.units as u
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic).icrs
COLD_TRUE = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                      math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                      math.sin(math.radians(cs.dec.deg))])
print("="*80); print("座標系修正"); print("="*80)
print(f"冷斑 Gal (209,−57) → ICRS: RA={cs.ra.deg:.4f}° Dec={cs.dec.deg:.4f}°")
print(f"node 0 (檔案): RA={raw[0,0]:.4f}° Dec={raw[0,1]:.4f}°")
print(f"node 0 ↔ 冷斑 角距: {math.degrees(math.acos(np.clip(np.dot(V[0],COLD_TRUE),-1,1))):.2e}°  ✅ node0 = 冷斑")

lb = (math.radians(209.0), math.radians(-57.0))
COLD_WRONG = np.array([math.cos(lb[1])*math.cos(lb[0]), math.cos(lb[1])*math.sin(lb[0]), math.sin(lb[1])])
print(f"O136 script 33 用嘅軸 (把 (209,−57) 當 ICRS) 與真冷斑角距: "
      f"{math.degrees(math.acos(np.clip(np.dot(COLD_WRONG,COLD_TRUE),-1,1))):.4f}°  ⚠️")

Tn = np.polynomial.chebyshev.Chebyshev.basis
Pl = np.polynomial.legendre.Legendre.basis
def a0(n): return 0.0 if n%2==1 else 1.0/(1-n*n)

print("\n"+"="*80); print("動差對比: 錯軸 (docs/19) vs 正確軸 (node 0)"); print("="*80)
docs19 = {1:0,2:0,3:0,4:0,5:0,6:0.873778,7:0,8:0,9:0,10:0.267446,11:0,12:-5.288945,
          13:0,14:0,15:0.199879,16:-1.175282}
xw, xt = V@COLD_WRONG, V@COLD_TRUE
print(f"\n{'l':>3} {'Σ P_l (錯軸)':>15} {'Σ P_l (正確軸)':>16} {'docs19':>11} {'差':>11}")
for l in range(1,17):
    sw = float(Pl(l)(xw).sum()); st = float(Pl(l)(xt).sum())
    d = docs19.get(l, None)
    print(f"{l:>3} {sw:>15.6f} {st:>16.6f} {d if d is None else format(d,'>11.6f')} {'' if d is None else format(sw-d,'>11.2e')}")

print("\n"+"="*80); print("模式選擇: 錯軸 vs 正確軸"); print("="*80)
def sel(axis, tol=1e-4):
    x = V@axis
    return [n for n in range(1,45) if abs(float(Tn(n)(x).sum())-60*a0(n))<tol]
s_w, s_t = sel(COLD_WRONG), sel(COLD_TRUE)
print(f"錯軸 (docs/19):  {len(s_w)} 個 = {s_w}")
print(f"正確軸:          {len(s_t)} 個 = {s_t}")
print(f"★ 相同: {s_w==s_t}  {'✅ 選擇律唔受軸影響' if s_w==s_t else '🔴'}")
print(f"★ docs/19 宣稱 [1,2,3,4,5,7,9,11,13] — 正確軸一致: {s_t==[1,2,3,4,5,7,9,11,13]} ✅")

print("\n"+"="*80); print("為何軸無關? 群論證明"); print("="*80)
print("""
Σ_i P_l(v_i·c) 作為 c 嘅函數 = I-invariant 調和多項式 (次數 l)。
h(l) := dim(此空間) 由 Molien 級數決定 (純群論):
    h(l)=0  ⟺  Σ_i P_l(v_i·c) ≡ 0 對【所有】c  (恆零)
    h(l)>0  ⟹  對一般 c 非零 (零集測度為零)

Molien (Part 1): h(l)=0 for l ∈ {1,2,3,4,5,7,8,9,11,13,14,17,19,23}
                 h(l)=1 for l ∈ {6,10,12,15,16,18,20,21,22,24,25,26}

T_n 嘅 Legendre 展開: T_n = Σ_{j≤n, j≡n(2)} a_j P_j
準則 Σ_i T_n = 60·a₀(n)  ⟺  Σ_{j≥2} a_j Σ_i P_j = 0
                       ⟺  a_j = 0 for all j≥2 with h(j) ≠ 0

奇 n: j 奇。h(奇 j)≠0 者 = {15,21,25,...} ⟹ n ≤ 13 ✅
偶 n: j 偶。h(偶 j)≠0 者 = {6,10,12,16,...} ⟹ n ∈ {2,4} ✅
合計 9 個 = {1,2,3,4,5,7,9,11,13}
""")
# 驗證 Legendre 分量條件
print(f"{'n':>3} {'選中':>5} {'j≥2 且 h(j)≠0 之 a_j':>40}")
hset = {1:0,2:0,3:0,4:0,5:0,6:1,7:0,8:0,9:0,10:1,11:0,12:1,13:0,14:0,15:1,16:1,
        17:0,18:1,19:0,20:1,21:1,22:1,23:0,24:1,25:1,26:1}
xq, wq = np.polynomial.legendre.leggauss(120)
for n in range(1,18):
    f = Tn(n)(xq)
    aj = {j: (2*j+1)/2*np.sum(wq*f*Pl(j)(xq)) for j in range(2,n+1) if hset.get(j,1)!=0}
    nz = {j: round(v,8) for j,v in aj.items() if abs(v)>1e-9}
    print(f"{n:>3} {'★' if n in s_t else ' ':>5} {str(nz) if nz else '全零 ⟹ 選中':>40}")
