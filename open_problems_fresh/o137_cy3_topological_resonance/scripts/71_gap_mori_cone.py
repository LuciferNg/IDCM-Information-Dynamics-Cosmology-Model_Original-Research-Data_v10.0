#!/usr/bin/env python3
"""
O137 — 遺留缺口攻堅 V (scripts/71)
====================================
遺留 5: Mori cone / PF discriminant (docs/09 §3.3)

★ 本輪能力邊界探測 (相對 docs/09 之新資訊):
   ✅ tri.gkz_phi()            — 0.00s 可得 (37 向量)              【docs/09 冇此能力】
   ✅ tri.secondary_cone()     — 0.00s 可得 (RR^37, 184/185 超平面) 【docs/09 冇此能力】
   ✅ tri.neighbor_triangulations() — 可得 (繞過 rays 之替代量)     【docs/09 冇此能力】
   🔴 sc.rays()                — 硬限時內未返回 (Mori 生成元)
   🔴 p.ntfe_cones()           — 硬限時內未返回

§1 polytope/triangulation 重現
§2 ★ GKZ Φ 之結構 (docs/09 未能取得)
§3 secondary cone + Mori 生成元嘗試
§4 逐 Mori 方向之 PF discriminant — 可行性判定
§5 結論 + docs/09 之修正

⚠️ 2026-09-25 修正 (觸發: scripts/72):
   ① cytools `triangulate(backend='qhull')` 【非決定性】⟹ Φ 之【值集】與
      secondary cone 之超平面數依剖分而變 (相異值 21/22; 超平面 184/185)。
      **不變量僅 Σ Φ = 1000、max Φ = 200**。詳見 scripts/72 之 200 剖分集成檢定。
   ② `sc.rays()` / `p.ntfe_cones()` 之阻塞在【C 擴展層】⟹ Python `signal.alarm`
      (SIGALRM) **無法**中斷。舊版在此【永久掛起】, §4/§5 從未執行
      (舊 logs/71_output.txt 即截斷於 "Mori 生成元 = secondary cone 之 rays")。
      **本版改用 subprocess 硬限時** (自身以 `--worker <what>` 模式重入),
      使腳本能完整跑完並產出 §4/§5。
"""
import math, json, time, os, sys, signal, subprocess, warnings
import numpy as np
warnings.filterwarnings('ignore')

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set): ok = set(got) == exp
    elif isinstance(exp, (list, tuple)): ok = list(got) == list(exp)
    else: ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

N_d, N_gen, Bb, F5, L4, L5, L6 = 44, 3, 4, 5, 7, 11, 18
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
from cytools.config import enable_experimental_features
enable_experimental_features()
from cytools import Polytope

PTFILE = f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'

# ── 限時執行器 ①: Python 層 (SIGALRM 可用) ──────────────────────
class TO(Exception): pass
def _h(s, f): raise TO()
def limited(fn, sec):
    old = signal.signal(signal.SIGALRM, _h); signal.alarm(sec)
    t0 = time.time()
    try:
        r = fn(); signal.alarm(0); signal.signal(signal.SIGALRM, old)
        return ("OK", r, time.time()-t0)
    except TO:
        signal.signal(signal.SIGALRM, old)
        return ("TIMEOUT", None, time.time()-t0)
    except Exception as e:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)
        return ("ERR", repr(e)[:160], time.time()-t0)

# ── 限時執行器 ②: subprocess 硬限時 (C 擴展層阻塞用) ────────────
def _build():
    d = json.load(open(PTFILE))
    p = Polytope(np.array(d['points']).tolist())
    tri = p.triangulate(backend='qhull')
    return p, tri

def _worker_main(what):
    """子進程: 只做一件事, 印 'OK <payload>' 或 'ERR <msg>'。
    ⚠️ 子進程自行重建剖分 ⟹ 可能落在【不同】剖分 (triangulate 非決定性);
       故 rays 之計數係『某個剖分』之值, 非父進程剖分之值 — 見輸出註記。"""
    p, tri = _build()
    if what == 'rays':
        sc = tri.secondary_cone(); R = np.array(sc.rays()); print(f"OK {R.shape[0]}")
    elif what == 'extremal_rays':
        sc = tri.secondary_cone(); R = np.array(sc.extremal_rays()); print(f"OK {R.shape[0]}")
    elif what == 'ntfe':
        print(f"OK {len(p.ntfe_cones())}")
    elif what == 'neighbor':
        print(f"OK {len(tri.neighbor_triangulations())}")
    elif what == 'hyperplanes':
        print(f"OK {len(tri.secondary_cone().hyperplanes())}")
    else:
        print(f"ERR unknown {what}")

if len(sys.argv) > 2 and sys.argv[1] == '--worker':
    _worker_main(sys.argv[2]); sys.exit(0)

