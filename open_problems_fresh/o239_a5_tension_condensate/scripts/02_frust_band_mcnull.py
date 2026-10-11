#!/usr/bin/python3
"""O239 — Script 02: 挫阻距離場離散帶 MC null（scripts/01 觀察 → 可證偽預言）
============================================================================
scripts/01 觀察（非 target-fit）: 88 節點 → 最近挫阻中點距離 d_i 形成 6 條極窄帶
  13.306°×40 / 16.107°×20 / 21.674°×12 / 24.395°×10 / 26.048°×2 / 29.353°×4
  unique count (1e-6) = 45; MC 隨機 88 點 = 88.0（全 unique, 連續）。
  簡併度 {40,20,12,10,2,4} 懷疑同 A₅ 面型結構（20△+12⬠=32 阻挫）有關。

本 script 將觀察提升為預註冊預言，用 MC null 檢定:
  D1 離散度: 觀察 unique count(45) ≪ MC 隨機 88 點 unique count 嘅 0.5th percentile
     ⟹ 距離場離散（唔係連續）—— 有結構
  D2 帶數: 觀察帶數(用 0.01° 容差) ≤ 6, MC 帶數 ≥ 60（隨機 88 點 → 32 挫阻幾乎全 unique）
  D3 簡併度: 最大帶簡併度 ≥ 40（MC 最大帶簡併度 ~26 期望? 唔好估 —— 用 MC 分佈嘅
     99.5th percentile 對照, obs > MC99.5 先算結構）
  D4 對照-隨機挫阻: 用 MC 隨機 32 點取代真 32 挫阻, 距離場 unique count ≈ 88
     （確認離散帶係「真挫阻子格特有」, 唔係「任何 32 點都有」）
  D5 對照-隨機節點: 用 MC 隨機 88 點 vs 真 32 挫阻, unique count ≈ 88
     （確認離散帶源於真 88 節點, 唔係單靠 32 挫阻規則）
  D6 簡併度 vs 面型: 頂三帶簡併度 {40,20,12} 同 A₅ 面型 {20△, 30□, 12⬠} 嘅交集
     {20, 12} 出現 —— 只記錄關係, 唔宣稱機制（帶簡併度 xN 可以係對稱性產物）

盲測紀律: D1-D5 判據跑前凍結; D6 只記錄。MC seed 固定可重現。
"""
import json, math
import numpy as np
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "o182_88grid_geometry/data"
rng = np.random.default_rng(20261012)
N_MC = 5000

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

