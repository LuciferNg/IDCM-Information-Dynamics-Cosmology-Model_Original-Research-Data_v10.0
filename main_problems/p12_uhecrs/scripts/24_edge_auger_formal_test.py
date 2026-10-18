#!/usr/bin/env python3
"""
P12 攻堅 — 32 阻挫邊 ±5° 正式 MC null 檢驗 + 低能段節點避開檢驗 (2026-10-18)
============================================================================
docs/03 §4.1 第二個幾何預言從未正式檢驗: 舊 script 07 只計描述性 d_edge,
冇 MC null p-value; 且 07 硬編碼已失效舊路徑 (~/Projects/IDCM/IDCM-v10.0/)。
本 script 補上:
  (A) 32 阻挫邊 (大圓 segment 垂直距離) ±5° 為主窗, 3/8/10° 掃描, MC null;
      ★ edge-only 控制: 剔除距最近節點 <8° 嘅事件 (否則邊命中只係節點命中嘅影子
        — 邊端點就係節點)。edge-only = 邊中段訊號。
  (B) 低能段 (46-80 EeV) 節點避開 (docs/03 §4.3: 0% vs 29%) 正式檢驗。
null: scramble RA keep dec (同 P5 預註冊保守 null 一致); seed 42。
數據: Auger Open Data catalogSD (109 events, E≥46 EeV) — 全部本機。
"""
import math, os, json, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P12  = os.path.dirname(HERE)
MAIN = os.path.dirname(P12)
CMB  = os.path.join(MAIN, 'p4_cmb_cold_spot', 'data')
DATA = os.path.join(P12, 'data')

