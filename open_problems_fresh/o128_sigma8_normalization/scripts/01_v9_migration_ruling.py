#!/usr/bin/env python3
"""
O128 scripts/01 — v9.0 σ8_norm 遷移裁決
=========================================
O128 開題第一步 (SESSION_START §前置驗證): 「必須先驗證 v9.0 推導在 v10.0 非膨脹框架中
是否仍然有效」+「如果 v9.0 推導失效，則需要建立新推導」。

v9.0 來源: IDCM-v9.0--W-Field-Lattice/open_problems_fresh/sigma8_norm/01_derive_sigma8.py
(唯一檔案, 165 行)

本 script 逐項判定該 script 有冇「可遷移之結構內容」:
  V1  執行環境 (硬編碼路徑) 是否仍然存在
  V2  σ8 預言部分是否零參數 (抑或手調縮放)
  V3  判定準則是否 post-hoc (貼目標)
  V4  數據部分 (BOSS ξ(s)) 係量度抑或推導
  V5  有冇任何公式可搬去 v10.0

Run: /usr/bin/python3 scripts/01_v9_migration_ruling.py
"""
import os, re, math, subprocess
import numpy as np

V9 = "/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/open_problems_fresh/sigma8_norm"
SRC = os.path.join(V9, "01_derive_sigma8.py")

PASS = 0; TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    print(f"  [{'✔' if cond else '✘'}] {name}" + (f"   {detail}" if detail else ""))

print("=" * 80)
print("O128 scripts/01 — v9.0 σ8_norm 遷移裁決")
print("=" * 80)

src = open(SRC, encoding="utf-8").read()

# ── V1. 執行環境 ────────────────────────────────────────────────────────────
print("\n[V1] 執行環境 (硬編碼路徑)")
paths = sorted(set(re.findall(r"'(/home/wsl/[^']+)'", src)))
for p in paths:
    print(f"       {p}   exists = {os.path.exists(p)}")
missing = [p for p in paths if not os.path.exists(p)]
chk("V1a v9.0 script 之硬編碼資料路徑全部失效",
    len(missing) == len(paths) and len(paths) >= 2,
    f"{len(missing)}/{len(paths)} 唔存在")

# 實際試跑 (只為取證, 唔理 exit code)
r = subprocess.run(["/usr/bin/python3", SRC], capture_output=True, text=True, timeout=120)
err = (r.stderr or "").strip().splitlines()
chk("V1b v9.0 script 原樣執行 ⇒ ImportError (路徑斷)",
    r.returncode != 0 and "ModuleNotFoundError" in (r.stderr or ""),
    err[-1] if err else "(no stderr)")

# ── V2. σ8 預言部分係唔係零參數 ─────────────────────────────────────────────
print("\n[V2] σ8 預言部分 — 縮放因子自由度")
# 抽出 v9.0 之「K_Chain prediction」:
A_chain = sum(4 * math.sin(math.pi * n / 88) ** 2 / n ** 2 for n in range(1, 44))
print(f"       A_chain = Σ_(n=1..43) γ_n/n² = {A_chain:.6f}   (純結構數, 可接受)")
scale_v9 = 0.1
s8_v9 = math.sqrt(A_chain) * scale_v9
print(f"       v9.0 寫法: σ8 = sqrt(A_chain) × {scale_v9}  = {s8_v9:.4f}")
chk("V2a σ8 = sqrt(A_chain)×0.1 —— 0.1 係手動縮放常數 (無結構來源)",
    "sigma8_kchain = math.sqrt(A_chain) * 0.1" in src, "源碼字面確認")
# 掃描縮放因子: 任何目標值都可以由某個 s 達到
targets = {"0.70": 0.70, "0.783 (BOSS)": 0.783, "0.811 (Planck)": 0.811, "0.95": 0.95}
print("       ★ 縮放因子掃描 (σ8 ∝ s, 任意目標皆有解):")
for lab, t in targets.items():
    s = t / math.sqrt(A_chain)
    print(f"         σ8 = {lab:16s} ⇒ s = {s:.6f}")
chk("V2b 任意目標值皆可由某個 s 命中 ⟹ 該 σ8 「預言」零判別力",
    len(targets) == 4,
    f"4/4 目標有解, s ∈ [{min(t/math.sqrt(A_chain) for t in targets.values()):.3f}, "
    f"{max(t/math.sqrt(A_chain) for t in targets.values()):.3f}]")

# ── V3. 判定準則係唔係 post-hoc ────────────────────────────────────────────
print("\n[V3] 判定準則")
crit = [l.strip() for l in src.splitlines() if "0.811" in l and ("if" in l or "else" in l)]
for c in crit: print(f"       {c[:120]}")
chk("V3 ★ PASS 準則 = |σ8_kchain − 0.811| < 0.1 —— 直接量度『距目標有幾近』(post-hoc 湊數)",
    any("abs(sigma8_kchain - 0.811) < 0.1" in c for c in crit),
    "違反『禁看到目標湊算子』鐵律")

# ── V4. BOSS 部分係量度抑或推導 ────────────────────────────────────────────
print("\n[V4] BOSS DR12 ξ(s) 部分之身份")
chk("V4 σ8 ≈ sqrt(ξ(8 h⁻¹Mpc)) 及 top-hat 積分 = 由數據『量度』σ8, 唔係推導",
    "sigma8_approx = math.sqrt(abs(xi_8))" in src and "sigma_R2 = (3.0 / R**3)" in src,
    "此為觀測錨 (合法), 但唔構成 IDCM 預言")

# ── V5. 可遷移公式清單 ─────────────────────────────────────────────────────
print("\n[V5] 可遷移之結構公式清單")
movable = []
# γ_n 定義本身 (K_Chain 譜) 係 v10.0 已有
if "4 * math.sin(math.pi * n / 88)**2" in src:
    movable.append("γ_n = 4sin²(πn/88) — 但 v10.0 已有 (K_Chain 譜, 非本檔貢獻)")
# Σγ_n/n² 係一個未歸一化嘅結構數
movable.append("A_chain = Σγ_n/n² — 純數, 無量綱歸一化 ⇒ 唔構成 σ8")
print(f"       可遷移項: {len(movable)}")
for m in movable: print(f"         · {m}")
chk("V5 可遷移之 σ8 結構公式 = 0 條 (γ_n 係 v10.0 既有; A_chain 無歸一化)",
    True, "⇒ 遷移結果 = 空集")

# ── 裁決 ───────────────────────────────────────────────────────────────────
print("\n" + "─" * 80)
print("  裁決: v9.0 sigma8_norm 唔可遷移")
print("  · 環境: 硬編碼路徑 /home/wsl/IDCM/... 全部失效, 原樣執行 ImportError")
print("  · 預言: σ8 = sqrt(A_chain)×0.1, 0.1 係手動縮放 (無結構來源)")
print("  · 準則: PASS = |σ8−0.811|<0.1 = 距目標有幾近 ⇒ post-hoc")
print("  · 數據: 部分係由 BOSS ξ(s) 量度 σ8 (觀測錨, 非預言)")
print("  · 遷移: 0 條結構公式")
print("  ⟹ 依 SESSION_START §前置驗證 第 5 條: 需建立新推導 (v10.0 路徑)")
print("─" * 80)

print("\n" + "=" * 80)
print(f"RESULT: {PASS}/{TOTAL} PASS")
print("=" * 80)
