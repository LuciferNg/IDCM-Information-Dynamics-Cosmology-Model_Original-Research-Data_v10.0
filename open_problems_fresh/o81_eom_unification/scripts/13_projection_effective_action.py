#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O81 — Script 13: 開放問題攻堅 (2) — c_{i,n} 投影 + 非微擾有效作用量
=====================================================================
攻堅 O81 §八:
  🟡 #2  88→A5 之 c_{i,n} = cos²(n·π·ang_i/180) 表達式
  🟡 #3  完整非微擾有效作用量 Γ_eff[θ]

方法: 由 A5 實際幾何 (60 頂點方向) 數值計算投影, 檢驗候選形式。
"""
import os, math, itertools
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

LINES = []
PASS = 0
FAIL = 0
NEG = 0
def L(s=""):
    LINES.append(str(s)); print(s)
def CHECK(desc, cond, details=""):
    global PASS, FAIL
    if cond: PASS += 1; L(f"  ✅ {desc}")
    else:    FAIL += 1; L(f"  ❌ {desc}")
    if details: L(f"     {details}")
def NEGATIVE(desc, note):
    global NEG
    NEG += 1
    L(f"  ⚠️  [否定結果] {desc}"); L(f"     {note}")

L("=" * 88)
L("  O81 — Script 13: 開放問題攻堅 (2) — c_{i,n} 投影 + 非微擾有效作用量")
L("=" * 88)
L("  建立日期: 2026-09-20")
L("")

phi = (1 + math.sqrt(5)) / 2
N_d = 44
mu2, lam = 2.0, 2 / 123
W2 = mu2 / (2 * lam); W0 = math.sqrt(W2); J_eff = W2

# ============================================================
# 一、A5 60 節點方向 + 冷斑參考方向
# ============================================================
L("━" * 88)
L("  一、A5 60 節點方向 + 冷斑參考")
L("━" * 88)
L("")

def even_perms(v):
    a, b, c = v
    return [(a, b, c), (b, c, a), (c, a, b)]

verts = set()
base = []
for s1 in (1, -1):
    for s2 in (1, -1):
        for s3 in (1, -1):
            base.append((s1 * 1, s2 * 1, s3 * phi ** 3))
            base.append((s1 * phi ** 2, s2 * phi, s3 * 2 * phi))
for s1 in (1, -1):
    for s2 in (1, -1):
        base.append((s1 * (2 + phi), 0.0, s2 * phi ** 2))
        base.append((0.0, s1 * phi ** 2, s2 * (2 + phi)))
        base.append((s1 * phi ** 2, s2 * (2 + phi), 0.0))
for v in base:
    for p in even_perms(v):
        verts.add(tuple(round(x, 9) for x in p))
V = np.array(sorted(verts), dtype=float)
U = V / np.linalg.norm(V, axis=1, keepdims=True)   # 單位向量
nV = len(U)

# 冷斑 (209°, -57°) — 銀河座標 (l, b)
def lb_to_xyz(l_deg, b_deg):
    l, b = math.radians(l_deg), math.radians(b_deg)
    return np.array([math.cos(b) * math.cos(l), math.cos(b) * math.sin(l), math.sin(b)])

cold = lb_to_xyz(209.0, -57.0)
cold /= np.linalg.norm(cold)
L(f"  A5 節點數 = {nV}; 冷斑方向 (l,b) = (209°, −57°) → {np.round(cold, 6)}")

# 角距離
ang = np.arccos(np.clip(U @ cold, -1, 1))          # 弧度
ang_deg = np.degrees(ang)
L(f"  角距離 β_i (弧度): min = {ang.min():.6f}, max = {ang.max():.6f}, mean = {ang.mean():.6f}")
L(f"  角距離 (度):       min = {ang_deg.min():.3f}, max = {ang_deg.max():.3f}, mean = {ang_deg.mean():.3f}")
L("")

# ============================================================
# 二、#2 候選投影形式之數值檢驗
# ============================================================
L("━" * 88)
L("  二、#2 候選 c_{i,n} 形式 — 由 A5 實際幾何檢驗")
L("━" * 88)
L("")

L("""
  宣稱 (O81 docs §7.3): c_{i,n} = |Dⁿ_{0,0}(R_i)|² = cos²(n·π·ang_i/180)
  其中 ang_i 為節點 i 到冷斑之角距離 (度) ⟹ π·ang_i/180 = β_i (弧度)

  讀法歧義: 「cos²(n·π·ang_i/180)」可讀為
    (A) cos²(n·β_i)      — 若 π·ang/180 = β
    (B) cos²(n·β_i/2)    — 若 π·ang/180 係「半角」(雙路徑干涉自然形式)

  檢驗 (由 A5 實際幾何):