nodes = np.loadtxt(os.path.join(CMB, 'a5_nodes.txt'))
edge_pairs = []
with open(os.path.join(CMB, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        edge_pairs.append(((float(p[4]), float(p[5])), (float(p[6]), float(p[7]))))
N_edges = len(edge_pairs)

ev_ra, ev_dec, ev_E, ev_id = [], [], [], []
with open(os.path.join(DATA, 'auger_catalogSD.csv')) as f:
    for row in csv.DictReader(f):
        ev_ra.append(float(row['ra'])); ev_dec.append(float(row['dec']))
        ev_E.append(float(row['energy'])); ev_id.append(row['id'])
ev_ra = np.array(ev_ra); ev_dec = np.array(ev_dec); ev_E = np.array(ev_E)
N_ev = len(ev_ra)

def uv(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def d_node_min(ra, dec):
    u = uv(ra, dec); nv = uv(nodes[:, 0], nodes[:, 1])
    return np.degrees(np.arccos(np.clip(u @ nv.T, -1, 1).max(axis=1)))

def d_edge_min_vec(ra, dec):
    """事件到 32 條大圓 segment 嘅最小垂直距離 (向量化)."""
    ra, dec = np.radians(np.atleast_1d(ra)), np.radians(np.atleast_1d(dec))
    u = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
    best = np.full(len(u), 1e10)
    for (r1, d1), (r2, d2) in edge_pairs:
        v1 = uv(r1, d1).ravel(); v2 = uv(r2, d2).ravel()
        nvec = np.cross(v1, v2); nvec = nvec / np.linalg.norm(nvec)   # 大圓法向
        pdotn = u @ nvec
        perp = np.degrees(np.arcsin(np.clip(np.abs(pdotn), 0, 1)))
        # ★ 正確弧內容判定 (2026-10-18 修正): 投影方向 Pp 落喺 A→B 之間 ⟺
        # cross(A,Pp)·n ≥ 0 且 cross(Pp,B)·n ≥ 0。
        # (舊用 d1a+d2a<arc 係錯: 弧內但離開弧嘅點 (如中段偏 10°) 會被誤判弧外,
        #  距離退化成端點距離 → 邊帶被誤縮成節點帶。)
        Pp = u - pdotn[:, None]*nvec
        Pp = Pp / np.maximum(np.linalg.norm(Pp, axis=1, keepdims=True), 1e-12)
        cr1 = np.cross(np.broadcast_to(v1, u.shape), Pp) @ nvec
        cr2 = np.cross(Pp, np.broadcast_to(v2, u.shape)) @ nvec
        inside = (cr1 >= 0) & (cr2 >= 0)
        d1a = np.degrees(np.arccos(np.clip(u @ v1, -1, 1)))
        d2a = np.degrees(np.arccos(np.clip(u @ v2, -1, 1)))
        d = np.where(inside, perp, np.minimum(d1a, d2a))
        best = np.minimum(best, d)
    return best

d_n = d_node_min(ev_ra, ev_dec)
d_e = d_edge_min_vec(ev_ra, ev_dec)
print(f"Auger {N_ev} 事件 | {len(nodes)} 節點 | {N_edges} 阻挫邊")
print(f"最近節點: 中位 {np.median(d_n):.2f}° / 最近邊: 中位 {np.median(d_e):.2f}°\n")

rng = np.random.default_rng(42)
N_MC = 5000

def mc_null(dec_vec, obs_fn, n_sub):
    """MC: scramble RA keep dec. obs_fn(ra, dec) -> count."""
    out = np.empty(N_MC, dtype=int)
    for i in range(N_MC):
        ras = rng.uniform(0, 360, n_sub)
        out[i] = obs_fn(ras, dec_vec)
    return out

# ---------------- (A) 阻挫邊檢驗 ----------------
print("=" * 74)
print("(A) 32 阻挫邊 大圓 segment 距離 — MC null (scramble RA keep dec)")
print("=" * 74)
edge_res = {}
for E_cut in [46, 100, 130, 150]:
    mask = ev_E >= E_cut
    n_sub = int(mask.sum())
    if n_sub < 3: continue
    sub_e = d_e[mask]; sub_n = d_n[mask]; decs = ev_dec[mask]
    row = {"n": n_sub}
    for r in [3, 5, 8, 10]:
        obs_all = int((sub_e < r).sum())
        mc = mc_null(decs, lambda ra, dc: int((d_edge_min_vec(ra, dc) < r).sum()), n_sub)
        p = float((mc >= obs_all).mean())
        row[f"edge<{r}"] = {"obs": obs_all, "pct": round(obs_all/n_sub*100, 1),
                            "mc_mean": round(float(mc.mean()), 1), "mc_sd": round(float(mc.std()), 1),
                            "p": p}
    # ⚠️ 條件化 edge-only 分析已移交 script 25 (三分區分解) — 舊版 MC 冇施加同一
    # d_node≥8° 條件 (比較唔對等, 2026-10-18 發現), 唔再喺本 script 出 p 值。
    edge_res[f"E>={E_cut}"] = row
    print(f"  E≥{E_cut:>3} EeV ({n_sub:>3} ev):")
    for r in [3, 5, 8, 10]:
        q = row[f"edge<{r}"]
        line = (f"    <{r:>2}°: {q['obs']:>3}/{n_sub} ({q['pct']:>5.1f}%) "
                f"MC={q['mc_mean']:>5.1f}±{q['mc_sd']:<4.1f} p={q['p']:.4f}")
        if "edge_only" in q:
            eo = q["edge_only"]
            line += (f"  | edge-only: {eo['obs']:>2}/{eo['n']:<3} ({eo['pct']:>5.1f}%) "
                     f"MC={eo['mc_mean']:>4.1f} p={eo['p']:.4f}")
        print(line)

# ---------------- (B) 低能段節點避開 ----------------
print()
print("=" * 74)
print("(B) 低能段 (46-80 EeV) 節點避開 — docs/03 §4.3 報 0% vs 29%")
print("=" * 74)
low = (ev_E >= 46) & (ev_E < 80)
n_low = int(low.sum())
obs8 = int((d_n[low] < 8).sum()); obs10 = int((d_n[low] < 10).sum())
mc8 = mc_null(ev_dec[low], lambda ra, dc: int((d_node_min(ra, dc) < 8).sum()), n_low)
mc10 = mc_null(ev_dec[low], lambda ra, dc: int((d_node_min(ra, dc) < 10).sum()), n_low)
# 兩尾: 避開 = 過少
p_low8 = float((mc8 <= obs8).mean()); p_low10 = float((mc10 <= obs10).mean())
# 合併兩段檢驗 (低能避開 + 高能聚集) — 用 46-80 vs 80+ 嘅 8° 命中率
high = ev_E >= 80
p_hi8 = float((d_n[high] < 8).mean())
p_lo8 = obs8 / n_low if n_low else float('nan')
print(f"  46-80 EeV: N={n_low}; 節點<8°: {obs8}/{n_low} ({p_lo8*100:.1f}%) "
      f"MC={mc8.mean():.1f}±{mc8.std():.1f}  p(避開,單尾)={p_low8:.4f}")
print(f"  46-80 EeV: 節點<10°: {obs10}/{n_low} MC={mc10.mean():.1f}±{mc10.std():.1f}  p={p_low10:.4f}")
print(f"  80+ EeV: N={int(high.sum())}; 節點<8° 命中率 {p_hi8*100:.1f}%")
low_res = {"n": n_low, "obs8": obs8, "pct8": round(p_lo8*100, 1),
           "mc8_mean": round(float(mc8.mean()), 1), "mc8_sd": round(float(mc8.std()), 1),
           "p_deficit8": p_low8, "obs10": obs10, "p_deficit10": p_low10,
           "high_n": int(high.sum()), "high_pct8": round(float(p_hi8)*100, 1)}

out = {"p12_edge_and_lowenergy_20261018": {
    "data": "Auger Open Data catalogSD (109 events)", "N_MC": N_MC, "seed": 42,
    "null": "scramble RA keep dec",
    "geometry": {"nodes": len(nodes), "frustration_edges": N_edges,
                 "note": "邊 = 大圓 segment 垂直距離; edge-only 剔除距節點 <8° 事件"},
    "edges_A": edge_res, "low_energy_B": low_res,
    "d_edge_summary": {"median": round(float(np.median(d_e)), 3),
                       "mean": round(float(np.mean(d_e)), 3)},
}}
dst = os.path.join(DATA, 'edge_auger_and_lowenergy.json')
json.dump(out, open(dst, 'w'), indent=2, ensure_ascii=False)
print(f"\n已存 {dst}")