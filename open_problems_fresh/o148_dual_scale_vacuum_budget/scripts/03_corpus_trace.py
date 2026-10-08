#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/03_corpus_trace.py
===============================
規範身份 → corpus 出處追溯 (用戶鐵律: 腳本發現必須 trace 到 docs)。

逐條 identity 喺 v10/v11 corpus 搜尋對應文檔行號, 輸出 file:line 引用。
冇出處嘅 identity 標 [NO-CORPUS] (即 O148 新註冊 / 新結果)。
"""
import re, os, sys

ROOT = "/home/wsl/Projects/IDCM-Original"
V10  = os.path.join(ROOT, "IDCM-v10.0--It-From-Beat")
V11  = os.path.join(ROOT, "IDCM-v11.0--Equation-Verification")

MD_FILES = []
for base in (V10, V11):
    for dirpath, dirnames, filenames in os.walk(base):
        if "node_modules" in dirpath or ".git" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".md"):
                MD_FILES.append(os.path.join(dirpath, fn))

def grep(pattern, limit=4):
    """搵 pattern 嘅 file:line 引用 (最多 limit 個)"""
    rx = re.compile(pattern)
    hits = []
    for fp in MD_FILES:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if rx.search(line):
                        rel = fp.replace(ROOT + "/", "")
                        hits.append(f"{rel}:{i}")
                        if len(hits) >= limit:
                            return hits
        except OSError:
            continue
    return hits

def show(name, pattern, limit=3):
    hits = grep(pattern, limit)
    tag = "✅" if hits else "❌ NO-CORPUS"
    print(f"  {tag} {name}")
    for h in hits:
        print(f"        {h}")

print("=" * 72)
print("O148 03: corpus 追溯 (規範身份 -> docs)")
print("=" * 72)

print("\n[A] 譜和身份 (第一性原理底層)")
show("Σγ_even = 90 (世界)", r"Σγ[_ ]?even\s*=\s*90|Σγ_even.*=.*90|Sigma_gamma_even = 90|Σγ even = 90")
show("Σγ_odd = 88 (觀察者)", r"Σγ[_ ]?odd\s*=\s*88|Σγ_odd.*=.*88|Sigma_gamma_odd = 88|Σγ odd = 88")
show("Σγ_all = 178 = 2F11", r"178\s*=\s*2F|Σγ_all = 178|total 178|178 = 2F₁₁")
show("閉式 2(Nd+1) / 2Nd", r"2\(N_d\+1\)|2\(N_d \+ 1\)|90 = 2\(N_d")

print("\n[B] 真空能身份")
show("⟨W⟩² = 61.5 = (90+33)/2 (O39)", r"61\.5\s*=\s*\(90\+33\)/2|⟨W⟩² = 61\.5")
show("61.5 = 44×123/88 (O41)", r"44×123/88|44\s*×\s*123\s*/\s*88|44 \* 123 / 88")
show("61.5 = 88×123/176 (O41)", r"88×123/176|88\s*×\s*123\s*/\s*176")
show("E_min = L10/(4Nd) = 123/176 (O41 Landauer)", r"L₁₀/\(4N_d\)|L10/\(4Nd\)|123/176")
show("61.5/90 = 41/60 = f_unproj (Q1/o33/o143)", r"41/60")
show("19/60 = f_proj", r"19/60")
show("n_unproj=41, n_proj=19 (o143 60 節點)", r"n_unproj|unproj_ratio|n_proj")

print("\n[C] 觀察者/邊界身份")
show("176 = B×Nd = 4×44 (O41)", r"176\s*=\s*B×N|176 = B.×.N|176\s*=\s*4×44")
show("176 = 2×88 (o137 φ[1])", r"φ\[1\].*176|176 = 2×88|176=2×88")
show("μ² = 2 = Σ_even−Σ_odd (O41)", r"μ²\s*=\s*2|mu\^2 = 2|μ² = Σγ")
show("90 = F11+1, 88 = F11−1", r"F₁₁[+]1|89\+1|89−1|89 \+ 1")

print("\n[D] 360/180 閉合身份")
show("360 = 4×Σγ (o137 GKZ φ_origin)", r"360 = 4[·×]?Σγ|φ_origin.*360|360 = 4·Σγ₄₄")
show("Σφ = 1800 = 20×Σγ (o137)", r"1800 = 20|Σφ = 1800")
show("360 = 4×90", r"360 = 4×90|360=4×90|4×90 = 360")
show("180 = 2×90 (O148 新註冊)", r"180 = 2×90|180 = 2 · 90")
show("冷斑經度 209° = 180°+29 (o32, 180 基底先例)", r"209° = 180")

print("\n[E] δ 族 (O148 新結果)")
show("δ₁ = 5.176e-5 (o33 觀察者稅命名)", r"觀察者稅|5\.176|0\.0052%")
show("δ₁ = (L10φ−L11)/(60(3φ+1)) (o34 恆等式)", r"L₁₀φ|L10φ|3φ\+1")
show("M* = 32.990683 ≠ 33 (Q1 拆穿)", r"32\.990683|M\*.*32\.99")
show("4/(φ⁴−1) = 1/(1+3ε) (o33/Q1)", r"3ε|3\\varepsilon|φ⁴−1|φ⁴-1")
show("Ω_m/Ω_Λ = 3ε (o33/o39)", r"3ε =|Ω_m/Ω_Λ = 3ε|回收率")

print("\n[F] 角度身份")
show("θ_site = π/44 (O74)", r"θ_site = π/44|π/44 樞紐|theta_site")
show("360/44 = 90/11 (O148 新註冊)", r"90/11|360/44")
show("π/22 = 4π/88 (O148 新註冊)", r"π/22")

print("\n[G] 骨架身份")
show("60 節點 Rhombicosidodecahedron χ=2", r"60−120\+62|60-120+62|χ = 2|χ=2")

print("\n" + "=" * 72)
print("RESULT: 追溯完成 — ❌ NO-CORPUS 項目 = O148 新註冊/新結果, 見 docs/")
print("=" * 72)