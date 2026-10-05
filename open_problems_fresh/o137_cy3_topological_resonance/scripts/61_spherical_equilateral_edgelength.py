#!/usr/bin/env python3
"""
O137 — Round 14 (scripts/61)
============================
缺口 ④ 之【正面】路線。

scripts/58–60 已證:
  ✅ R1 單向定理: 4-正則 + 20 邊不相交 △ + 12 邊不相交 ⬠ (覆蓋全部 120 邊)
                ⟹ MaxCut ≤ 88 = 2N_d  (界可取)
  🔴 R3 否證: 「MaxCut = 88 ⟹ RH/A₅ 網」係【假】—
     恰有 2 個 4-正則 Cayley 圖 of A₅ 給 88 (皆 20△+12⬠ 覆蓋 120 邊, 皆 Aut 階 120,
     皆頂點傳遞); 唯一判別 = 【平面性】(RH 平面, 另一個非平面)。
  ⟹ 額外輸入必須係【球面等邊嵌入】(spherical equilateral embedding)。

本輪 (正面): 由【球面等邊 + 頂點圖 3.4.5.4】唯一確定邊長 L* — 零參數。
  §1 RH 邊長實測
  §2 球面正 n 邊形內角公式 A_n(L) (以 n=3 對照等邊球面三角形公式驗證)
  §3 解 A₃(L) + 2A₄(L) + A₅(L) = 2π  → L*
  §4 對照 RH 實測邊長 + 角度和
  §5 判定
"""
import numpy as np, math
from scipy.optimize import brentq

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

BASE="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/"
D=BASE+"o137_cy3_topological_resonance/data/"
CMB=BASE+"cmb_cold_spot/"
RH=np.load(D+"rhombicosidodecahedron_unit.npy")

def edges_from_vecs(V,th=28.0):
    C=np.clip(V@V.T,-1,1); A=(np.degrees(np.arccos(C))<th)
    np.fill_diagonal(A,False); return A
def edge_lengths(V,th=28.0):
    A=edges_from_vecs(V,th); C=np.clip(V@V.T,-1,1)
    return np.degrees(np.arccos(C[A]))

print("="*88); print("§1 ★ RH 邊長實測 (單位球)"); print("="*88)
L_RH=edge_lengths(RH)
print(f"  120 條邊: mean = {L_RH.mean():.6f}°, std = {L_RH.std():.2e}°, min = {L_RH.min():.6f}°, max = {L_RH.max():.6f}°")
ck("RH 等邊 (std < 1e−5°)", float(L_RH.std()), 0.0, 1e-5)
L_obs_deg=float(L_RH.mean())
ck("RH 邊長 ≈ 25.8786°", L_obs_deg, 25.8786, 0.001)
# 歐氏 RH 公式對照: R = (a/2)√(11+4√5); 角邊長 = 2 arcsin(a/(2R))
R_over_a=math.sqrt(11+4*math.sqrt(5))/2
L_formula=2*math.degrees(math.asin(1/(2*R_over_a)))
print(f"  歐氏公式: R/a = √(11+4√5)/2 = {R_over_a:.9f};  L = 2·arcsin(a/2R) = {L_formula:.6f}°")
ck("★ 公式對照 (歐氏 RH 角邊長)", L_obs_deg, L_formula, 0.001)

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§2 ★ 球面正 n 邊形之內角公式 A_n(L)"); print("="*88)
def theta_of_L(L,n):
    """外接圓角半徑 θ: cos L = cos²θ + sin²θ·cos(2π/n)"""
    c2=(math.cos(L)-math.cos(2*math.pi/n))/(1-math.cos(2*math.pi/n))
    return math.acos(math.sqrt(max(0.0,min(1.0,c2))))
def angle_regular_n(L,n):
    """正 n 邊形內角 A = 2α, α = 三角形 (O,V1,V2) 在 V1 之角"""
    th=theta_of_L(L,n)
    num=math.cos(th)*(1-math.cos(L))
    den=math.sin(th)*math.sin(L)
    if den<=0: return math.pi
    c=num/den
    return 2*math.acos(max(-1,min(1,c)))
def angle_equilateral_tri(L):
    c=(math.cos(L)-math.cos(L)**2)/math.sin(L)**2
    return math.acos(max(-1,min(1,c)))
print(f"  {'L(°)':>8} {'A₃(L) 多邊形':>14} {'A₃(L) 三角形':>14} {'差':>10}")
for Ld in [1,5,10,20,25.8786,40,60]:
    L=math.radians(Ld)
    a=math.degrees(angle_regular_n(L,3)); b=math.degrees(angle_equilateral_tri(L))
    print(f"  {Ld:>8.4f} {a:>14.9f} {b:>14.9f} {abs(a-b):>10.2e}")
ck("★ n=3: 多邊形公式 ≡ 等邊球面三角形公式 (5° 處)",
   math.degrees(angle_regular_n(math.radians(5),3)),
   math.degrees(angle_equilateral_tri(math.radians(5))), 1e-9)
print(f"\n  L → 0 極限: A₃ = {math.degrees(angle_regular_n(1e-3,3)):.6f}°, "
      f"A₄ = {math.degrees(angle_regular_n(1e-3,4)):.6f}°, "
      f"A₅ = {math.degrees(angle_regular_n(1e-3,5)):.6f}°")
