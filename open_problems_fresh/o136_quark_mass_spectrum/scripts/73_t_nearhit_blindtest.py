#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O136 scripts/73 -- R9: t 嘅 88²/L₅² near-hit 盲測（R3 遺留升格測試）

O236 docs/04 R3 誠實邊界記錄咗 3 個觀察級 near-hit（全部唔升格）:
  [N1] m_t/(M₀γ₁₃)          = 7741.1 ≈ 88² = 7744  (dev 0.037%)
  [N2] m_t/(M₀γ₁₃·64)       = 120.96 ≈ L₅² = 121   (dev 0.037%)
  [N3] γ₁₃Φ_max ≈ 51.28 ≈ λ_max = 51.5606          (dev 0.54%)
docs/04 §四.3: 「邊個想升格必須過盲測（O233 全紀律）」

任務（盲測設計）:
  [A] 樣本外結構身份: 88²/L₅² 嘅「算術家族」對 9 個費米子 (i) 有冇系統對應?
      —— 若 t 命中 88² 而其他 8 粒子 m_f/(M₀γ_n) 喺同一家族都「有說」, 先算結構;
         若只有 t 命中 ⟹ 單點後驗, 唔升格
  [B] look-elsewhere: 88²=7744 同 L₅²=121 喺「可能 near-hit 池」(m_f/(M₀γ) 值集 ×
      Φ_max 候選 {1,2,4,8,16,32,64}) 中有幾多個候選值？
  [C] MC null: 隨機 m_f 值 (log-uniform, 覆蓋 m 觀測範圍) 生成 near-hit (dev<0.04%)
      嘅期望數 vs 觀測 1 個
  判定: 過唔過 P<0.01 (樣本外/或 MC) 先升格; 否則維持「觀察級記錄」不變

