#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cli.py — idcm-tool CLI (O160)

用法:
    python3 tools/cli.py list                     # 列出 4 套工具
    python3 tools/cli.py probe                    # smoke test 全部
    python3 tools/cli.py invariants A B C         # 單格不變量 (mpmath)
    python3 tools/cli.py spectra                  # 統一本徵值摘要
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("list", "ls", "-l"):
        from tools.registry import TOOLS
        for key, t in TOOLS.items():
            print(f"  {key:5s} {t['name']}")
            print(f"        path: {t['path']}")
            for a in t["api"]:
                print(f"        api:  {a}")
        return 0
    if args[0] == "probe":
        from tools.registry import probe_all
        return 0 if probe_all() == len(TOOLS) else 1
    if args[0] == "spectra":
        from tools.registry import get_spectra
        import numpy as np
        S = get_spectra()
        print("88-site 對偶鏈 (176-Laplacian):")
        print(f"  γ: Σ={S['gamma'].sum():.6f}  even={S['gamma'][1::2].sum():.6f}  odd={S['gamma'][0::2].sum():.6f}")
        print(f"  ω: Σ={S['omega'].sum():.6f}  γ_fsr max={S['gamma_fsr'].max():.6f}")
        print("K_Tree Dirichlet-33:")
        print(f"  λ: Σ={S['lam'].sum():.6f} (66=2K_tree)")
        print("44-chain 次框架:")
        print(f"  γ44: Σ={S['gamma44'].sum():.6f} (90)")
        return 0
    if args[0] == "invariants" and len(args) >= 4:
        from tools.registry import invariants
        a, b, c = int(args[1]), int(args[2]), int(args[3])
        for fam, v in invariants(a, b, c).items():
            print(f"  {fam:10s} = {v}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
