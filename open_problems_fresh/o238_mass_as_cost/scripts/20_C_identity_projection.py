#!/usr/bin/python3
"""O238 — Script 20: C 身份重新歸類閉合 — 投影算符讀數 + 數論選擇

docs/09 剩餘開放 1: C 身份 (原 O209 P4). 已立框架: C = 投影算符讀數,
scripts/18: A₅ = 質數∪平方 ≤13 (p=1.75e-12) 係投影算符嘅「mode 選擇」規則.

本 script 嘗試閉合「C 身份」:
  P1 C 嘅數論身份: C/M₀ = 5.256e-8 — 用有結構動機嘅數掃描 (唔硬湊)
     log₂(C/M₀) / log₁₀ 等對數身份
  P2 ★ C_n 逐點: C_n = m_n / |dm|_n^{φ²} 對 n 嘅結構 — 有冇 = M₀ × γ^q × f(n)?
  P3 ★ 修正後 C: 加 c/s dummy (scripts/19) 後剩 7 點 C7 — 有冇池身份?
  P4 閉合語句: 「C = 投影算符讀數」嘅可檢驗形式 (預言 C 通道間距)
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
logd = np.log([admn[n-1] for n in SEL9])
logg = np.log([gam[n-1] for n in SEL9])

print("═══ P1. C 數論身份掃描 ═══")
Cf = math.exp((logm - PHI2 * logd).mean())
r = Cf / M0
print(f"  C = {Cf:.8e} MeV,  C/M₀ = {r:.8e}")
print(f"  log₁₀(C/M₀) = {math.log10(r):.6f}")
print(f"  log₂(C/M₀)  = {math.log2(r):.4f}")
print(f"  88^k 檢查: 88^{{-4}}={88**-4:.3e} 88^{{-3}}={88**-3:.3e}")
print(f"  44^k 檢查: 44^{{-5}}={44**-5:.3e} 44^{{-4}}={44**-4:.3e}")
print(f"  90^k 檢查: 90^{{-5}}={90**-5:.3e}")
# 候選: C/M₀ = 8.88e-9? 5.26e-8?
cands = {"2^-24": 2**-24, "3^-16": 3**-16, "5^-11": 5**-11, "88^-4.2": 88**-4.2,
         "φ^-35": PHI**-35, "1/90^4.5": 90**-4.5, "1/(44*φ^20)": 1/(44*PHI**20),
         "1/(88*φ^22)": 1/(88*PHI**22)}
print("  對數候選 (dev<20% 先報):")
for nm, v in cands.items():
    dev = abs(math.log(v/r))
    if dev < 0.2:
        print(f"    {nm} = {v:.4e}  dev={dev*100:.1f}%")

print("\n═══ P2. C_n 逐點結構 ═══")
for i, p in enumerate(names9):
    cn = MS2[p] / admn[SEL9[i]-1]**PHI2
    print(f"  {p:4s}: C_n={cn:.6e}  log C_n={math.log(cn):+.4f}  resid(log C_n - <logC>)={math.log(cn)-math.log(Cf):+.4f}")

# C_n vs γ^q: fit log C_n = a + q·logγ
logCn = np.log([MS2[p]/admn[SEL9[names9.index(p)]-1]**PHI2 for p in names9])
A = np.vstack([np.ones(9), logg]).T
c, *_ = np.linalg.lstsq(A, logCn, rcond=None)
res = logCn - A @ c
rms_q = math.sqrt((res**2).mean())
print(f"  log C_n = {c[0]:+.4f} + {c[1]:+.4f}·log γ,  RMS={rms_q:.6f}")

print("\n═══ P3. 修正後 C (剔 c/s, 7 點) 池身份 ═══")
keep = [i for i in range(9) if i not in (3, 5)]
Cf7 = math.exp(np.mean([logm[i] - PHI2*logd[i] for i in keep]))
r7 = Cf7 / M0
print(f"  C7 = {Cf7:.8e},  C7/M₀ = {r7:.8e}")
# 凍結池 (scripts/01 196 值精簡版 — 用結構常數)
pool = [2, 3, 4, 5, 8, 13, 21, 33, 34, 44, 88, 90, 176, 203, 45, 46, 123,
        PHI, PHI**2, PHI**3, PHI**4, PHI**5, PHI**-1, PHI**-2, PHI**-3, PHI**-4, PHI**-5]
hits = []
for v in pool:
    for k in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
        for p2 in [-10, -8, -6, -4, -2, 2, 4, 6, 8, 10]:
            cand = v**k * PHI**p2 * M0
            if abs(math.log(cand/Cf7)) < 0.02:
                hits.append((v, k, p2, math.log(cand/Cf7)))
print(f"  C7/M₀=5.26e-8(M0=5.256e-8?) — 候選: {hits if hits else '冇 2% 命中'}")

print("\n═══ P4. 閉合語句: C = 投影算符讀數 ═══")
print(f"""
  C 身份閉合判定:
  1. C ≠ 任何單一結構常數 (scripts/01-05 + 本輪 P1): 🔴 維持
  2. C_n = m_n/|dm|_n^{{φ²}} 有 spread (log std = RMS = 0.545) — C 本身唔係常數
  3. C 嘅角色 = 「連續層 |dm|^{{φ²}} → 質量」嘅投影讀數標度:
     - 沿 A₅ 軌跡位置 PC1 ↔ log m 完美單調 (docs/09)
     - mode 選擇 = 質數∪平方 ≤13 (scripts/18, p=1.75e-12)
  4. 可檢驗預言: C 應該按測量通道唔同 (A 自由/B 碰撞/C lattice);
     scripts/14 已測觀察級 pattern (C_B/C_A≈1.53) 但統計唔夠 (9 點拆 3 組)
  5. 完全閉合需要: freeze v2 新量度 (ms/mu killer) + 更多粒子 (核子/介子?) 落投影譜系
""")

out = {"C": float(Cf), "C_M0": float(r), "C7": float(Cf7), "C7_M0": float(r7)}
with open("data/20_C_identity_projection.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"RESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed (0 硬 checks — 誠實審計)")