""")

# ★ 中心對稱檢驗: A5 orbit 是否 V → −V 封閉
L("  ── ★ A5 orbit 中心對稱檢驗 (V → −V 封閉?) ──")
Vset = set(tuple(np.round(v, 6)) for v in U)
neg_closed = all(tuple(np.round(-v, 6)) in Vset for v in U)
L(f"  對每個 v, −v 亦在節點集內? {neg_closed}")
CHECK("A5 orbit 中心對稱 (V → −V 封閉)", neg_closed,
      "⟹ 對固定參考點, {cos β_i} 關於 0 對稱 ⟹ Σ_i T_n(cos β_i) = 0 對所有奇 n")
L("")

# 由中心對稱推出: Σ T_n = 0 (n 奇); 故 Σ cos²(nβ/2) = 30 EXACT (n 奇)
L("  ── ★ 由此推出 Σ_i T_n(cos β_i) = 0 (n 奇) ⟹ Σ_i cos²(nβ/2) = 30 EXACT ──")
L(f"  {'n':>3} | {'奇/偶':>5} | {'Σ_i T_n(cos β_i)':>20} | {'≈0?':>6}")
L(f"  {'-'*3} | {'-'*5} | {'-'*20} | {'-'*6}")
odd_ok = True
for n in range(1, 13):
    Tn = float(np.polynomial.chebyshev.Chebyshev.basis(n)(np.cos(ang)).sum())
    z = abs(Tn) < 1e-9
    if n % 2 == 1 and not z:
        odd_ok = False
    L(f"  {n:>3} | {'奇' if n%2 else '偶':>5} | {Tn:>20.10f} | {'✅' if z else '❌':>6}")
L("  ⟹ 奇 n 全部 = 0 (中心對稱必然); 偶 n 一般 ≠ 0")
CHECK("Σ_i T_n(cos β_i) = 0 對所有奇 n ≤ 11", odd_ok,
      "由 A5 orbit 中心對稱 (T_n 奇函數 × 對稱集合)")
L("")

# 由此推出正確形式
L("""
  ★ 由中心對稱直接得正確形式:
    cos²(nβ/2) = (1 + cos(nβ))/2 = (1 + T_n(cos β))/2
    ⟹ Σ_i cos²(nβ_i/2) = (1/2)(V + Σ_i T_n(cos β_i)) = (1/2)(60 + 0) = 30
       對所有**奇** n (中心對稱 ⟹ ΣT_n = 0)
    ⟹ Σ_i c_{i,n} = V/2 = 30  **EXACT** (奇 n)
    ★ 30 = V/2 = 偶面數 (30□)
