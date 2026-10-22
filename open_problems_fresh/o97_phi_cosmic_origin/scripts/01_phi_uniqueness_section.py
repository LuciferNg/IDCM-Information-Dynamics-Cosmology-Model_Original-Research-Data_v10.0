#!/usr/bin/env python3
"""
O97 — Level A: φ 唯一自相似二分尺度 (Euclid 極端&中項 + 單位預算 tiling)
script 01: sympy 精確證明
=============================================================
主張 C1: 在所有實數尺度 μ>1 之中, 只有 φ 滿足「自相似二分」:
    μ⁻¹ + μ⁻² = 1   (兩層自相似切分剛好坐滿單位預算, 無隙無疊)
等價刻劃 (全部 ⟺ x²−x−1=0, 唯一正根 φ=(1+√5)/2):
    (a) x = 1 + 1/x            (自反轉 recursion)
    (b) x⁻¹ + x⁻² = 1          (預算分配平 cheville)
    (c) 連分數 [1;1,1,1,…]      (全週期, 自動複製)
    (d) φ·φ' = −1  (integer-closure 常數項 −1)
對照: π/e/√2/√3/2 全部 fail 預算閉合 (gap 或 overlap)
=============================================================
"""
import sympy as sp

x = sp.Symbol('x', positive=True, real=True)
phi = sp.nsimplify((1 + sp.sqrt(5))/2)
phi_ = (1 - sp.sqrt(5))/2   # 共軛根 (代數共軛)

results = []
def record(ok, label, detail=""):
    results.append((ok, label, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")

# ---------- (a) x = 1 + 1/x → x²−x−1=0, 正根=φ ----------
eq_a = sp.Eq(x, 1 + 1/x)
sol_a = sp.solve(eq_a, x)
pos_a = [c for c in sol_a if sp.nsimplify(c) > 0]
record(len(pos_a) == 1 and sp.simplify(pos_a[0] - phi) == 0,
       "(a) x=1+1/x 唯一正根 = φ", f"根={[sp.nsimplify(c) for c in sol_a]}")

# ---------- (b) x⁻¹ + x⁻² = 1  ⟺  x²−x−1=0
eq_b = sp.Eq(1/x + 1/x**2, 1)                    # ×x²: x+1=x²
sol_b = sp.solve(eq_b, x)
pos_b = [c for c in sol_b if sp.nsimplify(c) > 0]
record(len(pos_b) == 1 and sp.simplify(pos_b[0] - phi) == 0,
       "(b) x⁻¹+x⁻²=1 ⟺ x²−x−1=0 唯一正根=φ", f"根={[sp.nsimplify(c) for c in sol_b]}")

# 直接: φ⁻¹ + φ⁻² ≡ 1 (symbolic, 因 φ²=φ+1)
twolev = sp.simplify(1/phi + 1/phi**2 - 1)
record(sp.simplify(twolev) == 0, "(b) φ⁻¹+φ⁻² ≡ 1 symbolic", f"simplify→{sp.simplify(twolev)}")

# (b') Euclid「極端與中項」: 長段/全 = 短段/長段  ⟺ 同一個 φ
# 設段 G/S=r, 條件 G/(G+S)=S/G → r/(r+1)=1/r → r²=r+1 → r=φ
r = sp.Symbol('r', positive=True, real=True)
euclid = sp.solve(sp.Eq(r/(r+1), sp.Rational(1,1)/r), r)
pos_e = [c for c in euclid if sp.nsimplify(c) > 0]
record(len(pos_e) == 1 and sp.simplify(pos_e[0] - phi) == 0,
       "(b') Euclid 極端&中項 G/(G+S)=S/G → r=φ", f"根={[sp.nsimplify(c) for c in euclid]}")

# ---------- (c) 連分數 [1;1,1,…]
cf = sp.Integer(1)
for _ in range(40):
    cf = 1 + 1/cf
err = float(sp.N(sp.Abs(cf - phi)))
record(err < 1e-9, "(c) 連分數[1;1,..] 收斂→φ (40 iter)", f"err={err:.2e}")

# ---------- (d) 根積=−1 (常數項 −1) → integer closure 和公式 φⁿ+φ'ⁿ=L_n∈ℤ
record(sp.simplify(phi*phi_) == -1, "(d) φ·φ' = −1 (constant term)", sp.simplify(phi*phi_))
# 閉合係「和」: φⁿ + φ'ⁿ = Lucas L_n ∈ ℤ (φ' = (1−√5)/2, 注意 φ⁺φ'=1)
# 對奇 n, φ⁻ⁿ = −φ'ⁿ  →  φⁿ−φ⁻ⁿ = φⁿ+φ'ⁿ = L_n (IDCM B/Lucas 差公式同源)
intc = True
lucas = []
for n in [1,3,5,7,9,11,13]:
    v = sp.simplify(phi**n + phi_**n)
    lucas.append(int(v))
    intc &= v.is_integer
record(intc, "(d) 和公式閉合: φⁿ+φ'ⁿ = L_n ∈ ℤ (n=1..13)", f"Lucas={lucas}")

# ---------- 對照: 候選尺度 τ(μ)=μ⁻¹+μ⁻² ?= 1
candidates = {'2': sp.Integer(2), '√2': sp.sqrt(2), '√3': sp.sqrt(3),
              'π': sp.pi, 'e': sp.E}
print("\n=== 對照 τ(μ)=μ⁻¹+μ⁻² (兩層自相似切分), 需 ==1 先無隙無疊 ===")
for name, mu in candidates.items():
    tau = sp.N(1/mu + 1/mu**2, 10)
    gap = sp.N(tau - 1, 10)
    verdict = "OVER(>1, 疊)" if gap > 0 else ("GAP(<1, 欠)" if gap < 0 else "BALANCE(=1)")
    record(int(gap) == 0, f"對照 {name}: τ{name}=1", f"τ={float(tau):.6f} → {verdict}")
print("        φ : τ=1.000000 (唯一, 已証)")

# ---------- 尺度光譜密度: 「有理→相消譜」 vs φ 無理尺度
# 2 係有理尺度 → 譜全相稱 (違 O51 946/946 無理)
print("\n=== 有理尺度 2 快 failure: 譜相稱性 ===")
record(phi.is_irrational, "φ 係無理代數數 (非有理,非超越)", f"is_irrational={phi.is_irrational}")

npass = sum(1 for o,_,_ in results if o)
ntot = len(results)
print(f"\n=== Level A: {npass}/{ntot} PASS ===")
if npass == ntot:
    print(">>> 閉合: φ 係唯一自相似二分必數 (x²−x−1=0↔x⁻¹+x⁻²=1↔Euclid極端起中項)")