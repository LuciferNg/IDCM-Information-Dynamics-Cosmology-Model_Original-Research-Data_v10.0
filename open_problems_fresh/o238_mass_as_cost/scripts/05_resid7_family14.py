#!/usr/bin/python3
"""O238 — Script 05: 7 點殘差結構 + n≡1 mod4 族偏移檢定 (路線 1 收窄)

scripts/02-04 結果彙整:
  - R = 603.2 冇譜泛函/池身份 (全負)
  - c/s 遮蔽標度: 剔除後 C −24.6%, RMS 0.580→0.2515
  - n≡1 mod4 族 {μ,d,e} 殘差 ≈ −0.42 一致 (spread 0.04)
本 script 三問:
  P1 7 點 (剔 c/s) 殘差: 剩低結構係乜? 有冇第二離群者浮現?
  P2 n≡1 mod4 族偏移檢定: 族均值 −0.42 係咪顯著偏離其他點?
     隨機 null: 9 點抽 3 點做「族」嘅均值 |偏移| 分布 (同標度任意性控制)
  P3 若 n≡1 mod4 族有系統偏移 ⟹ 測試修正: m = C·|dm|^{φ²}·h(n mod 4)
     h(1)=δ, h(2)=h(3)=h(0)=1 (幾何 — 唔係新常數, 係族選擇律候選)
"""
import numpy as np, math, json, random

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

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MB = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
logd = np.log([admn[n-1] for n in SEL9])
logm = np.log(MB)
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
C9 = math.exp((logm - PHI2 * logd).mean())
resid = logm - (math.log(C9) + PHI2 * logd)

CS_IDX = [3, 5]  # c, s
keep = [i for i in range(9) if i not in CS_IDX]
C7 = math.exp((logm[keep] - PHI2 * logd[keep]).mean())
resid7 = logm[keep] - (math.log(C7) + PHI2 * logd[keep])

print("═══ P1. 7 點 (剔 c/s) 殘差結構 ═══")
for i, j in enumerate(keep):
    print(f"  {names9[j]:4s} (n={SEL9[j]:2d}, mod4={SEL9[j]%4}): resid7 = {resid7[i]:+.4f}")
rms7 = np.sqrt((resid7**2).mean())
print(f"  7 點 RMS = {rms7:.6f}; 最大 |resid| = {np.abs(resid7).max():.4f} ({names9[keep[np.argmax(np.abs(resid7))]]})")
worst2 = sorted(range(7), key=lambda i: -abs(resid7[i]))[:2]
print(f"  7 點殘差最大 2 點: {[names9[keep[i]] + f'({resid7[i]:+.3f})' for i in worst2]}")

print("\n═══ P2. n≡1 mod4 族偏移檢定 ═══")
fam14 = [i for i in range(9) if SEL9[i] % 4 == 1]
print(f"  n≡1 mod4 族: {[names9[i]+f'(n={SEL9[i]})' for i in fam14]}")
fam_resid = [resid[i] for i in fam14]
fam_mean = np.mean(fam_resid)
print(f"  族殘差均值 = {fam_mean:+.4f} (個別: {[f'{r:+.3f}' for r in fam_resid]})")
# null: 隨機抽 3 點做「族」, 計佢嘅殘差均值 |值|
rng = random.Random(12345)
null = []
for _ in range(100000):
    idx = rng.sample(range(9), len(fam14))
    null.append(abs(np.mean([resid[i] for i in idx])))
null = np.array(null)
p = (null >= abs(fam_mean)).mean()
print(f"  null (隨機 3 點族 |均值|): median={np.median(null):.4f}; P(|mean| ≥ {abs(fam_mean):.3f}) = {p:.5f}")
chk("P2.1 n≡1 mod4 族偏移顯著 (P<0.05)", p < 0.05, f"P={p:.5f}")

print("\n═══ P3. 族修正候選: m = C·|dm|^{φ²}·h(n mod 4) ═══")
# 零額外自由度: h(1)=δ 由族均值 fit (1 參數), 其餘 = 1
delta = math.exp(-fam_mean)  # 用族均值修正
logm_mod = logm.copy()
for i in fam14:
    logm_mod[i] -= (-fam_mean)  # 減去族偏移
Cmod = math.exp((logm_mod - PHI2 * logd).mean())
resid_mod = logm_mod - (math.log(Cmod) + PHI2 * logd)
rms_mod = np.sqrt((resid_mod**2).mean())
print(f"  δ = exp(−族均值) = {delta:.4f}  (h(1)=δ, 其他=1)")
print(f"  修正後 RMS = {rms_mod:.6f} (基線 {np.sqrt((resid**2).mean()):.6f})")
print(f"  修正後殘差: {[f'{r:+.3f}' for r in resid_mod]}")
# 公平比較: 2 參數 vs 3 參數? 用 AICc (9 點小樣本)
def aicc(rms, k, n=9):
    ll = -n/2*(1+math.log(2*math.pi*rms**2))
    return -2*ll + 2*k + 2*k*(k+1)/(n-k-1)
a0 = aicc(np.sqrt((resid**2).mean()), 2)
a1 = aicc(rms_mod, 3)
print(f"  AICc: 基線(2參數) = {a0:.2f}; 修正(3參數) = {a1:.2f}  Δ = {a1-a0:+.2f}")
chk("P3.1 族修正 AICc 改善 (>2)", a1 < a0 - 2, f"Δ={a1-a0:+.2f}")

out = {"rms7": float(rms7), "fam14_mean": float(fam_mean), "p_fam": float(p),
       "delta": float(delta), "rms_mod": float(rms_mod), "aicc_base": float(a0),
       "aicc_mod": float(a1)}
with open("data/05_resid7_family14.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")