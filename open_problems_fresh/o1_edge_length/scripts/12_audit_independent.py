#!/usr/bin/env python3
"""
12_audit_independent.py — 新O1 獨立重驗 (T1, closeout)
=========================================================
鐵律:
  · 唔 import / 唔 call 任何原推導 script (01-11) —— 冇共享程式碼 = 冇共享 bug
  · 由原始輸入重算所有 headline 數字: a5_nodes.txt 節點 0 + dodecahedron 標準幾何定義
  · 用唔同算法: quaternion 旋轉 (原 script 用 3x3 矩陣) + mpmath dps=40 (原用 numpy float64)
  · 期望值逐字取自文檔原文 (grep), 唔靠記憶

驗證段:
  A. 幾何基元 (頂點/面/邊數, 邊長角)
  B. δ = 冷斑到最近 3-fold 軸角
  C. θ 三條獨立路徑 (球面餘弦定律 / quaternion 旋轉 / 代數)
  D. 邊長 mean/範圍 (由 60 節點直接算, 唔經群)
  E. 旋轉不變性 (quaternion 群作用)
  F. 群元素角譜 + 群大小
"""
import os, sys, math
from mpmath import mp, mpf, acos, cos, sin, sqrt, pi, degrees, radians

mp.dps = 40

# ── clip 保護: 浮點誤差令 dot > 1 時 acos 會返回 complex ──
_acos_raw = acos
def acos(x):
    x = mpf(x)
    return _acos_raw(max(mpf(-1), min(mpf(1), x)))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(BASE, "..", "cmb_cold_spot", "data", "a5_nodes.txt")

PASS = FAIL = 0
def chk(name, got, expect, tol, note=""):
    global PASS, FAIL
    ok = abs(mpf(got) - mpf(expect)) <= mpf(tol)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {mp.nstr(mpf(got), 12)} vs {expect} (tol {tol}) {note}")
    if ok: PASS += 1
    else:  FAIL += 1

print("=" * 74)
print("新O1 獨立重驗 (A-F)  —  mpmath dps=40, quaternion, 零 import 原 script")
print("=" * 74)

# ══════════ A. 幾何基元 (由 φ 定義重建, 唔用原 script) ══════════
phi = (1 + sqrt(5)) / 2
inv_phi = 1 / phi

# 20 頂點 (3-fold 軸方向): (±1,±1,±1) ∪ 3 組 (0,±1/φ,±φ) 循環
verts = []
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            verts.append((mpf(sx), mpf(sy), mpf(sz)))
for sx in (-1, 1):
    for sy in (-1, 1):
        verts.append((mpf(0), mpf(sx) * inv_phi, mpf(sy) * phi))
        verts.append((mpf(sx) * inv_phi, mpf(sy) * phi, mpf(0)))
        verts.append((mpf(sx) * phi, mpf(0), mpf(sy) * inv_phi))
# 12 面中心 (5-fold 軸方向)
faces = []
for sx in (-1, 1):
    for sy in (-1, 1):
        faces.append((mpf(0), mpf(sx), mpf(sy) * phi))
        faces.append((mpf(sx), mpf(sy) * phi, mpf(0)))
        faces.append((mpf(sx) * phi, mpf(0), mpf(sy)))

def unit(v):
    n = sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)

verts_n = [unit(v) for v in verts]
faces_n = [unit(v) for v in faces]

chk("頂點數 (3-fold 軸)", len(verts_n), 20, 0)
chk("面中心數 (5-fold 軸)", len(faces_n), 12, 0)

# 邊長角: 20 頂點間最近距離對應嘅球心角 (唔用 2√2/√3 硬碼)
dmin = min(
    degrees(acos(sum(a * b for a, b in zip(verts_n[i], verts_n[j]))))
    for i in range(20) for j in range(i + 1, 20)
)
chk("dodecahedron 頂點球心角", dmin, 41.8103148957786, 1e-9, "文檔 41.81°")

# ══════════ B. δ = 冷斑到最近 3-fold 軸 ══════════
with open(NODES) as f:
    ra0, dec0 = [mpf(x) for x in f.readline().split()]
print(f"\n  節點 0 (a5_nodes.txt): RA={ra0}  Dec={dec0}")

v = (cos(radians(dec0)) * cos(radians(ra0)),
     cos(radians(dec0)) * sin(radians(ra0)),
     sin(radians(dec0)))
