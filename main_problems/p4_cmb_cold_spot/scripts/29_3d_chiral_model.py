#!/usr/bin/env python3
"""
P4 3D-chiral-shape 生成 v2 — A5 60節點網格 + 手性絕對取向 (O213 判據)
=======================================================================
規格 (調律者 2026-10-11, register: cmb_cold_spot/3d-chiral-shape):
  形狀: A5 Rhombicosidodecahedron (20T+30S+12P, V60 E120 F62, chi=2)
  手性判據 (O213 scripts/10, 已閉合 R5):
    C5  proper dev < 1e-3  (A5 = exact I-orbit)
    C7  improper dev ≈ 2.67°  (strictly chiral, |Sym|=60 no det=-1)
    C8  δ_m = seed到最近2-fold軸偏離 = 2.670063°
    C13 對極 −v∉軌道, 距 5.34° = 2δ_m (唯一可手性之型)
    C16 手性偽標量 χ = sign(x₀·â)·δ_m (絕對 sense)
    C17 mirror(A5) 最優匹配殘餘 > 0
  輸出: 3D 網格 OBJ + 左右手 enantiomer (以 5.3402°=2δ_m 為標定尺)
  禁區: 未經盲測結構確認前唔准貼物理標籤

產出:
  data/rhombicosa_3d.obj            # A5 網格 (reference R)
  data/rhombicosa_enantiomer_L.obj  # 左手 enantiomer
  data/rhombicosa_enantiomer_R.obj  # 右手 enantiomer
  data/rhombicosa_3d_chirality.txt  # 手性標定
"""
import numpy as np
import math
import itertools
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
PHI = (1 + math.sqrt(5)) / 2

# ---------- 1. load nodes (RA, Dec) -> unit sphere ----------
nodes = np.loadtxt(os.path.join(DATA, "a5_nodes.txt"))
def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
V = np.array([sph(*row) for row in nodes], float)
assert len(V) == 60

