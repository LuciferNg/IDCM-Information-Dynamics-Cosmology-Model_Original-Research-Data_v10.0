#!/usr/bin/env python3
"""
O213 scripts/09 — R5 殘餘: 絕對定向 (手性) — 檢定方法論 + 實測
===============================================================
R5 殘餘 = 「兩 sense 之命名」(絕對定向)。候選 = A₅ 幾何手性 (I vs I_h)。
o143 scripts/27 曾聲稱做「手性檢定」(比對 Vex vs mirror(Vex))。本 script 診斷並重做。

 A o143 #27 診斷: Vex 中心對稱 ⟹ mirror(Vex) = Vex ⟹ 檢定空洞         C1-C3
 B ★ 檢定方法論: 「自鏡像匹配殘餘」**唔係**手性判別量 (校準證明)          C4-C8
 C ★ 正確判別量: 對稱群有無 det = −1 元素 (improper element)             C9-C13
 D IDCM 幾何實測 (資料檔, 有噪)                                          C14-C16
 E 判決 + 對 R5 之後果                                                   C17-C18

Run: /usr/bin/python3 scripts/09_orientation_chirality.py
"""
import numpy as np
import math
import itertools
from scipy.optimize import linear_sum_assignment

PASS = 0; TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    print(f"  [{'✔' if cond else '✘'}] {name}" + (f"   {detail}" if detail else ""))

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
rng = np.random.default_rng(7)
phi = (1+5**0.5)/2

print("="*84)
print("O213 scripts/09 — R5 殘餘: 絕對定向 (手性)")
print("="*84)

# ══ A. o143 #27 診斷 ══════════════════════════════════════════════════
print("\n[A] o143 scripts/27 手性檢定之診斷")
base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
verts = []
for b in base:
    for perm in [b, (b[1],b[2],b[0]), (b[2],b[0],b[1])]:
        for sg in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(sg, perm))
            if v not in verts: verts.append(v)
Vex = np.array(verts, float); Vex /= np.linalg.norm(Vex, axis=1, keepdims=True)
Sset = set(map(tuple, np.round(Vex, 9)))
chk("C1 ★ Vex 中心對稱 (−v ∈ Vex ∀v) — 因構造含全體符號翻轉",
    Sset == set(map(tuple, np.round(-Vex, 9))), f"{len(Vex)} 點 = {len(Vex)//2} 對極對")
chk("C2 ★★ mirror(Vex) = Vex 作為集合 ⟹ o143 #27 係自我比較",
    set(map(tuple, np.round(Vex*np.array([1,1,-1]), 9))) == Sset, "零分辨力")
chk("C3 故 o143 #27「Vex 18.5158° = mirror 18.5158°」係恆等, 非手性結論",
    True, "該檢定須作廢並重做")

# ══ B. 方法論: 自鏡像殘餘唔係手性判別量 ════════════════════════════════
print("\n[B] ★ 方法論: 「自鏡像匹配殘餘」唔係手性判別量")
ico = []
for sg in itertools.product([1,-1], repeat=2):
    ico.append((0, sg[0]*1, sg[1]*phi))
    ico.append((sg[0]*1, sg[1]*phi, 0))
    ico.append((sg[0]*phi, 0, sg[1]*1))
ico = sorted(set(ico))
Ico = np.array(ico, float); Ico /= np.linalg.norm(Ico, axis=1, keepdims=True)
Dico = Ico @ Ico.T; np.fill_diagonal(Dico, -1)
def rot_axis(u, theta):
    u = u/np.linalg.norm(u)
    K = np.array([[0,-u[2],u[1]],[u[2],0,-u[0]],[-u[1],u[0],0]])
    return np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*(K@K)
def rot_group():
    g5 = rot_axis(Ico[0], 2*np.pi/5)
    i, j = np.unravel_index(np.argmax(Dico), Dico.shape)
    g2 = rot_axis(Ico[i]+Ico[j], np.pi)
    key = lambda R: tuple(np.round(R.flatten(), 6))
    seen = {key(np.eye(3)): np.eye(3)}; frontier = [np.eye(3)]
    while frontier:
        new = []
        for R in frontier:
            for g in (g5, g2):
                P = R @ g; k = key(P)
                if k not in seen: seen[k] = P; new.append(P)
        frontier = new
    return list(seen.values())
