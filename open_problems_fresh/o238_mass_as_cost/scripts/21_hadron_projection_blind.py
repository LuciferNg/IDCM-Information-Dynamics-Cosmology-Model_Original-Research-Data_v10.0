#!/usr/bin/python3
"""O238 — Script 21: 複合態投影盲測 — 強子質量 vs 全譜冪律預言

調律者原話: 「要精確測量時用高能碰撞就投影為夸克/中子/質子」— 即核子/強子
都係投影讀數. O238 一直只測基本費米子 9 點. 本 script 盲測:

  m_n = C · |dm|_n^{φ²}  (C 由 9 點 fit, 零新參數; S2 freeze v2 C=1.52151e-6)
  對 17 個強子質量: 88 個 mode 全掃 — 有冇 mode 命中 (<10%)?

  P1 全譜預言 m_n 對照強子: 最近 mode + 偏差
  P2 池密度: 88 mode × 17 強子 = 1496 比較, <10% 命中預期 ≈ 150 個
     — 命中必須 >> 池密度先算數
  P3 若命中 mode 集中某區 — pattern? 否則負結果: 複合態唔喺冪律層
  P4 特別: 質子 (938.27) 最近 mode 偏差 (O144 候選 A/B ~1%: 本盲測零參數)
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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
C = 1.52151e-6  # S2 freeze v2 (docs/04)

hadrons = {
    "pi0": 134.9768, "pi+": 139.57039, "eta": 547.862, "K+": 493.677,
    "K0": 497.611, "eta'": 957.78, "p": 938.272088, "n": 939.565421,
    "Lambda": 1115.683, "Sigma+": 1189.37, "Xi0": 1314.86, "Omega": 1672.45,
    "D0": 1864.84, "D+": 1869.66, "B+": 5279.32, "B0": 5279.63,
    "J/psi": 3096.9, "Upsilon": 9460.30}
# 只保留 PDG 主要 17 個 (去 Omega 重複)
hadrons.pop("Omega", None)

m_pred = np.array([C * admn[i] ** PHI2 for i in range(N)])
max_dm = admn.max(); max_pred = C * max_dm ** PHI2
print(f"全譜預言質量範圍: {m_pred.min():.4f} MeV (n=argmin) — {max_pred:.1f} MeV (n=44)")
print(f"88-chain |dm| max = {max_dm:.2f} (mode 44); Upsilon 9460 > max_pred={max_pred:.1f}? "
      f"{'超範圍' if 9460 > max_pred else '在範圍'}")

print("\n═══ P1. 強子 vs 全譜冪律預言 ═══")
hits10 = 0; hits5 = 0
for name, m_obs in sorted(hadrons.items(), key=lambda kv: kv[1]):
    devs = np.abs(m_pred - m_obs) / m_obs
    best = np.argmin(devs)
    print(f"  {name:>6s} {m_obs:10.3f}: best mode n={best+1:2d} pred={m_pred[best]:10.3f} dev={devs[best]*100:7.2f}%"
          + ("  <10%!!" if devs[best] < 0.10 else ""))
    hits10 += devs[best] < 0.10
    hits5 += devs[best] < 0.05
n_comp = len(hadrons) * N
expected10 = n_comp * (0.10 * 2)  # 對稱窗口 ±10% 唔夾 log 域; 粗略: 10% 帶寬 / 範圍
# 更準: log 域帶寬
log_range = math.log(max_pred / m_pred.min())
frac10 = math.log(1.10 / 0.90) / log_range  # log 帶寬比例
expected10_exact = n_comp * frac10
print(f"\n  <10% 命中: {hits10}/{len(hadrons)} 粒子, <5%: {hits5}/{len(hadrons)}")
print(f"  池密度: {n_comp} 比較, log-帶寬比例 {frac10:.4f} ⟹ 預期 <10% 命中 ≈ {expected10_exact:.1f}")
chk("P1.1 命中數 >> 池密度 (至少 3×)", hits10 > 3 * expected10_exact,
    f"hits={hits10} vs expected={expected10_exact:.1f}")

print("\n═══ P2. 命中 mode 分佈 ═══")
hit_modes = []
for name, m_obs in hadrons.items():
    devs = np.abs(m_pred - m_obs) / m_obs
    best = np.argmin(devs)
    if devs[best] < 0.10:
        hit_modes.append((name, best+1, devs[best]))
for nm, mode, dv in sorted(hit_modes, key=lambda x: x[1]):
    print(f"  {nm:>6s}: mode {mode:2d}  dev={dv*100:.2f}%")
if hit_modes:
    modes = [m for _, m, _ in hit_modes]
    print(f"  modes: {sorted(modes)}  range {min(modes)}-{max(modes)}")
print("  (若命中分散 88 區 — 池效應; 若集中低區 — 連續層低 mode 描述強子?)")

print("\n═══ P3. 質子專檢 ═══")
for nm_ in ["p", "n", "pi+", "K+"]:
    m_obs = hadrons[nm_]
    devs = np.abs(m_pred - m_obs) / m_obs
    best = int(np.argmin(devs))
    print(f"  {nm_:>3s}: best n={best+1}, pred={m_pred[best]:.2f}, dev={devs[best]*100:.2f}%")
mp_dev = np.abs(m_pred[np.argmin(np.abs(m_pred-938.272088))] - 938.272088)/938.272088
print(f"  (O144 候選 A/B 偏差 1.10%/0.61% — 本盲測鎖 C 後最近 = {mp_dev*100:.2f}%)")

out = {"hits10": int(hits10), "hits5": int(hits5), "expected10": float(expected10_exact),
       "best_mode_per_hadron": {k: int(np.argmin(np.abs(m_pred - v))) + 1 for k, v in hadrons.items()}}
with open("data/21_hadron_projection_blind.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")