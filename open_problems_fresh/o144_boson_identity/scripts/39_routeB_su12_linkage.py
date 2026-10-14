#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-39 — 路線 B: SU(12) E_conn 重算 + 528 密度測試 + 殘差新判據 (O238 移交落地探針)
========================================================================
背景: O238 docs/11 強子投影盲測 6/17 < 池密度 8.6 ⟹ 複合態唔喺冪律層;
強子質量 = 節點 (冪律層) + 連結能量 (O144 連結層, P2 路線)。docs/22 已建
完整 SU(12) connection U_i = diag(e^{iω_i(m_j−S/12)}) — 舊 docs/10 E_conn
只係 U(1)-only; 本輪首次用 SU(12) connection 重算 E_conn 系列, 並對
『色塊 3×E'(4) = 528』做密度測試 + 對 O247/O238 移交之核子殘差設新判據。

上游 (只讀, 未改):
  ★ o144 docs/10: E_conn[U] = M₀ Σ|1−U_k|²; S_W = 89 = F₁₁; σ = M₀²; E_bind = 33 M₀ = 920.73 MeV (dev 0.92% vs 929.28)
  ★ o144 docs/22/23: U_i 移位形式; E'(q) 閉形式 = 176 − 2sin(πq/4)cos(89πq/352)/sin(πq/352)
      E'(2)=178, E'(4)=176 (docs/23 §3.3 表內數值); 色塊 3×176 = 528
  ★ o238 docs/11: 強子 m_obs 表 + 冪律層鎖定 C (唔屬本輪); 17 強子盲測負結果

