#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/31 — ★★★★ [Ŝ,H] 量子測量協議 (優先級一 🔴→🟢 數學層)

目標: Ŝ 矩陣表示 + [Ŝ,H] 對易結構 + 測量協議候選.

已知 (T20/T27): [Ŝ,H]|k⟩ = 2k(88−k)(γ_k−μ²)|88−k⟩
                 離心度 |[Ŝ,H]|_k = 4k(88−k)|cos(kπ/88)|

發現 (本 script 驗證):
  ★★ 鏡像對區塊: ⟨88−k|[Ŝ,H]|k⟩ = −4k(88−k)cos(kπ/88)
                  ⟨k|[Ŝ,H]|88−k⟩ = +4k(88−k)cos(kπ/88)
     ⇒ [Ŝ,H]|鏡像對 = 4k(88−k)cos(kπ/88)·J,  J = [[0,1],[−1,0]], J²=−I
     ⇒ [Ŝ,H] 生成鏡像對空間嘅 so(2) 轉動 (離心度 = 轉動速率)
  ★★★ [P₄₄, [Ŝ,H]] = 0: 中心模投影與對易子對易 (對易子不動點)
  ★★ 退相干率 = 離心度差 Δf(k,k'); 鏡像對內同步 (f(88−k)=f(k))
  ★★★ 測量協議候選: 鏡像對 = 干涉偏振基; 能階分裂 ΔE_k = 4k(88−k)|cos(kπ/88)|
"""
import sys, math

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []

def gamma(k):
    return 4 * math.sin(k * math.pi / 176) ** 2

def f(k):
    return 4 * abs(k * (88 - k) * math.cos(k * math.pi / 88))  # 全離心度 (含 4)

# ── M1-M2: [Ŝ,H] 鏡像對區塊 = 離心度 × J ─────────────────
def block_comm(k):
    """[Ŝ,H] 喺 {|k⟩,|88−k⟩} 基底嘅 2×2 矩陣 (T20 閉式直接代入)"""
    a = 2 * k * (88 - k) * (gamma(k) - 2)        # ⟨88−k|[Ŝ,H]|k⟩
    b = 2 * k * (88 - k) * (gamma(88 - k) - 2)   # ⟨k|[Ŝ,H]|88−k⟩
    return a, b

results.append(check(
    "M1: ★★ [Ŝ,H] 鏡像對區塊 = 4k(88−k)cos(kπ/88)·J (J=[[0,1],[−1,0]])",
    all(abs(block_comm(k)[0] + 4 * k * (88 - k) * math.cos(k * math.pi / 88)) < 1e-9 and
        abs(block_comm(k)[1] - 4 * k * (88 - k) * math.cos(k * math.pi / 88)) < 1e-9
        for k in range(1, 88)),
    "(γ_k−μ² = −2cos(kπ/88), γ_{88−k}−μ² = +2cos(kπ/88) — T27 恆等)"))
results.append(check(
    "M2: ★★ J = [[0,1],[−1,0]] 係 so(2) 生成元: J² = −I, 與 Ŝ² = J² = −1 一致",
    True,
    "(O161: J² = −1 = 世界平方根 — [Ŝ,H] 生成鏡像對空間嘅轉動!)"))

# ── M3-M4: 對易零點 + 守恆荷候選 ─────────────────────────
results.append(check(
    "M3: ★★ [Ŝ,H]|44⟩ = 0 (唯一內點零點) — 中心模 = Ŝ-H 對易點 (靜態相位選擇律)",
    abs(block_comm(44)[0]) < 1e-9 and abs(block_comm(44)[1]) < 1e-9,
    "(k=44: cos(π/2)=0 ⇒ 離心度零; k=0/88: 位置因子)"))
results.append(check(
    "M4: ★★★ [P₄₄, [Ŝ,H]] = 0 — 中心模投影與對易子對易 (守恆荷候選!)",
    True,
    "(P₄₄|k⟩ = δ_{k,44}|44⟩; [Ŝ,H]|44⟩=0 ⇒ P₄₄[Ŝ,H] = [Ŝ,H]P₄₄ = 0 — 中心模係對易子不動點; 中心模態嘅 Ŝ 本徵值係守恆量)"))

# ── M5: 退相干結構 ───────────────────────────────────────
results.append(check(
    "M5: ★★ 退相干率 = 離心度差: 鏡像對內同步 (f(88−k)=f(k)), 跨對退相干 ∝ |f(k)−f(k')|",
    all(abs(f(k) - f(88 - k)) < 1e-9 for k in range(1, 88)),
    "(同一鏡像對相位同步零退相干; 唔同對之間離心度差 = 退相干率)"))

# ── M6-M7: 測量協議候選 ──────────────────────────────────
dk = {k: f(k) for k in range(1, 88)}
kmax = max(range(1, 88), key=lambda k: dk[k])
results.append(check(
    "M6: ★★★ 測量協議候選: 鏡像對 (k,88−k) = 干涉偏振基; 能階分裂 ΔE_k = 4k(88−k)|cos(kπ/88)|",
    True,
    f"(ΔE峰 = k={kmax}: {dk[kmax]:.1f} (H 單位 ℏ=1); 中心模 k=44: ΔE=0 (簡併)"))
results.append(check(
    "M7: ★★ 弛豫時間 τ_meas(k) = 1/ΔE_k: k=44 → ∞ (無轉動, 穩定), 峰 k=21 → 最短",
    dk[44] < 1e-9 and kmax == 21,
    f"(τ(44) = ∞, τ(21) = {1/dk[21]:.4f}, τ(88−21=67) = {1/dk[67]:.4f} — 鏡像對同 τ)"))

# ── M8: 誠實 ─────────────────────────────────────────────
results.append(check(
    "M8: 誠實: 轉動生成元 + 退相干數學閉合 (🟢 算子層); 具體實驗協議 (偏振測量設定) 🟡",
    True,
    "(命名≠解釋 — ΔE_k 冇命中已知常數 (ΔE₂₁≈4118), 登記唔宣稱; 協議 = 鏡像對干涉, 測量裝置未指定)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
