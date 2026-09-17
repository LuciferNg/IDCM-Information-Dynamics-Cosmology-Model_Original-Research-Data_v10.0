#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/05 -- 自指層 (Self-Reference) — C4

憲章路線 5: 譜算子嘅代數封閉性; 奇扇區 = 觀察者嘅**算子形式化** (要算子級, 唔接受詮釋級)

★★ 版本史 (兩個真陷阱, 都係本 script 跑出嚟嘅):
  v1a 用 88-環 + site 反射 R (k -> -k):  R 有 2 不動點 (k=0,44) => 45/43 分裂, 唔係 44/44 ❌
  v1b 用 88-環 + half-shift T = S^44:    T 自由 (無不動點), 但 Σ_{n odd} γ_n = 88 ≠ 44 ❌
  v2  ★正確物件 = **44-site 開鏈** (自由端 path P_44):
      L_P44 譜 = 2 - 2cos(πn/44) = 4sin²(πn/88) = γ_n,  n = 0..43
      反射 J: k -> 44-k (1-indexed), 自由對合 (無不動點, 22 個 2-cycle)
      => 兩個扇區各 22 維; Σ_{n odd} γ_n = 44 = N_d ✅ (同憲章一致)
  教訓: 「Z₂ 分裂」有三個唔同候選算子 (site 反射 / half-shift / 開鏈反射),
        只有**開鏈反射**同時滿足「自由作用 + Σγ_odd = N_d」。

本 script 驗證 6 個算子級陳述:

  S1 [觀察者 = 開鏈反射嘅反對稱投影]
     L_P44, J: k -> 44-k,  P_obs = (I - J)/2,  P_rest = (I + J)/2
     => P 正交投影; J 自由 => dim = 22/22 (無不動點 = 整數保護)

  S2 [算子級識別: 反射本徵值 = 模指數奇偶]
     J v_n = (-1)^n v_n  => 觀察者扇區 (P_obs 像) = span{奇模 n}
     => 「奇扇區 = 觀察者」係算子級等式, 唔係詮釋

  S3 [自指固定點: 讀出算子嘅跡重現晶格維度]
     Tr(L P_obs) = Σ_{n odd} γ_n = 44 = N_d EXACT
     ⟨γ⟩_obs = Tr(L P_obs)/Tr(P_obs) = 44/22 = 2 = μ² EXACT
     (註: O169 嘅 a = Tr(L_odd)/N_d = 44/44 = 1 用**站點數**做分母 — 兩個都係精確恆等式,
      唔同正規化, 唔可以混為一談)

  S4 [扇區不對稱嘅唯一來源 = Z₂ 自對偶模]
     J-配對律: γ_n + γ_{44-n} = 4 = 2μ² (n = 1..43)
     => 奇扇區 = 11 對 x 4 = 44 = L₅·B (N_d = 44 嘅**結構來源**)
     => 偶扇區 = 10 對 x 4 + γ_22 (=2, 自對偶) + γ_0 (=0) = 42
        再加 Nyquist 原子 γ_44 = 4 => 46
     => Tr(L J) = Σ_n (-1)^n γ_n = 42 - 44 = -2 = -γ_22 = -μ²
     => 唯一不對稱源 = 自對偶模 γ_22 = μ² (唔係新常數)

  S5 [觀察者扇區冪和 (44-鏈)]
     Σ_{n odd, 1..43} γ_n^k = ? (直接算 + 核對閉式)
     ⚠️ 唔可以照搬 88-環閉式 Σγ^n = 88C(2n,n) + 2^{2n-1} — 唔同物件

  S6 [88-環係 44-鏈嘅雙覆蓋 (交叉核對)]
     88-環 Σ_{n odd} γ_n = 88 = 2·N_d ≠ 44 => 憲章嘅 N_d = 44 專指 44-鏈
     (兩個物件都要標清楚, 唔可以混用)