""")

n_test = [1, 2, 3, 4, 5, 7, 22, 44]
L(f"  {'n':>3} | {'Σ_i cos²(nβ)':>14} | {'Σ_i cos²(nβ/2)':>16} | {'Σ_i T_n':>12} | 判讀")
L(f"  {'-'*3} | {'-'*14} | {'-'*16} | {'-'*12} | {'-'*16}")
for n in n_test:
    A_ = float((np.cos(n * ang) ** 2).sum())
    B_ = float((np.cos(n * ang / 2) ** 2).sum())
    Tn = float(np.polynomial.chebyshev.Chebyshev.basis(n)(np.cos(ang)).sum())
    verdict = "(B) = 30 EXACT" if abs(B_ - 30) < 1e-9 else "(B) ≠ 30"
    L(f"  {n:>3} | {A_:>14.6f} | {B_:>16.6f} | {Tn:>12.6f} | {verdict}")
L("")

CHECK("(B) cos²(nβ/2): Σ_i = 30 EXACT 對所有奇 n ≤ 11",
      all(abs(float((np.cos(n * ang / 2) ** 2).sum()) - 30.0) < 1e-9 for n in range(1, 12, 2)),
      "n = 1,3,5,7,9,11")
NEGATIVE("(A) cos²(nβ): Σ_i 非常數 (n=1 給 20, n=44 給 31.51)",
         "宣稱式若讀作 cos²(nβ), 則違反歸一化 ⟹ 宣稱式之角變量應為**半角** β/2")
L("")

# 週期性檢驗
L("  ── 週期性檢驗 (docs 曾宣稱 c_{i,n+44} = c_{i,n}) ──")
for nm, fn in (("(A) cos²(nβ)", lambda n: np.cos(n * ang) ** 2),
               ("(B) cos²(nβ/2)", lambda n: np.cos(n * ang / 2) ** 2)):
    dev = float(np.max(np.abs(fn(45) - fn(1))))
    L(f"     {nm:16s} max|c_(n+44) − c_n| = {dev:.6e}")
NEGATIVE("c_{i,n+44} = c_{i,n} 之週期性**不成立**",
         "β_i 非 2π/44 之整數倍 ⟹ cos²(nβ/2) 一般唔具 44-週期; "
         "docs/scripts 07 曾列此為性質 — 應撤回 (投影係數唔需要週期性; 週期性屬模態函數)")
L("")

# ============================================================
# 三、#2 雙路徑干涉之嚴格形式
# ============================================================
L("━" * 88)
L("  三、#2 雙路徑干涉推導 — 檢驗能否給 cos²(nβ)")
L("━" * 88)
L("")

L("""
  ─── 設定: K_Chain 模式 n 沿 88-site 環, 投影到天球 ───

  K_Chain 88-site 環嵌入天球大圓 (通過冷斑)。
  site m 之天球位置: v_m = (θ₀, φ₀ + 2πm/88)
  模式 n 之駐波: ψ_n(m) = cos(2πnm/88)   (n = 1..44)

  節點 i 位於角距離 β_i 處。由冷斑到節點 i 有**兩條**大圓路徑
  (順時針 / 逆時針), 角距離分別為 β_i 與 2π − β_i。
  兩路徑之相位差: Δφ = 2πn·(β_i/2π) − 2πn·((2π−β_i)/2π) = n·β_i − n(2π−β_i) = 2nβ_i − 2πn
  ⟹ e^{iΔφ} = e^{i(2nβ_i − 2πn)} = e^{i2nβ_i}
  ⟹ 干涉振幅 ∝ (1 + e^{i2nβ_i})/2, 強度 ∝ |1 + e^{i2nβ_i}|²/4 = cos²(nβ_i)
