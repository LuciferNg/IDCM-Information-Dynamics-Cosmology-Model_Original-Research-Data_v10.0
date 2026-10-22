#!/usr/bin/env python3
"""
O9-D9: ACT DR4 正確解析 — deep+wide, TT/TE/EE
=================================================
cl_cmb_ap.dat: 260 行
- deep (130): TT 40 + TE 45 + EE 45
- wide (130): TT 40 + TE 45 + EE 45

但 Binning.dat 得 52 行 — 唔對?
睇 pyactlike 點用 binning
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D9: ACT DR4 正確解析")
print("="*80)

# 睇 like.py 更多
import subprocess
r = subprocess.run(['grep', '-n', 'bval\|binning\|Binning\|l_bin', 'pyactlike/like.py'], capture_output=True, text=True, cwd=DATADIR)
print("like.py 相關行:")
print(r.stdout)

# 睇 test_like.py
r2 = subprocess.run(['cat', 'test_like.py'], capture_output=True, text=True, cwd=DATADIR)
print("\ntest_like.py:")
print(r2.stdout[:2000])