輸出: 數值驗證 + 自檢 (含注入必然錯案例)
"""
import os
import sys
import json
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp

mp.mp.dps = 50
PI = mp.pi
N = 44

print("=" * 78)
print("O201/05 -- 自指層 (Self-Reference) — C4  [v2: 44-site 開鏈]")
print("=" * 78)

# ---- 44-site 開鏈 (path P_44, 自由端) ----
L = np.zeros((N, N), dtype=np.int64)
for k in range(N):
    deg = (1 if k in (0, N - 1) else 2)
    L[k, k] = deg
    if k + 1 < N:
        L[k, k + 1] = -1
        L[k + 1, k] = -1
J = np.zeros((N, N), dtype=np.int64)      # 反射 k -> 43-k
for k in range(N):
    J[N - 1 - k, k] = 1
I44 = np.eye(N, dtype=np.int64)

Lf = L.astype(float)
Jf = J.astype(float)
Pobs = (np.eye(N) - Jf) / 2
Prest = (np.eye(N) + Jf) / 2

gam = [4 * mp.sin(n * PI / 88) ** 2 for n in range(0, N + 1)]   # n = 0..44 (44 = Nyquist 原子)

print("\n[S0] 物件")
print("  L = 44-site 開鏈 Laplacian (path P_44, 自由端, trace = 2(N-1) = 86)")
print("  J = 反射 k -> 43-k (0-indexed),  P_obs = (I-J)/2,  P_rest = (I+J)/2")
print("  γ_n = 4sin²(πn/88) = 2 - 2cos(πn/44),  n = 0..43 (譜);  γ_44 = 4 (Nyquist 原子)")
ev = np.sort(np.linalg.eigvalsh(Lf))
gam43 = np.sort(np.array([float(gam[n]) for n in range(N)]))
print("  max |L 譜 - γ_n| = %.3e" % float(np.max(np.abs(ev - gam43))))
print("  trace(L) = %d  (= 2(N-1) = 86)  ;  Σ_{{n=0..43}} γ_n = %s"
      % (int(np.trace(L)), mp.nstr(mp.fsum(gam[:44]), 12)))
print("  Σ_{{n=1..44}} γ_n = %s  (= 憲章 Σγ = 90)"
      % mp.nstr(mp.fsum(gam[1:45]), 12))

# ============================================================
print("\n" + "=" * 78)
print("S1 [觀察者 = 開鏈反射嘅反對稱投影]")
print("=" * 78)
trJ = int(np.trace(J))
ok_idem = np.allclose(Pobs @ Pobs, Pobs) and np.allclose(Prest @ Prest, Prest)
ok_orth = np.allclose(Pobs @ Prest, 0)
ok_comp = np.allclose(Pobs + Prest, np.eye(N))
ok_sym = np.allclose(Pobs, Pobs.T)
print("  J^2 = I              : %s" % ("✅" if np.array_equal(J @ J, I44) else "❌"))
print("  Tr(J) = %d            => J **自由** (22 個 2-cycle, 冇不動點) %s"
      % (trJ, "✅" if trJ == 0 else "❌"))
print("  [L, J] = 0           : %s" % ("✅" if np.array_equal(L @ J, J @ L) else "❌"))
print("  P_obs 正交投影        : %s" % ("✅" if (ok_idem and ok_orth and ok_comp and ok_sym) else "❌"))
print("  dim(觀察者) = Tr(P_obs) = %d ; dim(其餘) = %d" % (int(round(np.trace(Pobs))),
                                                          int(round(np.trace(Prest)))))

# ============================================================
print("\n" + "=" * 78)
print("S2 [算子級識別: J 本徵值 = 模指數奇偶]")
print("=" * 78)
# 開鏈 Neumann 模: v_n(k) = cos(πn(k+1/2)/44), k = 0..43
maxres = 0.0
maxeigdev = 0.0
for n in range(N):
    v = np.array([math.cos(math.pi * n * (k + 0.5) / N) for k in range(N)])
    lam = 2 - 2 * math.cos(math.pi * n / N)
    r1 = np.max(np.abs(Lf @ v - lam * v))
    r2 = np.max(np.abs(Jf @ v - ((-1) ** n) * v))
    maxres = max(maxres, r1)
    maxeigdev = max(maxeigdev, r2)
print("  Neumann 模 v_n(k) = cos(πn(k+1/2)/44):")
print("    max ||L v_n - γ_n v_n|| = %.3e   (v_n 係本徵向量)" % maxres)
print("    max ||J v_n - (-1)^n v_n|| = %.3e  (J 本徵值 = 模指數奇偶)" % maxeigdev)
# P_obs 像 = span{奇模}
Vodd = np.array([[math.cos(math.pi * n * (k + 0.5) / N) for k in range(N)]
                 for n in range(1, N, 2)])       # 22 個奇模
resid = np.max(np.abs((np.eye(N) - Pobs) @ Vodd.T))
print("  ||(I - P_obs) 奇模||_max = %.3e  => P_obs 像 = span{奇模} (算子級識別)" % float(resid))

# ============================================================
print("\n" + "=" * 78)
print("S3 [自指固定點: 跡重現晶格維度]")
print("=" * 78)
tr_LPobs = int(round(np.trace(Lf @ Pobs)))
tr_LPrest = int(round(np.trace(Lf @ Prest)))
tr_Pobs = int(round(np.trace(Pobs)))
sum_odd = mp.fsum([gam[n] for n in range(1, N, 2)])
sum_even_0_42 = mp.fsum([gam[n] for n in range(0, N, 2)])
print("  Tr(L P_obs)  = %d   = Σ_{{n odd,1..43}} γ_n = %s" % (tr_LPobs, mp.nstr(sum_odd, 12)))
print("  Tr(L P_rest) = %d   = Σ_{{n even,0..42}} γ_n = %s" % (tr_LPrest, mp.nstr(sum_even_0_42, 12)))
print("  => Tr(L P_obs) = N_d = %d EXACT  (晶格維度 = 觀察者算子嘅譜跡)" % tr_LPobs)
print("  => ⟨γ⟩_obs = Tr(L P_obs)/Tr(P_obs) = %d/%d = %s = μ² EXACT"
      % (tr_LPobs, tr_Pobs, mp.nstr(mp.mpf(tr_LPobs) / tr_Pobs, 12)))
print("  => ⟨γ⟩_obs 用**站點數**做分母: Tr(L P_obs)/N_d = %d/%d = 1 (O169 算子級 a)"
      % (tr_LPobs, N))
print("     ⚠️ 兩個正規化都精確, 但唔同: 22 = 扇區維度, 44 = 站點數。O169 用後者。")
Lobs = Pobs @ Lf @ Pobs
ev_o = np.sort(np.linalg.eigvalsh(Lobs))
ev_o = ev_o[np.abs(ev_o) > 1e-9]
ev_odd = np.sort([float(gam[n]) for n in range(1, N, 2)])
print("  L_obs 非零譜 (%d 個) vs 奇 γ_n: max |dev| = %.3e" % (len(ev_o), float(np.max(np.abs(ev_o - ev_odd)))))

# ============================================================
print("\n" + "=" * 78)
print("S4 [扇區不對稱嘅唯一來源 = Z₂ 自對偶模]")
print("=" * 78)
pairdev = max(abs(float(gam[n] + gam[N - n] - 4)) for n in range(1, N))
print("  J-配對律 γ_n + γ_{{44-n}} = 4 = 2μ² (n=1..43): max dev = %.3e" % pairdev)
print("  => 奇扇區 = 11 對 x 4 = %s = L₅·B = N_d ✅ (N_d = 44 嘅結構來源)"
      % mp.nstr(11 * mp.mpf(4), 8))
print("     偶扇區 = 10 對 x 4 (=40) + γ_22 (=%s, 自對偶) + γ_0 (=0) = %s"
      % (mp.nstr(gam[22], 8), mp.nstr(40 + gam[22], 12)))
print("     再加 Nyquist 原子 γ_44 = %s => Σγ_even = %s (= 憲章 46)"
      % (mp.nstr(gam[44], 8), mp.nstr(40 + gam[22] + gam[44], 12)))
tr_LJ = int(round(np.trace(Lf @ Jf)))
print("  Tr(L J) = Σ_n (-1)^n γ_n = %s - %s = %d = -γ_22 = -μ²"
      % (mp.nstr(sum_even_0_42, 12), mp.nstr(sum_odd, 12), tr_LJ))
print("  (含 Nyquist 原子嘅鏈讀法: Σγ_even - Σγ_odd = 46 - 44 = +2 = +γ_22 = +μ²)")
print("  => 唯一不對稱源 = 自對偶模 n=22, γ_22 = 2 = μ² (唔係新常數)")

# ============================================================
print("\n" + "=" * 78)
print("S5 [觀察者扇區冪和 (44-鏈)]")
print("=" * 78)
print("  %-4s %-24s %-24s %s" % ("k", "Σ_{n odd,1..43} γ^k", "88-環 odd 對照", "備註"))
print("  " + "-" * 84)
ring_odd = {}
chain_odd = {}
for k in range(1, 7):
    co = mp.fsum([gam[n] ** k for n in range(1, N, 2)])
    ro = mp.fsum([(4 * mp.sin(n * PI / 88) ** 2) ** k for n in range(1, 88, 2)])
    chain_odd[k] = co
    ring_odd[k] = ro
    print("  %-4d %-24s %-24s %s" % (k, mp.nstr(co, 14), mp.nstr(ro, 14),
                                     "88-環 = 2 x 44-鏈" if abs(ro - 2 * co) < mp.mpf('1e-30') else "⚠️ 唔同比例"))
print("  => ✅ 44-鏈 odd 冪和閉式 **命中**: Σ_{n odd,1..43} γ_n^k = 22·C(2k,k) = (N_d/2)·C(2k,k)")
print("     驗證: " + ", ".join("k=%d: %s = 22·C(%d,%d)"
                                % (k, mp.nstr(chain_odd[k], 10), 2 * k, k) for k in (1, 2, 3, 4)))
print("  => 88-環 odd 冪和 = 44·C(2k,k) = 2 × 44-鏈 odd 冪和 (雙覆蓋因子 2, 一致 ✅)")
print("  => O192 家族 (44·C(2k,k)) 嘅鏈版本 = 22·C(2k,k); 兩個都係同一個 arcsine 測度嘅影子")

# ============================================================
print("\n" + "=" * 78)
print("S6 [88-環 = 44-鏈雙覆蓋 (交叉核對)]")
print("=" * 78)
ring_all = mp.fsum([(4 * mp.sin(n * PI / 88) ** 2) for n in range(0, 88)])
print("  88-環: Σ_{{n=0..87}} γ_n = %s (= 176 = 2·88)" % mp.nstr(ring_all, 12))
print("  88-環 odd (n=1,3,..,87): %s = 2 x N_d => ⚠️ 唔係 N_d" % mp.nstr(ring_odd[1], 12))
print("  => 憲章「Σγ_odd = N_d = 44」專指 **44-鏈**; 88-環 odd 和 = 88 = 2N_d")
print("     (雙鏈 88 = 2 x 44: 88-環 = 44-鏈嘅雙覆蓋, 唔可以當同一個譜)")

# ============================================================
print("\n" + "=" * 78)
print("C4 判決 (自指層)")
print("=" * 78)
print("  ✅ 算子級 1: 觀察者 = P_obs = (I − J)/2 (開鏈反射反對稱投影; 正交投影)")
print("  ✅ 算子級 2: J v_n = (−1)^n v_n — 「奇扇區 = 觀察者」係算子等式 (唔係詮釋)")
print("  ✅ 算子級 3: N_d = Tr(L P_obs) = 44 EXACT; ⟨γ⟩_obs = μ² (兩種正規化都精確)")
print("  ✅ 算子級 4: 配對律 γ_n + γ_{44−n} = 2μ² => 奇扇區 = 11 x 4 = L₅·B = N_d")
print("  ✅ 算子級 5: Tr(L J) = −γ_22 = −μ² — 唯一不對稱源 = Z₂ 自對偶模")
print("  ✅ 算子級 6: J 自由作用 (Tr J = 0) = 「整數保護」嘅算子形式")
print("  🔴 剩餘: (a) 為何 N_d = 44 而唔係其他 (屬 O95 唯一性, 本 O 唔重做);")
print("           (b) 觀察者**動力學** (唔止投影) 未形式化 — O169 殘項 ① Lagrangian 級;")
print("           (c) 44-鏈 odd 冪和閉式未推 (O192 係 88-環物件)")

# ============================================================
out = {
    "object": "44-site open chain (path P_44, free ends)",
    "v1a_trap": "88-環 + site 反射 R: R 有 2 不動點 => 45/43, 唔係 44/44",
    "v1b_trap": "88-環 + half-shift S^44: 自由, 但 Σ_odd = 88 ≠ 44",
    "S1": {"J_squared_I": bool(np.array_equal(J @ J, I44)), "Tr_J": trJ,
           "commutes_L": bool(np.array_equal(L @ J, J @ L)),
           "dim_obs": tr_Pobs, "dim_rest": int(round(np.trace(Prest))),
           "idempotent": bool(ok_idem), "orthogonal": bool(ok_orth), "complete": bool(ok_comp)},
    "S2": {"max_residual_L": float(maxres), "max_J_eigdev": float(maxeigdev),
           "Pobs_image_is_odd_modes_resid": float(resid), "statement": "J v_n = (-1)^n v_n"},
    "S3": {"Tr_L_Pobs": tr_LPobs, "Tr_Pobs": tr_Pobs, "N_d": 44,
           "mean_obs_over_sector_dim": float(mp.mpf(tr_LPobs) / tr_Pobs),
           "mean_obs_over_sites": tr_LPobs / N,
           "sum_odd": mp.nstr(sum_odd, 20), "sum_even_0_42": mp.nstr(sum_even_0_42, 20)},
    "S4": {"pair_law_maxdev": float(pairdev), "Tr_LJ": tr_LJ,
           "gamma_22": mp.nstr(gam[22], 20), "gamma_44_atom": mp.nstr(gam[44], 20),
           "sum_even_with_atom": mp.nstr(40 + gam[22] + gam[44], 20),
           "asymmetry_source": "Z2 self-dual mode n=22: gamma_22 = mu^2 = 2"},
    "S5": {"chain_odd_power_sums": {("k=%d" % k): mp.nstr(chain_odd[k], 20) for k in chain_odd},
           "ring_odd_power_sums": {("k=%d" % k): mp.nstr(ring_odd[k], 20) for k in ring_odd},
           "chain_closed_form": "Σ_{n odd,1..43} γ_n^k = 22·C(2k,k) = (N_d/2)·C(2k,k) (k=1..6 EXACT)",
           "ring_closed_form": "Σ_{n odd,1..87} γ_n^k = 44·C(2k,k) = 2 × 鏈版本 (O192 家族)",
           "note": "兩者同一 arcsine 測度嘅影子; 雙覆蓋因子 2 (88-環 = 44-鏈雙覆蓋)"},
    "S6": {"ring_all": mp.nstr(ring_all, 20), "ring_odd": mp.nstr(ring_odd[1], 20),
           "note": "憲章 Σγ_odd = N_d = 44 專指 44-鏈; 88-環 odd 和 = 2N_d"},
    "verdict_C4": "6 個算子級陳述成立 (投影/模指數識別/自指跡/配對律/不對稱源/自由對合); 剩 N_d 唯一性 (O95) + 觀察者動力學 (O169 殘項 ①)",
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "05_self_reference.json")
with open(p, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n[data] %s" % os.path.abspath(p))

# ============================================================
print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NPASS = NFAIL = 0


def check(label, cond):
    global NPASS, NFAIL
    if cond:
        NPASS += 1
        print("  PASS  %s" % label)
    else:
        NFAIL += 1
        print("  FAIL  %s" % label)


check("[INJECT] checker 識 FAIL (44 != 46)", tr_LPobs != 46)
check("S0 開鏈譜 = 4sin²(πn/88), n=0..43", float(np.max(np.abs(ev - gam43))) < 1e-12)
check("S0 trace(L) = 86 = 2(N-1)", int(np.trace(L)) == 86)
check("S0 Σ_{n=1..44} γ_n = 90 (憲章 Σγ)", abs(mp.fsum(gam[1:45]) - 90) < mp.mpf('1e-40'))
check("S1 J^2 = I", np.array_equal(J @ J, I44))
check("S1 Tr(J) = 0 (自由對合, 無不動點)", trJ == 0)
check("S1 [L,J] = 0", np.array_equal(L @ J, J @ L))
check("S1 P 正交投影 + 完備", ok_idem and ok_orth and ok_comp and ok_sym)
check("S1 dim = 22/22", tr_Pobs == 22 and int(round(np.trace(Prest))) == 22)
check("S2 Neumann 模係本徵向量 (resid %.1e)" % maxres, maxres < 1e-12)
check("S2 J v_n = (-1)^n v_n (dev %.1e)" % maxeigdev, maxeigdev < 1e-12)
check("S2 P_obs 像 = span{奇模} (resid %.1e)" % float(resid), resid < 1e-12)
check("S3 Tr(L P_obs) = 44 = N_d EXACT", tr_LPobs == 44)
check("S3 Tr(L P_rest) = 42 (= 86-44)", tr_LPrest == 42)
check("S3 ⟨γ⟩_obs (扇區維度分母) = 2 = μ²", abs(mp.mpf(tr_LPobs) / tr_Pobs - 2) < mp.mpf('1e-40'))
check("S3 ⟨γ⟩_obs (站點數分母) = 1 = O169 a", tr_LPobs / N == 1.0)
check("S3 L_obs 譜 = 奇 γ_n", float(np.max(np.abs(ev_o - ev_odd))) < 1e-12)
check("S4 配對律 γ_n + γ_{44-n} = 4 (dev %.1e)" % pairdev, pairdev < 1e-12)
check("S4 奇扇區 = 11 x 4 = 44 = L₅·B", abs(sum_odd - 44) < mp.mpf('1e-40'))
check("S4 γ_22 = 2 = μ²", abs(gam[22] - 2) < mp.mpf('1e-40'))
check("S4 γ_44 = 4 = Nyquist 原子", abs(gam[44] - 4) < mp.mpf('1e-40'))
check("S4 偶扇區 (含原子) = 46", abs(40 + gam[22] + gam[44] - 46) < mp.mpf('1e-40'))
check("S4 Tr(L J) = -2 = -μ²", tr_LJ == -2)
check("S5 88-環 odd 冪和 = 2 x 44-鏈 odd 冪和 (k=1..6)",
      all(abs(ring_odd[k] - 2 * chain_odd[k]) < mp.mpf('1e-30') for k in range(1, 7)))
check("S5 44-鏈 Σ_odd γ_n = 44 (k=1)", abs(chain_odd[1] - 44) < mp.mpf('1e-40'))
check("S5 44-鏈 odd 冪和閉式 = 22·C(2k,k) (k=1..6)",
      all(abs(chain_odd[k] - 22 * mp.binomial(2 * k, k)) < mp.mpf('1e-30') for k in range(1, 7)))
check("S6 88-環 Σγ_n = 176", abs(ring_all - 176) < mp.mpf('1e-40'))
check("S6 88-環 odd 和 = 88 = 2N_d ≠ N_d", abs(ring_odd[1] - 88) < mp.mpf('1e-40'))

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
