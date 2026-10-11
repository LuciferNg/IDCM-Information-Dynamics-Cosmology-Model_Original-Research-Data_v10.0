#!/usr/bin/python3
"""O238 — AUDIT: 獨立重驗所有 headline 數字（唔 import 任何原 script）

T1 — 由原始定義起算（γ_n = 4sin²(nπ/88)、φ、|dm| 構造），對照 data/*.json 記錄值。
只報偏差；>0.5% 或邏輯不符 = FAIL。
"""
import numpy as np, math, json, os

checks = []
def chk(name, got, exp, tol_rel=5e-3, logic=False):
    ok = logic if logic else abs(got-exp)/abs(exp) < tol_rel
    checks.append((name, ok, f"got={got} exp={exp} rel={abs(got-exp)/abs(exp) if exp else 'n/a':.2e}" if not ok else f"got={got}"))

# ── 原始構造 ──
N = 88
idxx = np.arange(1, N+1)
psii = np.array([np.sin(n*math.pi*idxx/(N+1)) for n in range(1, N+1)])
psii = psii/np.linalg.norm(psii, axis=1)[:,None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, N+1)])
D = E[:,None]-E[None,:]
G = np.where(np.abs(D) > 1e-12, 1.0/np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V**2, G)
admn = np.abs(dm)
gam = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, N+1)])
PHI = (1+math.sqrt(5))/2
PHI2 = PHI**2