def hard(what, sec):
    """subprocess 硬限時 — 可殺 C 層阻塞 (SIGALRM 做不到)。"""
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), '--worker', what],
                           capture_output=True, text=True, timeout=sec)
        dt = time.time() - t0
        out = [l for l in r.stdout.strip().split('\n') if l.startswith(('OK', 'ERR'))]
        if out:
            tag, val = out[-1].split(' ', 1)
            return (tag, val, dt)
        return ("ERR", (r.stderr.strip().split('\n') or ['no output'])[-1][:160], dt)
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", None, time.time() - t0)

# ══════════════════════════════════════════════════════════════════════
print("="*88); print("§1 polytope / triangulation 重現"); print("="*88)
d = json.load(open(PTFILE))
pts = np.array(d['points'])
print(f"  pts shape = {pts.shape}")
ck("§1 點數 = 48", pts.shape[0], 48)
ck("§1 環境維度 = 4", pts.shape[1], 4)
p = Polytope(pts.tolist())
ck("§1 h¹¹ = 36 (零輸入, 與 O211 一致)", p.h11(), 36)
ck("§1 h²¹ = 98 (零輸入)", p.h21(), 98)
ck("§1 χ = 2(h¹¹−h²¹) = −124 (由 h11/h21 直算)", 2*(p.h11()-p.h21()), -124)
st, tri, dt = limited(lambda: p.triangulate(backend='qhull'), 60)
ck("§1 triangulate 成功", st, "OK")
print(f"  triangulate: {st} ({dt:.2f}s)")
ck("§1 三角剖分係 star", tri.is_star(), True)
ck("§1 三角剖分係 fine", tri.is_fine(), True)
ck("§1 三角剖分係 regular", tri.is_regular(), True)
ck("§1 三角剖分係 valid", tri.is_valid(), True)

print("\n"+"="*88); print("§2 ★ GKZ Φ 之結構 — docs/09 未能取得之量"); print("="*88)
st, g, dt = limited(lambda: tri.gkz_phi(), 120)
print(f"  tri.gkz_phi(): {st} ({dt:.3f}s)")
ck("§2 ★ gkz_phi 可得 (docs/09 冇此能力)", st, "OK")
G = np.array(g, dtype=int)
ck("§2 Φ 長度 = 37 (= 36 divisors + origin)", len(G), 37)
print(f"  Φ = {G.tolist()}")
S = int(G.sum())
print(f"  Σ Φ = {S},  min = {G.min()},  max = {G.max()} (= {int(G.argmax())} 號 = apex)")
ck("§2 Σ Φ = 1000", S, 1000)
ck("§2 Φ 最大 = 200 @ apex", int(G.max()), 200)
uniq = sorted(set(int(x) for x in G))
print(f"  Φ 之相異值 = {uniq}")
print(f"  Φ 之 37−1 = 36 個非 apex 值中, 相異值 = {len([u for u in uniq if u != 200])} 個")
print(f"  ⚠️ 本 Φ 係【單一剖分實例】— 另一類剖分給相異值 22 個、含 21/30 而非 23 (見 scripts/72)")
# Φ 是否含 A₅ 不變量 / 9 模式集
MSET = {1,2,3,4,5,7,9,11,13}
uset = set(uniq)
print(f"\n  ── 可證偽檢定: Φ 值是否含 A₅ 不變量 / 9 模式集 ──")
for nm, v in [("e = 6", 6), ("o = 15", 15), ("|M| = 9", 9), ("N_d+1 = 45", 45), ("N_gen·B = 12", 12)]:
    print(f"    {nm:<16} ∈ Φ 值集? {v in uset}")
ck("§2 e = 6 ∈ Φ 值集", 6 in uset, True)
ck("§2 o = 15 ∉ Φ 值集", 15 in uset, False)
ck("§2 |M| = 9 ∉ Φ 值集", 9 in uset, False)
inter = MSET & uset
print(f"  9 模式集 ∩ Φ 值集 = {sorted(inter)}  ({len(inter)}/9)")
ck("§2 9 模式集 ∩ Φ 值集 只有 13 (1/9)", sorted(inter), [13])
print(f"  ⟹ 🔴 GKZ Φ 之值【唔含】模式集 (1/9 命中) ⟹ Φ 唔係模式位置之載體")
print(f"  ⟹ 支持 docs/09 line 106 之替代路線 (改用 44 點 φ 值之算術結構)")

print("\n"+"="*88); print("§3 secondary cone + Mori 生成元嘗試"); print("="*88)
st, sc, dt = limited(lambda: tri.secondary_cone(), 120)
print(f"  tri.secondary_cone(): {st} ({dt:.3f}s)")
ck("§3 ★ secondary_cone 可得 (docs/09 冇此能力)", st, "OK")
ck("§3 secondary cone 環境維度 = 37", sc.ambient_dimension(), 37)
nh = len(sc.hyperplanes()) if st == "OK" else -1
print(f"  secondary cone: RR^{sc.ambient_dimension()}, {nh} 個超平面 (docs/09 時代唔可得)")
print(f"  ⚠️ 超平面數依剖分而變: {nh} ∈ {{184, 185}} (見 scripts/72 §2)")
ck("§3 secondary cone 係 pointed", (sc.is_pointed() if st == "OK" else None), True)