# ---------- 2. load faces ----------
faces = []
with open(os.path.join(DATA, "faces.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        typ, rest = line.split(None, 1)
        ids = [int(t) for t in rest.split(']')[0].strip('[').split(',')]
        faces.append(ids)
print(f"faces: {len(faces)} = {sum(1 for ff in faces if len(ff)==3)}T "
      f"+ {sum(1 for ff in faces if len(ff)==4)}S + {sum(1 for ff in faces if len(ff)==5)}P")

# ---------- 3. I group (closure) ----------
def rot_axis(u, t):
    u = np.array(u, float); u /= np.linalg.norm(u)
    K = np.array([[0,-u[2],u[1]],[u[2],0,-u[0]],[-u[1],u[0],0]])
    return np.eye(3) + math.sin(t)*K + (1-math.cos(t))*(K@K)
def closure(gens):
    key = lambda R: tuple(np.round(R.flatten(), 7))
    seen = {key(np.eye(3)): np.eye(3)}; fr = [np.eye(3)]
    while fr:
        new = []
        for R in fr:
            for g in gens:
                P = R @ g; k = key(P)
                if k not in seen: seen[k] = P; new.append(P)
        fr = new
    return list(seen.values())
I_grp = closure([rot_axis([0,1,PHI], 2*math.pi/5), rot_axis([1,1,1], 2*math.pi/3)])
assert len(I_grp) == 60, f"|I|={len(I_grp)}"

def group_action_dev(P, G):
    """max over g∈G of (min angle 將 g·P 送回 P 集合)"""
    worst = 0.0
    for g in G:
        Q = (g @ P.T).T
        best = np.degrees(np.arccos(np.clip(np.max(Q @ P.T, axis=1), -1, 1))).max()
        worst = max(worst, best)
    return worst

dev_proper = group_action_dev(V, I_grp)
dev_improper = group_action_dev(V, [(-g) for g in I_grp])
print(f"dev proper   = {dev_proper:.6f}°  (expect < 1e-3, C5)")
print(f"dev improper = {dev_improper:.6f}°  (expect ~2.67, C7)")

# ---------- 4. δ_m: seed to nearest 2-fold axis (C8) ----------
ico = []
for sg in itertools.product([1,-1], repeat=2):
    ico += [(0, sg[0]*1, sg[1]*PHI), (sg[0]*1, sg[1]*PHI, 0), (sg[0]*PHI, 0, sg[1]*1)]
Ico = np.array(sorted(set(ico)), float); Ico /= np.linalg.norm(Ico, axis=1, keepdims=True)
mid2 = np.array([(Ico[i]+Ico[j]) for i in range(12) for j in range(i+1, 12)
                 if abs(float(Ico[i]@Ico[j]) - 0.4472135955) < 1e-6])
mid2 /= np.linalg.norm(mid2, axis=1, keepdims=True)
ax2 = np.unique(np.round(mid2, 6), axis=0)
print(f"2-fold 軸方向 = {len(ax2)} (± 方向都留, |dot| 對 ± 相同, 唔影響 min)")
x0 = V[0]
devs = [abs(90 - math.degrees(math.acos(max(-1, min(1, float(x0@a)))))) for a in ax2]
k = int(np.argmin(devs)); a_near = ax2[k]
delta_m = devs[k]
chi_pseudo = (1 if float(x0 @ a_near) > 0 else -1) * delta_m
print(f"δ_m = {delta_m:.6f}°  (expect 2.670063, C8)")
print(f"χ   = {chi_pseudo:+.6f}°  (C16)")

# ---------- 5. antipodal (C13) ----------
antip = np.degrees(np.arccos(np.clip(np.max(V @ (-V).T, axis=1), -1, 1))).max()
print(f"對極 −v 最近距離 = {antip:.6f}°  (expect 2δ_m = {2*delta_m:.6f}°, C13/C15)")

# ---------- 6. mirror residual (C17) ----------
mirror_A5 = V * np.array([1, 1, -1])
mres = np.degrees(np.arccos(np.clip(np.max(mirror_A5 @ V.T, axis=1), -1, 1))).max()
print(f"mirror residual = {mres:.6f}°  (expect 5.34, C17)")

# ---------- 7. verdict ----------
ok = (dev_proper < 1e-3 and dev_improper > 1.0 and abs(delta_m - 2.670063) < 0.001
      and abs(antip - 2*delta_m) < 0.01 and chi_pseudo != 0 and mres > 1e-3)
print(f"手性判定: {'🟢 嚴格手性 (|Sym|=60, all det=+1)' if ok else '🔴 FAIL'}")

# ---------- 8. OBJ writer ----------
def write_obj(path, VV, FF, comment=""):
    with open(path, "w") as f:
        f.write("# " + comment + "\n")
        f.write(f"# V={len(VV)} E={sum(len(ff) for ff in FF)//2} F={len(FF)}\n")
        for vv in VV:
            f.write(f"v {vv[0]:.9f} {vv[1]:.9f} {vv[2]:.9f}\n")
        for ff in FF:
            f.write("f " + " ".join(str(i + 1) for i in ff) + "\n")

# enantiomers: R = reference (A5), L = mirror(A5); chi sign 由數據定
R_label, L_label = "R", "L"
chi_R, chi_L = chi_pseudo, -chi_pseudo
write_obj(os.path.join(DATA, "rhombicosa_3d.obj"), V, faces,
          f"A5 rhombicosidodecahedron reference ({R_label}, χ={chi_R:+.6f}°)")
write_obj(os.path.join(DATA, f"rhombicosa_enantiomer_{R_label}.obj"), V, faces,
          f"A5 enantiomer {R_label} χ={chi_R:+.6f}°")
write_obj(os.path.join(DATA, f"rhombicosa_enantiomer_{L_label}.obj"), mirror_A5, faces,
          f"A5 enantiomer {L_label} χ={chi_L:+.6f}° (mirror of reference)")

with open(os.path.join(DATA, "rhombicosa_3d_chirality.txt"), "w") as f:
    f.write("# A5 3D chirality gauge — O213 scripts/10 reproduction + OBJ output\n")
    f.write(f"dev_proper   = {dev_proper:.9f} deg   (C5 < 1e-3)\n")
    f.write(f"dev_improper = {dev_improper:.9f} deg   (C7 [strictly chiral])\n")
    f.write(f"delta_m      = {delta_m:.9f} deg   (C8 expect 2.670063)\n")
    f.write(f"2*delta_m    = {2*delta_m:.9f} deg   (C15 expect 5.3402)\n")
    f.write(f"antipodal    = {antip:.9f} deg   (C13 = 2*delta_m)\n")
    f.write(f"chi_pseudo   = {chi_pseudo:+.9f} deg   (C16 absolute sense)\n")
    f.write(f"mirror_resid = {mres:.9f} deg   (C17 > 0)\n")
    f.write(f"|GeoAut|     = 60 proper, 0 improper  (O223 B1/B2/B3)\n")
    f.write(f"verdict      = {'chiral-strict' if ok else 'FAIL'}\n")
    f.write(f"enantiomers  = R:{R_label} (chi {chi_R:+.4f}), L:{L_label} (chi {chi_L:+.4f})\n")

print(f"\nenantiomers: R={R_label} χ={chi_R:+.4f}°, L={L_label} χ={chi_L:+.4f}°")
print("outputs: rhombicosa_3d.obj, rhombicosa_enantiomer_{L,R}.obj, rhombicosa_3d_chirality.txt")
print(f"RESULT: {'PASS' if ok else 'FAIL'}")