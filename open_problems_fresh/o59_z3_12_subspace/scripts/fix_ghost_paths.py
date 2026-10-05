#!/usr/bin/env python3
"""
O59 closeout: fix ghost-tree hardcoded BASE paths + DATA repoint (2026-10-05).
- BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0" (ghost) -> computed repo root
- BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat" -> computed repo root
- DATA = os.path.join(BASE, "data") -> os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
Only touches scripts/ inside this O. Idempotent.
"""
import os, re, sys, pathlib

O_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent  # o59 dir
SCRIPTS = O_DIR / "scripts"

GHOST = 'BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"'
REAL  = 'BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"'
NEW_BASE = 'BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))'
OLD_DATA = 'DATA = os.path.join(BASE, "data")'
NEW_DATA = 'DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")'

changed = []
for p in sorted(SCRIPTS.glob("*.py")):
    if p.name == "fix_ghost_paths.py":
        continue
    txt = p.read_text(encoding="utf-8")
    orig = txt
    if GHOST in txt:
        txt = txt.replace(GHOST, NEW_BASE)
    if REAL in txt:
        txt = txt.replace(REAL, NEW_BASE)
    if OLD_DATA in txt:
        txt = txt.replace(OLD_DATA, NEW_DATA)
    if txt != orig:
        p.write_text(txt, encoding="utf-8")
        changed.append(p.name)
print(f"changed {len(changed)} files:")
for c in changed:
    print("  ", c)