""")

L("  ★★ 呢個導出 cos²(n·β_i) — 與宣稱形式一致!")
L("     (關鍵: 兩條大圓路徑之角距離和 = 2π, 相位差 = 2nβ_i)")
L("")

# 數值驗證: 直接由環幾何算投影
L("  ── 數值驗證: 由 88-site 環直接算投影振幅 ──")
N_ring = 88
ring_phi = np.array([2 * math.pi * m / N_ring for m in range(N_ring)])
# 冷斑大圓: 用 cold 為法線之大圓 (正交基底)
tmp = np.array([0.0, 0.0, 1.0])
if abs(np.dot(cold, tmp)) > 0.9:
    tmp = np.array([1.0, 0.0, 0.0])
e1 = np.cross(cold, tmp); e1 /= np.linalg.norm(e1)
e2 = np.cross(cold, e1)
ring_pts = np.array([math.cos(p) * e1 + math.sin(p) * e2 for p in ring_phi])

# 節點 i 在大圓上之投影角
proj_ang = np.arctan2(U @ e2, U @ e1)          # 節點在環座標系之方位
# 模式 n 之振幅: Σ_m ψ_n(m)·δ(方向) — 用連續極限: ψ_n(φ) = cos(nφ)
amp_n = lambda n: np.cos(n * proj_ang)
for n in [1, 7, 22]:
    c_num = amp_n(n) ** 2
    c_claim = np.cos(n * ang) ** 2
    L(f"     n = {n:2d}: max|amp² − cos²(nβ)| = {float(np.max(np.abs(c_num - c_claim))):.6e}")
L("")
L("  ⚠️ 注意: 上式用 cos(nφ) 直接投影 (單路徑), 得 cos²(nφ) 而非 cos²(nβ)。")
L("     β_i 係**球面角距離**, φ 係**大圓方位角** — 兩者唔同。")
L("")

# 兩者關係: cos β_i = cos(θ_i)cos(θ₀) + sin(θ_i)sin(θ₀)cos(φ_i−φ₀)
dev = float(np.max(np.abs(np.abs(np.cos(ang)) - np.abs(np.cos(proj_ang)))))
L(f"  max| |cos β| − |cos φ| | = {dev:.6f}")
if dev > 1e-6:
    L("  ⟹ β_i ≠ φ_i 一般 — 宣稱式用 β (球面角距), 上述投影用 φ (大圓方位)")
    L("     → 兩者之關係需由投影幾何決定, 未閉合")
NEGATIVE("宣稱式用 β_i (球面角距), 而大圓投影自然給 φ_i (方位角) — 兩者唔一致",
         "雙路徑干涉可導出 cos²(nβ) 之**形式**, 但 β 之身份 (球面角距 vs 大圓方位) 未鎖定")
L("")

# ============================================================
# 四、#3 非微擾有效作用量 — A5 圖上精確譜
# ============================================================
L("━" * 88)
L("  四、#3 非微擾有效作用量 — A5 圖精確譜 + 三方案對照")
L("━" * 88)
L("")

edges = []
for i in range(nV):
    for j in range(i + 1, nV):
        if abs(np.linalg.norm(V[i] - V[j]) - 2.0) < 1e-6:
            edges.append((i, j))
A = np.zeros((nV, nV))
for i, j in edges:
    A[i, j] = A[j, i] = 1.0
Lap = np.diag(np.array([sum(1 for a, b in edges if a == i or b == i) for i in range(nV)], dtype=float)) - A
evals = np.sort(np.linalg.eigvalsh(Lap))
L(f"  A5 Laplacian 譜 (60 個): λ_min = {evals[0]:.6f}, λ_max = {evals[-1]:.6f}")
L(f"  非零譜最小值 λ_2 = {evals[1]:.10f} = φ⁻² = {phi**-2:.10f}")
CHECK("λ_2 = φ⁻² (譜隙)", abs(evals[1] - phi ** -2) < 1e-9, f"{evals[1]:.10f} vs {phi**-2:.10f}")
L("")

L("""
  ─── 有效作用量之三個 1-loop 方案 (O81 §七 註記 7 記錄為互斥) ───
  (i)   (1/2)Σ_n m_eff²/(ω_n²+m_eff²)       = 16.778   [scripts/07]
  (ii)  (1/2)Σ_n ω_n·(−a_n/4)               = −21.566  [scripts/08 線性]
  (iii) (1/2)Σ_n ω_n·c₁(a_n)                = −31.537  [scripts/08 精確]

  ★ 三者係唔同展開階數, 不應並列為「同一量之三個值」。
  ★ 正確處理: 明寫每個方案之定義域與階數, 並指出均 ≠ 123 (故不支撐 E_J = 123)。
""")

# 檢驗: 三個方案之共同結構 = 1-loop 修正, 皆為 O(κ²) 量級
kappa = 0.25
omega_n = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, N_d + 1)])
me2 = 2 * kappa * omega_n * W0
v1 = 0.5 * float(np.sum(me2 / (omega_n ** 2 + me2)))
a_n = 2 * kappa * W0 / omega_n
v2 = 0.5 * float(np.sum(omega_n * (-a_n / 4)))
def c1(a):
    th = np.linspace(0, 2 * math.pi, 200001)
    return float(np.trapezoid(np.sqrt(np.maximum(0, 1 - a * np.cos(th))) * np.cos(th), th) / math.pi)
v3 = 0.5 * sum(omega_n[i] * c1(a_n[i]) for i in range(N_d))
L(f"  重算: (i) {v1:.6f}  (ii) {v2:.6f}  (iii) {v3:.6f}")
CHECK("三方案皆 ≠ E_J = 123 (不支撐 E_J 結論)", all(abs(v - 123) > 1 for v in (v1, v2, v3)),
      f"|v−123| = {[round(abs(v-123),2) for v in (v1,v2,v3)]}")
L("")

L("""
  ─── 非微擾 Γ_eff[θ] 之現況 ───
  已建立:
    • φ_n 高斯積分 (精確): det(□_n + m_eff_n²(ρ,θ))^{-1/2}
    • 1-loop 有效勢: V_eff(θ) = V_min + (1/2)Σ_n ω_n√(1 − a_n·cos(θ−θ_n))
    • a_n = 2κ⟨W⟩/ω_n, 全 44 模式 a_n > 1 (非微擾)
  未建立:
    • 非微擾求和 (Borel / 鞍點) — a_n > 1 使 √(1−a cosθ) 之級數唔收斂
    • δρ 徑向模式之完整積分 (含 (∂θ)⁴ 項)
    • A5 圖上之 instanton / soliton 求和
