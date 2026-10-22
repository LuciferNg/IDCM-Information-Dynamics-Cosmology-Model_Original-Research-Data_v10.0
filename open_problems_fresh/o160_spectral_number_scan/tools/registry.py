# -*- coding: utf-8 -*-
"""registry.py — 譜幾何張量工具統一註冊表 (O160 R1)

橋接 4 個獨立項目 (sys.path 注入, 唔需要 pip install):
  CSG   /home/wsl/Projects/ChronologicalStringSpectralGeometry
  KTSG  /home/wsl/Projects/KTreeSpectralGeometry
  V2    /home/wsl/Projects/ChronologicalStringSpectralGeometry-v2
  FSR   <IDCM>/open_problems_fresh/o140_finite_spectral_relativity

每個 tool 有: path, module, api, smoke test, 譜輸出函數。
掃描器 (scripts/03) 用 get_spectra() 攞統一本徵值 — 單一真源頭。
"""
import sys
import io
import importlib.util
import contextlib
from pathlib import Path

O160 = Path(__file__).resolve().parent.parent
OPF = O160.parent  # open_problems_fresh/
IDCM_ROOT = OPF.parent  # IDCM-v10.0--It-From-Beat/
PROJECTS = Path("/home/wsl/Projects")

TOOLS = {
    "csg": {
        "name": "CSG SpectralSpace (K_Chain 版譜張量)",
        "path": PROJECTS / "ChronologicalStringSpectralGeometry",
        "file": "src/spectral_tensor.py",
        "api": ["SpectralSpace(N_d, tree_spectrum, B)",
                "IDCMSpace() / ChromaticSpace() (instances)",
                "beat_tensor / spectral_gap / projection / dispersion"],
        "smoke": "SpectralSpace(44, np.ones(5)).total_energy() > 0",
        "integ": ["python3 -m src.instances.idcm", "python3 -m src.instances.music"],
    },
    "ktsg": {
        "name": "KTreeSpectralGeometry (K_Tree 版雙矩陣平台)",
        "path": PROJECTS / "KTreeSpectralGeometry",
        "file": "src/dual_matrix.py",
        "api": ["DualMatrix(N_d=44, n_tree=33)",
                "DockingPlatform (6 docks: Parity/Embedding/FieldBridge/ScaleLadder/Home/Generation)",
                "KTreeSpectralTensor (三層視圖, CSG 相容)"],
        "smoke": "DualMatrix().sum_Gamma() == 5940",
        "integ": ["python3 -m src.tests.test_platform",
                  "python3 -m src.docking", "python3 -m src.spectral_tensor",
                  "python3 -m src.instances.idcm", "python3 -m src.instances.string_space"],
    },
    "v2": {
        "name": "CSG-v2 v2core (T̂ 代數零參數核心)",
        "path": PROJECTS / "ChronologicalStringSpectralGeometry-v2",
        "file": "src/v2core.py",
        "api": ["gamma_n(n) = 4sin²(nπ/88), omega_n(n) = sin(nπ/88)",
                "F(n)/L(n) (T̂ 譜), M_TREE=33, E_PROJ=57/2, E_SYNC=123/2"],
        "smoke": "gamma_sum() == 90.0",
        "integ": [],
    },
    "fsr": {
        "name": "O140 FSR (有限譜相對論)",
        "path": OPF / "o140_finite_spectral_relativity",
        "file": "scripts/01_verify_fsr_identities.py",
        "api": ["gamma44(n)/gamma88(k) = 4sin²(...), vg(n), gamma_fsr(n) = csc(nπ/2N)",
                "eta(N,n) rapidity, doppler(N,n), gamma_max(l) 尺度精化"],
        "smoke": "abs(gamma_fsr(20)**2 * gamma44(20) - 4.0) < 1e-9",
        "integ": ["python3 scripts/01_verify_fsr_identities.py",
                  "python3 scripts/02_generic_n_verification.py"],
    },
}


def load(tool: str):
    """直接載入 tool 源檔 (spec_from_file_location), 避開跨項目 src 碰撞.

    返回 module; 獨特 module name = o160_<tool>_<basename>.
    """
    t = TOOLS[tool]
    fpath = t["path"] / t["file"]
    mname = f"o160_{tool}_{fpath.stem}"
    if mname in sys.modules:
        return sys.modules[mname]
    spec = importlib.util.spec_from_file_location(mname, fpath)
    mod = importlib.util.module_from_spec(spec)
    # FSR script 有 top-level 打印, import 時靜音
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    sys.modules[mname] = mod
    return mod


