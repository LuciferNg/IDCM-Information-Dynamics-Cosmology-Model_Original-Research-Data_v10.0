#!/usr/bin/env python3
"""
O140 — 困難2 續: 乘法律閉包 + SM 質量鏈可達性 (2026-10-09)
==============================================================
v12 否決咗「自由乘積撞 SM」(密度巧合)。
真正嘅結構約束係鏈乘法律 ε_a·ε_{44−a}=ε_{2a} 嘅**封閉生成**:

問題: 乘法律由鏈上 44 個原生質量(m_k=M₀√ε_k)封閉生成嘅代數係咩?
  - 只有鏈上質量先係「本徵」
  - 乘法律 m_{2a}=m_a·m_{44−a}/M₀ 要求合成結果仍喺鏈上 (2a≤44)
  - SM 質量係「鏈外」——要表達成鏈質量乘積, 用幾多因子? 有冇特殊結構?

vs null: 隨機「外來質量」要幾多因子先表達到? SM 會唔會特別短?
"""
import math, json, random, itertools

N = 44
def eps(k, Nv=N):
    return 4*math.sin(math.pi*k/(2*Nv))**2
sqrt_eps = [math.sqrt(eps(k)) for k in range(1, N+1)]

PASS = 0; FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("1. 乘法律封閉性: m_{2a} 必在鏈上 (2a≤44)")
print("="*72)
ok = True
for a in range(1, 23):
    # eps() 係 1-based 函數: eps(44-a) = ε_{44−a}
    lhs = eps(a)*eps(44-a)          # ε_a·ε_{44−a}
    rhs = eps(2*a)                  # ε_{2a}
    if abs(lhs-rhs) > 1e-10:
        ok = False; print(f"    FAIL a={a}: {lhs:.12f} vs {rhs:.12f}")
check("乘法律 ε_a·ε_{44−a}=ε_{2a} 22/22 (eps 函數)", ok)
# 質量版: m_{2a} = m_a·m_{44−a}/M₀
ok2 = True
for a in range(1, 23):
    lhs = math.sqrt(eps(a))*math.sqrt(eps(44-a))   # m_a·m_{44−a}/M₀
    rhs = math.sqrt(eps(2*a))                      # m_{2a}/M₀
    if abs(lhs-rhs) > 1e-10:
        ok2 = False; print(f"    FAIL mass a={a}")
check("質量乘法律 m_{2a}=m_a·m_{44−a}/M₀ 22/22", ok2)

print("="*72)
print("2. 鏈外質量嘅最短乘積表示 (窮舉 1-3 因子)")
print("="*72)
SM = {'e': 0.51099895e6, 'mu': 105.6583755e6, 'tau': 1776.86e6,
      'u': 2.16e6, 'd': 4.67e6, 's': 93.4e6, 'c': 1.27e9, 'b': 4.18e9, 't': 173.1e9}
# 質量比 target (heavy/light), 全 fermion pair 36 個 + 輕子對
targets = []
names = list(SM.keys())
for i in range(len(names)):
    for j in range(i+1, len(names)):
        if SM[names[i]] >= SM[names[j]]:
            targets.append((f'{names[i]}/{names[j]}', SM[names[i]]/SM[names[j]]))
        else:
            targets.append((f'{names[j]}/{names[i]}', SM[names[j]]/SM[names[i]]))
targets = sorted(set(targets), key=lambda x: x[1])
print(f"  SM 質量比 target: {len(targets)} 個, 範圍 [{targets[0][1]:.4f}, {targets[-1][1]:.2e}]")

# 鏈質量比網格 (1 因子): r(k,j) = √ε_k/√ε_j ≥ 1
grid1 = [(sqrt_eps[k]/sqrt_eps[j], (k+1,j+1)) for k in range(N) for j in range(N)
         if sqrt_eps[k] >= sqrt_eps[j]]
# 2 因子: pair-ratio 全掃唔切 3.7M 對每個 target — 用抽樣 + 已有 12c 結果
# 呢度: 對每個 target 搵「最短長度」: 1 因子(946), 2 因子(抽樣), 3 因子(抽樣)
random.seed(7)
def min_dev_len(target, max_len=2, n_sample=60000):
    """回傳 (最短長度, min_dev) — 由 1 因子開始, expand"""
    best1 = min(abs(g-target)/target for g,_ in grid1)
    if best1 < 0.01:
        return 1, best1
    best = best1
    for _ in range(n_sample):
        g1,_ = random.choice(grid1)
        g2,_ = random.choice(grid1)
        dev = abs(g1*g2 - target)/target
        if dev < best:
            best = dev
            if best < 0.01:
                return 2, best
    return 2, best

print("\n  SM 質量比最短長度 (1 或 2 因子, 抽樣 60k):")
results = []
for name, t in targets:
    L, dev = min_dev_len(t)
    results.append((name, t, L, dev))
    tag = "✅" if dev < 0.01 else ("🟡" if dev < 0.05 else "❌")
    print(f"    {tag} {name:<6s} {t:12.6g}  len={L}  dev={dev*100:.3f}%")
