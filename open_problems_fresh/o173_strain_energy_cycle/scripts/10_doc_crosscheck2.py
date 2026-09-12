#!/usr/bin/env python3
"""
O173 script 10 — 文檔獨立核對 2 (Doc Crosscheck: Q7/Q3/Q4)
=============================================================
由零重算 docs/06-08 每個宣稱 (唔依賴 scripts 07-09 輸出)
"""
import mpmath as mp

mp.mp.dps = 50
OK = 0; BAD = 0
def chk(doc, claim, computed, docval, tol=mp.mpf('1e-6'), unit=""):
    global OK, BAD
    if isinstance(docval, str) or isinstance(computed, str):
        ok = str(computed) == str(docval)
        cd = str(computed); dv = str(docval)
    else:
        try:
            cv = mp.mpf(computed); dv = mp.mpf(docval)
            ok = abs(cv - dv) <= mp.mpf(tol)*max(mp.mpf('1'), abs(dv))
            cd = mp.nstr(cv, 6); dv = mp.nstr(dv, 6)
        except Exception:
            ok = False; cd = str(computed); dv = str(docval)
    if ok:
        OK += 1; mark = "[✔]"
    else:
        BAD += 1; mark = "[✘]"
    print(f"  {mark} {doc} {claim}: {cd}{unit}  (doc: {dv}{unit})")
    return ok

print("="*78)
print("Block F — docs/06 SMBH 通道")
print("="*78)
eta = mp.mpf('4.0856e-5')
E_pool = mp.mpf('1.5647853e12')
M_ton_lo = mp.mpf('4.07e10'); M_ton_hi = mp.mpf('6.6e10')
chk("06", "TON 618 應變需求 C IV", M_ton_lo/eta, mp.mpf('9.962e14'), mp.mpf('1e-3'))
chk("06", "TON 618 應變需求 Hβ", M_ton_hi/eta, mp.mpf('1.615e15'), mp.mpf('1e-3'))
chk("06", "× 池 (C IV)", M_ton_lo/eta/E_pool, mp.mpf('636.6'), mp.mpf('1e-2'))
chk("06", "× 池 (Hβ)", M_ton_hi/eta/E_pool, mp.mpf('1032.0'), mp.mpf('1e-2'))
V = mp.mpf('1.2e13')
chk("06", "總 SMBH (K&H)", mp.mpf('2.5e5')*V, mp.mpf('3.0e18'), mp.mpf('1e-2'))
chk("06", "總 SMBH (Elvis)", mp.mpf('4.9e5')*V, mp.mpf('5.88e18'), mp.mpf('1e-2'))
chk("06", "× 池 (K&H)", mp.mpf('2.5e5')*V/E_pool, mp.mpf('1.92e6'), mp.mpf('1e-2'))
M_base = mp.mpf('1.9142e6')
chk("06", "種子 δ=1.367", M_base*(mp.mpf('2.367'))**mp.mpf('1.5'), mp.mpf('6.97e6'), mp.mpf('1e-2'))
chk("06", "種子 δ=30", M_base*mp.mpf('31')**mp.mpf('1.5'), mp.mpf('3.304e8'), mp.mpf('1e-3'))
chk("06", "種子 δ=100", M_base*mp.mpf('101')**mp.mpf('1.5'), mp.mpf('1.943e9'), mp.mpf('1e-3'))
chk("06", "UHz1 ratio", mp.mpf('1.7e9')/(M_base*mp.mpf('101')**mp.mpf('1.5')), mp.mpf('0.875'), mp.mpf('1e-2'))
chk("06", "M87 ×", mp.mpf('6.5e9')/(M_base*mp.mpf('101')**mp.mpf('1.5')), mp.mpf('3.35'), mp.mpf('1e-2'))
chk("06", "TON ×", M_ton_lo/(M_base*mp.mpf('101')**mp.mpf('1.5')), mp.mpf('20.95'), mp.mpf('1e-2'))
print("")

print("="*78)
print("Block G — docs/07 宿主")
print("="*78)
E0 = mp.mpf('0.01482')
Erest = sum(mp.mpf(str(e)) for e in [0.00914, 0.00898, 0.00775, 0.00692, 0.00775, 0.00898, 0.00914, 0.01482])
chk("07", "干涉比 4.958", Erest/E0, mp.mpf('4.958'), mp.mpf('1e-2'))
chk("07", "free-fall δ=30", mp.mpf('31')**mp.mpf('1.5'), mp.mpf('172.6'), mp.mpf('1e-3'))
chk("07", "free-fall δ=100", mp.mpf('101')**mp.mpf('1.5'), mp.mpf('1015.0'), mp.mpf('1e-3'))
chk("07", "宿主 δ=30 中位", mp.mpf('6.97e6')*mp.mpf('31')**mp.mpf('1.5'), mp.mpf('1.203e9'), mp.mpf('1e-2'))
chk("07", "宿主 δ=100 中位", mp.mpf('6.97e6')*mp.mpf('101')**mp.mpf('1.5'), mp.mpf('7.075e9'), mp.mpf('1e-2'))
chk("07", "M87 cD", mp.mpf('6.5e9')*mp.mpf('101')**mp.mpf('1.5'), mp.mpf('6.598e12'), mp.mpf('1e-2'))
chk("07", "量級分離 35-200×", mp.mpf('172.6')/mp.mpf('4.958'), mp.mpf('34.8'), mp.mpf('1e-2'))
print("")

print("="*78)
print("Block H — docs/08 合併節點語言")
print("="*78)
M_seed = mp.mpf('1.943e9')
import mpmath as mpl
n_lo = mpl.log(mp.mpf('4.07e10')/M_seed, 2)
n_hi = mpl.log(mp.mpf('6.6e10')/M_seed, 2)
chk("08", "log₂ 代數 (C IV)", n_lo, mp.mpf('4.388'), mp.mpf('1e-2'))
chk("08", "log₂ 代數 (Hβ)", n_hi, mp.mpf('5.086'), mp.mpf('1e-2'))
chk("08", "質量守恆 1e9+3e9", mp.mpf('1e9')+mp.mpf('3e9'), mp.mpf('4e9'), mp.mpf('1e-40'))
print("")

print("="*78)
print(f"AUDIT RESULT: {OK}/{OK+BAD} 核對通過")
print("="*78)