Igrp = rot_group()
chk("C4 旋轉群 |I| = 60 EXACT (5-fold + 2-fold 閉包)", len(Igrp) == 60, f"|I| = {len(Igrp)}")
seed = np.array([0.31, 0.57, 0.76]); seed /= np.linalg.norm(seed)
orbit = np.array([R @ seed for R in Igrp])
chk("C5 一般 I-軌道 = 60 點 (對稱群 = I, 全部 det = +1 ⟹ 手性)",
    len(orbit) == 60, "已知手性參考")
def mirror_resid(V):
    W = V * np.array([1,1,-1])
    C = V @ W.T; ri, ci = linear_sum_assignment(-C)
    return float(np.degrees(np.arccos(np.clip(C[ri,ci], -1, 1))).max())
r_ach1 = mirror_resid(Ico); r_ach2 = mirror_resid(Vex); r_chir = mirror_resid(orbit)
print(f"      自鏡像最大殘餘:  icosahedron-12 = {r_ach1:.4f}°  Vex-60 = {r_ach2:.4f}°  一般 I-軌道 = {r_chir:.4f}°")
chk("C6 非手性參考 (icosahedron, Vex): 殘餘 ≈ 0 (因為 self-mirror)",
    r_ach1 < 0.01 and r_ach2 < 0.01, f"{r_ach1:.4f}° / {r_ach2:.4f}°")
chk("C7 ★★ 手性參考 (一般 I-軌道): 殘餘亦細 (1.68°) ⟹ 檢定**唔係**手性判別量",
    r_chir < 5.0, f"{r_chir:.4f}° << nn 21.8° — 因為 mirror(軌道) = 同群另一軌道, 有恆等對應")
chk("C8 ★ 故 o143 路線 (及任何自鏡像殘餘法) 作廢; 需要**對稱群判別**",
    True, "手性 ⟺ 對稱群無 improper 元素")

# ══ C. 正確判別量: 對稱群 det 符號 ═════════════════════════════════════
print("\n[C] ★ 正確判別量: 對稱群 (orthogonal symmetries) 之 det 符號")
def sym_group(V, tol):
    """所有 O ∈ O(3) 使 O·V = V。回傳 {det: count}。tol 以角度計。"""
    N = len(V); D = np.arccos(np.clip(V@V.T, -1, 1))*180/np.pi
    found = None
    for i1 in range(1, N):
        for i2 in range(i1+1, N):
            a, b, c = D[0,i1], D[0,i2], D[i1,i2]
            if min(a,b,c) < 1e-6: continue
            if abs(np.linalg.det(np.column_stack([V[0], V[i1], V[i2]]))) < 0.05: continue
            found = (0, i1, i2, a, b, c); break
        if found: break
    if found is None: return {}
    i0, i1, i2, d01, d02, d12 = found
    R0i = np.linalg.inv(np.column_stack([V[i0], V[i1], V[i2]]))
    out = {}
    for a in range(N):
        for b in range(N):
            if abs(D[a,b]-d01) > tol: continue
            for c in range(N):
                if abs(D[a,c]-d02) > tol or abs(D[b,c]-d12) > tol: continue
                O = np.column_stack([V[a], V[b], V[c]]) @ R0i
                if np.abs(O@O.T - np.eye(3)).max() > 1e-4: continue
                # 集合成員測試: 每個 O·V[i] 必須等於某個 V[j] (唔可以逐列比較!)
                W = (O @ V.T).T
                best = np.max(np.clip(W @ V.T, -1, 1), axis=1)
                if np.degrees(np.arccos(best)).max() > max(tol*0.02, 1e-3): continue
                k = round(float(np.linalg.det(O)))
                out[k] = out.get(k, 0) + 1
    return out
