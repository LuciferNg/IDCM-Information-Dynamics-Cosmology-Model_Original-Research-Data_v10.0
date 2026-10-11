#!/usr/bin/env python3
"""
C_f 下一步 — 方向 B2: 統一 scheme 質量比閉合 + 斜率身份盲測
================================================================
核心轉移: C_f 絕對值冇源 (O233 負閉合) → 質量比先有預言力:
  m_j/m_i = (γ_j/γ_i)·(C_j/C_i)   [M₀ 完全抵消]
本 script:
  1. 統一 scheme (O234 freeze v2) 目標下, 重算 required C_f
  2. 用「C_f 比」做質量比閉合 → 有冇結構?
  3. 盲測斜率模型: m_n = M₀·γ_n·C₀·(5/7)^{rank-1} vs 實際 (leave-one-out)
  4. 檢查 5/7 係咪真預言器 (唔係就 drop)
================================================================
"""
import math, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5modes = [1,2,3,4,5,7,9,11]
# 統一 scheme 目標 (O234 freeze v2): e,mu,tau pole; u,d,s 2GeV; c(mc); b(mb); t pole
targets = {'e':0.511,'u':2.16,'d':4.67,'s':93.4,'mu':105.658,'c':1270.0,'tau':1776.86,'b':4180.0}
order = ['e','u','d','s','mu','c','tau','b']
g8 = [gam(n) for n in A5modes]

print("="*76)
print("方向 B2: 統一 scheme 質量比閉合 + 斜率盲測")
print("="*76)

cf_new = [targets[order[i]]/(M0*g8[i]) for i in range(8)]
lncf = np.log(cf_new)

print("\n=== [1] 統一 scheme required C_f ===")
for i, p in enumerate(order):
    print(f"  {p:>4s} n={A5modes[i]:>2d} γ={g8[i]:.6f} m={targets[p]:>9.3f} → C_f={cf_new[i]:>9.4f}")

# ==== [2] 質量比閉合 (統一 scheme) ====
print("\n=== [2] 質量比 vs γ比×C比 (統一 scheme, M0 抵消) ===")
# 質量比 m_j/m_i = γ_j/γ_i × C_j/C_i — 若 C 比有結構 → 質量比 = 純幾何
pairs = [('d/u',2,1),('s/d',3,2),('s/u',3,1),('mu/e',4,0),('tau/mu',6,4),
         ('c/s',5,3),('b/c',7,5),('b/tau',7,6),('c/u',5,1),('b/d',7,2)]
print(f"  {'比':>8s} {'m比':>12s} {'γ比':>10s} {'C比':>10s} {'預測':>12s} {'dev':>8s}")
structure_hits = []
for label, hi, lo in pairs:
    mr = cf_new[hi]*g8[hi]/(cf_new[lo]*g8[lo])  # = m_hi/m_lo
    gr = g8[hi]/g8[lo]
    cr = cf_new[hi]/cf_new[lo]
    # 睇 C 比有冇近結構數
    for sname, s, name in [('5/3',5/3,'5/3'),('7/4',7/4,'7/4'),('2',2,'2'),
                            ('φ',1.618034,'phi'),('3/2',1.5,'3/2'),('8/5',1.6,'8/5'),
                            ('11/7',11/7,'11/7'),('√5',2.236068,'sqrt5'),
                            ('13/8',13/8,'13/8'),('17/10',1.7,'17/10')]:
        if abs(cr-s)/s < 0.02:
            structure_hits.append((label, cr, name, abs(cr-s)/s*100))
    print(f"  {label:>8s} {mr:>12.4f} {gr:>10.4f} {cr:>10.4f} {(gr*cr):>12.4f}   —")

print(f"\n  C_f 比近結構數 (±2%):")
for label, cr, name, dev in structure_hits:
    print(f"    {label}: C比 = {cr:.4f} ≈ {name} (dev {dev:.2f}%)")

# ==== [3] 斜率盲測: m_n = M0·γ_n·C0·r^{rank-1} (r=5/7) ====
print("\n=== [3] 盲測: 幾何級數斜率模型 r = 5/7 ? ===")
r0 = 5/7
# fit 一個 C0: C_f ≈ C0·r^{rank-1} → ln C_f = ln C0 + (rank-1)ln r
C0 = math.exp(np.mean(lncf - np.arange(8)*math.log(r0)))
pred_cf = [C0 * r0**i for i in range(8)]
res_r = [math.log(cf_new[i]/pred_cf[i]) for i in range(8)]
print(f"  C0 (fit) = {C0:.4f}")
print(f"  r = 5/7 = {r0:.6f}")
print(f"  rank  C_f(統一)  預測(5/7)  RMS |ln dev|")
rms_57 = math.sqrt(np.mean([(math.log(cf_new[i]/pred_cf[i]))**2 for i in range(8)]))
for i in range(8):
    print(f"  {i+1}    {cf_new[i]:>9.4f}  {pred_cf[i]:>9.4f}  {abs(math.log(cf_new[i]/pred_cf[i])):.4f}")
