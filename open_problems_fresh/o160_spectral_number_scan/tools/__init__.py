# -*- coding: utf-8 -*-
"""idcm-spectral-tools — 譜幾何張量工具統一註冊層 (O160)

4 套工具:
  1. CSG  (K_Chain 版譜張量)     ChronologicalStringSpectralGeometry
  2. KTSG (K_Tree 版譜張量平台)  KTreeSpectralGeometry
  3. v2   (T̂ 代數零參數核心)     ChronologicalStringSpectralGeometry-v2
  4. FSR  (有限譜相對論)         open_problems_fresh/o140_finite_spectral_relativity

用法 (agent):
    from tools.registry import probe_all, get_spectra, invariants
    probe_all()                    # 全部工具 smoke test PASS/FAIL
    gamma, omega, lam, fsr = get_spectra()   # 統一本徵值 (numpy)
    invariants(a, b, c)            # 單格全部不變量 (mpmath)

CLI:
    python3 tools/cli.py list
    python3 tools/cli.py probe
    python3 tools/cli.py invariants 21 24 33
"""
