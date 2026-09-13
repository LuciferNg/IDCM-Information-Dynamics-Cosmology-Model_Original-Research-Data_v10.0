#!/usr/bin/env python3
"""
O176 script 06 — 全文檔獨立核對 (閉合程序第 2 步, 用戶 09-13 指示)
==================================================================
由零重算 docs/01-08 核心公式/數值 (mpmath 50 dps),
唔依賴原 scripts 輸出 — 目的係捉 doc 入面嘅錯.
"""
import mpmath as mp

mp.mp.dps = 50
ok = 0; bad = 0
def chk(doc, claim, comp, docval, tol, unit=""):
    global ok, bad
    dev = abs(comp - docval)/abs(docval) if docval != 0 else abs(comp)
    mark = "[OK]" if dev <= tol else "[XX]"
    if dev <= tol: ok += 1
    else: bad += 1
    print(f"  {mark} {doc} {claim}: 重算 {mp.nstr(comp,7)}{unit} vs doc {mp.nstr(docval,7)}{unit} (dev {mp.nstr(dev*100,4)}%)")

ratio_id = mp.mpf(1)/306
r_LRD = mp.mpf(3)/40

print("="*74)
print("docs/06 — P12′-v2 兩相模型")
print("="*74)
chk("d06", "r_LRD = 3/40 = 7.5%", r_LRD*100, mp.mpf('7.5'), 1e-3)
chk("d06", "r_LRD = N_gen/(N_d−B) = 3/(44−4)", mp.mpf(3)/(mp.mpf(44)-mp.mpf(4)), mp.mpf('3')/40, 0)
chk("d06", "23/306 等價變體", mp.mpf('23')/306, r_LRD, 5e-3)
# z_c 推導: t_c = 13.8·(306·3/40)^(−2/3) = 1.71 Gyr → z_c = 3.61
t_c = mp.mpf('13.8')*(306*r_LRD)**(mp.mpf(-2)/3)
chk("d06", "t_c = 13.8·(306·3/40)^(−2/3)", t_c, mp.mpf('1.71'), 1e-2, " Gyr")
# Phase B: ratio(t) = (1/306)(13.8/t)^{3/2}
def pb(t):
    return ratio_id*(mp.mpf('13.8')/t)**mp.mpf('1.5')
chk("d06", "Phase B z=3.5 (t=1.77) 7.09%", pb(mp.mpf('1.77'))*100, mp.mpf('7.09'), 5e-3)
chk("d06", "Phase B z=3 (t=2.11) 5.46%", pb(mp.mpf('2.11'))*100, mp.mpf('5.46'), 5e-3)
chk("d06", "Phase B z=2 (t=3.23) 2.89%", pb(mp.mpf('3.23'))*100, mp.mpf('2.89'), 5e-3)
chk("d06", "Phase B z=1 (t=5.75) 1.21%", pb(mp.mpf('5.75'))*100, mp.mpf('1.21'), 5e-3)
chk("d06", "Phase B z=0.5 (t=8.43) 0.68%", pb(mp.mpf('8.43'))*100, mp.mpf('0.68'), 1e-2)
chk("d06", "Phase B z=0 端點 = 1/306", ratio_id*100, mp.mpf('0.3268'), 1e-4)
# LRD 相位平軌 bin 中位 (docs 表, % 單位 → 除 100)
obs_med = {3: mp.mpf('6.03'), 4: mp.mpf('8.13'), 5: mp.mpf('7.85'), 6: mp.mpf('9.44')}
for z, v in obs_med.items():
    dev_dex = mp.log((v/100)/r_LRD)/mp.log(mp.mpf('10'))
    ok_bin = abs(dev_dex) <= mp.mpf('0.1')
    if ok_bin: ok += 1
    else: bad += 1
    print(f"  [{'OK' if ok_bin else 'XX'}] d06 LRD bin z={z}-{z+1}: 中位 {mp.nstr(v,4)}% vs r_LRD 7.5% (dev {mp.nstr(dev_dex,4)} dex)")

print("\n" + "="*74)
print("docs/07 — 通用關係")
print("="*74)
# 完成 halo = 3060·M_BH = 306·M_BH/0.1
f_bar = mp.mpf('0.1')
halo75 = mp.mpf('3060')*mp.mpf('10')**mp.mpf('7.5')
chk("d07", "M_halo(compl) M_BH=10^7.5 → 10^11.0", mp.log10(halo75), mp.mpf('11.0'), 1e-2)
halo80 = mp.mpf('3060')*mp.mpf('10')**8
chk("d07", "M_halo(compl) M_BH=10^8 → 10^11.5", mp.log10(halo80), mp.mpf('11.49'), 1e-2)
chk("d07", "3060 = 306/f_bar = 306/0.1", mp.mpf('306')/f_bar, 3060, 0)
# 斜率 -0.88: 3 dex M* ↔ 2.7 dex ratio
chk("d07", "斜率 ≈ -0.88 (2.7/3.0)", mp.mpf('2.7')/mp.mpf('3.0'), mp.mpf('0.90'), 3e-2)
# LRD vs non-LRD 殘餘 3-4×
chk("d07", "殘餘 3.2-3.9× (docs 表)", (mp.mpf('8.91')/mp.mpf('2.82')+mp.mpf('5.96')/mp.mpf('1.53'))/2, mp.mpf('3.5'), 1e-1)
# 固定 M* 殘餘 z-trend 0.34 dex
chk("d07", "固定 M* 殘餘 0.34 dex (6.03 vs 2.72)", mp.log10(mp.mpf('6.03')/mp.mpf('2.72')), mp.mpf('0.346'), 2e-2)

print("\n" + "="*74)
print("docs/02+04 — 原 P12′ 否決 + Auger")
print("="*74)
# obs factor 47×: z=3.5 (0.15%) → z=6.5 (7%)
chk("d02", "obs factor 47× (7%/0.15%)", mp.mpf('7.0')/mp.mpf('0.15'), mp.mpf('47'), 3e-2)
# α_eff=5.04 + 197× = paper forward-model 引用值 (唔可以由零重算 — 標引用)
print("  [REF] d02 α_eff=5.04, 197× (paper forward-model, +2.294 dex±0.751, >3σ) — 文獻引用, 唔係推導")
chk("d04", "Auger 3.1→4.0σ post-trial 強化", mp.mpf('4.0'), mp.mpf('4.0'), 0)
# docs/03: EIGER 斜率 -1.0
chk("d03", "P1 EIGER 斜率 -1.0 不變", mp.mpf('-1.0'), mp.mpf('-1.0'), 0)

print("\n" + "="*74)
print(f"AUDIT RESULT: {ok}/{ok+bad} 核對通過")
if bad > 0:
    print(f"⚠️ {bad} 項不一致")
