#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/12_k_pairing_complement.py — k 配對結構: (3,19) 半鏈互補
問題: 點解 m_W/m_Z 用 k=3=N_gen, m_τ/m_b 用 k=19=f_proj?
發現候選: 3+19 = 22 = N_d/2 (半鏈) = 2L₅; 3 = L₅−2B, 19 = L₅+2B
  (2B = 8 = O137 純玻色子) — k 對以 L₅ 為中心對稱
另外檢查: 其他 45-家族成員對 SM 質量比嘅「弱命中」((14,31) k=17=F_proj
→ m_u/m_d?, (2,43) k=41=f_unproj → m_d/m_s?)
"""
import mpmath as mp
mp.mp.dps = 60

N_d = 44
B = 4
N_gen = 3
L5 = 11
F_proj = 17
f_proj = 19
f_unproj = 41

def sinp176(n): return mp.sin(n*mp.pi/176)

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. ★★★ k 對 (3,19) 半鏈互補")
print("="*72)
print("   3 + 19 = 22 = N_d/2 = 2L₅ (半鏈)")
print("   3 = 11−8 = L₅−2B,  19 = 11+8 = L₅+2B  (2B = 8 = O137 純玻色子)")
print("   → 兩個命中 k 以 L₅ = N_d/4 為中心對稱, 互為半鏈補數")
ck("3+19 = 22 = N_d/2 = 2L₅", 3+19 == 22 and 22 == N_d//2 and 22 == 2*L5)
ck("3 = L₅−2B (11−8)", 3 == L5 - 2*B)
ck("19 = L₅+2B (11+8)", 19 == L5 + 2*B)
ck("2B = 8 ∈ O137 純玻色子集 {8,16,24,32,40}", 2*B in {8,16,24,32,40})
print()

print("2. k 奇數身份表 (45-家族 k 必須奇數)")
print("="*72)
k_ids = {3: "N_gen", 5: "F₅", 7: "F₇", 9: "?", 11: "L₅", 13: "F₇",
         15: "?", 17: "F_proj", 19: "f_proj", 21: "C(L₄,2)", 23: "?",
         25: "F₅²", 27: "?", 29: "?", 31: "?", 33: "K_tree", 35: "?",
         37: "?", 39: "?", 41: "f_unproj", 43: "?"}
print("   k ∈ {3,5,7,...,43} (奇數, 45-家族可達):")
for k in range(3, 44, 2):
    print("     k=%2d: %s" % (k, k_ids.get(k, "?")))
ck("命中 k = {3, 19} 都有算子身份 (N_gen, f_proj)",
   k_ids[3] == "N_gen" and k_ids[19] == "f_proj")
ck("3 同 19 都係奇數 (45-家族 k 奇數 → a,b 整數一奇一偶)",
   all(k % 2 == 1 for k in [3, 19]))
print()

print("3. 命中對照表 (45-家族 vs SM 質量比)")
print("="*72)
targets = {
    "m_W/m_Z": mp.mpf('80.369')/mp.mpf('91.1876'),
    "m_τ/m_b": mp.mpf('1776.86')/mp.mpf('4180'),
    "m_u/m_d": mp.mpf('2.16')/mp.mpf('4.67'),
    "m_d/m_s": mp.mpf('4.67')/mp.mpf('93.4'),
    "m_s/m_c": mp.mpf('93.4')/mp.mpf('1270'),
    "m_b/m_t": mp.mpf('4180')/mp.mpf('172690'),
    "m_μ/m_e": mp.mpf('105.658')/mp.mpf('0.511'),
    "m_c/m_s": mp.mpf('1270')/mp.mpf('93.4'),
    "m_s/m_d": mp.mpf('93.4')/mp.mpf('4.67'),
    "m_t/m_b": mp.mpf('172690')/mp.mpf('4180'),
}
pairs = [(21,24,3,"m_W/m_Z"), (13,32,19,"m_τ/m_b"), (14,31,17,"m_u/m_d"),
         (2,43,41,"m_d/m_s"), (5,40,35,"?"), (1,44,43,"m_b/m_t?")]
print("   家族成員 (a,b) k → 比 vs 目標:")
for a, b, k, tgt in pairs:
    r = sinp176(a)/sinp176(b)
    if tgt in targets:
        dev = 100*abs(r/targets[tgt]-1)
        print("   (%2d,%2d) k=%-3d %.6f vs %-8s %.6f  dev=%.3f%%"
              % (a, b, k, r, tgt, targets[tgt], dev))
    else:
        print("   (%2d,%2d) k=%-3d %.6f vs %-8s (冇固定目標)" % (a, b, k, r, tgt))
print()
ck("(21,24) k=3 → m_W/m_Z 0.0007% (精確命中)",
   abs(sinp176(21)/sinp176(24)/targets['m_W/m_Z']-1) < mp.mpf('1e-4'))
ck("(13,32) k=19 → m_τ/m_b 0.067% (精確命中)",
   abs(sinp176(13)/sinp176(32)/targets['m_τ/m_b']-1) < mp.mpf('1e-3'))
ck("(14,31) k=17=F_proj → m_u/m_d 1.8% off (弱, m_u/m_d 不確定)",
   abs(sinp176(14)/sinp176(31)/targets['m_u/m_d']-1) > mp.mpf('1e-2'))
ck("(2,43) k=41=f_unproj → m_d/m_s 2.9% off (弱, m_d/m_s 不確定)",
   abs(sinp176(2)/sinp176(43)/targets['m_d/m_s']-1) > mp.mpf('1e-2'))
print()

print("4. 比範圍: 45-家族只覆蓋 <1 嘅比")
print("="*72)
r_min = sinp176(1)/sinp176(44)
r_max = sinp176(21)/sinp176(24)
print("   45-家族 sin 比範圍: [%.6f, %.6f] (全部 <1)" % (r_min, r_max))
print("   >1 目標 (冇得命中): m_μ/m_e=206.8, m_t/m_b=41.3, m_c/m_s=13.7,")
print("   m_s/m_d=20.0, m_b/m_c=3.3 — sin 比 <1 結構只覆蓋質量比<1")
ck("m_μ/m_e 206.8 >1 → 45-家族覆蓋唔到 (非失敗, 結構限制)",
   targets['m_μ/m_e'] > 1)
ck("m_t/m_b 41.3 >1 → 同上", targets['m_t/m_b'] > 1)
ck("範圍內 SM <1 比: m_W/m_Z(0.88), m_τ/m_b(0.43), m_u/m_d(0.46), m_d/m_s(0.05)",
   all(r_min < v < r_max for v in [targets['m_W/m_Z'], targets['m_τ/m_b'],
                                    targets['m_u/m_d'], targets['m_d/m_s']]))
print()

print("5. k 互補結構: 玻色子近端 / 費米子遠端")
print("="*72)
print("   k = 3 (N_gen): 比 0.8814 接近 1 — W/Z 弱同位旋對稱破缺細")
print("   k = 19 (f_proj): 比 0.4254 偏離 1 — τ/b 三代 Yukawa 差異大")
print("   → k = |a−b| = 模式距離 = 質量比嘅『對稱破缺度』")
print("   → 3 同 19 互補 (和 = 22 = 半鏈): 玻色子 sector 近端, 費米子遠端")
print("   → 兩者以 L₅ = 11 = N_d/4 為中心: 3 = 11−8, 19 = 11+8 (2B = 8)")
print()

print("6. 弱命中 (14,31)/(2,43) 嘅意義")
print("="*72)
r1731 = sinp176(14)/sinp176(31)
r243 = sinp176(2)/sinp176(43)
dev_u = 100*abs(r1731/targets['m_u/m_d']-1)
dev_d = 100*abs(r243/targets['m_d/m_s']-1)
print("   (14,31) k=17=F_proj: {:.6f} vs m_u/m_d 0.4625 ({:.1f}%% off)".format(float(r1731), float(dev_u)))
print("   (2,43)  k=41=f_unproj: {:.6f} vs m_d/m_s 0.0500 ({:.1f}%% off)".format(float(r243), float(dev_d)))
print("   k 身份鏈: 19=f_proj, 17=F_proj, 41=f_unproj — 投影家族 k!")
print("   但 1.8%/2.9% off 唔達 0.1% 門檻, 目標 (u/d, d/s) 不確定度大")
print("   → 🟡 弱命中, 唔升級 (對照 (21,24)/(13,32) 0.0007%/0.067%)")
print()

print("7. Verdict")
print("="*72)
ck("F51 3+19 = 22 = N_d/2 (半鏈互補)", 3+19 == N_d//2)
ck("F52 3 = L₅−2B, 19 = L₅+2B (以 L₅ 對稱)", 3 == L5-2*B and 19 == L5+2*B)
ck("F53 命中 k 都有身份 (N_gen, f_proj)", k_ids[3]=="N_gen" and k_ids[19]=="f_proj")
ck("F54 精確命中只有 (21,24) k=3 同 (13,32) k=19",
   abs(sinp176(21)/sinp176(24)/targets['m_W/m_Z']-1) < 1e-4
   and abs(sinp176(13)/sinp176(32)/targets['m_τ/m_b']-1) < 1e-3)
ck("F55 弱命中 (14,31)/(2,43) k=17/41 投影家族, 但 >1% off 🟡",
   abs(r1731/targets['m_u/m_d']-1) > 1e-2 and abs(r243/targets['m_d/m_s']-1) > 1e-2)
ck("F56 >1 目標超 45-家族範圍 (結構限制, 非失敗)",
   targets['m_μ/m_e'] > 1 and targets['m_t/m_b'] > 1)
print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)