def sph(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def uniform_sphere(k, rng):
    z = rng.uniform(-1, 1, k)
    phi = rng.uniform(0, 2*np.pi, k)
    r = np.sqrt(1 - z*z)
    return np.column_stack([r*np.cos(phi), r*np.sin(phi), z])

nodes = np.loadtxt(DATA / "g88_nodes.txt")
frust = np.loadtxt(DATA / "g32_frustration_midpoints.txt")
Vn = sph(nodes[:, 0], nodes[:, 1])
Vf = sph(frust[:, 0], frust[:, 1])

def dist_field(A, B):
    """A (N,3) -> min distance to B (M,3), degrees"""
    return np.degrees(np.arccos(np.clip(A @ B.T, -1, 1))).min(axis=1)

def bands(v, tol=0.01):
    """group by rounded tol; return (band_count, max_band_deg, sorted bands)"""
    import collections
    c = collections.Counter(np.round(v, 2).tolist())
    return len(c), max(c.values()), sorted(c.items())

# ── 觀察 ──
d_obs = dist_field(Vn, Vf)
uc_obs = len(set(np.round(d_obs, 6).tolist()))
nb_obs, mb_obs, _ = bands(d_obs)

print("="*78)
print("O239 scripts/02 — 挫阻距離場離散帶 MC null")
print("="*78)
print(f"\n觀察: unique(d_i;1e-6) = {uc_obs}, 帶數(0.01°) = {nb_obs}, 最大帶簡併 = {mb_obs}")
print(f"     帶: {dict(sorted(bands(d_obs)[2]))}")

# ── MC 1: 隨機 88 點 → 真 32 挫阻（離散度 null）──
mc_uc = np.empty(N_MC)
mc_nb = np.empty(N_MC)
mc_mb = np.empty(N_MC)
for i in range(N_MC):
    R = uniform_sphere(88, rng)
    d = dist_field(R, Vf)
    mc_uc[i] = len(set(np.round(d, 6).tolist()))
    nb, mb, _ = bands(d)
    mc_nb[i] = nb; mc_mb[i] = mb

uc_lo = np.percentile(mc_uc, 0.5)
nb_lo = np.percentile(mc_nb, 0.5)
mb_hi = np.percentile(mc_mb, 99.5)
print(f"\nMC1 隨機88點→真32挫阻 (n={N_MC}):")
print(f"  unique: mean={mc_uc.mean():.1f} 0.5th={uc_lo:.1f}   obs={uc_obs}")
print(f"  帶數:   mean={mc_nb.mean():.1f} 0.5th={nb_lo:.1f}   obs={nb_obs}")
print(f"  最大帶: mean={mc_mb.mean():.1f} 99.5th={mb_hi:.1f}   obs={mb_obs}")

# ── MC 2: 真 88 節點 → 隨機 32 點（源頭對照）──
mc2_uc = np.empty(N_MC)
for i in range(N_MC):
    F = uniform_sphere(32, rng)
    mc2_uc[i] = len(set(np.round(dist_field(Vn, F), 6).tolist()))
print(f"\nMC2 真88節點→隨機32點: unique mean={mc2_uc.mean():.1f} 0.5th={np.percentile(mc2_uc,0.5):.1f}  obs={uc_obs}")

# ── MC 3: 隨機 88 點 → 隨機 32 點（雙隨機對照）──
mc3_uc = np.empty(N_MC)
for i in range(N_MC):
    R = uniform_sphere(88, rng)
    F = uniform_sphere(32, rng)
    mc3_uc[i] = len(set(np.round(dist_field(R, F), 6).tolist()))
print(f"MC3 雙隨機: unique mean={mc3_uc.mean():.1f} 0.5th={np.percentile(mc3_uc,0.5):.1f}  obs={uc_obs}")

print("\n── 預註冊判據 ──")
chk("D1 離散度: obs unique ≪ MC1 0.5th（距離場離散 ≠ 連續）",
    uc_obs < uc_lo, f"obs={uc_obs} vs MC1 0.5th={uc_lo:.0f}")
chk("D2 帶數: obs 帶數 ≤ 6 而 MC1 0.5th ≥ 60",
    nb_obs <= 6 and nb_lo >= 60, f"obs={nb_obs} vs MC1 0.5th={nb_lo:.0f}")
chk("D3 最大帶簡併: obs > MC1 99.5th（有超密集帶）",
    mb_obs > mb_hi, f"obs={mb_obs} vs MC1 99.5th={mb_hi:.1f}")
chk("D4 真挫阻特有: obs unique < MC2 0.5th（離散源於真 32 挫阻子格）",
    uc_obs < np.percentile(mc2_uc, 0.5), f"obs={uc_obs} vs MC2 0.5th={np.percentile(mc2_uc,0.5):.1f}")
chk("D5 真節點特有: obs unique < MC3 0.5th（離散唔係單靠 32 挫阻規則, 要真 88 節點）",
    uc_obs < np.percentile(mc3_uc, 0.5), f"obs={uc_obs} vs MC3 0.5th={np.percentile(mc3_uc,0.5):.1f}")
# 簡併度對面型（只記錄）
face_ints = sorted(set([20, 12]).intersection([v for _, v in sorted(bands(d_obs)[2])]))
print(f"\n[D6 記錄] 帶簡併度 ∩ {{20△,12⬠}} = {face_ints} （只記錄, 唔宣稱機制）")

out = {
    "obs": {"unique": uc_obs, "n_bands": nb_obs, "max_band": mb_obs,
            "bands": dict(sorted(bands(d_obs)[2]))},
    "mc1_rand88_true32": {"unique_mean": float(mc_uc.mean()), "unique_0.5pct": float(uc_lo),
                           "nband_mean": float(mc_nb.mean()), "nband_0.5pct": float(nb_lo),
                           "maxband_mean": float(mc_mb.mean()), "maxband_99.5pct": float(mb_hi)},
    "mc2_true88_rand32": {"unique_mean": float(mc2_uc.mean()), "unique_0.5pct": float(np.percentile(mc2_uc, 0.5))},
    "mc3_double_random": {"unique_mean": float(mc3_uc.mean()), "unique_0.5pct": float(np.percentile(mc3_uc, 0.5))},
    "face_cross": face_ints,
    "N_MC": N_MC,
}
outfile = Path(__file__).parent.parent / "data" / "02_frust_band_mcnull.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")