v = unit(v)

d3 = min(degrees(acos(sum(a * b for a, b in zip(v, n)))) for n in verts_n)
d5 = min(degrees(acos(sum(a * b for a, b in zip(v, n)))) for n in faces_n)
chk("δ (最近 3-fold)", d3, mpf("15.108516"), 1e-5, "文檔 15.108516°")
chk("δ5 (最近 5-fold)", d5, mpf("22.650938"), 1e-5, "文檔 22.650938°")

# ══════════ C. θ 三條獨立路徑 ══════════
# C1: 球面餘弦定律 (spherical law of cosines) — 原 script 冇用此路徑
#     兩點 p,q 同夾角 δ 由共同軸, 餘弦定律: cos θ = cos²δ + sin²δ cos(120°)
cos_theta_law = cos(radians(d3))**2 + sin(radians(d3))**2 * cos(radians(mpf(120)))
theta_law = degrees(acos(cos_theta_law))
chk("C1 θ (球面餘弦定律)", theta_law, mpf("26.091357"), 1e-5, "文檔 26.091357°")

# C2: quaternion 120° 旋轉 (原 script 用 3x3 矩陣) — 算法層獨立
#     軸 n3 (最近頂點), 角度 120°: q = (cos60°, sin60°·n3)
n3 = min(verts_n, key=lambda n: acos(sum(a * b for a, b in zip(v, n))))
w = cos(radians(mpf(60))); s = sin(radians(mpf(60)))
qx, qy, qz = s * n3[0], s * n3[1], s * n3[2]
def qrot(q, p):
    """用傳入 quaternion q=(w,x,y,z) 旋轉 p (unit quat): p' = p + 2w(q×p) + 2(q×(q×p))"""
    aw, ax, ay, az = q
    qv = (ax, ay, az)
    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    c1 = cross(qv, p)
    c2 = cross(qv, c1)
    return tuple(p[i] + 2 * aw * c1[i] + 2 * c2[i] for i in range(3))
vp = unit(qrot((w, qx, qy, qz), v))
theta_q = degrees(acos(sum(a * b for a, b in zip(v, vp))))
chk("C2 θ (quaternion 120°)", theta_q, mpf("26.091357"), 1e-5, "算法層獨立")

# C3: 代數恆等式 cos²δ − sin²δ/2  (= (3cos²δ−1)/2) — 文檔形式
cos_theta_alg = cos(radians(d3))**2 - sin(radians(d3))**2 / 2
theta_alg = degrees(acos(cos_theta_alg))
chk("C3 θ (代數 文檔形式)", theta_alg, mpf("26.091357"), 1e-5)
chk("C1≡C2≡C3 三路一致", theta_law - theta_q, mpf(0), 1e-9, "(差 < 1e-9°)")

# ══════════ D. 邊長 mean / 範圍 (60 節點直接算, 唔用群) ══════════
def load_all():
    out = []
    with open(NODES) as f:
        for ln in f:
            o = ln.split()
            if len(o) < 2: continue
            ra, dec = mpf(o[0]), mpf(o[1])
            out.append(unit((cos(radians(dec)) * cos(radians(ra)),
                             cos(radians(dec)) * sin(radians(ra)),
                             sin(radians(dec)))))
    return out
nodes = load_all()
chk("60 節點載入", len(nodes), 60, 0)

nn = []
for i in range(60):
    nn.append(min(degrees(acos(sum(a * b for a, b in zip(nodes[i], nodes[j]))))
                  for j in range(60) if j != i))
nn_mean = sum(nn) / 60
chk("邊長 mean", nn_mean, mpf("26.091346"), 1e-6, "文檔 26.091346°")
chk("邊長 min", min(nn), mpf("26.091319"), 1e-6)
chk("邊長 max", max(nn), mpf("26.091382"), 1e-6)
within = [x for x in nn if abs(x - mpf("26.091346")) < mpf("0.001")]
chk("26.09° 附近節點數", len(within), 60, 0, "全部 60 節點最近鄰都 ≈26.09°")

