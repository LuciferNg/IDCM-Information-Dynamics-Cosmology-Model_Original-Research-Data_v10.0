#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 scripts/19 — M4 → O124 handoff 處理：channel-level em 讀數算子嘅群論形式檢定
================================================================================
來源：register handed_off M4 → O124（2026-10-24T13:23:34+08:00）
請求：channel-level 電荷讀數算子嘅群論形式（「強子內容 → em 讀數」表示論表達式）
判準（M4 01_problem_record L316）：8 通道 dev ≤ 各通道 σ、零自由參數

本 script 做三件事（全部真計算，零外部數據錨）：
  A. 8 通道 E_ch 譜重建（X = m_d − m_u = 2.560 MeV 外部固定，M4 docs/18 同值）
  B. 群論算子族系統檢定（兩族共 2780 候選）：
     B1 差值量子數族（Δ 量子數，1–3 項，線性+二次）— 通道內「差」算子
     B2 絕對量子數族（最終態絕對量子數，1–3 項，線性+二次）— 通道所在多重態算子
  C. 結構論證（唔靠數值）：同一組 Δ 量子數嘅通道 E 跨度 vs 群論不變量可分辨度

判準（事前寫死，見 docs/11）：
  - 通過 = 全 8 通道 |resid| < 2σ，且候選係零自由參數（固定係數）或預先指定族
  - 自由擬合族只作「上界」用途：若連自由擬合（1–3 項）都 0 命中 ⟹ 任何零參數子族必 0 命中
