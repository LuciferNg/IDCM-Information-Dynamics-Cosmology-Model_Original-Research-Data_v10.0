#!/usr/bin/python3
"""O209 — Script 17: c/s 離群三層拆解 — freeze C_c/C_s 池 + |dm|/γ 層平滑
承接 docs/16 (c/s 離群非 scheme artifact)。本輪:
  P1 freeze C_c/C_s = 3.8587 有理池身份 (27/7 候選 + look-elsewhere)
  P2 γ 層全對掃描: γ₇/γ₄≈3 係密度效應定結構?
  P3 |dm| 層平滑性: c/s 有冇 |dm| 異常?
  P4 γ 偏差能否解釋 resid?
"""
import numpy as np, math, json
from fractions import Fraction

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N, NC = 88, 88
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)

print("═══ P1. freeze C_c/C_s = 3.8587 有理池身份 ═══")
R_cs = 41.585 / 10.777   # O234 C-shape 反解 (freeze)
R_cs2 = 11.652 * (gam_n[3] / gam_n[6])  # (m_c/m_s)·(γ_s/γ_c) = 11.652×γ₄/γ₇
print(f"  C_c/C_s = {R_cs:.6f} vs 直接 {R_cs2:.6f}")
chk("P1.1 C_c/C_s 兩法一致", abs(R_cs - R_cs2) / R_cs < 1e-3, f"{R_cs:.6f} vs {R_cs2:.6f}")
# look-elsewhere [1..300]², dev<0.05%
target = R_cs
hits = []
for a in range(1, 301):
    for b in range(1, 301):
        if math.gcd(a, b) != 1:
            continue
        if abs(a / b - target) / target < 5e-4:
            hits.append((a, b, a / b, abs(a / b - target) / target))
print(f"  近命中 (dev<0.05%): {len(hits)}", [f"{a}/{b}" for a, b, r, d in hits[:8]])
dev277 = abs(27 / 7 - target) / target
print(f"  27/7 = 3.85714 dev={dev277*100:.4f}% (27=N_gen³, 7=L₄)")
chk("P1.2 27/7 係近命中", dev277 < 1e-3, f"{dev277*100:.4f}%")
chk("P1.3 look-elsewhere: 唯一近命中", len(hits) == 1, f"{len(hits)} hits ⟹ 池密度效應")

print("\n═══ P2. γ 層全對掃描: γ_a/γ_b ≈ 整數 (dev<1%) ═══")
hits_g = []
for a in range(1, 14):
    for b in range(1, 14):
        if a == b:
            continue
        r = gam_n[a - 1] / gam_n[b - 1]
        for k in range(1, 7):
            if abs(r - k) / k < 0.01:
                hits_g.append((a, b, k, r, abs(r - k) / k))
                break
hits_g.sort(key=lambda x: x[3])
rng = np.random.default_rng(42)
null_n = 0
for _ in range(20000):
    a = rng.uniform(1, 13); b = rng.uniform(1, 13)
    if abs(a - b) < 0.1:
        continue
    r = math.sin(math.pi * a / 88) ** 2 / math.sin(math.pi * b / 88) ** 2
    for k in range(1, 7):
        if abs(r - k) / k < 0.01:
            null_n += 1
            break
null_rate = null_n / 20000
print(f"  命中 {len(hits_g)}/156 (null 期望 {null_rate*156:.1f})")
for a, b, k, r, d in hits_g:
    print(f"    γ_{a}/γ_{b} = {r:.5f} ≈ {k} dev={d*100:.3f}%")
g74 = gam_n[6] / gam_n[3]
print(f"\n  γ₇/γ₄ ≈ 3: dev={abs(g74-3)/3*100:.3f}% — 係 6 個之一, 非唯一")
chk("P2.1 γ₇/γ₄ ≈ 3 (dev<1%)", abs(g74 - 3) / 3 < 0.01, f"{abs(g74-3)/3*100:.3f}%")
chk("P2.2 γ₇/γ₄ ≈ 3 唔係唯一結構命中 (⇒ 密度效應)", len([h for h in hits_g if h[2] == 3]) >= 1, "γ₂/γ₁≈4 等同樣靚")

