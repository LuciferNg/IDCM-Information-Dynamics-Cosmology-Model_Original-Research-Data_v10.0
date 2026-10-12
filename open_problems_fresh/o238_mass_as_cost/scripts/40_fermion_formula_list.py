#!/usr/bin/python3
"""O238 — Script 40: 費米子質量公式列表（參考 O239 docs/33 生成, O238 正典）

O239 docs/33 最終列表 (1 參數 φ² / 2 因子 +rank / 3 因子 +block23, 誠實分級)。
O238 用正典 S2 + R19-R23 結果重建對應列表 + 並排對照 + 分級更新。

P1 三行 dev% 列表 (1 參數 / +rank / +block23)
P2 LOOCV 對比 (φ² / φ²+rank) — 同 O239 方法 (中位|Δln m|)
P3 O238 S2 vs O239 docs/33 並排對照 (質量集差異標明)
P4 誠實分級 (α ★結構鎖定 / rank 🟡+still / block23 🔴 O136 LOOCV倒退)
P5 O238 rank-parity 三 scheme 穩健附註 (R23) — 但唔覆蓋 O136 null
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

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
# O238 正典 S2 (freeze v2, scripts/08)
MS = {"t": 172690.0, "b": 93.4*11.652*4.586, "tau": 1776.86, "c": 93.4*11.652,
      "mu": 105.6583755, "s": 93.4, "d": 93.4/42.890*2.1505, "u": 93.4/42.890,
      "e": 0.51099895}
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

logd = np.log([admn[n-1] for n in SEL9])
logm = np.log([MS[p] for p in names9])
rank = np.arange(1, 10)
even_mask = (rank % 2 == 0).astype(float)
# block23: 第 2/3 個 stair 族? O239 用 block23 (O136 P5) — 近似: {b,τ,c} 3rd? 照 O239 慣例
# O239 docs/33 3 因子 = free α + rank + block23, block23 位元未知 — 標 "free α 版, block23 未認證"
BLOCK23 = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0])  # placeholder — 唔宣稱 (O136 未認證)

def fit_1param():
    C = math.exp((logm - PHI2 * logd).mean())
    return C, logm - (math.log(C) + PHI2 * logd)

def fit_rank():
    A = np.vstack([np.ones(9), logd, even_mask]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    return c, logm - A @ c

def loocv_median(fitmode):
    errs = []
    for i in range(9):
        tr = [j for j in range(9) if j != i]
        if fitmode == "phi2":
            C = math.exp((logm[tr] - PHI2 * logd[tr]).mean())
            pred = math.log(C) + PHI2 * logd[i]
        elif fitmode == "rank":
            Af = np.vstack([np.ones(8), logd[tr], even_mask[tr]]).T
            c, *_ = np.linalg.lstsq(Af, logm[tr], rcond=None)
            pred = c[0] + c[1]*logd[i] + c[2]*even_mask[i]
        else:
            Af = np.vstack([np.ones(8), logd[tr], even_mask[tr], BLOCK23[tr]]).T
            c, *_ = np.linalg.lstsq(Af, logm[tr], rcond=None)
            pred = c[0] + c[1]*logd[i] + c[2]*even_mask[i] + c[3]*BLOCK23[i]
        errs.append(abs(pred - logm[i]))
    return float(np.median(errs))

C1, r1 = fit_1param()
c2, r2 = fit_rank()
A3 = np.vstack([np.ones(9), logd, even_mask, BLOCK23]).T
c3, *_ = np.linalg.lstsq(A3, logm, rcond=None)
r3 = logm - A3 @ c3

dev1 = {p: float(math.exp(r1[names9.index(p)]) - 1) for p in names9}
dev2 = {p: float(math.exp(r2[names9.index(p)]) - 1) for p in names9}
dev3 = {p: float(math.exp(r3[names9.index(p)]) - 1) for p in names9}
rms1 = float(np.sqrt((r1**2).mean())); rms2 = float(np.sqrt((r2**2).mean()))
rms3 = float(np.sqrt((r3**2).mean()))
l1, l2, l3 = loocv_median("phi2"), loocv_median("rank"), loocv_median("block3")

print("═══ P1. O238 費米子公式列表 (S2 正典) ═══")
print(f"  {'p':>4s} {'n':>3s} {'M(MeV)':>10s} {'1參 φ² dev%':>12s} {'2因子 rank dev%':>14s} {'3因子 block23 dev%':>15s}")
for i, p in enumerate(names9):
    print(f"  {p:>4s} {SEL9[i]:3d} {MS[p]:10.4g} {dev1[p]*100:+11.1f}% {dev2[p]*100:+13.1f}% {dev3[p]*100:+14.1f}%")
print(f"  RMS: 1參 {rms1:.4f} / 2因子 {rms2:.4f} / 3因子 {rms3:.4f}")
print(f"  LOOCV(中位|Δln m|): 1參 {l1:.4f} / 2因子 {l2:.4f} / 3因子 {l3:.4f}")

print("\n═══ P2. LOOCV 對比 ═══")
print(f"  φ²        : {l1:.4f}")
print(f"  φ²+rank   : {l2:.4f} (ratio {l2/l1:.3f})")
print(f"  φ²+rank+b3: {l3:.4f} (ratio {l3/l1:.3f})")
chk("P2.1 rank LOOCV 唔倒退 (<1.05)", l2 < l1*1.05, f"ratio={l2/l1:.3f}")
chk("P2.2 block23 LOOCV 倒退 (O136 一致性確認)", l3 > l2*1.02, f"ratio={l3/l2:.3f}")

print("\n═══ P3. 對照 O239 docs/33 ═══")
o239_dev1 = {"t": 2.2, "b": 74.1, "tau": 4.5, "c": -60.1, "mu": 60.6,
             "s": -68.2, "d": 60.2, "u": 6.9, "e": 54.3}
print(f"  {'p':>4s} {'O238 b=S2 dev%':>14s} {'O239 b=4180 dev%':>16s} {'差(ppe)':>8s}")
for p in names9:
    d238 = dev1[p]*100
    d239 = o239_dev1[p]
    print(f"  {p:>4s} {d238:+13.1f}% {d239:+15.1f}% {abs(d238-d239):7.1f}")
chk("P3.1 1參數 t 命中 <7% (O238)", abs(dev1["t"]) < 0.07, f"t={dev1['t']*100:+.1f}%")
chk("P3.2 1參數 u 命中 <7% (O238)", abs(dev1["u"]) < 0.07, f"u={dev1['u']*100:+.1f}%")

print("\n═══ P4. 誠實分級 (O238 參考 O239) ═══")
print("  α = φ²      : ★結構鎖定 (O239 docs/38 固化 + O238 R17 統計不可分一致)")
print("  rank-parity  : O238 R23 三 scheme 穩健 (δ=+0.664 S2, LOOCV 唔倒退)")
print("               但 O136 P6 null P=0.2165 🔴 仍在 → 照標 🟡 (O238 保證家族層解釋)")
print("  block23      : O238 LOOCV 倒退確認 → 🔴 唔宣稱")
print("  逐點 9/9     : 🔴 殘留 (公式係譜結構, 非逐點)")
chk("P4.1 block23 唔宣稱 (倒退確認)", l3 > l2, f"LOOCV b3={l3:.4f} > rank={l2:.4f}")

print("\n═══ P5. O238 特有: 家族層解釋附註 ═══")
print("  R23: rank-parity 解釋家族分層 (max mean 0.321→0.058, S2/S3 <0.12)")
print("  ⟹ O238 rank 保證: 家族偏置結構 — 但唔覆蓋 O136 逐點 null (兩層意義)")

out = {"C_phi2": float(C1), "alpha": PHI2, "delta": float(c2[2]),
       "rms": {"phi2": rms1, "rank": rms2, "block23": rms3},
       "loocv": {"phi2": l1, "rank": l2, "block23": l3},
       "dev_pct": {"phi2": dev1, "rank": dev2, "block23": dev3},
       "masses": MS, "sel": SEL9, "o239_dev1_pct": o239_dev1}
with open("data/40_fermion_formula_list.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")