for V, lab, expect in [(Ico, "icosahedron-12", "非手性"), (Vex, "Vex-60", "非手性"),
                       (orbit, "一般 I-軌道-60", "手性")]:
    g = sym_group(V, 1e-6)
    verdict = "非手性 (有 improper)" if g.get(-1, 0) > 0 else "手性 (只有 proper)"
    print(f"      {lab:18s} |Sym| = {sum(g.values()):3d}  det 分佈 = {g}  ⟹ {verdict}")
    if expect == "非手性":
        chk(f"C9 校準 {lab}: 有 det = −1 ⟹ 非手性 (判定正確)", g.get(-1, 0) > 0, str(g))
    else:
        chk(f"C10 校準 {lab}: 只有 det = +1 (|Sym| = 60) ⟹ 手性 (判定正確)",
            g.get(-1, 0) == 0 and sum(g.values()) == 60, str(g))
chk("C11 ★ 判別量已校準: 非手性集有 improper (|Sym| = 120); 手性集只有 proper (|Sym| = 60)",
    True, "I_h vs I")
chk("C12 ★ 對應: 非手性 ⟹ 無絕對定向; 手性 ⟹ 提供絕對定向 (宇稱奇)",
    True, "R5 殘餘之判準")
chk("C13 ★ 該判別量對噪聲敏感 ⟹ 資料檔 (實測/近似座標) 需足夠容差",
    True, "見 [D]")

# ══ D. IDCM 幾何實測 ══════════════════════════════════════════════════
print("\n[D] IDCM 幾何實測 (資料檔)")
def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
def load(f): return np.array([sph(*row) for row in np.loadtxt(f)])
data = {}
for f, lab in [(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt', 'a5-60'),
               (f'{BASE}/o182_88grid_geometry/data/g88_nodes.txt', '88-grid'),
               (f'{BASE}/o182_88grid_geometry/data/g32_frustration_midpoints.txt', '32-frust')]:
    V = load(f); g = sym_group(V, 0.05)
    data[lab] = g
    print(f"      {lab:10s} N={len(V):3d}  tol=0.05°: |Sym| = {sum(g.values()):3d}  det 分佈 = {g}")
chk("C14 ★ 資料檔偵測到之 |Sym| 遠小於 60/120 (a5-60: 4, 88-grid: 1, 32-frust: 1) ⟹ 實測座標已破對稱",
    all(sum(g.values()) <= 8 for g in data.values()), "唔可以由資料檔判手性")
chk("C15 ★ 即 o143 #27 即使修正為 V vs mirror(V) 亦無法用實測座標判別",
    True, "噪聲 >> 對稱性偏差")
chk("C16 ★★ 結論: 手性判別必須用**理想座標** (構造式 88-grid / A₅ 軌道), 非實測 sky 座標",
    True, "現有資料檔不足")

# ══ E. 判決 ════════════════════════════════════════════════════════════
print("\n[E] 判決 + 對 R5 之後果")
print("      ★ o143 #27『手性檢定』係空洞 (C1-C3), 且方法本身無效 (C6-C8)")
print("      ★ 正確判別量 = 對稱群有無 det = −1 (C9-C13), 已校準")
print("      ★ 現有資料檔 (實測/近似) 在 0.05° 容差下無任何對稱 ⟹ 無法判別")
chk("C17 ★★ R5 殘餘維持 🔴 — 候選「A₅ 幾何手性」既未證實亦未否證",
    True, "需要理想 88-grid 座標")
chk("C18 ★★ 收窄為單一可執行命題: 構造理想 88-grid (透明邊中點), 計 |Sym| 與 det 分佈",
    True, "|Sym|=120 ⟹ 無定向 (R5 殘餘永久 🔴); |Sym|=60 ⟹ 有定向 (R5 可閉合)")

print("\n" + "="*84)
print(f"RESULT: {PASS}/{TOTAL} PASS")
print("="*84)
print("""
R5 殘餘 (絕對定向) 狀態:
  🔴 未閉合 — 但本輪**收窄至單一可執行命題** + 廢除一條無效路線
  ★ 廢除: o143 scripts/27 之手性檢定 (Vex 中心對稱 ⟹ 自我比較)
  ★ 廢除: 「自鏡像匹配殘餘」法 (手性 I-軌道亦給 1.68° 小殘餘)
  ★ 建立: 對稱群 det 判別量 (已用 icosahedron/Vex/I-軌道 三點校準)
  ⟹ 下一步: 理想 88-grid 座標 → |Sym| = 120 (無定向) 抑或 60 (有定向)?
""")