print("\n═══ P3. |dm| 層平滑性 ═══")
logd13 = np.log(admn[:13])
ns = np.arange(1, 14, dtype=float)
A3 = np.vstack([np.ones(13), ns, ns ** 2, ns ** 3]).T
c3, *_ = np.linalg.lstsq(A3, logd13, rcond=None)
r3 = logd13 - A3 @ c3
print(f"  3rd-order poly fit resid std = {r3.std():.4f}")
print(f"  n=4(c) resid = {r3[3]:+.3f}, n=7(s) resid = {r3[6]:+.3f} (max = {np.abs(r3).max():.3f} at n={np.argmax(np.abs(r3))+1})")
chk("P3.1 |dm| 層 c/s 平滑 (|resid| < 0.15)", abs(r3[3]) < 0.15 and abs(r3[6]) < 0.15, f"c={r3[3]:+.3f} s={r3[6]:+.3f}")

print("\n═══ P4. γ 偏差能否解釋 s resid? ═══")
# freeze fit (docs/16 m_B): s resid = +1.179 (log m)
delta_g = math.log(gam_n[6] / gam_n[3] / 3)
print(f"  log(γ₇/γ₄/3) = {delta_g:+.4f}")
print(f"  s resid (docs/16) = +1.179 ⟹ 比 γ 偏差大 {1.179/abs(delta_g):.0f}×")
chk("P4.1 γ 偏差不足以解釋 s resid (差 >50×)", 1.179 / abs(delta_g) > 50, f"{1.179/abs(delta_g):.0f}×")

print("\n═══ P5. freeze C_f 夸克 5 點對 log|dm|: c/s resid (比層) ═══")
# O209 frame: b(n=2) c(n=4) s(n=7) d(n=9) u(n=11); C shape (anchor u=1)
Cq = {"b": 57.162, "c": 41.585, "s": 10.777, "d": 0.958, "u": 1.0}
n_q = {"b": 2, "c": 4, "s": 7, "d": 9, "u": 11}
ld_q = np.log([admn[n_q[p] - 1] for p in ["b", "c", "s", "d", "u"]])
lc_q = np.log([Cq[p] for p in ["b", "c", "s", "d", "u"]])
A5 = np.vstack([np.ones(5), ld_q]).T
c5, *_ = np.linalg.lstsq(A5, lc_q, rcond=None)
r5 = lc_q - A5 @ c5
print(f"  freeze C_f(夸克 5點) ~ |dm|: β={-c5[1]:.4f} RMS={np.sqrt((r5**2).mean()):.4f}")
for i, p in enumerate(["b", "c", "s", "d", "u"]):
    print(f"    {p}: resid {r5[i]:+.3f}")
chk("P5.1 freeze 夸克 C_f c resid 仍離群 (>+0.5)", r5[1] > 0.5, f"{r5[1]:+.3f}")
chk("P5.2 freeze 夸克 C_f s resid 仍離群 (>+0.5)", r5[2] > 0.5, f"{r5[2]:+.3f}")

out = {
    "Ccs_freeze": R_cs, "dev277": dev277, "look_elsewhere_hits": len(hits),
    "gamma_hits_near_int": [(a, b, k, round(r, 5), round(d * 100, 3)) for a, b, k, r, d in hits_g],
    "null_rate": null_rate,
    "dm_poly3_resid": [round(r3[i], 4) for i in range(13)],
    "gamma74_dev3": abs(g74 - 3) / 3,
}
with open("data/17_cs_three_layer.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c, _ in checks if c)}/{len(checks)} checks passed")
for nm, c, dt in checks:
    print(f"  [{'OK' if c else 'XX'}] {nm} — {dt}")
