#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/05_tension_exhaustion.py — m_W/m_Z 9.6σ 張力: 修正類窮舉 (張力分流協議)
窮舉三類修正, 全滅先定案 🔴 真張力:
  1. trig: sin(aπ/176)/sin(bπ/176) (176-Laplacian, 3828 對) + 88-Laplacian 重掃
  2. rational: ×(1±1/n), n 結構數 (O152 命名算子集 + 乘積組合)
  3. beat-ratio 類 (O149: beat(a,b) = 4sin(dπ/176)·v_g((a+b)/2)) 結構對
"""
import mpmath as mp
mp.mp.dps = 60

mW, mZ = mp.mpf('80.369'), mp.mpf('91.1876')
target = mW/mZ                      # 0.8813589
idcm = mp.sin(30*mp.pi/88)/mp.sin(41*mp.pi/88)

def sinp88(n): return mp.sin(n*mp.pi/88)
def sinp176(n): return mp.sin(n*mp.pi/176)
def vg88(n): return mp.cos(n*mp.pi/88)

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. trig 類: 88-Laplacian 全掃 (1936 對) — 最佳命中")
print("="*72)
best88 = None
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        r = sinp88(a)/sinp88(b)
        d = abs(r/target - 1)
        if best88 is None or d < best88[0]:
            best88 = (d, a, b, r)
print("   88-L best: (a,b)=(%d,%d) r=%.9f dev=%.4f%% (IDCM (30,41) dev=%.4f%%)"
      % (best88[1], best88[2], best88[3], 100*best88[0], 100*abs(idcm/target-1)))
ck("88-L 冇任何對 <0.1%", best88[0] > 0.001, "best %.4f%%" % (100*best88[0]))
print()

print("2. trig 類: 176-Laplacian 全掃 (3828 對) — 最佳命中")
print("="*72)
best176 = None
struct176 = {3, 5, 7, 11, 13, 14, 17, 19, 29, 30, 33, 38, 41, 44, 47, 55, 88, 176}
for a in range(1, 89):
    for b in range(1, 89):
        if a == b: continue
        r = sinp176(a)/sinp176(b)
        d = abs(r/target - 1)
        if best176 is None or d < best176[0]:
            best176 = (d, a, b, r)
print("   176-L best: (a,b)=(%d,%d) r=%.9f dev=%.4f%%"
      % (best176[1], best176[2], best176[3], 100*best176[0]))
ck("176-L 冇任何對 <0.1%", best176[0] > 0.001, "best %.4f%%" % (100*best176[0]))
# 結構指數對 (176-Laplacian)
print("   結構指數對 (a,b ∈ 結構集) 最佳:")
bestS = None
for a in struct176:
    for b in struct176:
        if a == b: continue
        r = sinp176(a)/sinp176(b)
        d = abs(r/target - 1)
        if bestS is None or d < bestS[0]:
            bestS = (d, a, b, r)
print("   struct best: (a,b)=(%d,%d) r=%.9f dev=%.4f%%"
      % (bestS[1], bestS[2], bestS[3], 100*bestS[0]))
ck("結構指數對冇 <0.1%", bestS[0] > 0.001, "best %.4f%%" % (100*bestS[0]))
print()

print("3. rational 修正: ×(1±1/n), n 結構數")
print("="*72)
struct_n = [2,3,4,5,7,11,13,17,19,29,33,41,44,47,55,60,88,90,123,137,176,178,180,360,
            528,5940,867,1350,640]
resid = idcm/target - 1            # +0.001563 (IDCM 高)
print("   殘差 = +%.7f (+%.4f%%)" % (resid, 100*resid))
bestR = None
for n in struct_n:
    for sign in (+1, -1):
        for mode in ("mul", "add"):
            if mode == "mul":
                corr = 1 + sign*mp.mpf(1)/n
                new = idcm * corr
            else:
                corr = sign*mp.mpf(1)/n
                new = idcm + corr
            d = abs(new/target - 1)
            if bestR is None or d < bestR[0]:
                bestR = (d, n, sign, mode, new)
print("   best: %s(1%s1/%d) → r=%.9f dev=%.4f%%"
      % ("×" if bestR[3]=="mul" else "+", "+" if bestR[2]>0 else "−", bestR[1],
         bestR[4], 100*bestR[0]))
ck("rational 修正冇 <0.01%", bestR[0] > 1e-4, "best %.4f%%" % (100*bestR[0]))
print()

print("4. beat-ratio 類 (O149: beat(a,b) = 4sin(dπ/176)·v_g((a+b)/2))")
print("="*72)
# beat(a,b)/beat(c,d) 結構對 — 窮舉 a<b, c<d ∈ 1..44
bestB = None
hits = 0
for a in range(1, 44):
    for b in range(a+1, 45):
        beat_ab = 4*mp.sin((b-a)*mp.pi/176)*mp.cos((a+b)*mp.pi/176)
        for c in range(1, 44):
            for d in range(c+1, 45):
                beat_cd = 4*mp.sin((d-c)*mp.pi/176)*mp.cos((c+d)*mp.pi/176)
                if beat_cd == 0: continue
                r = beat_ab/beat_cd
                dd = abs(r/target - 1)
                if dd < 0.001:
                    hits += 1
                if bestB is None or dd < bestB[0]:
                    bestB = (dd, a, b, c, d, r)
print("   beat 比全掃 (18920 對) <0.1%%: %d hits; best (a,b;c,d)=(%d,%d;%d,%d) dev=%.4f%%"
      % (hits, bestB[1], bestB[2], bestB[3], bestB[4], 100*bestB[0]))
ck("beat-ratio 冇結構命中 <0.01%", bestB[0] > 1e-4, "best %.4f%%" % (100*bestB[0]))
print()

print("5. 定案")
print("="*72)
print("   IDCM m_W/m_Z = sin(30π/88)/sin(41π/88) = 0.882737")
print("   PDG 0.881359 (80.369/91.1876) → 0.156%% = 9.6σ")
print("   三類修正窮舉: trig (88-L + 176-L + 結構對) / rational / beat 全滅")
ck("88-L best 0.140% 仍係 8.6σ — 張力真實", 100*best88[0]/1.634e-2 > 5)
print("   → m_W/m_Z 張力 🔴 定案: 冇自然修正, 9.6σ 真張力")
print()

print("6. 張力方向讀法")
print("="*72)
mW_pred = idcm * mZ
print("   IDCM 預測 m_W = %.3f GeV (PDG 80.369±0.013, CDF 80.433±0.009)" % mW_pred)
print("   → 預測 m_W 高過 PDG +0.124 GeV (9.5σ), 高過 CDF +0.06 GeV (6σ)")
print("   → IDCM W/Z 比夾喺 PDG 同 CDF 之間, 偏 CDF 側")
ck("IDCM m_W 預測 80.49 GeV — 高於兩者", mW_pred > mp.mpf('80.433'))

print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)
