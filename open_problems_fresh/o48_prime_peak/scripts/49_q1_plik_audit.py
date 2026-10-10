#!/usr/bin/env python3
"""
O48 Q1.31 AUDIT: Plik-lite 三 block 結構 vs QL 已記錄結論
=============================================================
⚠️ 數據完整性問題: cl_cmb_plik_v22.dat = 215 TT + 199 TE + 199 EE
(O214 06 script header 明載)。QL scripts (28/30/31/32/33/34/43/45-48)
全部 `sorted(plik)` 讀晒 613 行 → 混咗 TE/EE!

Audit:
  A. 確認 3 block (TT 32..2492, TE 32..1988?, EE 32..1988?)
  B. 用 block1 純 TT 重算谷位 → 同記錄 [464,734,1058,1355] 對比
  C. 對比 O9 planck_tt.txt (o9 or o163 版, 215 bins 純 TT?)
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
data = f"{base}/o214_energy_budget_definition/data/planck2018_plik_lite"

rows = []
for line in open(f"{data}/cl_cmb_plik_v22.dat"):
    p = line.split()
    if len(p) >= 3:
        try:
            rows.append((float(p[0]), float(p[1]), float(p[2])))
        except ValueError:
            pass
rows = sorted(rows)
ells = np.array([r[0] for r in rows])
vals = np.array([r[1] for r in rows])
errs = np.array([r[2] for r in rows])

# 3 block 邊界 (ell 重複 158 => sorted 後每個 ℓ 最多 3 個值)
uniq, counts = np.unique(ells, return_counts=True)
print("="*72)
print("A. 檔案結構確認")
print("="*72)
print(f"總 rows: {len(rows)}, unique ℓ: {len(uniq)} ({uniq[0]:.0f}..{uniq[-1]:.0f})")
print(f"counts: 出現1次 {sum(counts==1)} 個 ℓ, 2次 {sum(counts==2)}, 3次 {sum(counts==3)}")
# block1 = 每個 ℓ 最大值 (TT 最大), block2/3 細
# 分組: 對每個 unique ℓ, 3 個值
idx_by_ell = {}
for i, e in enumerate(ells):
    idx_by_ell.setdefault(e, []).append(i)
v1, v2, v3, e1 = [], [], [], []
for e in uniq:
    ids = idx_by_ell[e]
    vs = [vals[i] for i in ids]
    v1.append(max(vs))
    if len(vs) >= 2:
        v2.append(sorted(vs)[-2])
    else:
        v2.append(np.nan)
    if len(vs) >= 3:
        v3.append(min(vs))
    else:
        v3.append(np.nan)
    e1.append(e)
v1, v2, v3, e1 = map(np.array, (v1, v2, v3, e1))
print(f"block max (TT?):   rows 對應 {sum(counts==1)+sum(counts==2)+sum(counts==3)} 點, ell {e1[0]:.0f}..{e1[-1]:.0f}")
print(f"  TT 值範圍: {v1.min():.3e}..{v1.max():.3f} 負數: {(v1<0).sum()}")
m2v = v2[~np.isnan(v2)]
print(f"  中間值(TE?) 範圍: {m2v.min():.3e}..{m2v.max():.3e} 負數: {(m2v<0).sum()}")
m3v = v3[~np.isnan(v3)]
print(f"  最小(EE?) 範圍: {m3v.min():.3e}..{m3v.max():.3e} 負數: {(m3v<0).sum()}")

print("\n" + "="*72)
print("B. 純 TT (每 ℓ 最大值) 谷位 vs 記錄 [464,734,1058,1355]")
print("="*72)
PEAKS = np.array([221, 527, 815, 1121, 1409])

def valleys_of(ell_arr, val_arr):
    out = {}
    for i, p in enumerate(PEAKS[:-1]):
        m2 = PEAKS[i+1]
        span = m2 - p
        lo, hi = p + 0.12*span, m2 - 0.12*span
        seg_ix = np.where((ell_arr >= lo) & (ell_arr <= hi))[0]
        if len(seg_ix) == 0:
            continue
        gmin = min(seg_ix, key=lambda ix: val_arr[ix])
        out[m2] = ell_arr[gmin]
    return out

vt = valleys_of(e1, v1)
print(f"純 TT 谷: {[int(vt[m]) for m in vt]}")
print(f"記錄 (QL): [464, 734, 1058, 1355]")
rec = {527: 464, 815: 734, 1121: 1058, 1409: 1355}
for m in vt:
    ok = abs(vt[m] - rec[m]) < 2
    check(f"B m={m}: 純 TT 谷={int(vt[m])} vs QL={rec[m]}", ok,
          f"Δ={int(vt[m]-rec[m])}")

print("\n" + "="*72)
print("C. 原 613-row sorted 谷位 (重現 QL 錯誤?)")
print("="*72)
v_all = valleys_of(ells, vals)
print(f"613混和谷: {[int(v_all[m]) for m in v_all]}")

print("\n" + "="*72)
print("D. O9 planck_tt.txt (o163 版) 對照")
print("="*72)
o9p = f"{base}/o163_dm_identity/data/planck_tt.txt"
try:
    o9 = np.loadtxt(o9p)
    print(f"O9(o163) shape: {o9.shape}, ell {o9[0,0]:.0f}..{o9[-1,0]:.0f}")
    vo9 = valleys_of(o9[:,0], o9[:,1])
    print(f"O9(o163) 谷: {[int(vo9[m]) for m in vo9]}")
    print(f"QL 記錄 O9 谷: [437,716,1040,1346]")
except Exception as ex:
    print(f"O9(o163) 讀取失敗: {ex}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)