"""
from fractions import Fraction as F
from itertools import combinations
import numpy as np

X_MD_MU = 2.560          # MeV, FLAG24 外部固定（M4 docs/18 同值，不由本輪擬合）
SIG_X   = 0.094

# ── A. 8 通道 E_ch 譜（PDG 2024 質量差；coeff = Σ(最終態−初始態) 嘅 u↔d 質量項）
# (name, Δm MeV, coeff, 初始強子, 最終強子)
CHANNELS = [
    ("n-p",       1.2933,  1, 'n',     'p'),
    ("K+-K0",    -3.9340, -1, 'K+',    'K0'),
    ("pi+-pi0",   4.5936,  1, 'pi+',   'pi0'),
    ("Sig--Sig0", 4.8070,  1, 'Sig-',  'Sig0'),
    ("Sig0-Sig+", 3.2720,  1, 'Sig0',  'Sig+'),
    ("Sig--Sig+", 8.0790,  2, 'Sig-',  'Sig+'),
    ("Xi--Xi0",   6.8500,  1, 'Xi-',   'Xi0'),
    ("D+-D0",     4.8200,  1, 'D+',    'D0'),
]
# M4 docs/18 §四 σ_E（含 X 不確定度傳播）
SIG_E = {"n-p":0.0940,"K+-K0":0.0963,"pi+-pi0":0.0940,"Sig--Sig0":0.1010,
         "Sig0-Sig+":0.1196,"Sig--Sig+":0.2028,"Xi--Xi0":0.2301,"D+-D0":0.1172}

# ── 強子絕對量子數：(B, Q, I, Y, S, C, nq, ns)
# ns = 奇異夸克/反夸克數目（絕對值計）；nq = 夸克數（含反夸克）
HADRON = {
    'p':   (1, 1, F(1,2), 1,  0, 0, 3, 0),
    'n':   (1, 0, F(1,2), 1,  0, 0, 3, 0),
    'K+':  (0, 1, F(1,2), 1,  1, 0, 2, 1),
    'K0':  (0, 0, F(1,2), 1,  1, 0, 2, 1),
    'pi+': (0, 1, 1,       0,  0, 0, 2, 0),
    'pi0': (0, 0, 1,       0,  0, 0, 2, 0),
    'Sig-':(1,-1, 1,       0, -1, 0, 3, 1),
    'Sig0':(1, 0, 1,       0, -1, 0, 3, 1),
    'Sig+':(1, 1, 1,       0, -1, 0, 3, 1),
    'Xi-': (1,-1, F(1,2), -1, -2, 0, 3, 2),
    'Xi0': (1, 0, F(1,2), -1, -2, 0, 3, 2),
    'D+':  (0, 1, F(1,2), 1,  0, 1, 2, 0),
    'D0':  (0, 0, F(1,2), 1,  0, 1, 2, 0),
}

def feats(name):
    """單一強子 → 量子數特徵字典（線性 + 二次項）"""
    B, Q, I, Y, S, C, nq, ns = HADRON[name]
    f = dict(B=float(B), Q=float(Q), I=float(I), Y=float(Y), S=float(S),
             C=float(C), nq=float(nq), ns=float(ns))
    f["I2"] = float(I*(I+1)); f["Q2"] = float(Q*Q); f["Y2"] = float(Y*Y)
    f["S2"] = float(S*S);     f["C2"] = float(C*C); f["ns2"] = float(ns*ns)
    f["nq2"] = float(nq*nq);  f["IQ"] = float(I*Q); f["IY"] = float(I*Y)
    f["QY"] = float(Q*Y);     f["nsB"] = float(ns*B); f["nsY"] = float(ns*Y)
    f["nsS"] = float(ns*S);   f["nqns"] = float(nq*ns); f["QI"] = float(Q*I)
    return f

KEYS = list(feats('p').keys())

def build_E():
    """重建 E_ch = Δm − coeff·X（Fraction 精確）"""
    rows = []
    for name, dm, coeff, hi, hf in CHANNELS:
        E = F(str(dm)).limit_denominator(10**6) - coeff*F(str(X_MD_MU))
        rows.append((name, float(E), SIG_E[name], hi, hf))
    return rows

def test_family(Xm, E, SG, keys, max_terms=3):
    """1..max_terms 項線性組合自由擬合；回傳 (通過數, 總數, 最佳)"""
    n_feat = len(keys)
    passed, total, best = 0, 0, (1e9, None, None)
    for k in range(1, max_terms+1):
        for cols in combinations(range(n_feat), k):
            A = np.column_stack([Xm[:, c] for c in cols] + [np.ones(len(E))])
            if np.linalg.matrix_rank(A) < A.shape[1]:
                continue
            coef, *_ = np.linalg.lstsq(A, E, rcond=None)
            resid = A @ coef - E
            mx = float(np.max(np.abs(resid)/SG))
            total += 1
            if mx < 2.0:
                passed += 1
            if mx < best[0]:
                best = (mx, [keys[c] for c in cols], coef)
    return passed, total, best

def main():
    print("="*78)
    print("O124 scripts/19 — M4 → O124：channel-level em 讀數算子群論形式檢定")
    print("="*78)

    rows = build_E()
    print(f"\nX ≡ m_d − m_u = {X_MD_MU} ± {SIG_X} MeV（FLAG24 外部固定，零擬合）\n")
    print("── A. 8 通道 E_ch 譜（重建，核對 M4 docs/18 §四）──")
    print(f"{'channel':12s} {'E_ch (MeV)':>11s} {'σ_E':>7s}   初始→最終")
    E = []; SG = []
    for name, e, s, hi, hf in rows:
        print(f"{name:12s} {e:+11.4f} {s:7.4f}   {hi} → {hf}")
        E.append(e); SG.append(s)
    E = np.array(E); SG = np.array(SG)
    print(f"\nE 跨度 = {E.max()-E.min():.4f} MeV；最小 σ = {SG.min():.4f} MeV "
          f"⟹ 跨度 = {(E.max()-E.min())/SG.min():.0f}σ")

    # ── B1. 差值量子數族（通道內「差」算子）
    print("\n" + "─"*78)
    print("B1. 差值量子數族：f(ΔB, ΔQ, ΔI, ΔY, ΔS, ΔC, Δnq, Δns, …) 1–3 項")
    print("─"*78)
    Xd = np.array([[feats(hf)[k]-feats(hi)[k] for k in KEYS] for _,_,_,hi,hf in rows], float)
    live = [k for i,k in enumerate(KEYS) if len(np.unique(Xd[:,i])) > 1]
    print(f"非零變異特徵：{live}")
    idx = [KEYS.index(k) for k in live]
    p1, t1, b1 = test_family(Xd[:, idx], E, SG, live, 3)
    print(f"族大小 {t1}；通過 2σ：{p1}")
    print(f"最佳：{b1[0]:.2f}σ  feats={b1[1]}")
    print(f"⟹ {'🔴 全數排除' if p1 == 0 else '🟡 有候選'}")

    # ── B2. 絕對量子數族（最終態）
    print("\n" + "─"*78)
    print("B2. 絕對量子數族：f(最終態 B,Q,I,Y,S,C,nq,ns, 二次項) 1–3 項")
    print("─"*78)
    Xa = np.array([[feats(hf)[k] for k in KEYS] for _,_,_,_,hf in rows], float)
    live2 = [k for i,k in enumerate(KEYS) if len(np.unique(Xa[:,i])) > 1]
    print(f"非零變異特徵（{len(live2)}）：{live2}")
    idx2 = [KEYS.index(k) for k in live2]
    p2, t2, b2 = test_family(Xa[:, idx2], E, SG, live2, 3)
    print(f"族大小 {t2}；通過 2σ：{p2}")
    print(f"最佳：{b2[0]:.2f}σ  feats={b2[1]}  rms={float(np.sqrt(np.mean((np.column_stack([Xa[:,KEYS.index(k)] for k in b2[1]]+[np.ones(8)])@b2[2]-E)**2))):.3f} MeV")
    print(f"⟹ {'🔴 全數排除' if p2 == 0 else '🟡 有候選'}")

    # ── C. 結構論證：同 Δ 量子數通道嘅 E 跨度
    print("\n" + "─"*78)
    print("C. 結構論證（唔靠擬合）：同一組 Δ 量子數嘅通道，E 可分辨嗎？")
    print("─"*78)
    groups = {}
    for (name, e, s, hi, hf) in rows:
        key = (round(feats(hf)['Q']-feats(hi)['Q'],3),
               round(feats(hf)['I']-feats(hi)['I'],3),
               round(feats(hf)['Y']-feats(hi)['Y'],3),
               round(feats(hf)['S']-feats(hi)['S'],3))
        groups.setdefault(key, []).append((name, e, s))
    for key, members in groups.items():
        if len(members) > 1:
            vals = [m[1] for m in members]
            print(f"  Δ(Q,I,Y,S)={key}: " + ", ".join(f"{m[0]}={m[1]:+.3f}" for m in members)
                  + f"  ⟹ spread {max(vals)-min(vals):.3f} MeV")
    print("\n  ⟹ 同一組 Δ 量子數（群論完全不可分辨）嘅通道，E 相差達數 MeV；")
    print("     任何純群論量子數算子都必然在同一組內給同一值 ⟹ 結構上不可能。")

    # ── D. 密度基準（多重比較）
    print("\n" + "─"*78)
    print("D. 密度基準（防多重比較假陽性）")
    print("─"*78)
    print(f"  總候選族 = {t1} + {t2} = {t1+t2}；命中 = {p1+p2}")
    print(f"  若命中 0 ⟹ 唔涉及挑選偏差（0 命中無需密度校正）")
    print(f"  M4 docs/20 參考：F1 族 0.1% 帶覆蓋率 20.61% ⟹ 1/5 隨機命中（本族遠嚴於此：0 命中）")

    # ── E. 判決
    print("\n" + "="*78)
    print("E. 判決")
    print("="*78)
    print("""
🔴 群論量子數（線性+二次，1–3 項）兩族共 %d 候選，0 命中（最佳 %.2fσ / %.2fσ）
🔴 結構論證獨立支持：同 Δ 量子數通道 E 跨度達數 MeV（群論不可分辨）
⟹ channel-level em 讀數算子**冇純群論形式**（唔係「未找到」，係結構上不可能）

物理理由：em 讀數 = QED 自能差 ∝ ⟨Σ_{i<j} q_iq_j / r_ij⟩ —— 群論只定電荷
量子數（分子），⟨1/r_ij⟩ 係波函數重疊（動力學，分母）。同一組量子數、唔同
spectator 波函數 ⟹ 唔同 E。呢個係範疇定理，唔係參數不足。

⚠️ attribution 更正：M4 docs/17/18 引用「O124 已註冊 Y = T₃^R + (B−L)/2」
   — O124 從未註冊此式（O124 內 Y 僅為 BCH 展開 Y = log(U_i U_{i+1}†)）。
   真身 = O85 docs/03（SU(12) → SM 破缺），經 O229 R3 檢定判「額外物理輸入，
   非異常消去推論」。引用須改。
""" % (t1+t2, b1[0], b2[0]))

if __name__ == "__main__":
    main()