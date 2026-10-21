#!/usr/bin/env python3
"""
O257 scripts/10 — R3: ε 殘差身份攻堅 (2026-10-21)
====================================================
R2 留低: M_pl/M_comp ≈ 88³/2 × ⁷⁶√10 (dev 0.118%)
即 M_comp ≈ M_pl·(2/88³)·⁷⁶√10, ε = 0.118% 未有 operator 身份。

精確化:
  ε+1 = 10^{1/γ₆}/(88³/2)  (代數, root 因子抵消)
  問題變: 10^{1/γ₆} 點解 ≈ 88³/2? 差 ε 有冇身份?

候選結構:
  A. 88³/2 = N_d³·γ₄₄ (γ₄₄=4=μ²=Πγ_odd, 全譜積 operator)
  B. δ = 1/γ₆ − log10(88³/2) = ? (若 = 1/44² 或 γ₆ 組合...)
  C. ε⁻¹ 結構池掃描 (845? 846? F₅F₇²?)
  D. q = r/88² = 42.7374 身份 (171/4 = N_gen²·19/4?)
  E. 盲測: ε 嘅 1/x 池 (x ∈ 結構池, |1/x−ε|/ε < 0.1% 命中)

判據: EXACT < 1e-12; 名義一致 <0.1%; 密度閘。
"""
import mpmath as mp
mp.mp.dps = 80

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B, Nd, N, Ngen = 4, 44, 88, 3

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

passed = 0
failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

print("=" * 72)
print("O257 scripts/10 — R3: ε 殘差身份攻堅")
print("=" * 72)

g6 = gamma(6)
M_pl = mp.mpf("1.2209e19")
target_log10 = 1/g6 - 1/mp.mpf(76)
M_comp = M_pl * mp.power(10, -target_log10)
r = M_pl / M_comp

e88 = mp.mpf(88)**3/2          # 88³/2 = 340736
pow_1g6 = mp.power(10, 1/g6)   # 10^{1/γ₆}
eps = pow_1g6/e88 - 1          # ε
print(f"10^(1/γ₆)     = {mp.nstr(pow_1g6, 16)}")
print(f"88³/2          = {mp.nstr(e88, 16)}")
print(f"ε = 10^(1/γ₆)/(88³/2) − 1 = {mp.nstr(eps, 18)}")
print(f"1/ε = {mp.nstr(1/eps, 14)}")
print(f"ε×88  = {mp.nstr(eps*88, 10)}")
print(f"ε×7744 = {mp.nstr(eps*7744, 10)}")
print(f"ε×7744² = {mp.nstr(eps*7744**2, 10)}")
print()

# ── A. 88³/2 = N_d³·γ₄₄ ──
print("[A] 88³/2 operator 身份")
g44 = gamma(44)   # 4
ck("γ₄₄(88) = 4 = μ²", abs(g44 - 4) < 1e-15)
ck("88³/2 = N_d³×γ₄₄ = 44³×4", Nd**3*g44 == 88**3/2, f"(44³×4 = {44**3*4})")
ck("88³/2 = N_d³×Πγ_odd (R2 恆等 Πγ_odd=4)", Nd**3*4 == 88**3/2)
print(f"  → 10^(1/γ₆) ≈ N_d³×Πγ_odd — 大數 = 鏈三次方 × 奇模譜積, 全 operator")
print()

# ── B. δ = 1/γ₆ − log10(88³/2) ──
print("[B] δ = 1/γ₆ − log10(88³/2)")
log10_88_3_2 = mp.log(e88)/mp.log(10)
delta = 1/g6 - log10_88_3_2
print(f"  log10(88³/2) = {mp.nstr(log10_88_3_2, 16)}")
print(f"  1/γ₆          = {mp.nstr(1/g6, 16)}")
print(f"  δ = {mp.nstr(delta, 18)}")
print(f"  δ×88    = {mp.nstr(delta*88, 10)}")
print(f"  δ×7744  = {mp.nstr(delta*7744, 10)}")
print(f"  δ×1936  = {mp.nstr(delta*1936, 12)}   (1936 = Πγ_even = 44²)")
print(f"  δ×88²  = {mp.nstr(delta*88**2, 12)}")
one_44sq = 1/mp.mpf(44)**2
print(f"  1/44²   = {mp.nstr(one_44sq, 14)}  dev = {mp.nstr(abs(delta - one_44sq)/one_44sq*100, 6)}%")
ck("δ ≈ 1/44² (Πγ_even 倒數)", abs(delta - one_44sq)/one_44sq < 0.001,
   f"(dev {mp.nstr(abs(delta-one_44sq)/one_44sq*100,5)}%)")
# 若 δ = 1/44²:  1/γ₆ = log10(88³/2) + 1/44² → 1/γ₆ − 1/44² = log10(88³/2) EXACT?
# => 10^{1/γ₆ − 1/44²} = 88³/2 ⇒ 10^{1/γ₆} = 88³/2 × 10^{1/44²}
print(f"  驗: 10^(1/γ₆−1/44²) = {mp.nstr(mp.power(10, 1/g6 - one_44sq), 12)} vs 88³/2 = {mp.nstr(e88, 10)}")
# ε 嘅更精確形式: ε = 10^{1/44²} − 1??
test = mp.power(10, one_44sq) - 1
print(f"  10^(1/44²)−1 = {mp.nstr(test, 14)}  vs ε = {mp.nstr(eps, 14)}")
ck("ε = 10^(1/44²)−1 (δ=1/44² 推論)", abs(test - eps)/eps < 0.01,
   f"(dev {mp.nstr(abs(test-eps)/eps*100,5)}%)")