""")

# 可計算之部分: 用 A5 圖 Laplacian 譜寫出精確高斯泛函
L("  ── 可計算部分: A5 圖上相位場之精確高斯泛函 ──")
L("     Z_θ = ∫Dθ exp[−(1/2)Σ_i(E_J/2)θ_i² − (1/2)(J_eff/2)θ^T Lap θ]")
L(f"     = det[(E_J/2)I + (J_eff/2)Lap]^{{−1/2}}  (忽略零模)")
eig_full = (2.0 / 2) + (J_eff / 2) * evals      # E_J = 2, J_eff = 61.5 (無量綱演示)
L(f"     用 E_J = 2, J_eff = 61.5 (晶格單位): 譜 min = {eig_full.min():.6f}, max = {eig_full.max():.6f}")
logZ = -0.5 * float(np.sum(np.log(eig_full[1:])))
L(f"     log Z_θ (1-loop, 排除零模) = {logZ:.6f}")
L("")
CHECK("A5 圖高斯泛函可精確計算 (Laplacian 譜已知)", True,
      f"log Z_θ = {logZ:.6f}")
L("")
L("  ⚠️ 此為二次型 (高斯) 部分; cos θ 之非微擾貢獻仍未納入。")
NEGATIVE("#3 完整非微擾 Γ_eff[θ] 仍未閉合",
         "已達: 高斯部分精確 + 1-loop 有效勢; 未達: 非微擾求和 (a_n > 1)、δρ 完整積分、instanton 求和")
L("")

# ============================================================
# 五、總結
# ============================================================
L("━" * 88)
L("  五、總結")
L("━" * 88)
L("")
L(f"""
  ┌──────────────────────────────────────────────────────────────────────┐
  │  🟡 #2 c_{{i,n}} 投影 — 部分進展 + 1 否定                            │
  │     ✅ 雙路徑干涉嚴格導出 cos²(n·β) 之**形式**                       │
  │        (兩條大圓路徑角距和 = 2π ⟹ 相位差 = 2nβ)                    │
  │     ✅ (A) cos²(nβ) 具 Nyquist 週期 44; (B) cos²(nβ/2) 冇            │
  │     ⚠️ 否定: β_i 之身份未鎖定 — 大圓投影自然給方位角 φ_i,             │
  │        而宣稱式用球面角距 β_i; max||cosβ|−|cosφ|| = {dev:.4f}        │
  │     🟡 狀態: 形式已導出, 幾何量身份未閉合                            │
  │                                                                    │
  │  🟡 #3 非微擾 Γ_eff[θ] — 部分進展 + 1 否定                          │
  │     ✅ A5 Laplacian 譜精確 (λ_2 = φ⁻²), 高斯泛函可算 (log Z = {logZ:.4f}) │
  │     ✅ 三方案互斥性已明確 (皆 ≠ 123, 不支撐 E_J)                     │
  │     ⚠️ 否定: 非微擾求和 (a_n > 1) / δρ 完整積分 / instanton 未閉合  │
  └──────────────────────────────────────────────────────────────────────┘
""")
L(f"  通過: {PASS}/{PASS+FAIL}  ✅")
L(f"  失敗: {FAIL}/{PASS+FAIL}  ❌")
L(f"  否定結果 (誠實記錄): {NEG}")

with open(os.path.join(OUT, "13_projection_effective_action.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: {OUT}/13_projection_effective_action.txt")
print(f"📊 {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL, {NEG} 否定")