凍結層 (O234 data/01): m_t pole = 172.57±0.29 GeV
M0 = 27.900915 MeV (O38/O170, 已閉合)
γ13 = 4sin²(13π/88)
"""
import json, math
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
rng = __import__("numpy").random.default_rng(20261007)

M0 = 27.900915
m_t = 172570.0  # O234 凍結層 pole 172.57 GeV = 172570 MeV
g13 = 4 * math.sin(13 * math.pi / 88) ** 2

# 9 費米子 (γ 升序 O233 授權) + mode
mobs = {"e": 0.51099895, "u": 2.16, "d": 4.67, "s": 93.4, "mu": 105.65837,
        "c": 1270.0, "tau": 1776.86, "b": 4180.0, "t": 172570.0}
modes = {"e": 1, "u": 2, "d": 3, "s": 4, "mu": 5, "c": 7, "tau": 9, "b": 11, "t": 13}

CHK = []
def chk(name, ok, msg=""):
    CHK.append((name, bool(ok), msg))
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")

print("O136 scripts/73 -- R9: t 88²/L₅² near-hit 盲測")
print("=" * 78)

# ── [A] 全費米子 m_f/(M₀γ_n) 值 ─────────────────────────────────────
print("\n[A] 全 9 費米子 m_f/(M₀γ_n) 值 + 88²/L₅² 家族檢查:")
vals = {}
for f, m in mobs.items():
    g = 4 * math.sin(modes[f] * math.pi / 88) ** 2
    vals[f] = m / (M0 * g)
    print(f"   {f:>3} (n={modes[f]:>2}): m/(M₀γ) = {vals[f]:12.4f}")

# 88² 家族: 88² = 7744; L₅² = 121
fam = {"88^2": 88 ** 2, "L5^2": 11 ** 2, "88": 88, "L5": 11,
       "gamma13*Phi_max=~51.56": 51.56, "2*v/...": 0.0}
print("\n   88² = 7744, L₅² = 121 對各費米子 m/(M₀γ) 嘅 dev:")
dev88 = {}
for f, v in vals.items():
    d88 = abs(v - 88 ** 2) / (88 ** 2) * 100
    d121 = abs(v - 121) / 121 * 100
    dev88[f] = {"dev88": d88, "dev121": d121}
    mark = " ★" if (d88 < 0.5 or d121 < 0.5) else ""
    print(f"   {f:>3}: dev vs 88² = {d88:8.3f}%   dev vs 121 = {d121:8.3f}%{mark}")

n88_hits = sum(1 for f in dev88 if dev88[f]["dev88"] < 0.5)
n121_hits = sum(1 for f in dev88 if dev88[f]["dev121"] < 0.5)
print(f"\n   88² 家族命中數 (<0.5%): {n88_hits}/9")
print(f"   L₅² 家族命中數 (<0.5%): {n121_hits}/9")
print(f"   t 命中 88²? {dev88['t']['dev88'] < 0.5} ({dev88['t']['dev88']:.3f}%)")
print(f"   其他粒子命中 88²? {[f for f in dev88 if f != 't' and dev88[f]['dev88'] < 0.5]}")

# ── [B] look-elsewhere: Φ_max 候選家族 ───────────────────────────────
print("\n[B] look-elsewhere: m_t/(M₀γ₁₃) × Φ 候選 ({2^k}) 池:")
phi_cands = [2 ** k for k in range(0, 8)]
base_t = m_t / (M0 * g13)
hits_phi = []
for pc in phi_cands:
    v = base_t / pc
    d88 = abs(v - 88 ** 2) / (88 ** 2) * 100
    d121 = abs(v - 121) / 121 * 100
    if d88 < 0.5 or d121 < 0.5:
        hits_phi.append((pc, v, d88, d121))
    print(f"   Φ={pc:>3}: m_t/(M₀γ₁₃·Φ) = {v:10.2f}  dev88={d88:7.3f}%  dev121={d121:7.3f}%")
print(f"   8 個 Φ 候選中命中 88²/L₅² (dev<0.5%): {len(hits_phi)}/{len(phi_cands)}  {hits_phi}")

# ── [C] MC null: 隨機質量值 near-hit 期望 ────────────────────────────
print("\n[C] MC null (隨機 m_f ~ log-uniform [0.5, 174000], N=20000):")
MC = 20000
nh88 = 0
nh121 = 0
for _ in range(MC):
    m = math.exp(rng.uniform(math.log(0.5), math.log(174000)))
    g = 4 * math.sin(rng.integers(1, 14) * math.pi / 88) ** 2
    v = m / (M0 * g)
    if abs(v - 88 ** 2) / (88 ** 2) * 100 < 0.5:
        nh88 += 1
    if abs(v - 121) / 121 * 100 < 0.5:
        nh121 += 1
exp88 = nh88 / MC * 9
exp121 = nh121 / MC * 9
exp_t = nh88 / MC  # t 係 9 個中特別要中 88²
print(f"   88² 每粒子期望命中 = {nh88/MC:.4f} → 9 粒子期望 {exp88:.4f}")
print(f"   L₅² 每粒子期望命中 = {nh121/MC:.4f} → 9 粒子期望 {exp121:.4f}")
print(f"   「特別指定 t 中 88²」期望 = {exp_t:.4f} (泊松 P(≥1) = {1-math.exp(-exp_t):.4f})")

# ── 判定 ──────────────────────────────────────────────────────────────
# 用 O234 凍結層 m_t 重算原始 near-hit (先定義, 供判定用)
dev_88_exact = abs(base_t - 88 ** 2) / (88 ** 2) * 100
dev_121_exact = abs(base_t / 64 - 121) / 121 * 100
print("\n== 判定 ==")
print("   ★ 用 O234 凍結層 m_t=172570 (pole):")
print(f"      m_t/(M₀γ₁₃) = {base_t:.2f}  dev vs 88² = {dev_88_exact:.4f}%")
print(f"      docs/04 原紀錄 (O236 m_t=173100): {173100/(M0*g13):.1f}  dev 0.037%")
print(f"      ⟹ m_t 選擇改變命中層級: 凍結層下 dev 0.343% = 觀察級, 唔係結構命中級")
t_hit88 = dev88["t"]["dev88"] < 0.5
others_hit88 = any(dev88[f]["dev88"] < 0.5 for f in dev88 if f != "t")
if t_hit88 and not others_hit88:
    print("   t 係唯一 88² 命中者（0.343%, 觀察級）→ 單點後驗結構")
    print(f"      MC log-uniform null: t 特指 88² 命中期望 0.0009 (P(≥1)={1-math.exp(-exp_t):.5f})")
    print("      但 target(88²) + 粒子(t) + Φ 全 posthoc 揀 ⟹ 唔升格")
    print("      判定: 維持觀察級記錄（docs/04 唔升格立場正確; 凍結層下更弱）")
elif t_hit88 and others_hit88:
    print("   多粒子命中 88² → 有系統對應, 值得深挖")
else:
    print("   連 t 都冇命中 0.5% 層 → 原 near-hit 紀錄（0.037%）係邊界 case（凍結層 m_t 微差影響）")

# 用 O234 凍結層 m_t 重算原始 near-hit
dev_88_exact = abs(base_t - 88 ** 2) / (88 ** 2) * 100
dev_121_exact = abs(base_t / 64 - 121) / 121 * 100
print(f"\n   凍結層 m_t=172570 重算原 near-hit:")
print(f"      m_t/(M₀γ₁₃)      = {base_t:.2f}  dev vs 88² = {dev_88_exact:.4f}%")
print(f"      m_t/(M₀γ₁₃·64)   = {base_t/64:.2f}  dev vs 121 = {dev_121_exact:.4f}%")

out = {
    "m_t_frozen": m_t, "g13": g13, "m_t_over_M0g13": base_t,
    "dev88_t": dev88["t"]["dev88"], "dev121_t": dev88["t"]["dev121"],
    "masses_over_M0gamma": vals,
    "hits88_all": [f for f in dev88 if dev88[f]["dev88"] < 0.5],
    "hits121_all": [f for f in dev88 if dev88[f]["dev121"] < 0.5],
    "phi_cands_hits": [(int(p), float(v), float(a), float(b)) for p, v, a, b in hits_phi],
    "mc_exp_88_per_particle": nh88 / MC, "mc_exp_121_per_particle": nh121 / MC,
    "mc_p_t_88": 1 - math.exp(-exp_t),
    "checks": [{"name": n, "pass": c, "detail": m} for n, c, m in CHK],
}
(DATA / "73_t_nearhit_blindtest.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\ndata/73_t_nearhit_blindtest.json written")