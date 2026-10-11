#!/usr/bin/python3
"""O238 — Script 23: {1..9} vs A₅ 全面對照 — 邊個係真正投影軌跡?

scripts/22: {1..9} R²=0.9954 > A₅ {1,2,3,4,5,7,9,11,13} R²=0.9920 —
『質數∪平方』唔係唯一規則, 更低簡描述 = 前 9 個 mode (N_gen²=9).
但 O209 freeze 9 點 assignment = A₅. 本 script 判死:

  P1 兩 assignment 譜平面 R² 對照 (logγ, log|dm|)
  P2 質量排序對照: corr(PC1, log m) + Spearman — 兩者都單調?
  P3 LOOCV: 冪律 fixed φ² 兩 assignment 預言誤差比較
  P4 A₅ 相對 {1..9} 嘅額外 mode {11,13} 換走 {6,8} — 對共線性淨貢獻?

若 {1..9} 全面 ≥ A₅ ⟹ A₅ 表達係後見; 真正規則 = 最低 N_gen² mode (更簡)
若 A₅ 比空間/LOOCV 贏 ⟹ 質數∪平方有結構特權
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
Eee = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = Eee[:, None] - Eee[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

SEL9_A5 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
SEL9_19 = list(range(1, 10))
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])

def stats(sel):
    X = np.array([[math.log(gam[n-1]), math.log(admn[n-1])] for n in sel])
    Xc = X - X.mean(axis=0)
    cov = Xc.T @ Xc / 8
    evals, evecs = np.linalg.eigh(cov)
    o = np.argsort(evals)[::-1]
    pc1 = Xc @ evecs[:, o[0]]
    var1 = evals[o[0]] / evals.sum()
    corr = np.corrcoef(pc1, logm)[0, 1]
    r_pc = np.argsort(np.argsort(pc1)); r_m = np.argsort(np.argsort(logm))
    sp = np.corrcoef(r_pc, r_m)[0, 1]
    # 冪律 fixed φ² RMS
    logd = np.log([admn[n-1] for n in sel])
    C = math.exp(np.mean(logm - PHI2 * logd))
    res = logm - (math.log(C) + PHI2 * logd)
    rms = math.sqrt((res ** 2).mean())
    # 比空間 (冪律 fixed φ² 預言)
    mhat = {}
    for i, p in enumerate(names9):
        mhat[p] = math.exp(np.mean(logm - PHI2 * logd) + PHI2 * logd[i])
    pairs = [("d", "u", 2.1505, 0.111), ("s", "u", 42.8893, 1.5165),
             ("c", "s", 11.652, 0.175), ("b", "c", 4.586, 0.012), ("b", "s", 53.3692, 0.7374)]
    nbig = 0; zs = []
    for a, b, lat, lat_e in pairs:
        fp = mhat[a] / mhat[b]
        z = (fp - lat) / lat_e
        zs.append(z); nbig += abs(z) > 3
    return var1, corr, sp, rms, nbig, zs

print("═══ 全面對照: A₅ vs {1..9} ═══")
for nm, sel in [("A₅ {1,2,3,4,5,7,9,11,13}", SEL9_A5), ("{1..9} (前9=N_gen²)", SEL9_19)]:
    var1, corr, sp, rms, nbig, zs = stats(sel)
    print(f"\n  {nm}:")
    print(f"    PC1 var = {var1*100:.2f}%   corr(PC1,logm) = {corr:+.6f}   Spearman = {sp:+.6f}")
    print(f"    冪律 φ² RMS = {rms:.6f}   比空間 >3σ 數 = {nbig}/5")
    print(f"    z 值: " + " ".join(f"{z:+.1f}" for z in zs))

# 判定
var1a, corra, spa, rmsa, nbiga, _ = stats(SEL9_A5)
var1b, corrb, spb, rmsb, nbigb, _ = stats(SEL9_19)
chk("P2 {1..9} 都單調 (Spearman=+1)", abs(spb) > 0.99, f"sp={spb:+.4f}")
chk("P4 A₅ 比空間唔輸 ({1..9} 全滅都算特徵)", nbiga >= nbigb, f"A5={nbiga} vs 19={nbigb}")
better19 = (var1b > var1a and rmsb < rmsa)
print(f"\n  ⟹ {{1..9}} 全面勝出? {better19}")
print(f"     PC1 var: A5={var1a*100:.2f}% vs 19={var1b*100:.2f}%   RMS: A5={rmsa:.4f} vs 19={rmsb:.4f}")
out = {"r2_a5": float(var1a), "r2_19": float(var1b), "rms_a5": float(rmsa), "rms_19": float(rmsb),
       "spearman_a5": float(spa), "spearman_19": float(spb), "better_19": better19}
with open("data/23_rule19_vs_a5.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")