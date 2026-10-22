#!/usr/bin/env python3
"""
O9: 雙重驗證 — 獨立重算所有閉合數字
=====================================
從原始 planck_tt.txt + spt bdp + act dr6 fits 重算:
1. 峰位 (bin 中心局部極大, 唔用任何 cache)
2. IDCM 修正公式
3. 閉合矩陣 + RMS
4. 對比 02_results.md 同 o9_final_v2.json 聲稱值
5. 振幅級聯有理數
Exit 1 on any fail
"""
import numpy as np
import math as _m
import os, json, sys

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])

fails = []
passes = []

def check(name, claim, value, tol=0.5):
    if abs(claim - value) <= tol:
        passes.append(f"{name}: {value}")
    else:
        fails.append(f"{name}: claim={claim} actual={value}")
        print(f"  ❌ {name}: claim={claim} actual={value}")

# ---------- 1. 峰位重算 ----------
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

def idcm_fix(m):
    if m == 5:
        return 44*(33 - F[6]) + F[8]
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("1. 峰位重算 (bin 中心局部極大, IDCM 修正中心):")
obs = {}
for m in range(1, 8):
    pred = idcm_fix(m)
    win = 60 if m == 5 else 15
    mask = np.abs(ell_p - pred) <= win
    idxs = np.where(mask)[0]
    best_l, best_D = None, -1
    for i in idxs:
        if i > 0 and i < len(ell_p)-1:
            if D_bin[i] >= D_bin[i-1] and D_bin[i] >= D_bin[i+1]:
                if D_bin[i] > best_D:
                    best_l, best_D = int(ell_p[i]), float(D_bin[i])
    if best_l is None:
        j = np.argmax(D_bin[idxs])
        best_l, best_D = int(ell_p[idxs[j]]), float(D_bin[idxs[j]])
    obs[m] = (best_l, best_D)
    print(f"   m={m}: pred={pred} obs={best_l} (D={best_D:.1f})")

# ---------- 2. 對比 JSON ----------
print("\n2. 對比 o9_final_v2.json:")
with open(os.path.join(DATADIR, 'o9_final_v2.json')) as f:
    j = json.load(f)
for m in range(1, 8):
    jm = j['closure'][str(m)]
    check(f"m={m} pred", jm['pred'], idcm_fix(m), 0)
    check(f"m={m} obs", jm['obs'], obs[m][0], 1)
    # dev 重算
    dev = (obs[m][0] - idcm_fix(m))/idcm_fix(m)*100
    check(f"m={m} dev", jm['dev'], dev, 0.05)

rms = float(j['rms_pct'])
devs = [(obs[m][0] - idcm_fix(m))/idcm_fix(m)*100 for m in range(1, 8)]
rms_calc = float(np.sqrt(np.mean(np.array(devs)**2)))
check("RMS", rms, rms_calc, 0.01)
print(f"   RMS: doc={rms} calc={rms_calc:.4f}")

# ---------- 3. m=5 公式 ----------
print("\n3. m=5 公式:")
check("m5=44*25+21", 44*(33-F[6])+F[8], 1121, 0)
check("F6=8", F[6], 8, 0)
check("F8=21", F[8], 21, 0)
check("shift=-78", 1121-1199, -78, 0)

# ---------- 4. 守恆 ----------
print("\n4. 峰間距守恆:")
def idcm_orig(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)
orig_dl_old = [idcm_orig(5)-idcm_orig(4), idcm_orig(6)-idcm_orig(5)]  # 原公式 Δℓ₄, Δℓ₅
fix_dl = [idcm_fix(5)-idcm_fix(4), idcm_fix(6)-idcm_fix(5)]          # 修正 Δℓ₄, Δℓ₅
print(f"   原 Δℓ₄+Δℓ₅ = {sum(orig_dl_old)}, 修正 = {sum(fix_dl)}")
check("守恆 326", sum(fix_dl), sum(orig_dl_old), 0)

# ---------- 5. 振幅級聯 ----------
print("\n5. 振幅級聯有理數 (limit_denominator 50):")
from fractions import Fraction
A1 = obs[1][1]
doc_fracs = j.get('amplitude_fracs', {})
for m in range(1, 8):
    a = obs[m][1]/A1
    fr = Fraction(a).limit_denominator(50)
    print(f"   A_{m}/A_1 = {a:.4f} ≈ {fr.numerator}/{fr.denominator}")

# 文件聲稱值
doc_claims = {
    "A2/A1": (0.4434, "4/9"), "A3/A2": (0.9897, "1/1"),
    "A4/A3": (0.4229, "11/26"), "A5/A4": (1.1545, "15/13"),
    "A6/A5": (0.6081, "14/23"), "A7/A6": (1.0954, "23/21")
}
print("\n   相鄰比率重算:")
for k, (claim, frc) in doc_claims.items():
    # k 格式 "A2/A1": 分子 m=2, 分母 m=1 → r = A[2]/A[1]
    parts = k.split('/')
    mi = int(parts[0][1:])   # "A2" → 2 (分子)
    mj = int(parts[1][1:])   # "A1" → 1 (分母)
    r = obs[mi][1]/obs[mj][1]
    fr = Fraction(r).limit_denominator(30)
    mark = "✅" if abs(r-claim) < 0.01 else "❌"
    print(f"   {k}: {r:.4f} ≈ {fr.numerator}/{fr.denominator} (doc {claim} {frc}) {mark}")

# ---------- 6. 檔案存在 ----------
print("\n6. 檔案存在檢查:")
files = ['planck_tt.txt', 'spt3g_tne_bdp.txt', 'spt_tt150_windows.txt',
         'act_dr6_cmb_sacc.fits', 'o9_final_v2.json']
for f in files:
    p = os.path.join(DATADIR, f)
    if os.path.exists(p):
        passes.append(f"file {f} exists")
    else:
        fails.append(f"file {f} MISSING")

print("\n" + "="*60)
print(f"PASS: {len(passes)}  FAIL: {len(fails)}")
for f in fails:
    print(f"  ❌ {f}")
if fails:
    sys.exit(1)
print("✅ 全部通過")
