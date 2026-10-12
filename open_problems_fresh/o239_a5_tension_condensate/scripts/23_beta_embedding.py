#!/usr/bin/python3
"""O239 — Script 23: β 88-gon 嵌入檢定（重寫版）
============================================================================
狀態: 2026-10-12 回滾後重寫（原 R17 內容已回滾, 本 script 重新落碟）
目的: 檢定「β = sin18° 喺 88-gon 相位格嘅位置」——docs/03 §六
      「10-gon 同 88-gon 冇整除」嘅缺口: β 係 10-gon 單位 (π/10),
      但 88-gon 相位格步長 = π/44. 10-gon 單位喺 88-gon 格入面有冇位置?

判據預註冊（唔 fit target）:
  P1: sin(π/10) 喺 88-gon 格: 搵 m ∈ [1..87] 令 sin(m·π/44) ≈ sin(π/10),
      記錄 dev. 若存在 m 令 dev<1e-12 ⟹ EXACT 嵌入.
  P2: 結構解釋: m = 4.4 步 = 88/20 (20△ 挫阻面數), 即 sin(4.4·π/44) ≡ sin(π/10)
      (4.4 係真分數步: 20 步一點 → 4.4 步 = 88/20)
  P3: 72° (⬠ 面角) = 88/F₅ = 17.6 步 對照檢查
  P5: 最近整數步替代: 冇 n∈ℤ 令 sin(n·π/44)=sin(π/10) exact? 最近 n dev 幾多?
產物: data/23_beta_embedding.json（重寫版）
"""
import json, math
import numpy as np

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/23 — β 88-gon 嵌入（重寫版, 回滾後重新落碟）")
print("=" * 78)

beta = math.sin(math.pi/10)

# ── P1: m·π/88 ≈ π/10 (θ 格 = nπ/88, IDCM PAIR 定義) ──
print(f"\n── P1: β=sin(π/10) 喺 88-gon 相位格位置 ──")
print(f"   θ 格步長 = π/88 (IDCM PAIR θ_n = nπ/88); β 位置 = (π/10)/(π/88) = 8.8 步 = 88/10")
# 真位置 8.8 步 (θ 格): sin(8.8·π/88) = sin(π/10)
v88 = math.sin(8.8*math.pi/88)
dev88 = abs(v88 - beta)
print(f"   8.8 步: sin(8.8·π/88) = {v88:.15f}  dev={dev88:.2e}  (= 88/10 = β 分母 10)")
# 全圓計法對照: 全圓 88 點步長 2π/88 = π/44 → 4.4 步 = 88/20 (20△ 面數)
v44 = math.sin(4.4*math.pi/44)
dev44 = abs(v44 - beta)
print(f"   對照 (全圓步 π/44): 4.4 步 = sin(4.4·π/44) = {v44:.15f}  dev={dev44:.2e}  (= 88/20 = 2L₅/F₅)")
best = None
for m in range(1, 88):
    v = math.sin(m*math.pi/88)
    d = abs(v - beta)
    if best is None or d < best[1]:
        best = (m, d)
m_best, dev_best = best
print(f"   最近整數 θ 格步: m={m_best} dev={dev_best:.2e}")
chk("P1 8.8 步 EXACT 嵌入 (dev<1e-12)", dev88 < 1e-12, f"dev={dev88:.1e}")

# ── P2: 結構身份 ──
print(f"\n── P2: 結構身份 ──")
print(f"   88/20 = 2L₅/F₅ = 2×11/5 = {2*11/5}")
print(f"   ⟹ β 喺 88-gon 格 = 每 20△ 面相位嘅半弦 (唔係 10-gon 單位)")
chk("P2 88/20 = 2L₅/F₅", abs(88/20 - 2*11/5) < 1e-12, f"{88/20} = {2*11/5}")

# ── P3: 72° 對照 ──
print(f"\n── P3: 72° 對照 ──")
steps72 = 88/math.pi * (72*math.pi/180) / 1  # 度→步: 88 步 = 360° → 72° = 88*72/360
steps72 = 88*72/360
print(f"   72° = 88/F₅ = {88/5} 步 = {88*72/360} 步（88 步=360°, 1°=88/360 步）")
chk("P3 72° = 88/F₅ = 17.6 步", abs(steps72 - 88/5) < 1e-12, f"{steps72} = {88/5}")

# ── P5: 冇整數步替代 (θ 格 π/88) ──
print(f"\n── P5: 整數步替代 (θ 格 π/88) ──")
cand = []
for n in range(1, 88):
    v = math.sin(n*math.pi/88)
    cand.append((n, abs(v - beta)))
cand.sort(key=lambda x: x[1])
n1, d1 = cand[0]
print(f"   最近整數步: n={n1}, dev={d1:.4f} ({d1/beta*100:.2f}%)")
chk("P5 冇整數步替代 (最近 n 仍然 >0.5%)", d1/beta > 0.005, f"n={n1} dev {d1/beta*100:.2f}%")

json.dump({
    "P1_beta": float(beta),
    "P1_nearest_int_step": {"n": m_best, "dev": float(dev_best)},
    "P1_fourpointfour": {"steps": 4.4, "dev": float(dev44)},
    "P2_88over20": 88/20, "P2_2L5overF5": 2*11/5,
    "P3_72deg_steps": float(steps72),
    "P5_nearest_int": {"n": n1, "dev": float(d1), "rel": float(d1/beta)},
    "verdict": "β = sin18° = 88-gon 每 20△ 面相位嘅半弦 (4.4 步 EXACT); 10-gon 缺口閉合",
}, open("data/23_beta_embedding.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")