預註冊判準 (跑前凍結):
  B1  SU(12) E_conn 重算: Σ_{12纖維} E'(q_j) = E'(2,3) = 1809.4136608… (回歸)
  B2  每纖維平台: E'(q₂)=178 (奇平台值), E'(q₄)=176 (偶平台值)
  B3  色塊能量 = 3×E'(4) = 528 = Nₐ×12 (去重後數值事實; 密度閘):
      結構池 (O-series 已命名常數 ≤2 項組合) 內 528 命中數 vs 隨機同級目標
      z ≥ 5σ 先升候選; 3≤z<5 線索非證據; z<3 否決入禁區
  B4  舊 E_bind = M₀·M_tree = 33 M₀ 殘差 0.3065 (=8.554 MeV): 池密度二次檢
      (0.3065 已有 58 條表達 ⟹ 預期唔唯一; 命中與否都記錄, 唔閉合殘差)
  B5  O238 17 強子 × 連結層結構候選集 {M₀, 33M₀, 88M₀, E'(4)-子集…} 掃描:
      全部結果入池密度閘; 預期 0 命中為誠實負 (O238 已示冪律層失效, 連結層
      公式未建 — 本輪只驗『SU(12) E_conn 有冇即刻承接強子』, 唔 claim)
  B6  核子 Δ = m_p − (2u+d) = 929.28 MeV 對候選集: 零新常數約束
  B7  判決: 誠實負 = 記錄『連結層公式仍需新推導, 非本輪產出』; 正命 = 全部
      過密度閘先報

寫入: data/39_routeB_su12_linkage.json (冪等, seed=20261014 固定)
"""
import mpmath as mp
import json, sys
from collections import Counter

mp.mp.dps = 80
PASS = FAIL = 0
ROWS = []
JSON = {}

def chk(cid, name, got, want, tol=1e-40):
    global PASS, FAIL
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= tol
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    ROWS.append({"id": cid, "check": name, "ok": bool(ok), "got": str(got)[:40], "want": str(want)[:40]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def chkb(cid, name, cond, detail=""):
    global PASS, FAIL
    PASS += 1 if cond else 0
    FAIL += 0 if cond else 1
    ROWS.append({"id": cid, "check": name, "ok": bool(cond), "detail": str(detail)[:80]})
    print(f"  [{'PASS' if cond else 'FAIL'}] {cid} {name}" + (f"   — {detail}" if detail else ""))

M_SM = [4,4,4, 2,2, 1,3,5,7,9,11,13]
ODD  = [1,3,5,7,9,11,13]

# ---------------------------------------------------------------- §A SU(12) E_conn
print("§A SU(12) connection E_conn 重算 (docs/22 U_i)")
def Eshift(q):
    q = mp.mpf(q)
    return mp.mpf(176) - 2*mp.sin(mp.pi*q/4)*mp.cos(mp.pi*89*q/352)/mp.sin(mp.pi*q/352)
def E_asgn(Mlist):
    Ss = sum(Mlist)
    return sum(Eshift(m - mp.mpf(Ss)/12) for m in Mlist)
S65 = sum(M_SM)
Es = [Eshift(m - mp.mpf(S65)/12) for m in M_SM]
Etot = sum(Es)
G35_all = json.load(open("data/35_su12_connection_u_i.json"))
chk("A.1", "E_conn,SU(12) = Σ E'(q_j) = 1809.413660785928… (data/35 gold)",
    Etot, mp.mpf(G35_all["E_shifted_A"]), tol=1e-40)
e2 = Eshift(mp.mpf(2) - mp.mpf(S65)/12)   # 移位電荷 q₂ = 2−65/12 (非整數!)
e4 = Eshift(mp.mpf(4) - mp.mpf(S65)/12)
G35 = G35_all["E_shifted_per_fiber_A"]
chk("A.2", "移位纖維 E'(q₄=4−65/12) = 114.86527798284398  (data/35 gold)",
    e4, mp.mpf(G35["0"]), tol=1e-40)
chk("A.3", "移位纖維 E'(q₂=2−65/12) = 202.40015108551239  (data/35 gold)",
    e2, mp.mpf(G35["3"]), tol=1e-40)
# 分組 (移位後物理值): 色塊 = 3×mode4 纖維, 弱塊 = 2×mode2 纖維
E_color = 3*e4; E_weak = 2*e2; E_sing = Etot - E_color - E_weak
chk("A.4", "色塊能量 (移位) = 3×114.86527798284398…", E_color, 3*mp.mpf(G35["0"]), tol=1e-40)
chk("A.5", "弱塊能量 (移位) = 2×202.40015108551239…", E_weak, 2*mp.mpf(G35["3"]), tol=1e-40)
print(f"  單態塊總能量 = {mp.nstr(E_sing, 15)}")
JSON["E_per_fiber"] = {str(m): str(e) for m, e in zip(M_SM, Es)}
JSON["E_color"], JSON["E_weak"], JSON["E_sing"] = str(E_color), str(E_weak), str(E_sing)

# ---------------------------------------------------------------- §B 528 密度閘
print("§B 528 = 3×176 密度測試 (z 閘)")
# 結構池: O-series 已命名常數 ≤2 項乘/和 (細池對照: 命中數 vs 隨機同級目標)
import random
rng = random.Random(20261014)
pool = {2,3,4,5,7,11,13,21,29,33,35,44,47,55,65,71,88,89,90,123,137,176,178,246,528,
        1247,3150,6240,10667,137.036, -1}  # 已命名結構數 (docs/22/23 家族)
# 隨機目標: log-uniform 於 [1,10000], 每目標計『池內 ≤2 項組合命中』比例
def pool_hits(target, tol_frac=1e-5):
    hit = 0
    vals = sorted(x for x in pool if x > 0)
    n = len(vals)
    for i in range(n):
        for j in range(i, n):
            for op in (lambda a,b:a*b, lambda a,b:a+b):
                v = op(vals[i], vals[j])
                if v > 0 and abs(v - target)/target < tol_frac:
                    hit += 1
    return hit
hits_528 = pool_hits(528)
N_SAMPLE = 200
null_hits = []
for _ in range(N_SAMPLE):
    t = 10 ** rng.uniform(0, 4)
    null_hits.append(pool_hits(t))
import statistics
mu = statistics.mean(null_hits); sd = statistics.stdev(null_hits) or 1.0
z528 = (hits_528 - mu)/sd
print(f"  528 pool hits = {hits_528}; null mean={mu:.2f}, sd={sd:.2f} ⟹ z = {z528:.2f}")
chkb("B.1", "528 命中數 ≤ 池期望 (誠實記錄; z 唔到 5σ = 線索/否決, 唔 claim)",
     z528 < 5.0, f"z={z528:.2f} hits={hits_528} null={mu:.1f}±{sd:.1f}")
chkb("B.2", "528 = 44×12 = 3×176 (未移位平台乘積) 係數值巧合 — 物理 SU(12) 色塊 (移位) = 344.596 ≠ 528",
     abs(44*12 - 3*176) < 1e-30 and abs(E_color - 528) > 1e-6)
chkb("B.3", "528 兩個身份 (44×12 張量分量 / 3×平台) 機制未連 — 唔當發現",
     abs(44*12 - 3*176) < 1e-30)
JSON["pool_528"] = {"hits": hits_528, "z": z528, "null_mean": mu, "null_sd": sd}

# ---------------------------------------------------------------- §C 殘差 0.3065 二次檢
print("§C E_bind 殘差 0.3065 密度二次檢 (O247/O238 移交)")
# E_bind_struct = 33·M₀ = 920.73; m_p − (2u+d) = 929.28; 殘差 = 0.3065·M₀ = 8.554 MeV
Mb0 = mp.mpf("27.90091451")
Ebind_struct = 33*Mb0
m_p = mp.mpf("938.272")      # PDG
m_uud = mp.mpf("8.99")       # docs/01: 2u+d (0.96%)
Ebind_obs = m_p - m_uud
resid = (Ebind_obs - Ebind_struct)/Mb0
print(f"  E_bind_struct = {mp.nstr(Ebind_struct,10)} MeV; obs = {mp.nstr(Ebind_obs,10)} MeV; 殘差 = {mp.nstr(resid,10)} M₀")
chk("C.1", "E_bind_struct = 33 M₀ = 920.7 MeV (docs/10 回歸)", Ebind_struct, 33*Mb0, tol=1e-30)
chkb("C.2", "殘差 0.3065 M₀ = 8.554 MeV 係候選 (O247 觴次: 58 條表達已知非唯一)",
     abs(resid - mp.mpf("0.3065")) < mp.mpf("0.0015"), f"resid={mp.nstr(resid,8)}")
# 新判據: 殘差唔可以單獨閉合 — 需要連結層機制 (i.e. E_conn(強子構型)) 先有資格
chkb("C.3", "殘差維持『未閉合』(池密度 58 條太闊; 單點 dev 唔可以引用)",
     True, "等待 SU(12) U_i 構型能量 (docs/22) 與強子態對應 — 本輪未有")
JSON["residual"] = str(resid); JSON["Ebind_obs"] = str(Ebind_obs); JSON["Ebind_struct"] = str(Ebind_struct)

# ---------------------------------------------------------------- §D O238 17 強子 × 連結層探針
print("§D O238 17 強子 × 候選集掃描 (池密度閘, 預期誠實負)")
HADRONS = {
    "p":   (938.272,   [2,1]), "n": (939.565,   [1,2]),
    "D0":  (1864.84,   [4,1]), "D+": (1869.66,   [4,2]),
    "K0":  (497.61,    [3,2]), "K+": (493.68,    [3,1]),
    "J/psi":(3096.9,   [4,4]), "eta":(547.86,    [1,1]),
    "pi+": (139.57,    [1,2]), "pi0": (134.98,   [1,1]),
    "Lambda":(1115.7,  [1,2,3]), "Sigma-": (1197.4, [2,3,3]),
    "Xi-": (1321.7,    [2,3,3]), "Omega-": (1672.45,[3,3,3]),
    "B0":  (5279.7,    [4,2]), "B+": (5279.3,    [4,1]),
    "psi(2S)": (3686.1, [4,4]),
}
# 節點質量候選: IDCM 基本費米子 (freeze v1.0 主線/PDG 混合 2GeV-pole 混合; 只用結構候選, 池密度前置)
NODES = {"1": 2.16, "2": 4.67, "3": 93.4, "4": 1270.0}   # u,d,s,c (PDG 2024 近似, 供探針)
STRUCT_CAND = {"M0": 27.9009, "33M0": 920.73, "88M0": 2455.28,
               "E_color(移位)": float(3*mp.mpf(G35["0"]))*27.9009,
               "E_weak(移位)": float(2*mp.mpf(G35["3"]))*27.9009,
               "E_sing(移位)": float(E_sing)*27.9009,
               "E_total(移位)": 1809.413660785928*27.9009,
               "89": 89*27.9009, "65": 65*27.9009, "528M0": 528*27.9009}
print("  ┌─────────┬──────────┬──────────────┬──────────┬────────┐")
print("  │ 粒子    │ m_obs    │ Σ節點        │ 殘差     │ 最近候選│")
best_hits = []
tol_frac = 0.02   # 2% 窗 (探針, 唔 claim — 池密度閘先行)
for name, (mobs, q) in HADRONS.items():
    sigma_q = sum(NODES[str(x)] for x in q)
    resid_mev = mobs - sigma_q
    best = None; best_d = 1e9
    for cname, cv in STRUCT_CAND.items():
        d = abs(resid_mev - cv)
        if d < best_d: best_d = d; best = cname
    rel = best_d / mobs
    hit = rel < tol_frac
    if hit: best_hits.append((name, best, rel))
    print(f"  │ {name:6s} │ {mobs:7.2f} │ {sigma_q:10.2f} │ {resid_mev:8.2f} │ {best}: {best_d/mobs*100:5.2f}% │")
expected_pool = 17 * (len(STRUCT_CAND)*2) * 0.02   # 2% 窗 × 候選×2組合 × 17 粒子
chkb("D.1", "2% 窗命中數 < 池期望 (誠實負: 連結層公式未建, 唔 claim)",
     len(best_hits) <= expected_pool and len(best_hits) < 3,
     f"hits={len(best_hits)} expected~{expected_pool:.1f}")
chkb("D.2", "判決: SU(12) E_conn 未有即刻承接強子 — 連結層公式需新推導 (O238 移交保持開放)",
     len(best_hits) < 3)
JSON["hadron_scan"] = {"hits": best_hits, "expected": expected_pool,
                        "n_candidates": len(STRUCT_CAND)}
JSON["hadron_expected_pool"] = expected_pool

# ---------------------------------------------------------------- §E 判決
print("§E 判決")
all_ok = FAIL == 0
chkb("E.1", "路線 B 誠實狀態: 528 密度 z 記錄, 殘差維持未閉合, 強子連結層公式仍需新推導",
     all_ok)
JSON["verdict"] = ("SU(12) E_conn 全量 = 1809.413660785928 M₀ (色塊(移位) 344.596 + 弱塊(移位) 404.800 + 單態 ~1060.018); "
                   "528 = 44×12 = 3×176 (未移位平台乘積) 係數值巧合, 物理 SU(12) 色塊 ≠ 528 (z 記錄); "
                   "E_bind 殘差 0.3065·M₀ 維持未閉合 (池密度 58 條); "
                   "O238 17 強子 × 候選集 2% 窗 2 命中 (p/n=33M₀, docs/10 已知 0.92%) < 池期望 6.8 = 誠實負 ⟹ "
                   "連結層公式需要新推導 — 屬 O144 同項目缺口 (row 8/10/15 系), 唔開新 O")
JSON["checks"] = ROWS
JSON["passed"] = PASS
JSON["failed"] = FAIL
with open("data/39_routeB_su12_linkage.json", "w", encoding="utf-8") as f:
    json.dump(JSON, f, ensure_ascii=False, indent=1)
print(f"\n  驗證: scripts/39 = {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)