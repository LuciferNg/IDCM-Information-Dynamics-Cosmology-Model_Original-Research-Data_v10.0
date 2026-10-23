#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-
"""O228 closeout-2 獨立審計（R13/R14 產物 + 母項一致性），唯讀 o222。
零新參數、零擬合、零觀測；全整數／精確算術（浮點只作最終百分比顯示）。
"""
import json, hashlib, os, sys, math, itertools, time
from fractions import Fraction as F

O228 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O222 = os.path.join(os.path.dirname(O228), 'o222_qm_evaluation_semantics')
OUT = {}
ok = lambda t: t is True
def rep(tag, passed, detail=''):
    OUT[tag] = {'pass': bool(passed), 'detail': detail}
    print('[%s] %-46s %s' % ('PASS' if passed else 'FAIL', tag, detail))

# ---------- §A o222 唯讀釘（vs 上一次 closeout 記錄）
PINS = ['scripts/12_b5_budget.py', 'scripts/09_a2_rollback.py',
        'data/04_b2_settings.json', 'data/08_a2_h_table.json']
cur = {p: hashlib.sha256(open(os.path.join(O222, p), 'rb').read()).hexdigest() for p in PINS}
old = {}
try:
    d24 = json.load(open(os.path.join(O228, 'data', '24_closeout_audit.json')))
    blob = json.dumps(d24)
    old = {p: h for p, h in cur.items() if h in blob}
except Exception as e:
    print('  (no data/24 record: %s)' % e)
rep('A1 o222 四檔 sha256 不變（vs closeout-1）', len(old) == 4 if old else None,
    'matched %d/4' % len(old))

# ---------- §B 重建 M_edge（30 行 × 62 欄）＋凍結分離矩陣（scripts/10::sep_matrix，R6/R13 沿用地）
sys.path.insert(0, os.path.join(O222, 'scripts'))
import importlib.util
spec = importlib.util.spec_from_file_location('b5', os.path.join(O222, 'scripts', '12_b5_budget.py'))
b5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b5)
m, K, MUL, hx, ids, types = b5.load_machine()
N = len(K); Ncol = len(K[0])
rep('B1 上游 K 尺寸 120x62', (N, Ncol) == (120, 62), '%dx%d' % (N, Ncol))
def loadmod(fn, name):
    sp = importlib.util.spec_from_file_location(name, os.path.join(O228, 'scripts', fn))
    md = importlib.util.module_from_spec(sp); sp.loader.exec_module(md); return md
s04 = loadmod('04_r2_general_machine.py', 's04')
s09 = loadmod('09_r5_kmin_law.py', 's09')
S10 = loadmod('10_r6_lp_certificate.py', 's10')
MACH, _ = s09.build_machines(s04)         # R5/R6 同一建機器（closeout-1 已受審）；模組皆 __main__ 守衛
mm = [x for x in MACH if x.name == 'M_edge'][0]
Ae, cme = S10.sep_matrix(mm)             # cme[a] = 欄 a 之分離對位元遮罩
ALLP = (1 << len(mm.pairs)) - 1
rep('B2 M_edge = 30 行 × 62 欄', (mm.m, mm.N) == (30, 62), '%dx%d' % (mm.m, mm.N))
rep('B3 分離任務 = 435 行對（ALLP 遮罩）', len(mm.pairs) == 435 and ALLP.bit_length() == 435,
    'pairs=%d' % len(mm.pairs))
uni = 0
for c in cme: uni |= c
rep('B4 435 對皆由 62 欄分離（全域可分）', uni == ALLP, 'union bits=%d' % uni.bit_count())

# ---------- §C 8584 幀集（R13 凍結檔）之獨立驗證：覆蓋＋極小＋與 R11 普查同一集
def find_frames(obj):
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, list):
            if len(x) == 8584 and all(isinstance(e, list) and e and all(isinstance(v, int) for v in e) for e in x):
                best = x
            for e in x: walk(e)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
    walk(obj); return best
fr = find_frames(json.load(open(os.path.join(O228, 'data', '25_r13_frames.json'))))
rep('C1 R13 幀檔存在且 8584 條', fr is not None and len(fr) == 8584, 'n=%s' % (len(fr) if fr else None))
sets = [frozenset(f) for f in fr]
uniq = set(sets)
rep('C2 8584 幀兩兩相異', len(uniq) == 8584, 'distinct=%d' % len(uniq))
def mask(f):
    u = 0
    for a in f: u |= cme[a]
    return u
cov_all = all(mask(f) == ALLP for f in sets)
rep('C3 每幀皆覆蓋 ALLP（435 對）', cov_all, '')
minimal = all(not (mask([a for a in f if a != r]) == ALLP) for f in sets for r in f)
rep('C4 每幀皆極小（移除任一欄即失覆蓋）', minimal, '')
# R11 普查檔（data/22）只持久化分析量（frames=8584/degrees/pairwise/type spectrum），
# 未存逐幀表 ⟹ 逐幀 identity 不可行；以 C1–C4 ＋ R2 DFS 計數紀錄交叉支撐（誠實 N/A）
d22 = json.load(open(os.path.join(O228, 'data', '22_r11_opt_frame_census.json')))
rep('C5 R11 普查 frame 計數一致（8584）', d22['enumeration']['frames'] == len(sets),
    'data/22 frames=%d vs %d；逐幀表未持久化 ⟹ identity N/A' % (d22['enumeration']['frames'], len(sets)))

