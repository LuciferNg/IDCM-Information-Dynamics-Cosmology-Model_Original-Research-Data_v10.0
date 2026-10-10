#!/usr/bin/env python3
"""
O48 Q1.16: 「谷係咪另一頻率嘅峰？」— 峰+谷合併序列盲測
=============================================================
調律者問題: 「即是谷也可能是另一頻率的峰？」

Q1.14-15 發現谷同峰共享 mod-9 梳 (ℓ≡5 mod 9) — 本 script 深測:
A. 峰+谷合併序列 (9 點) 全喺 9-梳上? 間距模式?
B. 谷間距頻率 vs 峰間距頻率 — 另一頻率?
C. 峰→谷 vs 谷→峰 距離比 (谷偏近後峰? ¼ 週期位?)
D. 統計: 合併序列全 9 倍數嘅概率
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

peaks = np.array([221, 527, 815, 1121, 1409])
v_plik = np.array([464, 734, 1058, 1355])
v_o9 = np.array([437, 716, 1040, 1346])

print("="*72)
print("A. 峰+谷 合併序列 — 單一 9-梳?")
print("="*72)
merged = sorted(list(peaks) + list(v_plik))
mg = np.diff(merged)
print(f"合併: {merged}")
print(f"間距: {mg}")
mul9 = [int(g//9) for g in mg]
print(f"間距/9: {mul9}")
check("A1: 峰+谷全序列 9 倍數間距", all(g % 9 == 0 for g in mg), f"gap/9={mul9}")
# 谷點全部 ≡5 mod 9?
vm9 = [v % 9 for v in v_plik]
check("A2: 谷全 ≡5 mod 9", all(x == 5 for x in vm9), f"{vm9}")

print("\n" + "="*72)
print("B. 谷間距頻率 vs 峰間距頻率")
print("="*72)
pg = np.diff(peaks)
vg_p = np.diff(v_plik)
vg_o = np.diff(v_o9)
print(f"峰間距:    {pg}  中心={pg.mean():.1f}")
print(f"Plik 谷間距: {vg_p}  中心={vg_p.mean():.1f}")
print(f"O9 谷間距:   {vg_o}  中心={vg_o.mean():.1f}")
# 峰週期 ~297, 谷週期亦 ~297
check("B1: 谷間距中心 ≈ 峰間距中心 (同一頻率)",
      abs(vg_p.mean() - pg.mean()) < 15, f"297={vg_p.mean():.1f} vs {pg.mean():.1f}")
print("→ 谷唔係『另一頻率』 — 同一聲學週期 ~297")

print("\n" + "="*72)
print("C. 谷位置: 偏近後峰? (峰→谷 vs 谷→峰)")
print("="*72)
# 谷→後峰距離
d2p = np.array([527-464, 815-734, 1121-1058, 1409-1355])
d2v = np.array([464-221, 734-527, 1058-815, 1355-1121])
print(f"谷→後峰: {d2p}   (峰→谷: {d2v})")
frac = d2p / (d2p + d2v)
print(f"谷→後峰佔峰間隙比例: {[round(x,3) for x in frac]}")
print(f"平均: {frac.mean():.3f}  (¼=0.25, ½=0.5)")
# 如果谷係聲學 trough 反相 → 應該喺半週期位 (²/₄=0.5)
# 實測 ~0.2-0.3 → 谷偏近後峰, 唔係半週期反相
check("C1: 谷偏近後峰 (比例 ~0.2-0.3, 唔係 0.5)",
      0.15 < frac.mean() < 0.45, f"mean={frac.mean():.3f}")

print("\n" + "="*72)
print("D. 峰+谷 序列 n (ℓ=9n+5) 模式")
print("="*72)
n_merged = (np.array(merged) - 5)//9
print(f"峰+谷 n 序列: {n_merged}")
n_gaps = np.diff(n_merged)
print(f"n 步差: {n_gaps}")
# 峰間隙 34/32 = 峰間距/9; 谷將其分做 (a,b)
# a+b = 34 或 32
print("每峰間隙嘅 (峰→谷, 谷→峰) n 步:")
m_idx = [list(merged).index(p) for p in [221, 527, 815, 1121, 1409]]
for i, p in enumerate(peaks[:-1]):
    # 谷 = merged 中喺 p 同後峰之間
    nxt = peaks[i+1]
    v_in = [v for v in merged if p < v < nxt]
    if v_in:
        a = int((v_in[0]-p)/9)
        b = int((nxt-v_in[0])/9)
        print(f"  峰{i+1}→峰({i+2}): 谷步距 a={a}, b={b}, a+b={a+b} (峰間距 {nxt-p})")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)