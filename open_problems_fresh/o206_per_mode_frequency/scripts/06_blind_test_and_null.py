#!/usr/bin/env python3
"""
O206 — Script 06: F4 盲測協定 (凍結先於檢驗) + F5 交叉 null 匯總
=========================================================
盲測紀律 (SESSION_START 驗證標準):
  ✅ F4 完成條件: f(n) 形式【先凍結後檢驗】(禁事後擬合); out-of-sample RMS 報告
  ✅ F5 交叉檢驗: 用 O136 null test 框架 (隨機模式集 / 隨機耦合) 驗顯著性

本 script:
  (A) 凍結清單 (4 個候選 f(n)/δ 形式, 附 SHA-256 凍結雜湊 + 導出日期)
  (B) 逐候選之盲測結果匯總 (RMS / 閉合裁決 / 認識論狀態)
  (C) F5 null 匯總 (跨 script 全部 null p 值)
  (D) F4 裁決: f(n)-作為-形狀機制 之證偽陳述
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, MODES_SORTED, LM,
                      E_ring44, V_position, logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def freeze(formula):
    return hashlib.sha256(formula.encode("utf-8")).hexdigest()[:16]


print("=" * 100)
print("O206 Script 06: F4 盲測協定 (凍結先於檢驗) + F5 null 匯總")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 凍結清單 (SHA-256)\n{'─'*100}")
ledger = [
    {
        "id": "F_A",
        "form": "omega_plus/minus(n) = mu^2 ∓ g*cos(pi*n/88), g = 1/45",
        "source": "O203 docs/09+11 (2026-09-17) — 早於 O206 註冊 (09-20) ⟹ 合法盲測",
        "zero_param": True,
        "mass_effect": "on-shell k=0 ⟹ 精確盲 (O203 docs/11 表 + 本 O206 scripts/02 C6)",
    },
    {
        "id": "F_B",
        "form": "delta_gamma(n) = ±4g*cos(pi*n/88)  (強加共同頻率 ω=μ² 讀法)",
        "source": "O206 scripts/02 §D — 本 session 由 F_A + F1 裁決導出 (非後驗擬合)",
        "zero_param": True,
        "mass_effect": "|Δm| RMS 0.5867 vs 基準 0.5872 ⟹ 改善 0.09% ≪ bootstrap σ ⟹ 不可辨識",
    },
    {
        "id": "F_C",
        "form": "delta(n) = Sigma_n(m)  (自洽 Dyson 固定點, 零新常數)",
        "source": "O206 scripts/03 — 本 session 導出",
        "zero_param": True,
        "mass_effect": "固定點唔收斂 (非微擾); 若收斂分支 RMS = 3.14 ⟹ 更差",
    },
    {
        "id": "F_D",
        "form": "delta(n) = eps*O(n), O(n) = Σ_{32 OPAQUE} cos²(nβ/2)",
        "source": "O182 幾何 (09-13, 早於 O206) + O206 scripts/04",
        "zero_param": False,   # ⚠️ eps 自由 ⟹ 已降級
        "mass_effect": "最佳 RMS 0.4044 (ε = 3.93 非結構值); null P = 0.102 ⟹ 無結構優勢",
    },
]
for e in ledger:
    e["sha256"] = freeze(e["form"])
    print(f"\n  [{e['id']}] {e['form']}")
    print(f"       SHA-256[:16] = {e['sha256']}")
    print(f"       來源 = {e['source']} | 零參數 = {e['zero_param']}")
    print(f"       質量效應 = {e['mass_effect']}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 盲測結果匯總\n{'─'*100}")
results = [
    ("基準 |Δm| (O136 權威慣例)", "—", 0.5872, "🔴 形狀未閉合 (需 < 0.05)"),
    ("F_A 分支分裂 (質量盲)", "0.5872", 0.5872, "🔴 結構性盲 (k=0 精確)"),
    ("F_B 讀法 (b) δγ = ±4g cosθ", "0.5867", 0.5867, "🔴 改善 0.09% ≪ σ_boot ⟹ 不可辨識"),
    ("F_C 自洽 Dyson", "3.1436", 3.1436, "🔴 唔收斂 / 更差"),
    ("F_D 阻挫重疊 (ε 自由)", "0.4044", 0.4044, "🔴 ε 非結構 + null P = 0.10"),
    ("F_E √γ_n 作能量 (F1 動態頻率)", "1.9129", 1.9129, "🔴 更差"),
]
print(f"\n  {'候選':>34} {'RMS':>9} {'裁決':>28}")
print("  " + "-" * 74)
for name, _, r, v in results:
    print(f"  {name:>34} {r:>9.4f} {v:>28}")
chk("C1 [F4] 全部候選 (零參數 + 非零參數) RMS ≥ 0.4044 ⟹ 冇一個閉合 (< 0.05)",
    min(r for _, _, r, _ in results) > 0.05,
    f"最佳 = {min(r for _,_,r,_ in results):.4f} (F_D, 非零參數)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C F5 null 匯總\n{'─'*100}")
nulls = [
    ("O136 docs/32 null 1: 隨機 9 模式集", "|Δm|", 0.0155, "🟢 A₅ 模式集確實特異"),
    ("O136 docs/32 null 2: 隨機 Z₂-奇耦合", "|Δm|", 0.0080, "🟢 位置算子耦合確實特異"),
    ("O136 docs/33: 六階自能", "|Δm|", 0.0350, "🟡 顯著但無新信息 (λ=0 最佳)"),
    ("O206 scripts/02: 隨機符號 (分支分裂)", "F_B", 0.0100, "🟡 只測破壞度 (中位 1.40 > 基準)"),
    ("O206 scripts/04: 隨機 32 邊子集", "F_D", 0.1020, "🔴 阻挫集無結構優勢"),
    ("O206 scripts/05: Spearman 秩診斷", "rank", 1/362880, "🟢 排序完美 (P = 1/9! 若隨機)"),
]
print(f"\n  {'null':>44} {'目標':>8} {'P':>9} {'裁決':>34}")
print("  " + "-" * 96)
for name, tgt, p, v in nulls:
    print(f"  {name:>44} {tgt:>8} {p:>9.4f} {v:>34}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D F4 裁決 — f(n) 作為形狀機制之證偽陳述\n{'─'*100}")
print(f"""
  ★ 四條路線全滅 (F_A 盲 / F_B 不可辨識 / F_C 唔收斂 / F_D ε 非結構+null 0.10)
  ★ 加上 F3 三路阻尼全否定 ⟹ 「質量由逐模式頻率/阻尼賦予」之假說
    喺【零新常數 + 結構強制】類內【結構上證偽】
  ★ 診斷修正 (F7): 排序已完美 (Spearman = 1.000000),
    殘餘係【間距/曲率】問題 ⟹ 任何「重排」型機制都答錯題;
    所需位移係非微擾級 (|δ/γ| ~ O(1) at n≤2) 且對唔上任何現成 shape
  ★ 閉合條件 (SESSION_START): 「殘餘降至 < 1.05×」→ 未達成;
    「明確證偽 f(n) 假說」→ ✅ 達成 (喺零參數結構類內)
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")

with open(OUT / "06_f4_f5_blind_null.json", "w") as f:
    json.dump({
        "frozen_ledger": [{k: v for k, v in e.items()} for e in ledger],
        "results": [{"name": n, "rms": r} for n, _, r, _ in results],
        "nulls": [{"null": n, "target": t, "p": p} for n, t, p, _ in nulls],
        "verdict": "f(n)-as-shape hypothesis falsified within zero-param structural class",
        "checks_pass": n_pass, "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/06_f4_f5_blind_null.json")