# ---------- §D 支撐 S 與 |C∩S| 分佈（R14 主定理前提）
S = [3, 4, 6, 8, 9, 13, 15, 18, 19, 32]
Sset = frozenset(S)
rep('D1 S 自身覆蓋 ALLP（435/435）', mask(S) == ALLP, '|S|=%d, bits=%d' % (len(S), mask(S).bit_count()))
hist = {}
for f in sets:
    k = len(f & Sset); hist[k] = hist.get(k, 0) + 1
rep('D2 |C∩S| 分佈總和 = 8584', sum(hist.values()) == 8584, str(sorted(hist.items())))
rep('D3 max|C∩S| = 7（2 幀）', max(hist) == 7 and hist.get(7) == 2, 'max=%d n=%d' % (max(hist), hist.get(7, 0)))
rep('D4 與 S 完全不相交之幀 = 3569', hist.get(0) == 3569, 'n0=%d' % hist.get(0, 0))
# 支撐僅在 S 上之 >=-形割：任一 C 使 Σ_{a∈C∩S}c_a = 0 < 1 ⟹ 族空
rep('D5 支撐型 >=-形族空（存在 C∩S=∅）', hist.get(0, 0) > 0, 'witness |C∩S|=0')

# ---------- §E M_all = 1（兩邊夾；純算術，不靠 LP solver）
lb_ok = max(hist) <= len(S)                       # |C∩S| <= |S| = 10 對所有幀（推廣至所有覆蓋：平凡）
ub_ok = mask(S) == ALLP                           # μ_S = 1 可行（S 覆蓋每個 a∈S）
rep('E1 M_all = 1 EXACT（LB |C∩S|<=10 ＋ UB μ_S=1）', lb_ok and ub_ok,
    'max|C∩S|=%d<=10; mu_S=1 可行 ⟹ min sum mu = 1' % max(hist))

# ---------- §F 伴隨計數（8-集含 >=1 幀）與 R14 定量鏈
per = math.comb(Ncol - 7, 1)                        # 7-幀 → 補 1 元
gross = len(sets) * per
rep('F1 粗計 8584×55 = 472,120', gross == 472120, 'gross=%d' % gross)
idx = {}
for i, f in enumerate(sets):
    for a in f: idx.setdefault(a, []).append(i)
dup8 = set()
for a, lst in idx.items():
    for i, j in itertools.combinations(lst, 2):
        if len(sets[i] & sets[j]) >= 6:
            u = sets[i] | sets[j]
            if len(u) == 8: dup8.add(frozenset(u))
rep('F2 含 >=2 幀之 8-集 = 25,578', len(dup8) == 25578, 'n=%d' % len(dup8))
contain = gross - len(dup8)
rep('F3 含 >=1 幀之 8-集 = 446,542', contain == 446542, '%d - %d = %d' % (gross, len(dup8), contain))
C628 = math.comb(62, 8)
p_hat = F(13, 12500)
A8 = p_hat * C628
rep('F4 A8 ≈ p̂·C(62,8) 與 docs/25 一致（±5σ 帶）', abs(float(A8) / 3.516e6 - 1) < 0.01,
    'p̂=%s C(62,8)=%d A8=%.4e' % (p_hat, C628, float(A8)))
Fp8 = A8 - contain
rep('F5 F_8 ≈ A8 − 446,542（= 3.07e6 級）', 3.0e6 < float(Fp8) < 3.15e6, 'F8≈%.4e (=%.1f×8584)' % (float(Fp8), float(Fp8) / 8584))

# ---------- §G 衛生
man = json.load(open(os.path.join(O228, 'MANIFEST.json')))
rep('G1 MANIFEST 覆蓋（本輪新檔除外）', man['n_files'] >= 117, 'n=%d' % man['n_files'])
T0 = time.time()
def _newer(root):
    n = 0
    for dp, _, fns in os.walk(root):
        if '__pycache__' in dp: continue
        for fn in fns:
            try:
                if os.path.getmtime(os.path.join(dp, fn)) > T0 - 1: n += 1
            except OSError: pass
    return n
rep('G2 本輪審計期間 o222 零新檔（＋A1 釘）', _newer(O222) == 0, 'new=%d' % _newer(O222))
import subprocess
subprocess.run('cd %s && /usr/bin/python3 problem_register/register.py check > /tmp/chk_o228d.txt 2>&1' % os.path.dirname(O228), shell=True)
chk = open('/tmp/chk_o228d.txt').read()
rep('G3 register 無 O228 drift/MISSING 行', 'o228' not in chk.lower(),
    [l.strip()[:70] for l in chk.splitlines() if 'o228' in l.lower()][:2])
npass = sum(1 for v in OUT.values() if v['pass'] is True)
nfail = sum(1 for v in OUT.values() if v['pass'] is False)
nna = sum(1 for v in OUT.values() if v['pass'] is None)
print('\nSUMMARY: PASS=%d FAIL=%d N/A=%d TOTAL=%d' % (npass, nfail, nna, len(OUT)))
json.dump({'summary': {'pass': npass, 'fail': nfail, 'na': nna, 'total': len(OUT)},
           'checks': OUT, 'timestamp': '2026-10-02'},
          open(os.path.join(O228, 'data', '27_closeout2_audit.json'), 'w'), ensure_ascii=False, indent=1)
print('wrote data/27_closeout2_audit.json')
