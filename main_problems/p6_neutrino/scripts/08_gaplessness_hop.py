#!/usr/bin/env python3
"""
P6 工具 #3: gaplessness 條件 — hop 帶頂 = 譜頂 (t=Δ/2 嘅結構出處)
========================================================
發現: γ₄ + 2t = γ₅ ⟺ t = (γ₅−γ₄)/2 = Δ/2
  → hop 帶 (tight-binding N-環, bandwidth 4t) 嘅頂點 (m=0, γ₄+2t)
    啱好接上 K_Chain 連續譜頂 γ₅ — 「無間隙連接」條件

結構原則: IDCM 連續 W-field, 帶結構唔可以留 gap (gap = 額外維度量/新常數)
  → gaplessness 係零新常數原則嘅直接後果, 唔係 fit

任務:
1. 驗證 gapless: γ₄+2t=γ₅ 唯一解 t=Δ/2
2. 其他 t 值留 gap 幾多? (結構判斷: 有 gap = 違背原則)
3. 推廣: 帶底 γ₄−2t = 2γ₄−γ₅ >0 檢查 (positive spectrum)
4. 對 N=8, N=10 m=1 態: γ₄+Δcos(2π/N) — 驗證喺帶內
"""
import math

def gamma(n, N=88):
    return 4 * math.sin(n * math.pi / N) ** 2

g4, g5 = gamma(4), gamma(5)
DELTA = g5 - g4
T0 = DELTA / 2

print("="*78)
print("【1】gaplessness: γ₄+2t = γ₅ → t = Δ/2")
print("="*78)
print(f"γ₄ = {g4:.10f}  γ₅ = {g5:.10f}  Δ = {DELTA:.10f}")
print(f"條件 γ₄+2t = γ₅ → t = (γ₅−γ₄)/2 = {T0:.10f} EXACT")
print(f"驗證: γ₄+2T0 = {g4+2*T0:.10f} = γ₅ ✓")
print(f"帶頂 m=0: E₀ = γ₄+2t = {g4+2*T0:.10f} = γ₅ (無間隙 ✓)")
print(f"帶底 m=N/2: E_min = γ₄−2t = {g4-2*T0:.10f} (>0? {'✓' if g4-2*T0>0 else '✗'})")

print()
print("="*78)
print("【2】其他 t 值嘅 gap（結構判準）")
print("="*78)
print(f"{'t/T0':>8} {'t':>12} {'band top':>12} {'gap to γ₅':>12} {'gap/Δ':>10} {'結構':>6}")
for f in [0.5, 0.75, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5]:
    t = T0*f
    top = g4 + 2*t
    gap = g5 - top
    verdict = "❌" if abs(gap) > 1e-10 else "✅"
    print(f"{f:8.2f} {t:12.8f} {top:12.8f} {gap:12.8f} {gap/DELTA:10.4f} {verdict}")
print("→ 只有 t=T0 (f=1.0) 令 gap=0; 其他全部留帶隙 (違背 gapless 原則)")

print()
print("="*78)
print("【3】m=1 Hob 態位置 (束縛態) 帶内驗證")
print("="*78)
for N in [8, 10]:
    c = math.cos(2*math.pi/N)
    E1 = g4 + 2*T0*c
    # 帶範圍 [γ₄−Δ, γ₄+Δ] = [2γ₄−γ₅, γ₅]
    lo, hi = g4-2*T0, g5
    inside = lo <= E1 <= hi
    print(f"N={N}: cos=2π/{N}={c:.6f}; E₁=γ₄+Δcos = {E1:.8f}")
    print(f"  帶範圍 [{lo:.8f}, {hi:.8f}]: {'帶内 ✓' if inside else '帶外 ✗'}")
    # 相對位置
    pos = (E1-lo)/(hi-lo)*100
    print(f"  帶内位置: {pos:.1f}% (由底起)")

print()
print("="*78)
print("【4】譜頂 γ₅ 嘅 K_Chain 身份")
print("="*78)
print(f"γ₅ = 4sin²(5π/88) — mode 5 = 最小非基態 mode")
print(f"γ₄ = 4sin²(4π/88) — mode 4 = 基態 (γ_B)")
print(f"能隙 Δ = γ₅−γ₄ 夾住基態之上第一激發")
print(f"hop 帶 [γ₄−Δ, γ₄+Δ] = [{2*g4-g5:.6f}, {g5:.6f}] — 上緣係 γ₅ 本身")
print(f"→ interference band 由 chain 連續譜「借」出: 上接 γ₅, 底 2γ₄−γ₅")
print(f"  底 = γ₁²? check: 2γ₄−γ₅ = {2*g4-g5:.8f} vs γ₄ = {g4:.8f}")

print()
print("="*78)
print("【5】結論 — gaplessness 推導")
print("="*78)
print("""
  t = Δ/2 嘅結構出處 (new, 2026-10-20):
    IDCM 連續性原則 (零新常數) ⟹ hop 帶 (任何 interference 帶結構)
    唔可以同 K_Chain 連續譜之間留 gap ⟹ 帶頂 γ₄+2t = 譜頂 γ₅
    ⟹ t = (γ₅−γ₄)/2 = Δ/2  EXACT, 唯一

  呢個唔係 fit:
    - gaplessness 係結構原則 (連續譜無縫接合), 唔係針對 m₁/m₂ 調 t
    - 一旦接受, t 完全固定, 冇自由度
    - 帶底 2γ₄−γ₅ = 0.03593 > 0 保證正譜 (唔越零)

  #1 機制鏈而家:
    γ_B (K_Tree 33-block 基態 = γ₄, O68)
    + hop 帶 (gapless 條件 → t=Δ/2, 帶頂接 γ₅)
    + N-環 Bloch 激發 (N=2B/2F₅ = O179 hop 週期)
    = 束縛態 γ_B + Δ·cos(2π/N) ✓
""")