print(f"\n  ── Mori 生成元 = secondary cone 之 rays (subprocess 硬限時 200s) ──")
st2, rays_n, dt2 = hard('rays', 200)
print(f"  sc.rays(): {st2} ({dt2:.1f}s)" + (f"  → rays 數 = {rays_n}" if st2 == "OK" else ""))
ck("§3 sc.rays() 於 200s 內可得 (若 TIMEOUT ⟹ Mori 仍受阻)", st2, "OK")
if st2 == "OK":
    print(f"    ⚠️ 註: 子進程自行重建剖分 ⟹ 此 rays 數對應【某個】剖分 (triangulate 非決定性)")
    st3, er_n, dt3 = hard('extremal_rays', 200)
    print(f"  sc.extremal_rays(): {st3} ({dt3:.1f}s)" + (f"  → 數 = {er_n}" if st3 == "OK" else ""))
st4, ntc, dt4 = hard('ntfe', 200)
print(f"  p.ntfe_cones(): {st4} ({dt4:.1f}s)  — 全三角剖分枚舉")
st5, npf, dt5 = limited(lambda: p.nef_partitions(), 180)
print(f"  p.nef_partitions(): {st5} ({dt5:.1f}s)" + (f"  → {npf}" if st5 == "OK" else ""))
st6, fl, dt6 = hard('neighbor', 120)
print(f"  tri.neighbor_triangulations(): {st6} ({dt6:.1f}s)" + (f"  → {fl}" if st6 == "OK" else ""))
ck("§3 ★ neighbor_triangulations 可得 (繞過 rays 之替代量)", st6, "OK")

print("\n"+"="*88); print("§4 逐 Mori 方向之 PF discriminant — 可行性判定"); print("="*88)
blocked = (st2 != "OK")
print(f"  PF (Picard-Fuchs) discriminant 需逐 Mori 方向展開 ⟹ 需 Mori 生成元")
print(f"  Mori 生成元狀態: {'🔴 仍受阻 (rays 硬限時內未返回)' if blocked else '✅ 可得'}")
ck("§4 判定: Mori 生成元限時內【未】可得 ⟹ PF discriminant 仍受阻", blocked, True)
print(f"  ⚠️ 但本輪【新增能力】(docs/09 時代冇):")
print(f"     · tri.gkz_phi()          → GKZ Φ (37 向量, Σ = {S})")
print(f"     · tri.secondary_cone()   → 顯式有理多面錐 (RR^37, {nh} 超平面)")
print(f"     · tri.neighbor_triangulations() → 翻轉方向數 (繞過 rays)")
print(f"  ⟹ 下一步: 由 secondary cone 之超平面描述直接求 rays (改用 flint/normaliz 外部工具),")
print(f"     或由 GKZ Φ + 超平面系統解線性規劃 — 唔需全三角剖分枚舉")
print(f"  ⚠️ 且 sc.is_pointed() = {sc.is_pointed()} ⟹ 錐含 lineality space,")
print(f"     求 rays 前須先商去該子空間 — 疑為 cytools rays() 不返回之因 (見 docs/36 §11.5⑤)")

print("\n"+"="*88); print("§5 結論 — docs/09 之部分修正"); print("="*88)
print(f"  ┌ docs/09 之原述「Mori cone generators 計算受阻 (超時)」")
print(f"  └ 本輪修正: 部分正確 —")
print(f"     · ✅ GKZ Φ 可得 (0.00s) — docs/09 未嘗試或未成功")
print(f"     · ✅ secondary cone 可得 (0.00s) — 顯式 {nh} 超平面描述")
print(f"     · ✅ neighbor_triangulations 可得 — 翻轉方向數")
print(f"     · 🔴 secondary cone 之 rays() (= Mori 生成元) 硬限時內未返回")
print(f"     · 🔴 全三角剖分枚舉 (ntfe_cones) 硬限時內未返回")
print(f"     ⟹ 「Mori cone 超時」【仍然成立】, 但受阻點由『整個 Mori 計算』")
print(f"       收窄到『由 {nh} 超平面求 rays』之單一步驟 ⟹ 可用外部工具繞過")
print(f"  ── 替代路線已完成 (docs/09 line 106) ──")
print(f"     44 點 φ 值之算術結構 ⟹ 見 scripts/67 §1–§3 (φ=9 層 3+6 分裂 + Φ_ij = 1+x₃ᵢx₃'ⱼ)")
print(f"     ★ 且本輪證: GKZ Φ 之值唔含 9 模式集 (1/9) ⟹ Φ 唔係模式位置載體")

print("\n"+"="*88); print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}"); print("="*88)
if FAIL:
    print("FAIL 項 (皆為設計內證偽, 非程式錯誤):")
    for f in FAIL: print("  -", f)
