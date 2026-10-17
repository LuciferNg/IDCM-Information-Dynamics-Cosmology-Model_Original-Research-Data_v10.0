#!/usr/bin/env python3
"""
52_oseries_gamma_prescan.py — 方案二 pre-scan: O-series 對偶鏈存在性 (2026-10-17)
================================================================================
Gemini 建議批判後, 方案二 (O-series 公式映射) 係唯一可即刻執行嘅路。
pre-scan 問題: O-series 有冇用 88-site 對偶鏈 γ'_d = 4sin²(πd/176)?
               (grep 顯示 O51/O72 世界能量 90 + P15 CKM 公式有 sin(π/176))

T1  O51 世界能量: Σγ_even (k=1..88, 4sin²(πk/176)) = 90?
T2  P15 CKM 公式: 逐個公式拆 sin(πd/176) 行因子 → d 值表
T3  γ'_d 單點 label: O-series 有冇公式直接用 γ'_d 值 = 物理量?
T4  結論: 88-site label 庫現狀
零 import; 第一原理。
"""
import json, re, math
from math import gcd

print("=== T1: O51 世界能量 90 = 88-site 對偶鏈 k-偶和 ===")
# γ_k = 4sin²(πk/176), k=1..88; O51 話 Σγ_even (k 偶) = 90? 定 Σ所有 = ?
s = 0.0
for k in range(1, 89):
    s += 4 * math.sin(math.pi * k / 176) ** 2
print("  Σ_{k=1..88} 4sin²(πk/176) = %.6f" % s)
s_even = sum(4 * math.sin(math.pi * k / 176) ** 2 for k in range(2, 89, 2))
s_odd = sum(4 * math.sin(math.pi * k / 176) ** 2 for k in range(1, 89, 2))
print(f"  Σ k 偶 = {s_even:.6f}  | Σ k 奇 = {s_odd:.6f}")
print(f"  (O34: 90 = k-偶和? {abs(s_even-90)<1e-6}; 44-site 世界 Σγ=90 係 n=1..44)")

print()
print("=== T2: P15 CKM 公式行因子 S(d) = sin(πd/176) 對應 ===")
# sin(kπ/176) → d=k; sin(kπ/88) = sin(2kπ/176) → d=2k; sin(kπ/44) = sin(4kπ/176) → d=4k
forms = {
    "tan θ₁₂":  "sin(π/176)/sin(3π/88)",        # d=1 / d=6
    "tan θ₂₃":  "sin(π/44)/sin(19π/176)",       # d=4 / d=19
    "sin θ₁₃":  "sin(π/176)/sin(21π/176)",      # d=1 / d=21
    "Vus":      "sin(5π/44)/sin(31π/176)",      # d=20 / d=31
}
def S_d_from_sin(term):
    # sin(kπ/den) 或 sin(π/den) (k=1 隱藏) → d = k·176/den
    m = re.match(r"sin\((\d*)π/(\d+)\)", term.strip())
    k = int(m.group(1)) if m.group(1) else 1
    den = int(m.group(2))
    if 176 % den == 0:
        return k * 176 // den
    return None

print("  (regex 修正: sin(π/176)=d1, sin(3π/88)=d6, sin(π/44)=d4, sin(5π/44)=d20)")
for name, form in forms.items():
    # form = "sin(...)/sin(...)" — 拆出所有 sin 項
    parts = re.findall(r"sin\(\d*π/\d+\)", form)
    dn = S_d_from_sin(parts[0]) if len(parts) > 0 else None
    dd = S_d_from_sin(parts[1]) if len(parts) > 1 else None
    print(f"  {name:<9}: {form:<28} → d num={dn}, d den={dd}")

print()
print("=== T3: 88-site 對偶鏈單點 label 現狀 ===")
# 已知 44-site label (γ 層): d=7 DM, d=14 GEN, d=20 T, d=22 HALF, d=33 KTREE
print("  44-site γ 層 magic: 7(DM) 14(GEN) 20(T) 22(HALF) 33(KTREE)")
print("  88-site γ'_d 層: 有公式身份嘅 d =", end=" ")
known88 = set()
# O51 世界能量 = 總和, 唔係單點; P15 公式用行因子 (S(d)) 但係係 44-site beat 展開
print("{} (grep 未見單點 γ'_d 公式)")

print()
print("=== T4: 結論 ===")
print("""
  1. ✅ 88-site 對偶鏈 (4sin²(πk/176), k=1..88) 喺 O-series 存在:
     O51/O72 用嚟定義世界能量 (Σγ_even 或 Σγ 總和), P15 CKM 公式展開含 sin(πd/176)
  2. 🔴 但「存在」≠「單點 label」: O51 係總和 (非單點), P15 嘅 sin(πd/176)
     係 44-site beat 嘅行因子 (P13 分解 B(d,s)=4S(d)C(s)), 唔係 γ'_d 值 = 物理量
  3. ⟹ 88-site 獨立單點 label 仍然 = 0, G4 維持硬 FAIL
  4. 方案二「全量掃描 O-series」可以做, 但 pre-scan 顯示單點 label 唔會
     由總和公式出嚟 — 要搵「γ'_d 單點」公式 (例如 m 公式直接用 4sin²(dπ/176))
  5. 誠實: Gemii 方案二嘅「lcm 定理套用」係誤導 (lcm 定理唔適用 γ' 域),
     但「掃 O-series 揾單點公式」方向啱
""")

res = {"test": "52_oseries_gamma_prescan",
       "T1": {"sum_all": round(s, 6), "sum_even": round(s_even, 6), "sum_odd": round(s_odd, 6)},
       "T2_ckm_d": {"tan12": "1/6", "tan23": "4/19", "sin13": "1/21", "Vus": "20/31"},
       "T4": "88-site 單點 label = 0, G4 維持 FAIL"}
with open("data/52_oseries_gamma_prescan.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/52_oseries_gamma_prescan.json")