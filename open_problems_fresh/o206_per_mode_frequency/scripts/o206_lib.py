#!/usr/bin/env python3
"""
O206 — 共用工具 (唯讀上游, 不修改任何上游檔案)
=========================================================
提供:
  * 88-site 鏈模 ψ_n(i) = sin(nπi/89)  (O136 scripts/41/59 慣例)
  * 位置算子 V = ⟨n|X|m⟩,  X = diag(i − ⟨i⟩)   [精確 Z₂-奇]
  * 環譜 E_n = 4sin²(nπ/88)  (O136/O169 慣例) 與 其他慣例譜
  * 對數度量 logscore (O136 scripts/59 §定義, 秩配對)
  * 9 個費米子質量 + A₅ 模式集
⚠️ 慣例標籤: 本 lib 內每個譜函數名都帶慣例 (ring44 / dd88 / o159_88)
"""
import math
import numpy as np

NC = 88           # 鏈長 (site 數)
ND = 44           # N_d
MU2 = 2.0         # μ²
MU4 = 4.0         # μ⁴ = γ_max (ring 慣例)
B_ = 4

# 9 個費米子質量 (MeV) — O136 慣例
MASS = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
MODE_OF = {"t": 1, "b": 2, "tau": 3, "c": 4, "mu": 5, "s": 7, "d": 9, "u": 11, "e": 13}
A5_MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
SORTED_PARTICLES = sorted(MASS, key=lambda p: MASS[p])          # e,u,d,s,mu,c,tau,b,t
LM = np.array([math.log(MASS[p]) for p in SORTED_PARTICLES])    # 升序 log 質量
MODES_SORTED = [MODE_OF[p] for p in SORTED_PARTICLES]           # 13,11,9,7,5,4,3,2,1
NEED = 0.05                                                     # 閉合門檻 (RMS)


def chain_psi(nc=NC):
    """88-site D-D 鏈模 (O136 慣例)"""
    x = np.arange(1, nc + 1, dtype=float)
    P = np.zeros((nc, nc))
    for n in range(1, nc + 1):
        P[:, n - 1] = np.sin(n * math.pi * x / (nc + 1))
    for n in range(nc):
        P[:, n] /= np.linalg.norm(P[:, n])
    return P, x


def V_position(nc=NC):
    """位置算子耦合 V_nm = ⟨n|X|m⟩, X = diag(i − ⟨i⟩) — 精確 Z₂-奇"""
    P, x = chain_psi(nc)
    return P.T @ np.diag(x - x.mean()) @ P


def E_ring44(nc=NC):
    """[慣例=44-site ring / O136·O169] E_n = 4sin²(nπ/88), n=1..88"""
    return np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, nc + 1)])


def E_dd88(nc=NC):
    """[慣例=D-D 88 鏈] λ_k = 2 − 2cos(kπ/89), k=1..88 (ψ_n 之真本徵值)"""
    return np.array([2 - 2 * math.cos(k * math.pi / (nc + 1)) for k in range(1, nc + 1)])


def E_o159_88(nc=NC):
    """[慣例=88-site O159 半格] γ_k = 4sin²(kπ/176) = |1−e^{ikπ/88}|², k=1..88"""
    return np.array([4 * math.sin(k * math.pi / 176) ** 2 for k in range(1, nc + 1)])


def logscore(vals, LMv=None):
    """★ 冪律對數度量 (O136 scripts/59): 秩配對 ln m ↔ ln|f|, RMS = σ_y·√(1−ρ²)"""
    y = LM if LMv is None else LMv
    v = np.abs(np.array(vals, dtype=float))
    if (v <= 0).any() or v.std() < 1e-14:
        return 9e9
    lv = np.log(v)
    if lv.std() < 1e-14:
        return 9e9
    xs = np.sort(lv)
    ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std() * math.sqrt(max(0.0, 1.0 - r * r)))


def sum_V2_dE(E, V, modes=A5_MODES, nc=NC):
    """|Δm_n| = |Σ_{m: parity 反} V_nm² / (E_n − E_m)| — O136 權威定義"""
    out = []
    for n in modes:
        idx = [m for m in range(nc) if m != n - 1 and (m - (n - 1)) % 2 == 1]
        dE = E[n - 1] - E[idx]
        aV2 = np.abs(V[n - 1, idx]) ** 2
        out.append(abs(float((aV2 / dE).sum())))
    return np.array(out)


def signed_sum_V2_dE(E, V, modes=A5_MODES, nc=NC):
    """帶號 Σ_n = Σ_m V_nm²/(E_n − E_m)"""
    out = []
    for n in modes:
        idx = [m for m in range(nc) if m != n - 1 and (m - (n - 1)) % 2 == 1]
        dE = E[n - 1] - E[idx]
        aV2 = np.abs(V[n - 1, idx]) ** 2
        out.append(float((aV2 / dE).sum()))
    return np.array(out)