print()

# ── C. ε⁻¹ 結構池 ──
print("[C] 1/ε 結構身份掃描")
inv_eps = 1/eps
pool_c = {
  "F₅×F₇² (845)": 5*13**2,
  "F₅×F₇²−1 (844)": 5*13**2-1,
  "L₇×29 (841)": 29**2,
  "44²+?": None,
  "88×9.6 (844.8)": 88*9.6,
  "L₄×L₇×4 (812)": 7*29*4,
  "176×4.8 (844.8)": 176*4.8,
}
print(f"  1/ε = {mp.nstr(inv_eps, 12)}")
for name, v in pool_c.items():
    if v is None: continue
    dev = abs(inv_eps - v)/v*100
    print(f"    {name} = {v}: dev {mp.nstr(dev, 5)}%")
# 掃 x ∈ 800..900 整數
best = None
for x in range(780, 900):
    dev = abs(inv_eps - x)/x
    if best is None or dev < best[1]: best = (x, dev)
if best:
    print(f"  整數 [780,900] 最近: {best[0]} dev {mp.nstr(best[1]*100, 6)}%")
# ε×88^n
print(f"  ε×88³ = {mp.nstr(eps*88**3, 10)}")
print(f"  ε×88²×44 = {mp.nstr(eps*88**2*44, 10)}")
print(f"  ε×88×44² = {mp.nstr(eps*88*44**2, 10)}")
print()

# ── D. q = r/88² = 42.7374 身份 ──
print("[D] q = r/88² = 42.7374")
q = r/7744
print(f"  q = {mp.nstr(q, 14)}")
cand_q = {
  "171/4 (N_gen²×19/4)": mp.mpf(171)/4,
  "L₅×L₆/4 (11×18/4)": mp.mpf(11*18)/4,
  "90×88/185.3": None,
  "176/4.118": None,
  "44−1.2626": None,
  "11×88/22.65": None,
  "F₉×φ?": None,
  "L₄×L₅×90/??": None,
}
for name, v in cand_q.items():
    if v is None: continue
    dev = abs(q - v)/v*100
    print(f"    {name} = {mp.nstr(v, 10)}: dev {mp.nstr(dev, 5)}%")
# q 嘅結構: 42.7374 ≈ ? 42+0.7374
print(f"  q−42 = {mp.nstr(q-42, 10)}")
print(f"  (q−42)×88 = {mp.nstr((q-42)*88, 10)}  (0.7372×88 = 64.87)")
print(f"  (q−42)×44 = {mp.nstr((q-42)*44, 10)}")
print(f"  (q−42)×γ₆⁻¹ = {mp.nstr((q-42)/g6, 10)}")
# 42.7374 vs 88×(1−γ₆·k/2) k=14 之前 scripts/09: dev 0.0055%
for k in range(1, 30):
    cand = (88 - g6*k)/2
    dev = abs(q - cand)/cand*100
    if dev < 0.01:
        print(f"    q ≈ (88−γ₆×{k})/2 = {mp.nstr(cand,10)} dev {mp.nstr(dev,5)}%")
print()

# ── E. ε 密度盲測 ──
print("[E] 密度閘: ε 嘅 1/x 池暗示 (x ∈ 結構池, |1/x−ε|/ε < 0.1%)")
# 池: Lucas, Fib, 88k, 44k, 90k, 76k, 176k, 7744k, 44²k, 平方
poolE = set()
L = {1,3,4,7,11,18,29,47,76,123,199,322,521,843}
F = {1,2,3,5,8,13,21,34,55,89,144,233,377,610}
poolE.update(L); poolE.update(F)
for k in range(1, 25):
    poolE.add(88*k); poolE.add(44*k); poolE.add(90*k); poolE.add(76*k)
    poolE.add(176*k); poolE.add(7744*k); poolE.add(1936*k)
for a in range(2, 100):
    poolE.add(a*a)
hitsE = []
for x in sorted(poolE):
    if x <= 0: continue
    v = 1/mp.mpf(x)
    if abs(v - eps)/eps < 0.001:
        hitsE.append((x, mp.nstr(v, 12), mp.nstr(abs(v-eps)/eps*100, 5)))
print(f"  池 {len(poolE)} 項, ±0.1% 命中 {len(hitsE)}:")
for h in hitsE:
    print(f"    1/{h[0]} = {h[1]} (dev {h[2]}%)")
# 隨機對照
import random
random.seed(25710)
n_mc = 10000
cnt = 0
for _ in range(n_mc):
    x = random.randint(500, 10000)
    v = 1/mp.mpf(x)
    if abs(v - eps)/eps < 0.001: cnt += 1
print(f"  隨機 x∈[500,10000]: {cnt}/{n_mc} = {cnt/n_mc*100:.2f}% (帶寬期望)")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")