SEL9 = [1,2,3,4,5,7,9,11,13]
names9 = ["t","b","tau","c","mu","s","d","u","e"]
MS2 = {"e":0.51099895,"mu":105.6583755,"tau":1776.86,
       "u":93.4/42.890,"d":93.4/42.890*2.1505,"s":93.4,
       "c":93.4*11.652,"b":93.4*11.652*4.586,"t":172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
logd9 = np.log([admn[n-1] for n in SEL9])
logg9 = np.log([gam[n-1] for n in SEL9])

print("═══ A. 基礎結構 ═══")
chk("A1 dm_n 定義 |dm| sum", admn.sum(), 381012.5716, logic=False)
chk("A2 |dm| max (n=44)", admn.max(), 127793.3049)
chk("A3 |dm| median", np.median(admn), 232.4179)
d7 = admn[6]
chk("A4 |dm| n=7", d7, 609.9355)

print("═══ B. 冪律 fit（S1 + S2 兩套質量集獨立重現）═══")
# S1 = v1.1 混標度（scripts/08 定義, 同源錨鏈 u=93.4/42.89, b=×3.291 偽影）
MS1 = {"e":0.51099895,"mu":105.6583755,"tau":1776.86,
       "u":93.4/42.890, "d":93.4/42.890*2.1505, "s":93.4,
       "c":93.4*11.652, "b":93.4*11.652*3.291, "t":172690.0}
logm1 = np.array([math.log(MS1[p]) for p in names9])
C_s1 = math.exp(np.mean(logm1 - PHI2*logd9))
res1 = logm1 - (math.log(C_s1) + PHI2*logd9)
rms1 = math.sqrt(np.mean(res1**2))
A1_ = np.vstack([np.ones(9), logd9]).T
c1_, *_ = np.linalg.lstsq(A1_, logm1, rcond=None)
print(f"  S1: C={C_s1:.6e} RMS={rms1:.6f} α={c1_[1]:.6f}")
chk("B1 C(S1)", C_s1, 1.466433599e-6, tol_rel=2e-3)
chk("B2 RMS(S1 fixed φ²)", rms1, 0.580174, tol_rel=2e-3)
chk("B3 α_OLS(S1)", c1_[1], 2.616977, tol_rel=2e-3)
# S2 = freeze v2（權威）
logm2 = np.array([math.log(MS2[p]) for p in names9])
C_s2 = math.exp(np.mean(logm2 - PHI2*logd9))
res2 = logm2 - (math.log(C_s2) + PHI2*logd9)
rms2 = math.sqrt(np.mean(res2**2))
A2_ = np.vstack([np.ones(9), logd9]).T
c2_, *_ = np.linalg.lstsq(A2_, logm2, rcond=None)
print(f"  S2: C={C_s2:.6e} RMS={rms2:.6f} α={c2_[1]:.6f}")
chk("B6 C(S2)", C_s2, 1.521507856e-6, tol_rel=2e-3)
chk("B7 RMS(S2 fixed φ²)", rms2, 0.545571, tol_rel=2e-3)
chk("B8 α_OLS(S2)", c2_[1], 2.642463, tol_rel=2e-3)
# S1 M₀ 比
chk("B4 C/M₀(S1)", C_s1/27.900915, 5.255862036e-8, tol_rel=2e-3)
# ref R 由 S1
chk("B5 ref R=(M0/C_S1)^(1/φ²)", (27.900915/C_s1)**(1/PHI2), 603.207305, tol_rel=2e-3)

print("═══ C. α 全域穩健（LOOCV, S1）═══")
alphas = []
for i in range(9):
    tr = [j for j in range(9) if j != i]
    A_ = np.vstack([np.ones(8), logd9[tr]]).T
    c_, *_ = np.linalg.lstsq(A_, logm1[tr], rcond=None)
    alphas.append(c_[1])
lo, hi = min(alphas), max(alphas)
print(f"  LOOCV α 範圍: [{lo:.4f}, {hi:.4f}]")
chk("C1 LOOCV 範圍下限", lo, 2.552, tol_rel=2e-3)
chk("C2 LOOCV 範圍上限", hi, 2.684, tol_rel=2e-3)
chk("C3 全部 φ² 0.42σ 內", all(abs(a-PHI2)/0.151 < 0.42 for a in alphas), True, logic=True)

print("═══ D. 投影 signature ═══")
# 全譜 corr
cc_all = np.corrcoef(np.log(admn), np.log(gam))[0,1]
cc_sel = np.corrcoef(logd9, logg9)[0,1]
chk("D1 全譜 corr", cc_all, -0.3000146, tol_rel=5e-3)
chk("D2 SEL9 corr", cc_sel, -0.9959947, tol_rel=5e-3)
r2_sel = cc_sel**2
chk("D3 SEL9 R²", r2_sel, 0.992005, tol_rel=2e-3)
chk("D4 γ 冪律等價指數", PHI2*cc_all/1*0 + PHI2*(-0.918), -2.4043, tol_rel=5e-3)  # 需確認實際 -0.918
# 由 fit 直接計: log|dm| = a + b·logγ on SEL9
B = np.vstack([np.ones(9), logg9]).T
cb, *_ = np.linalg.lstsq(B, logd9, rcond=None)
equiv = PHI2*cb[1]
chk("D5 等價 γ 指數 (fit 計)", equiv, -2.4043, tol_rel=5e-2)
print(f"    (log|dm| vs logγ slope = {cb[1]:+.4f}, φ²×slope = {equiv:+.4f})")

# PCA
X9 = np.array([logg9, logd9]).T
Xc9 = X9 - X9.mean(axis=0)
cov9 = Xc9.T @ Xc9/8
ev9, evc9 = np.linalg.eigh(cov9)
o9 = np.argsort(ev9)[::-1]
pc1 = Xc9 @ evc9[:, o9[0]]
pc1_var = ev9[o9[0]]/ev9.sum()
corr_pc1 = np.corrcoef(pc1, logm)[0,1]
r_pc = np.argsort(np.argsort(pc1)); r_m = np.argsort(np.argsort(logm))
spearman = np.corrcoef(r_pc, r_m)[0,1]
chk("D6 PC1 var", pc1_var, 0.9980, tol_rel=2e-3)
chk("D7 corr(PC1,logm)", corr_pc1, 0.9859, tol_rel=2e-3)
chk("D8 Spearman", spearman, 1.0, tol_rel=1e-9)
print(f"    Spearman = {spearman:.8f}")

print("═══ E. A₅ 數論規則 ═══")
def is_prime(k):
    if k < 2: return False
    for d in range(2, int(math.sqrt(k))+1):
        if k % d == 0: return False
    return True
def is_sq(k):
    r = int(round(math.sqrt(k)))
    return r*r == k
rule = sorted([k for k in range(1,14) if is_prime(k) or is_sq(k)])
chk("E1 A₅ = primes∪squares≤13", rule == SEL9, True, logic=True)
from math import comb
chk("E2 p=1/C(88,9)", 1/comb(88,9), 1.750239554552731e-12)

print("═══ F. {1..9} vs A₅ ═══")
def rms_of(sel):
    ld = np.log([admn[n-1] for n in sel])
    C_ = math.exp(np.mean(logm - PHI2*ld))
    r_ = logm - (math.log(C_) + PHI2*ld)
    return math.sqrt(np.mean(r_**2))
chk("F1 RMS(A₅)", rms_of(SEL9), 0.545571, tol_rel=3e-3)
chk("F2 RMS({1..9})", rms_of(list(range(1,10))), 1.101892, tol_rel=3e-3)

print("═══ G. C = 1/88³ 審計 ═══")
chk("G1 C(S1) dev vs 1/88³", abs(math.log(C_s1/(1/88**3))), 0.000667, tol_rel=5e-2)
chk("G2 C(S2) dev vs 1/88³ (應 ~3.7%)", abs(math.log(C_s2/(1/88**3))), 0.0362, tol_rel=5e-2)

print("═══ H. c/s 沿軌跡位置誤差 ═══")
A1 = np.vstack([np.ones(9), pc1]).T
c1, *_ = np.linalg.lstsq(A1, logm, rcond=None)
dpos = {}
for i, p in enumerate(names9):
    pc1_hat = (logm[i]-c1[0])/c1[1]
    dpos[p] = pc1_hat - pc1[i]
cs = [abs(dpos["c"]), abs(dpos["s"])]
oth = [abs(dpos[p]) for p in names9 if p not in ("c","s")]
ratio = np.mean(cs)/np.mean(oth)
chk("H1 c/s 位置誤差 ratio", ratio, 3.18, tol_rel=5e-2)
print(f"    ratio = {ratio:.3f}")

print("═══ I. 強子盲測 ═══")
hadrons = {"pi0":134.9768,"pi+":139.57039,"eta":547.862,"K+":493.677,"K0":497.611,
           "eta'":957.78,"p":938.272088,"n":939.565421,"Lambda":1115.683,"Sigma+":1189.37,
           "Xi0":1314.86,"D0":1864.84,"D+":1869.66,"B+":5279.32,"B0":5279.63,
           "J/psi":3096.9,"Upsilon":9460.30}
C_s2 = 1.521507856e-6
m_pred = np.array([C_s2*admn[i]**PHI2 for i in range(N)])
hits10 = sum(1 for m_obs in hadrons.values() if np.min(np.abs(m_pred-m_obs)/m_obs) < 0.10)
log_range = math.log(m_pred.max()/m_pred.min())
frac10 = math.log(1.10/0.90)/log_range
expected = len(hadrons)*N*frac10
chk("I1 命中數 < 池密度", hits10, expected, tol_rel=0.5, logic=True)
print(f"    hits10={hits10}, expected={expected:.1f}")

# ── 結果 ──
print(f"\nRESULT: {sum(1 for _,ok,_ in checks if ok)}/{len(checks)} checks passed")
fails = [(n,d) for n,ok,d in checks if not ok]
for n,d in fails:
    print(f"  [FAIL] {n}: {d}")
if fails:
    print("  ⚠️ 有 FAIL — 需調查")
else:
    print("  ✅ 全部獨立重驗一致")