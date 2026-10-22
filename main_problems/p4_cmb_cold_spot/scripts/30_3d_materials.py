#!/usr/bin/env python3
"""
P4 3D chiral OBJ 材質版 — 兩款:
  A) MTL face-color: 冷/熱面著色 (anchored coloring) + 阻挫面標示
  B) CMB texture: SMICA 5° 平滑 equirectangular 貼圖 (UV 映射)
================================================================
原料:
  data/a5_nodes.txt       (60 節點 RA/Dec)
  data/faces.txt          (62 面, 每面 colors + frust)
  data/anchored_coloring.txt (60 節點 cold/hot)
  SMICA map: /home/wsl/.hermes/cache/scratch/planck_smica/smica.fits
輸出:
  data/rhombicosa_color.obj + rhombicosa_color.mtl     (版 A)
  data/rhombicosa_cmbtex.obj + rhombicosa_cmbtex.mtl
  data/rhombicosa_cmbtex.png                            (texture PNG)
"""
import numpy as np
import healpy as hp
import math, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
SMICA = "/home/wsl/.hermes/cache/scratch/planck_smica/smica.fits"

# ---------- load ----------
nodes = np.loadtxt(os.path.join(DATA, "a5_nodes.txt"))
RA, Dec = nodes[:, 0], nodes[:, 1]

faces = []
face_color = []   # cold/hot label per face (0=hot,1=cold), by majority
frust = []
with open(os.path.join(DATA, "faces.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        typ, rest = line.split(None, 1)
        ids = [int(t) for t in rest.split(']')[0].strip('[').split(',')]
        cl = rest.split("colors=[", 1)[1].split("]")[0]
        colors = [int(x) for x in cl.split(",")]
        fr = int(rest.split("frust=", 1)[1].split()[0]) if "frust=" in rest else 0
        faces.append(ids)
        face_color.append(1 if sum(colors) > len(ids) / 2 else 0)  # majority cold
        frust.append(fr)
print(f"faces={len(faces)} (20T+30S+12P)")
print(f"face majority cold={sum(face_color)}, hot={len(face_color)-sum(face_color)}")
print(f"frust counts: { {f: frust.count(f) for f in set(frust)} }")

# ---------- UV (equirectangular) ----------
# u = RA/360 (lonlat), v = (90 - Dec)/180 ; OBJ v=0 底部
uv = np.array([RA / 360.0, (90.0 - Dec) / 180.0]).T
# RA 0..360 -> u 0..1, 但唔好捲 wrap (faces 唔應該跨 0/360; 檢查最大邊界)
RA = np.mod(RA, 360.0)
uv = np.array([RA / 360.0, (90.0 - Dec) / 180.0]).T

# ---------- A) MTL face-color ----------
def write_color_obj(path_obj, path_mtl):
    with open(path_obj, "w") as f:
        f.write("# A5 rhombicosidodecahedron — face colors (cold/hot + frust)\n")
        f.write(f"mtllib {os.path.basename(path_mtl)}\n")
        f.write("usemtl facecold\n")
        for i in range(60):
            # each node goes to sphere; vn from node vector
            r, d = math.radians(RA[i]), math.radians(Dec[i])
            v = (math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d))
            f.write(f"v {v[0]:.9f} {v[1]:.9f} {v[2]:.9f}\n")
            f.write(f"vt {uv[i,0]:.9f} {uv[i,1]:.9f}\n")
        for i, ids in enumerate(faces):
            mtl = "facecold" if face_color[i] == 1 else "facehot"
            f.write(f"usemtl {mtl}\n")
            f.write("f " + " ".join(f"{j+1}/{j+1}" for j in ids) + "\n")
    with open(path_mtl, "w") as f:
        f.write("newmtl facecold\nKd 0.25 0.45 0.90\nKa 0.1 0.1 0.1\n\n")
        f.write("newmtl facehot\nKd 0.90 0.35 0.25\nKa 0.1 0.1 0.1\n")

write_color_obj(os.path.join(DATA, "rhombicosa_color.obj"),
                os.path.join(DATA, "rhombicosa_color.mtl"))

# ---------- B) CMB texture ----------
# read SMICA, smooth 5deg, cartview (equirectangular full sky)
print("load SMICA...")
sm = hp.read_map(SMICA, field=0)
nside = hp.get_nside(sm)
sig = np.radians(5.0) / (2 * np.sqrt(2 * np.log(2)))
sm_s = hp.remove_dipole(hp.smoothing(sm, sigma=sig))
# equirectangular texture via hp.cartview: lonlat range [-180,180] x [-90,90]; rot=[0,0,0]
# cartview returns a figure-based map; better: use hp.cartview with return_proj_map
img = hp.cartview(sm_s * 1e6, lonra=[-180, 180], latra=[-90, 90],
                  xsize=1024, ysize=512, return_projected_map=True, title=None)
# img = 2D array (float, projection units) — values in (mK*1e3??) we rescale to 8-bit
a = np.asarray(img)
# normalize to 0..255 (use robust percentiles)
lo, hi = np.percentile(a, 2), np.percentile(a, 98)
a8 = np.clip((a - lo) / (hi - lo + 1e-12) * 255, 0, 255).astype(np.uint8)
# cartview X axis: lon -180..180 (X=0 -> -180); Y: lat 90..-90 (Y=0 -> +90)
# our UV: u=0 -> RA 0 (lon 0), v=0 -> Dec 90.  mapping: u = (lon+180)/360
def uv_to_tex(u, v):
    lon = u * 360.0          # 0..360
    lon = lon - 360 if lon >= 180 else lon   # -180..180
    lat = 90 - v * 180       # 90..-90
    x = (lon + 180) / 360 * 1023
    y = (90 - lat) / 180 * 511
    return int(round(x)), int(round(y))
imgRGB = np.stack([a8, a8, a8], axis=-1)
tex_path = os.path.join(DATA, "rhombicosa_cmbtex.png")
Image.fromarray(imgRGB, "RGB").save(tex_path)
print(f"texture saved: {tex_path} ({imgRGB.shape})")

with open(os.path.join(DATA, "rhombicosa_cmbtex.obj"), "w") as f:
    f.write("# A5 rhombicosidodecahedron — SMICA 5deg equirectangular texture\n")
    f.write("mtllib rhombicosa_cmbtex.mtl\n")
    f.write("usemtl cmbtex\n")
    for i in range(60):
        r, d = math.radians(RA[i]), math.radians(Dec[i])
        v = (math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d))
        f.write(f"v {v[0]:.9f} {v[1]:.9f} {v[2]:.9f}\n")
        tx, tyex = uv_to_tex(uv[i, 0], uv[i, 1])
        # OBJ vt origin = bottom-left; our image row 0 = top (lat+90)
        vt_v = tyex / 511.0
        f.write(f"vt {tx/1023.0:.9f} {vt_v:.9f}\n")
    for ids in faces:
        f.write("f " + " ".join(f"{j+1}/{j+1}" for j in ids) + "\n")
with open(os.path.join(DATA, "rhombicosa_cmbtex.mtl"), "w") as f:
    f.write("newmtl cmbtex\n")
    f.write("Ka 1 1 1\nKd 1 1 1\nKs 0 0 0\n")
    f.write("map_Kd rhombicosa_cmbtex.png\n")

print("B done: rhombicosa_cmbtex.obj / .mtl / .png")
print("A done: rhombicosa_color.obj / .mtl")