def probe(tool: str, verbose=True) -> bool:
    """Smoke test 單一 tool. 返回 True = 可用."""
    t = TOOLS[tool]
    try:
        m = load(tool)
        if tool == "csg":
            ok = m.SpectralSpace(44, [1, 1, 1, 1, 1]).total_energy() > 0
        elif tool == "ktsg":
            dm = m.DualMatrix()
            ok = abs(dm.sum_Gamma() - 5940.0) < 1e-9
        elif tool == "v2":
            ok = abs(m.gamma_sum() - 90.0) < 1e-9
        elif tool == "fsr":
            ok = abs(m.gamma_fsr(20) ** 2 * m.gamma44(20) - 4.0) < 1e-9
        else:
            ok = m is not None
        if verbose:
            print(f"  [{'PASS' if ok else 'FAIL'}] {tool:5s} {t['name']}")
        return ok
    except Exception as e:
        if verbose:
            print(f"  [FAIL] {tool:5s} {t['name']} — {type(e).__name__}: {e}")
        return False


def probe_all(verbose=True) -> int:
    """全部 tool smoke test. 返回 PASS 數."""
    n = sum(1 for t in TOOLS if probe(t, verbose))
    if verbose:
        print(f"RESULT: {n}/{len(TOOLS)} tools ready")
    return n


def integrate(tool: str, verbose=True) -> bool:
    """Integration test: 喺 tool 自己 root 跑官方入口 (subprocess)."""
    import subprocess
    t = TOOLS[tool]
    all_ok = True
    for cmd in t.get("integ", []):
        r = subprocess.run(cmd, shell=True, cwd=str(t["path"]),
                           capture_output=True, text=True, timeout=300)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ""
        ok = r.returncode == 0
        all_ok = all_ok and ok
        if verbose:
            print(f"    [{'PASS' if ok else 'FAIL'}] {cmd}  ({tail[:80]})")
    return all_ok


def get_spectra():
    """統一本徵值 (掃描器真源頭) — numpy float64 數組 + mpmath 版本.

    慣例 (O155 量→譜對照表):
      γ_k = 4sin²(kπ/176)  k=1..88   (88-site 對偶鏈, 主框架)
      ω_k = 2sin(kπ/176)   k=1..88   (頻率)
      λ_c = 4sin²(cπ/68)   c=1..33   (K_Tree Dirichlet)
      γ_fsr(k) = csc(kπ/176)         (FSR Lorentz 階梯 = 2/ω_k)

    44-chain 次框架 (對照用):
      γ44_n = 4sin²(nπ/88), ω44_n = 2sin(nπ/88), n=1..44
    """
    import numpy as np
    import mpmath as mp

    mp.mp.dps = 50
    k = np.arange(1, 89)
    c = np.arange(1, 34)
    n = np.arange(1, 45)
    gamma = 4.0 * np.sin(k * np.pi / 176.0) ** 2
    omega = 2.0 * np.sin(k * np.pi / 176.0)
    lam = 4.0 * np.sin(c * np.pi / 68.0) ** 2
    gamma_fsr = 1.0 / np.sin(k * np.pi / 176.0)
    gamma44 = 4.0 * np.sin(n * np.pi / 88.0) ** 2
    omega44 = 2.0 * np.sin(n * np.pi / 88.0)
    return dict(gamma=gamma, omega=omega, lam=lam, gamma_fsr=gamma_fsr,
                gamma44=gamma44, omega44=omega44)


def invariants(a: int, b: int, c: int, mpmath=True):
    """單格 (a,b,c) 全部不變量 — mpmath 50 dps 精確值.

    回傳 dict: family -> mp.mpf 值.
      R88   γ_a/γ_b          (純鏈比)
      O88   ω_a/ω_b          (頻率比 = FSR γ 比, 恆等)
      BEAT  |ω_a−ω_b|        (拍頻)
      GT    γ_a·λ_c, γ_a/λ_c (鏈×樹)
      OT    ω_a·λ_c, ω_a/λ_c
      FULL  (ω_a/ω_b)·λ_c, (γ_a/γ_b)·λ_c, (γ_a/γ_b)/λ_c, |ω_a−ω_b|·λ_c
      SUM   γ_a+γ_b+λ_c, γ_a+γ_b−λ_c
    """
    import mpmath as mp
    mp.mp.dps = 50
    s = mp.sin
    pi = mp.pi
    ga = 4 * s(a * pi / 176) ** 2
    gb = 4 * s(b * pi / 176) ** 2
    wa = 2 * s(a * pi / 176)
    wb = 2 * s(b * pi / 176)
    lc = 4 * s(c * pi / 68) ** 2
    out = {
        "R88": ga / gb, "O88": wa / wb, "BEAT": abs(wa - wb),
        "GT_prod": ga * lc, "GT_div": ga / lc,
        "OT_prod": wa * lc, "OT_div": wa / lc,
        "FULL_wr": (wa / wb) * lc, "FULL_gr": (ga / gb) * lc,
        "FULL_gd": (ga / gb) / lc, "FULL_beat": abs(wa - wb) * lc,
        "SUM_plus": ga + gb + lc, "SUM_minus": ga + gb - lc,
    }
    return out
