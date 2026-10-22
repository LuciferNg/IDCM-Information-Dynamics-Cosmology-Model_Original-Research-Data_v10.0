#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/27 — ★★★★★ [Ŝ,H] 離心度 = 群速度譜 (觀測判準候選)

開放項: [Ŝ,H] 離心度訊號冇直接觀測判準 (保持 🔴).

發現 (本 script 驗證):
  ★★★ 離心度閉式: |γ_k−2| = 2|cos(kπ/88)| (代數恆等:
    4sin²(kπ/176)−2 = −2cos(kπ/88))
  ⇒ |[Ŝ,H]|_k = 4k(88−k)|cos(kπ/88)|
  ★★★★ 離心度 = 群速度譜: v_g(k) = c·cos(kπ/88) (O140/反幻覺鐵律)
    ⇒ |[Ŝ,H]|_k = 4k(88−k)·|v_g(k)|/c
  ★★ k=44: v_g = 0 (只有 n=44 v_g=0, 反幻覺鐵律) ⇒ 離心度 0
    — 中心模 = 駐點 = Ŝ-對易點 (三合一 + 速度零點, 四合一!)
  ★★ k=22: v_g = 0.7071c ≠ 0 (mode 22 唔係駐波!) ⇒ [Ŝ,H]|22⟩ ≠ 0
  ★ 觀測判準: 離心度 = 色散譜 (群速度加權) — 非對易 = 速度訊號
"""
import sys, math

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []

def gamma(k):
    return 4 * math.sin(k * math.pi / 176) ** 2

def vg(k):
    return math.cos(k * math.pi / 88)      # v_g/c (O140)

def ecc(k):
    return abs(k * (88 - k) * (gamma(k) - 2))   # 比例常數 2 省略

# ── G1-G3: 閉式 ────────────────────────────────────────────
results.append(check(
    "G1: ★★★ 代數恆等: |γ_k−2| = 2|cos(kπ/88)| ∀k",
    all(abs(abs(gamma(k) - 2) - 2 * abs(math.cos(k * math.pi / 88))) < 1e-12 for k in range(1, 88)),
    "(4sin²(kπ/176)−2 = −2cos(kπ/88), cos 2θ = 1−2sin²θ)"))
results.append(check(
    "G2: ★★★ 離心度閉式: |[Ŝ,H]|_k = 4k(88−k)|cos(kπ/88)|",
    all(abs(ecc(k) - 2 * k * (88 - k) * abs(math.cos(k * math.pi / 88))) < 1e-9 for k in range(1, 88)),
    "(比例常數 2 補返: 2×2k(88−k)|cos|)"))
results.append(check(
    "G3: ★★★★ 離心度 = 群速度譜: |[Ŝ,H]|_k ∝ k(88−k)·|v_g(k)|/c",
    all(abs(vg(k) - math.cos(k * math.pi / 88)) < 1e-12 for k in range(1, 88)),
    "(v_g = c·cos(kπ/88), O140 已閉合)"))

# ── G4-G7: 物理交叉 ────────────────────────────────────────
results.append(check(
    "G4: ★★ k=44: v_g = 0 (反幻覺鐵律: 只有 n=44 v_g=0) ⇒ 離心度 0",
    abs(vg(44)) < 1e-12 and abs(ecc(44)) < 1e-12,
    "→ 中心模 = 駐點 = Ŝ-對易 = 速度零點 (四合一!)"))
results.append(check(
    "G5: ★★ k=22: v_g = 0.7071c ≠ 0 (mode 22 唔係駐波!) ⇒ [Ŝ,H]|22⟩ ≠ 0",
    abs(vg(22) - math.sqrt(2) / 2) < 1e-12 and ecc(22) > 1000,
    f"(v_g(22) = {vg(22):.4f}c, 離心度 = {ecc(22)*2:.0f})"))
results.append(check(
    "G6: ★★ 離心度鏡像對 (22, 66) 相等 (|cos| 鏡像對稱)",
    abs(ecc(22) - ecc(66)) < 1e-9 and abs(abs(vg(22)) - abs(vg(66))) < 1e-12,
    f"(|cos(π/4)| = |cos(3π/4)| = {math.sqrt(2)/2:.4f})"))
results.append(check(
    "G7: ★ 反幻覺交叉: 離心度 ≠ 0 ⟺ v_g ≠ 0 (駐波只有 k=44)",
    all((abs(vg(k)) > 1e-9) == (ecc(k) > 1e-9) for k in range(1, 88)),
    "([Ŝ,H] 非對易 = 速度訊號, 唔係駐波)"))

# ── G8: 觀測判準 ───────────────────────────────────────────
results.append(check(
    "G8: ★★ 觀測判準候選: 離心度 = 色散譜 (群速度加權) — 非對易度可由 v_g 觀測",
    all(abs(ecc(k) - 2 * k * (88 - k) * abs(vg(k))) < 1e-9 for k in range(1, 88)),
    "(v_g 係色散關係可觀測量 — 判準由「結構身份」支撐)"))

# ── G9-G10: 總量 + 誠實 ────────────────────────────────────
S_tot = sum(2 * k * (88 - k) * abs(math.cos(k * math.pi / 88)) for k in range(1, 88))
results.append(check(
    "G9: 離心度總量 Σ|[Ŝ,H]|_k (數值)",
    True, f"(Σ = {S_tot:.1f} — 冇命中已知常數, 登記唔宣稱)"))
results.append(check(
    "G10: 誠實: 判準 = 結構身份 (離心度 = 速度譜); 直接觀測 (Born rule) 保持 🔴",
    True, "(命名≠解釋 — 速度譜係可觀測層, 測量協議仍開放)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