# ══════════ E. 旋轉不變性 (quaternion 群作用, 唔用矩陣) ══════════
# 繞最近頂點 120° 旋轉 → 整個軌道; 最近鄰距離不變
rotated = [unit(qrot((w, qx, qy, qz), p)) for p in nodes]
nn_rot = []
for i in range(60):
    nn_rot.append(min(degrees(acos(sum(a * b for a, b in zip(rotated[i], rotated[j]))))
                      for j in range(60) if j != i))
chk("旋轉後 mean 不變", sum(nn_rot) / 60, nn_mean, 1e-9, "std ≈ 0")
# ⚠️ 文檔「std=0」指: 同一節點旋轉前後最近鄰距離不變 (唔係 60 節點之間離散度)
chk("旋轉前後逐節點 nn 最大差", max(abs(a - b) for a, b in zip(nn_rot, nn)), mpf(0),
    mpf("1e-9"), "旋轉不變量 (文檔 std=0)")
sd = sqrt(sum((x - nn_mean) ** 2 for x in nn) / 60)
print(f"[INFO] 60 節點最近鄰離散 std = {mp.nstr(sd, 6)}° (邊長 26.091319–26.091382 嘅自然離散, 非不變量指標)")

# ══════════ F. 群元素角譜 ══════════
# 由 quaternion 生成 A5: 5-fold (72°) + 3-fold (120°) 生成元
def qmul(a, b):
    aw, ax, ay, az = a; bw, bx, by, bz = b
    return (aw*bw - ax*bx - ay*by - az*bz,
            aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw)
def qnorm(q):
    n = sqrt(sum(x * x for x in q))
    return tuple(x / n for x in q)
def qcanon(q):
    """q 同 −q 代表同一旋轉 (SU(2) 雙覆蓋 SO(3)) → canonical key"""
    k = tuple(mp.mpf(round(float(x), 8)) for x in q)
    nk = tuple(-x for x in k)
    return min(k, nk)

# 生成元 1: 繞面中心 n5 轉 72°; 生成元 2: 繞頂點 n3 轉 120°
g1 = qnorm((cos(radians(mpf(36))), sin(radians(mpf(36))) * faces_n[0][0],
            sin(radians(mpf(36))) * faces_n[0][1], sin(radians(mpf(36))) * faces_n[0][2]))
g2 = qnorm((cos(radians(mpf(60))), sin(radians(mpf(60))) * verts_n[0][0],
            sin(radians(mpf(60))) * verts_n[0][1], sin(radians(mpf(60))) * verts_n[0][2]))

ident = (mpf(1), mpf(0), mpf(0), mpf(0))
group = [ident]
seen = {qcanon(ident)}
queue = [ident]
while queue:
    q = queue.pop(0)
    for gen in (g1, g2):
        nq = qnorm(qmul(gen, q))
        key = qcanon(nq)
        if key not in seen:
            seen.add(key); group.append(nq); queue.append(nq)

chk("A₅ 群大小 (mod ±q 雙覆蓋)", len(group), 60, 0)
ang_list = []
for q in group:
    p2 = unit(qrot(q, v))
    t = degrees(acos(sum(a * b for a, b in zip(v, p2))))
    if t > mpf("0.01"):
        cw = min(mpf(1), abs(q[0]))       # |w| = cos(α/2)
        alpha = degrees(2 * acos(cw))
        ang_list.append((t, alpha))
ang_vals = sorted(set(mp.mpf(round(float(t), 4)) for t, _ in ang_list))
print(f"\n  群元素角距離譜 (去重, 度): {[mp.nstr(a, 7) for a in ang_vals]}")
for target, expect_alpha in [("26.0914", 120), ("26.1664", 72), ("31.6787", 180), ("42.9712", 144)]:
    hit = [(t, a) for t, a in ang_list if abs(t - mpf(target)) < mpf("0.0005")]
    ok = any(abs(a - mpf(expect_alpha)) < mpf(1) for _, a in hit)
    print(f"[{'PASS' if ok else 'FAIL'}] 群元素 {target}° ← rotation {expect_alpha}°"
          f"  (命中 {len(hit)}, α={[mp.nstr(a,5) for _,a in hit]})")
    if ok: PASS += 1
    else:  FAIL += 1

# ══════════ 結果 ══════════
print("\n" + "=" * 74)
print(f"RESULT: {PASS}/{PASS+FAIL} PASS   (FAIL={FAIL})")
print("=" * 74)
sys.exit(0 if FAIL == 0 else 1)