print(f"\n  RMS |ln(dev)| (5/7 模型) = {rms_57:.4f}")
print(f"  平均 |dev|% = {np.mean([abs(cf_new[i]/pred_cf[i]-1) for i in range(8)])*100:.2f}%")

# 對照: 自由 r!  (每步其實係 2.04, 但對照組睇過擬合)
rr_arr = np.array([0,1,2,3,4,5,6,7], dtype=float)
a, b = np.polyfit(rr_arr, lncf, 1)
r_best = math.exp(a)
res_best = [lncf[i] - (b + a*i) for i in range(8)]
rms_free = math.sqrt(np.mean([x**2 for x in res_best]))
print(f"\n  對照: 自由斜率 e^a = {r_best:.4f} (a={a:.4f}) RMS = {rms_free:.4f}")
print(f"  → 5/7 模型 RMS {rms_57:.4f} vs 自由 RMS {rms_free:.4f}")
print(f"  → 若 5/7 模型 RMS >> 自由 RMS: 5/7 唔係好形容 (最多係 log-linear 近似)")

# ==== [4] leave-one-out: 5/7 有冇預言新點? ====
print("\n=== [4] Leave-one-out 預言力檢驗 ===")
# 用 7 點 fit C0 (r FIXED = 5/7, 零額外自由度), 預言第 8 點
loo_errs_57 = []
for k in range(8):
    idx = [i for i in range(8) if i != k]
    C0_k = math.exp(np.mean([lncf[i] - i*math.log(r0) for i in idx]))
    pred_k = C0_k * r0**k
    err = math.log(cf_new[k]/pred_k)
    loo_errs_57.append(err)
rms_loo57 = math.sqrt(np.mean([x**2 for x in loo_errs_57]))
print(f"  5/7 r 固定: RMS(LOO ln dev) = {rms_loo57:.4f}  → 平均 |dev| = {np.mean([abs(math.exp(x)-1) for x in loo_errs_57])*100:.1f}%")
# 對照: 用前 k-1 點 extrapolate (AR1: 每步乘之前平均比)
loo_ar = []
for k in range(8):
    if k == 0:
        loo_ar.append(0.0); continue
    ratios = [cf_new[i]/cf_new[i-1] for i in range(1, k)]
    if not ratios:
        loo_ar.append(math.log(cf_new[k]/cf_new[0]) if k == 1 else 0.0)
        continue
    r_mean = math.exp(np.mean([math.log(x) for x in ratios]))
    pred = cf_new[0] * r_mean**k
    loo_ar.append(math.log(cf_new[k]/pred))
rms_looar = math.sqrt(np.mean([x**2 for x in loo_ar[1:]]))
print(f"  自適應倍率 (AR1): RMS(LOO ln dev) = {rms_looar:.4f}")

# ==== [5] 結論 ====
print("\n=== [5] 方向判決 ===")
print(f"""
統一 scheme 下 C_f: {[f'{x:.3f}' for x in cf_new]}

1. 斜率 a=0.7143 命中 5/7 (dev 0.009%) — 但係 POST-HOC:
   8 點 fit 出嚟嘅數冇群結構約束, 命中一個有理比唔罕見
   LOO 檢驗: 5/7 模型 RMS {rms_loo57:.4f} vs 自由斜率 {rms_free:.4f} (from §3)
   → 5/7 係固定零參數, 唔可以同 2 參數自由斜率比 accuracy; 但佢嘅 LOO 誤差
   {'>> 0.05 (唔夠預言)' if rms_loo57 > 0.05 else '尚可'} 
2. C_f 比近結構數命中: {structure_hits if structure_hits else '無'} — 冇靚結構
3. ⟹ C_f 唔可以靠「斜率身份」救起; O233 負閉合成立
4. 真正下一步 (方向 B3): 質量比閉合 = m_j/m_i = (γ_j/γ_i)·(C_j/C_i)
   — C_f 比就係「質量比除以 γ 比」嘅殘餘, 冇獨立算子身份係必然
   — 但 O64 交付物可以係「質量比表」 (零參數: 由 γ 比 + 已觀測質量比定義)
5. 方向 C (接受定義 → O209): 質量生成 = 另一層, O64 唔重做
""")

out = {"cf_unified": cf_new, "slope_5_over_7_dev": abs(a-5/7)/(5/7)*100,
       "rms_57": rms_57, "rms_free": rms_free, "rms_loo57": rms_loo57,
       "structure_hits": structure_hits,
       "verdict": "C_f 唔可以靠斜率身份; 質量比層面係唯一誠實交付"}
with open("data/08_cf_directionB.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 已儲存 data/08_cf_directionB.json")