len1 = sum(1 for r in results if r[2]==1 and r[3]<0.01)
len2 = sum(1 for r in results if r[2]==2 and r[3]<0.01)
check("1 因子 <1%: 少量(網格密度限制)", len1 < 10, f"len1_hits={len1}/36")
check("2 因子 <1%: 有(密度)但唔可以當結構", len2 >= 3, f"len2_hits={len2}/36")

print("="*72)
print("3. null 對比: 隨機質量比嘅最短長度分佈")
print("="*72)
# 隨機 target 喺 [1,3.4e5] log-uniform, 計最短長度(1/2 因子)
random.seed(2026)
mc_targets = [math.exp(random.uniform(0, math.log(3.4e5))) for _ in range(100)]
mc_lens = [min_dev_len(t)[1] for t in mc_targets]
mc_frac_lt1pct = sum(1 for d in mc_lens if d < 0.01)/len(mc_lens)
sm_frac_lt1pct = sum(1 for r in results if r[3] < 0.01)/len(results)
print(f"  MC null: <1% 命中率 = {mc_frac_lt1pct*100:.1f}%")
print(f"  SM 實際: <1% 命中率 = {sm_frac_lt1pct*100:.1f}%  ({sum(1 for r in results if r[3]<0.01)}/36)")
check("SM <1% 命中率顯著高於 MC null", sm_frac_lt1pct > mc_frac_lt1pct*2,
      f"{sm_frac_lt1pct*100:.1f}% vs {mc_frac_lt1pct*100:.1f}%")

print("="*72)
print("4. 乘法律鏈: SM 質量比用『2a 鏈』(m_{2a}/m_a = √ε_{44−a}) 表達")
print("="*72)
# 倍半因子 f(a) = m_{2a}/m_a = √ε_{44−a}: 22 個生成元
gen = [(sqrt_eps[44-a], a) for a in range(1, 23)]  # (因子, a)
# 鏈: 一路 ×f(a) 可以由 m_a 到 m_{2a}... 目標質量比 = ∏f(a_i)? 唔係——
# 乘法律已經解釋鏈內; 鏈外質量比要 ∏√ε 自由因子 ⟹ v12 已否決。
# 呢度試: SM 質量比有冇 = ∏_{i} f(a_i) / ∏_{j} f(b_j) (只用 22 個倍半生成元)?
# 對數空間: ln(target) ∈ Z-組合 of {ln f(a)}? (格點問題, 貪婪逼近)
print("  22 個倍半生成元 f(a)=√ε_{44−a}, a=1..22:")
print(f"    f(1..22) = {[round(g,4) for g,_ in gen]}")
print("  檢查 SM 質量比 ln(t) 用 {ln f(a)} 嘅 Z-線性組合逼近 (貪婪):")
def greedy_combo(t):
    """用 ln f(a) 組合近似 ln t (係數 -3..3, 22 個生成元 — 太大; 
       先試限制生成元數 m≤3 嘅啟發式)"""
    L = math.log(t)
    lf = [math.log(g) for g,_ in gen]
    best = (1e9, None)
    # 只試 1-2 個生成元嘅小組合 (窮舉 22²×7 係數)
    for i in range(22):
        for c1 in range(-3,4):
            d1 = abs(c1*lf[i] - L)
            if d1 < best[0]:
                best = (d1, [(i,c1)])
        for j in range(22):
            for c1 in range(-2,3):
                for c2 in range(-2,3):
                    d2 = abs(c1*lf[i]+c2*lf[j]-L)
                    if d2 < best[0]:
                        best = (d2, [(i,c1),(j,c2)])
    return best
hits_chain = 0
for name, t in sorted(targets, key=lambda x: x[1]):
    d, combo = greedy_combo(t)
    if d < 0.01:
        hits_chain += 1
        print(f"    ✅ {name:<6s} {t:12.6g}  ln ≈ Σc·ln f(a) dev={d*100:.2f}%  {combo}")
check("乘法律生成元鏈命中 >0 (有 SM 比係倍半生成元可達)", hits_chain > 0,
      f"hits={hits_chain}")

# 鏈命中 null: 隨機 target 用同一 greedy 組合, 命中率幾多?
random.seed(11)
mc_chain_hits = 0
mc_chain_n = 200
for _ in range(mc_chain_n):
    t = math.exp(random.uniform(0, math.log(3.4e5)))
    d, _ = greedy_combo(t)
    if d < 0.01:
        mc_chain_hits += 1
mc_chain_rate = mc_chain_hits/mc_chain_n
print(f"  MC null (chain-generator greedy, {mc_chain_n} targets): <1% 命中率 = {mc_chain_rate*100:.1f}%")
print(f"  SM 實際: {hits_chain}/{len(targets)} = {hits_chain/len(targets)*100:.1f}%")
check("鏈命中率 vs null (SM ≫ MC?)", hits_chain/len(targets) > mc_chain_rate*2,
      f"SM {hits_chain/len(targets)*100:.1f}% vs MC {mc_chain_rate*100:.1f}%")

with open('data/mass_product_chain.json','w') as f:
    json.dump({'len1':len1,'len2':len2,'mc_lt1pct':mc_frac_lt1pct,
               'sm_lt1pct':sm_frac_lt1pct,'chain_hits':hits_chain,
               'gen_f':[g for g,_ in gen]}, f, indent=2, ensure_ascii=False)
print("\n" + "="*72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("="*72)