ck("L→0: A₃ = 60°", math.degrees(angle_regular_n(1e-3,3)), 60.0, 1e-4)
ck("L→0: A₄ = 90°", math.degrees(angle_regular_n(1e-3,4)), 90.0, 1e-4)
ck("L→0: A₅ = 108°", math.degrees(angle_regular_n(1e-3,5)), 108.0, 1e-4)

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§3 ★★ 解 A₃(L) + 2A₄(L) + A₅(L) = 2π  → 邊長 L*"); print("="*88)
def S(L):
    return angle_regular_n(L,3)+2*angle_regular_n(L,4)+angle_regular_n(L,5)
def f(L): return S(L)-2*math.pi
print(f"  L = 0°    →  ΣA = {math.degrees(S(1e-3)):.6f}°  (348° 平面值 = 60+180+108)")
ck("L→0: ΣA = 348° (< 360°)", math.degrees(S(1e-3)), 348.0, 1e-3)
hi=math.radians(80)
print(f"  L = 80°   →  ΣA = {math.degrees(S(hi)):.4f}°")
ck("ΣA 隨 L 單調增 (L=80° 時 > 360°)", math.degrees(S(hi))>360, True)
Lstar=brentq(f,1e-6,hi,xtol=1e-15,rtol=1e-15)
print(f"\n  ★★ L* = {math.degrees(Lstar):.9f}°")
print(f"  ★★ ΣA(L*) = {math.degrees(S(Lstar)):.9f}°  (目標 360°)")
ck("★★ ΣA(L*) = 360°", math.degrees(S(Lstar)), 360.0, 1e-6)

print("\n"+"="*88); print("§4 ★★ 對照 RH 實測"); print("="*88)
print(f"  RH 實測邊長      = {L_obs_deg:.9f}°")
print(f"  ★★ 零參數 L*     = {math.degrees(Lstar):.9f}°")
print(f"  差               = {abs(L_obs_deg-math.degrees(Lstar)):.9f}°  ({abs(L_obs_deg-math.degrees(Lstar))/L_obs_deg*100:.6f}%)")
ck("★★ L* = RH 實測邊長 (tol 1e−3°)", L_obs_deg, math.degrees(Lstar), 1e-3)
print(f"\n  RH 頂點之角度和 (用實測邊長):")
Lr=math.radians(L_obs_deg)
print(f"    A₃ = {math.degrees(angle_regular_n(Lr,3)):.6f}°, A₄ = {math.degrees(angle_regular_n(Lr,4)):.6f}°, "
      f"A₅ = {math.degrees(angle_regular_n(Lr,5)):.6f}°")
print(f"    ΣA = {math.degrees(S(Lr)):.6f}°  (應 = 360°)")
ck("★★ RH 實測邊長下 ΣA = 360° (tol 1e−4°)", math.degrees(S(Lr)), 360.0, 1e-4)

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§5 觀測節點集 (冷斑 A₅ 軌道) 之邊長"); print("="*88)
nodes=[tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()]
def rd(ra,dec):
    r,d=math.radians(ra),math.radians(dec)
    return np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)])
obs=np.array([rd(a,b) for a,b in nodes])
Lo=edge_lengths(obs)
print(f"  120 條邊: mean = {Lo.mean():.6f}°, std = {Lo.std():.3e}°, min = {Lo.min():.6f}°, max = {Lo.max():.6f}°")
print(f"  與 RH 邊長之差 = {Lo.mean()-L_obs_deg:+.6f}°  ({(Lo.mean()-L_obs_deg)/L_obs_deg*100:+.4f}%)")
print(f"  與 L* 之差     = {Lo.mean()-math.degrees(Lstar):+.6f}°")
Sobs=math.degrees(S(math.radians(Lo.mean())))
print(f"  觀測平均邊長下之 ΣA = {Sobs:.6f}°  (偏離 360° 共 {Sobs-360:+.6f}°)")

print("\n"+"="*88); print("§6 判定"); print("="*88)
print(f"""
  ★★ 正面結果 (零參數):
     頂點圖 3.4.5.4 (由 20△ + 30□ + 12⬠ 強制) + 球面等邊嵌入
     ⟹ 角度和方程 A₃(L) + 2A₄(L) + A₅(L) = 2π
     ⟹ 邊長【唯一確定】L* = {math.degrees(Lstar):.6f}°
     RH 實測 = {L_obs_deg:.6f}°  (差 {abs(L_obs_deg-math.degrees(Lstar)):.2e}°)

  ⟹ 缺口 ④ 之最終地位:
     🔴 「88 ⟹ A₅ 網」否證 (scripts/59–60: 2 個 Cayley 圖同給 88, 唯一判別 = 平面性)
     🟢 「球面等邊 + 面結構 3.4.5.4 ⟹ 邊長零參數確定 + Archimedean 唯一 (RH)」
     ⟹ 額外輸入 = 球面等邊嵌入; 該輸入 IDCM 側【確實提供】(88 sites 係天球點)
       但【唔可以】由 88 呢個純數字推出。
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
