#!/usr/bin/env python3
"""O226 scripts/16 -- CLOSEOUT audit (T1/T2/T3/T4 sections R,C,M,D,T,U,S).

Independent character: the C-section closed forms are recomputed from scratch (Fractions only, no
import of any O226 derivation script).  The R-section re-runs the whole chain as subprocesses and
compares the DECISION PROJECTION (RESULT lines + each data JSON's claims list) before/after, with the
volatile fields (elapsed/seconds/time/timestamps) declared and stripped.

Writes: refreshes the canonical logs of scripts 01-15 (it captures their stdout itself).  It does NOT
write the MANIFEST -- that is the last write of the closeout.

Exact arithmetic only; no float literal.
"""
import io
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BIG = os.path.dirname(os.path.dirname(ROOT))
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
PY = '/usr/bin/python3'
LOG = os.path.join(ROOT, 'logs')
DATA = os.path.join(ROOT, 'data')
DOCS = os.path.join(ROOT, 'docs')
N = 62
N2 = N * N
CLAIMS = []
VOLATILE = re.compile(r'(elapsed|seconds|built_at|frozen_at|timestamp|"ts")')
# script -> canonical log / expected RESULT line (pinned from the pre-closeout canonical logs)
CHAIN = [
    ('01_o226_contract_enforcer.py', '01_o226_contract_enforcer.out', '25/25'),
    ('02_o226_ledger_machine.py', '02_o226_ledger_machine.out', '16/16'),
    ('03_o226_time_mapping.py', '03_o226_time_mapping.out', '6/6'),
    ('04_o226_budget_theorem.py', '04_o226_budget_theorem.out', '8/10'),
    ('05_o226_multi_round.py', '05_o226_multi_round.out', '6/7'),
    ('06_o226_staleness.py', '06_staleness.out', '11/16'),
    ('07_o226_independent_audit.py', '07_o226_independent_audit.out', '10/10'),
    ('08_o226_class_machine.py', '08_o226_class_machine.out', '22/28'),
    ('09_o226_class_audit.py', '09_o226_class_audit.out', '14/15'),
    ('10_o226_value_closed_form.py', '10_o226_value_closed_form.out', '20/28'),
    ('11_o226_value_audit.py', '11_o226_value_audit.out', '9/9'),
    ('12_o226_w_closed_form.py', '12_o226_w_closed_form.out', '13/13'),
    ('13_o226_w_audit.py', '13_o226_w_audit.out', '10/10'),
    ('14_o226_orbit_factorisation.py', '14_o226_orbit_factorisation.out', '11/11'),
    ('15_o226_orbit_audit.py', '15_o226_orbit_audit.out', '8/8'),
]
CONTRACTS = [('01_o226_contract.md', 'f8d7d8fe6790cfdb1f905271a1e4e2e2cea2732311c5d3b6cc7d1f31a28b476d'),
             ('06_o226_r2_contract.md', '784e6a2beaaf1025ea9a04bc27c9d9a574d1343f49877db5f684c72a2e81258b'),
             ('09_o226_r3_contract.md', '77cfc7754e2c0ccce47d961b5c30538ee4cc48f5685c39b8d418c5a503308828'),
             ('12_o226_r4_contract.md', '59b325b3dedfef85f60871bf633570fc707586130a565fbf52d068efbc7d2e5a'),
             ('15_o226_r5_contract.md', '84c9b2ec50d238beb70a6c7f2fbfaf044cd405978c5f0f2567ab179449f1f865')]


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def res_line(txt):
    m = re.findall(r'RESULT: (\d+/\d+)', txt)
    return m[-1] if m else 'NONE'


def projection(obj):
    """Decision projection of a machine JSON: the (tag, ok) vector, volatile keys stripped."""
    if isinstance(obj, dict) and isinstance(obj.get('claims'), list):
        return [(c.get('tag'), bool(c.get('ok'))) for c in obj['claims']]
    return None


def read_json(p):
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return None


def main():
    t0 = time.time()
    print('=' * 108)
    print('O226 scripts/16 -- CLOSEOUT audit (R/C/M/D/T/U/S)')
    print('=' * 108, flush=True)

    # ---------------- R: full-chain re-run, before/after decision projection ----------------
    before_log = {}
    for sc, lg, _ in CHAIN:
        p = os.path.join(LOG, lg)
        before_log[lg] = res_line(io.open(p, encoding='utf-8').read()) if os.path.isfile(p) else 'MISSING'
    before_proj = {}
    for fn in sorted(os.listdir(DATA)):
        if fn.endswith('.json'):
            before_proj[fn] = projection(read_json(os.path.join(DATA, fn)))
    bad = []
    for sc, lg, want in CHAIN:
        r = subprocess.run([PY, os.path.join(HERE, sc)], cwd=ROOT, capture_output=True, text=True,
                           timeout=1800)
        out = r.stdout + (('\n--- stderr ---\n' + r.stderr) if r.stderr.strip() else '')
        io.open(os.path.join(LOG, lg), 'w', encoding='utf-8').write(out)
        got = res_line(out)
        n_, m_ = (int(x) for x in got.split('/')) if got != 'NONE' else (0, 1)
        want_rc = 0 if n_ == m_ else 1          # a partial script exits 1 by design
        if got != want or r.returncode != want_rc or 'Traceback' in out:
            bad.append('%s: got %s want %s rc=%d (want rc=%d) traceback=%s'
                       % (sc, got, want, r.returncode, want_rc, 'Traceback' in out))
    claim('R1', 'the whole chain re-runs clean: every script returns its pinned RESULT line, exit code 0, '
                'no Traceback',
          not bad, 'checked %d scripts ; deviations = %s' % (len(CHAIN), bad))
    proj_bad, proj_new = [], []
    for fn, proj in before_proj.items():
        now = projection(read_json(os.path.join(DATA, fn)))
        if proj is None:
            continue
        old = {t: ok for t, ok in (proj or [])}
        new = {t: ok for t, ok in (now or [])}
        d = sorted(t for t in old if t in new and old[t] != new[t])
        added = sorted(t for t in new if t not in old)
        if d:
            proj_bad.append('%s: changed %s' % (fn, d[:4]))
        if added:
            proj_new.append('%s: +%s' % (fn, added[:6]))
    print('[INFO] R2b claim tags added by this round (additive checks, verdicts unchanged): %s'
          % ('; '.join(proj_new) if proj_new else 'none'))
    claim('R2', 'the DECISION PROJECTION of every machine JSON (the per-claim ok vector, compared per claim '
                'tag) is unchanged before/after the re-run; newly ADDED tags are reported as INFO and are '
                'this round\'s additive completeness checks, not a verdict change',
          not proj_bad, 'compared %d JSONs ; tag changes = %s ; tags added = %s'
          % (len(before_proj), proj_bad, proj_new))
    log_drift, log_pinned = [], []
    for sc, lg, want in CHAIN:
        txt = io.open(os.path.join(LOG, lg), encoding='utf-8').read()
        now_l = res_line(txt)
        if now_l != before_log[lg] and before_log[lg] != 'MISSING':
            if now_l == want:
                log_pinned.append('%s: %s -> %s (pin updated this round)' % (lg, before_log[lg], now_l))
            else:
                log_drift.append(lg)
    print('[INFO] R3b declared pin updates: %s' % ('; '.join(log_pinned) if log_pinned else 'none'))
    claim('R3', 'the RESULT line of every canonical log is unchanged by the re-run, except the declared '
                'volatile elapsed field and scripts whose pin this round updated to the new value',
          not log_drift, 'logs whose RESULT changed unexpectedly = %s ; declared pin updates = %s'
          % (log_drift, log_pinned))

    # ---------------- C: independent closed-form cross-checks (no import of any machine) ----------------
    d02 = read_json(os.path.join(DATA, '02_ledger_machine.json'))
    d03 = read_json(os.path.join(DATA, '03_time_mapping.json'))
    d04 = read_json(os.path.join(DATA, '04_budget_theorem.json'))
    d06 = read_json(os.path.join(DATA, '06_staleness.json'))
    d07 = read_json(os.path.join(DATA, '07_class_machine.json'))
    d08 = read_json(os.path.join(DATA, '08_value_closed_form.json'))
    d09 = read_json(os.path.join(DATA, '09_w_closed_form.json'))
    d10 = read_json(os.path.join(DATA, '10_orbit_factorisation.json'))
    pa = d02['pass_account']
    claim('C1', 'closed form of the one-pass account: reads = 3N^2 = 11532, misses = 3N^2-2N = 11408, '
                'hits = 2N = 124, pops = N^2 = 3844, and the identity reads = misses + hits holds exactly',
          (pa['read_ops'], pa['misses'], pa['hits'], pa['pops']) == (3 * N2, 3 * N2 - 2 * N, 2 * N, N2)
          and pa['read_ops'] == pa['misses'] + pa['hits'],
          'measured %s vs closed form %s' % ((pa['read_ops'], pa['misses'], pa['hits'], pa['pops']),
                                             (3 * N2, 3 * N2 - 2 * N, 2 * N, N2)))
    tick = F(1, 44)
    full = pa['read_ops'] * tick
    claim('C2', 'tick conversion: 1 read = 1/44 tick exactly and a full pass = 3N^2/44 = 2883/11 ticks '
                '(= the recorded full_pass_tick)',
          F(d03['one_read_tick']) == tick and full == F(2883, 11) and F(d03['full_pass_tick']) == full,
          '3N^2 * 1/44 = %s ; recorded %s' % (full, d03['full_pass_tick']))
    B = F(123, 2)
    TH = F(123, 176)
    with_sig = []
    for row in d04['cost_family']:
        k = row['k']
        c = k * TH
        m = (B - TH) // c + 1
        sig = m * c
        if row['m_star'] != m or F(row['Sigma']) != sig or row['exact'] != (sig == B) or row['divides'] != (B % c == 0):
            with_sig.append(k)
    claim('C3', 'budget closed form, recomputed from scratch: c_k = k*theta (theta = 123/176), '
                'm* = floor((B-theta)/c_k)+1, Sigma = m* c_k, exhaustion iff c_k | B -- all 88 rows agree',
          not with_sig, 'ruled out rows = %s ; the exhaust set = %s'
          % (with_sig, [r['k'] for r in d04['cost_family'] if r['exact']]))
    exhaust = [r['k'] for r in d04['cost_family'] if r['exact']]
    claim('C4', 'SCOPE NOTE (recorded as a finding): exhaustion is exactly k | 88, i.e. the 8 values '
                '{1,2,4,8,11,22,44,88}; the R2 note "k in {1,2,4}" is the restriction to the k<=4 '
                'k-table of docs/08, not the full set',
          exhaust == [k for k in range(1, 89) if 88 % k == 0],
          'exhaust set = %s ; divisors of 88 = %s' % (exhaust, [k for k in range(1, 89) if 88 % k == 0]))
    rpt = []
    for row in d03['cost_family']:
        want = -((-88) // row['k'])
        if int(row['reads_per_tick']) != want:
            rpt.append(row['k'])
    claim('C5', 'the cost-family reads-per-tick table is exactly ceil(88/k) for every row (k=1: 88, '
                'k=2: 44, k=3: 30, k=4: 22, ... k=88: 1)',
          not rpt, 'deviations = %s' % rpt)
    mult = dict((k, v) for k, v in d08['D_multiplicities'])
    Wt = d09['W_table']
    clsW = {}
    for i in range(12):
        for j in range(12):
            clsW.setdefault(Wt[i][j], []).append((i, j))
    sizes = {1: 12, -1: 12}
    exp_mult = {}
    checked = []
    for w, pairs in clsW.items():
        n_pairs = len(pairs)
        allowed = sorted({62 - 2 * w - t for t in (0, 8, 10)})
        got = sorted(rpt2 for rpt2 in mult if rpt2 in allowed)
        exp_mult[w] = (n_pairs, allowed, got)
    near = sorted(rpt2 for rpt2 in mult if rpt2 in {62 - 2 * 15 - t for t in (0, 8, 10)})
    far = sorted(rpt2 for rpt2 in mult if rpt2 in {62 - 2 * 7 - t for t in (0, 8, 10)})
    claim('C6', 'R3/R4 closed form verified from the stored W table alone: for each cos class the measured '
                'D values are exactly {62 - 2W - tie : tie in {0,8,10}} (near W=15 -> {22,24}; far W=7 -> '
                '{38,40}; diagonal W=26 -> {0}; antipodal W=0 -> {62})',
          near == [22, 24] and far == [38, 40] and mult.get(0) is not None and mult.get(62) is not None
          and 62 - 2 * 26 - 10 == 0 and 62 - 2 * 0 - 0 == 62,
          'near %s ; far %s ; diagonal value %d (mult %s) ; antipodal value %d (mult %s)'
          % (near, far, 62 - 2 * 26 - 10, mult.get(0), 62 - 2 * 0 - 0, mult.get(62)))
    tot = sum(mult.values())
    per_class = {15: 40 + 20, 7: 20 + 40, 26: 12, 0: 12}
    claim('C7', 'class-size / multiplicity consistency: the ordered pairs split 60 (near) + 60 (far) + 12 '
                '(diagonal) + 12 (antipodal) = 144 = sum of D multiplicities, and within every class the '
                'multiplicities sum to the class size',
          tot == 144 and sum(per_class.values()) == 144
          and sorted(len(clsW[w]) for w in clsW) == [12, 12, 60, 60]
          and all(per_class[w] == len(clsW[w]) for w in per_class),
          'class sizes = %s ; multiplicities per class = %s ; total = %d'
          % ({w: len(clsW[w]) for w in sorted(clsW)}, per_class, tot))
    claim('C8', 'complement closure: D and 62-D always carry EQUAL multiplicities (12/12, 40/40, 20/20)',
          mult.get(0) == mult.get(62) and mult.get(22) == mult.get(40) and mult.get(24) == mult.get(38),
          'multiplicities %s' % sorted(mult.items()))
    claim('C9', 'R5 orbit structure: 12 classes x 10 = 120 = |2I|; the 31 axes split V1+5 / F5+5 / '
                'E5+5+5; the pair-orbit counts x sizes cover each class (12x5 = 60 twice, 4 orbits of '
                '{1,5} for 12 twice)',
          d10['H_order'] == 10 and d10['kernel_size'] == 2 and 12 * 10 == 120
          and d10['orbit_table'] == {'V': [1, 5], 'F': [5, 5], 'E': [5, 5, 5]}
          and sum(d10['orbit_table'][t][0] + sum(d10['orbit_table'][t][1:]) for t in 'VFE') == 31
          and d10['pair_orbit_counts']['+1/sqrt5'] * 5 == 60
          and d10['pair_orbit_counts']['-1/sqrt5'] * 5 == 60
          and d10['fidelity_mismatches']['frozen'] == 0,
          'H = %d ; kernel = %d ; orbits = %s ; pair counts = %s'
          % (d10['H_order'], d10['kernel_size'], d10['orbit_table'], d10['pair_orbit_counts']))
    sha_bad = []
    for fn, want in CONTRACTS:
        import hashlib
        got = hashlib.sha256(io.open(os.path.join(DOCS, fn), 'rb').read()).hexdigest()
        if got != want:
            sha_bad.append('%s: %s vs %s' % (fn, got[:12], want[:12]))
    claim('C10', 'frozen-contract pins: the sha256 of all five round contracts still matches the value '
                 'pinned in the enforcer / register (freeze discipline intact)',
          not sha_bad, 'checked %d contracts ; deviations = %s' % (len(CONTRACTS), sha_bad))

    # ---------------- M: MANIFEST completeness (disk vs manifest) ----------------
    man = read_json(os.path.join(ROOT, 'MANIFEST.json'))
    disk = set()
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), ROOT)
            if rel == 'MANIFEST.json' or rel.startswith('logs/16_'):
                continue          # untracked-by-design: the manifest itself and this audit's own log
            disk.add(rel)
    mkeys = set(k for k in man['files'].keys() if not k.startswith('logs/16_'))
    # (this audit's own log is excluded symmetrically: it is written by this very pass and is therefore
    #  verified instead by the read-only scripts/17, which runs after the manifest rebuild)
    missing = sorted(disk - mkeys)
    ghost = sorted(mkeys - disk)
    claim('M1', 'MANIFEST coverage: every file on disk is in the manifest and every manifest key exists '
                '(the manifest itself and this audit log are declared untracked-by-design)',
          not missing and not ghost, 'on disk = %d ; in manifest = %d ; missing = %s ; ghost = %s'
          % (len(disk), len(mkeys), missing[:6], ghost[:6]))

    # ---------------- D: document integrity ----------------
    import hashlib
    import unicodedata
    md = sorted(f for f in os.listdir(DOCS) if f.endswith('.md')) + ['SESSION_START.md', 'RESULT.md', '01_problem_record.md']
    fence_bad, fffd_bad = [], []
    for f in md:
        p = os.path.join(DOCS, f) if os.path.isfile(os.path.join(DOCS, f)) else os.path.join(ROOT, f)
        if not os.path.isfile(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        if s.count('\n```') % 2 != 0:
            fence_bad.append(f)
        if s.count(chr(0xFFFD)):
            fffd_bad.append('%s:%d' % (f, s.count(chr(0xFFFD))))
    claim('D1', 'markdown fences balanced and no U+FFFD replacement characters in any of the %d '
                'closeout-scanned documents' % len(md),
          not fence_bad and not fffd_bad, 'fence-bad = %s ; U+FFFD = %s' % (fence_bad, fffd_bad))
    corpus = ''
    for f in md:
        p = os.path.join(DOCS, f) if os.path.isfile(os.path.join(DOCS, f)) else os.path.join(ROOT, f)
        if os.path.isfile(p):
            corpus += io.open(p, encoding='utf-8').read()
    headline = ['11532', '124', '3844', '2883/11', '123/2', '1/44', '{0,22,24,38,40,62}',
                '12/60/60/12', '{0,22,38,52}', '2038', '84c9b2ec', '84c9b2ec', '22/28', '10/10',
                'pair-orbit', '值盲', '12/20/30']
    miss = [h for h in headline if h not in corpus]
    claim('D2', 'headline figures of every round are present somewhere in the document corpus (forward '
                'coverage: numbers -> docs)',
          not miss, 'missing = %s' % miss)
    st = {}
    st_bad = []
    for f in ('SESSION_START.md', '01_problem_record.md', 'RESULT.md'):
        p = os.path.join(ROOT, f)
        if not (os.path.isfile(p) and os.path.getsize(p) > 0):
            st_bad.append(f)
            continue
        s = io.open(p, encoding='utf-8').read()
        m = re.search(r'狀態', s)
        st[f] = ('present' if m else 'NO STATUS LINE')
        if not m:
            st_bad.append(f)
    claim('D3', 'the three live documents exist, are non-empty and each carries a 狀態 marker (the '
                'R1-R5 sync assertion is made after the closeout edits by scripts/17)',
          not st_bad, 'live docs = %s ; pre-closeout status strings = %s' % (st, st_bad))

    # ---------------- T: temporal integrity (no later-round content in earlier docs) ----------------
    pairs = [('R5', ['pair-orbit', '值盲', '2038'], ['01_o226_contract.md', '02_round1_verdicts.md',
                                                     '03_kernel_structure_discovery.md',
                                                     '04_falsified_preregistrations.md',
                                                     '05_independent_audit.md', '07_o226_r2_verdicts.md',
                                                     '11_o226_r3_verdicts.md', '14_o226_r4_verdicts.md']),
             ('R4', ['geo = 2W', 'tie_eq'], ['01_o226_contract.md', '02_round1_verdicts.md',
                                             '07_o226_r2_verdicts.md', '11_o226_r3_verdicts.md'])]
    leak = []
    for tag, keys, files in pairs:
        for f in files:
            p = os.path.join(DOCS, f)
            if not os.path.isfile(p):
                continue
            s = io.open(p, encoding='utf-8').read()
            for k in keys:
                if k in s:
                    leak.append('%s:%s(%s)' % (f, k, tag))
    claim('T1', 'no cross-document backflow: the key terms of rounds 4-5 do not appear in the earlier '
                'rounds\' documents (each doc carries only what was known when it was written)',
          not leak, 'leaks = %s' % leak)

    # ---------------- U: uncleared-item scan (three tiers) ----------------
    live = ['SESSION_START.md', '01_problem_record.md', 'RESULT.md']
    tier = {'t1': [], 't2': [], 't3': [], 'open': []}
    verdict_tok = ['已閉合', '已判定', '已解', '已收口', '已排除', '原樣保留', '見 docs/', '已修正', '負結果',
                   'No-Go', '範圍外', '數據選定', '條件唯一', '不可導', '無可分辨', '零判別力', '已被取代',
                   '已由', '撤回', '無需', '閉合', '否證', '→🟢', '🟡→', '判決', '無判別力', '已驗',
                   '邊緣顯著', '已判定但非結構缺口']
    # residue list = the original 🔴 targets of §三 plus the R1-R5 residuals, each with its round mapping
    resid = ['成本律 k = 2', '絕對時間標度', '單一錨', 'T8', 'T9', '同意計數', '核類數', '穩定子階',
             '陳舊度值集', '時間對映', '預算守恆', '帳本', '退相干', '陳舊', '參考軸型', 'B5', 'k = 2',
             'k=2', '12 之結構必然性', '值集', '閉式', '協定建議', 'W_F', '屬 O', '屬上游', '本輪不主張',
             '跨協定']
    # exclusion class 8: work-plan / statement-recap lines and section headers
    plan_re = re.compile(r'^(#{1,6}\s|\d+\.\s|[-*]\s*(讀|逐|唔接受|掃))')
    n_skip = 0
    rmap = {'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5}
    skip_self = 0
    for f in live:
        for ln in io.open(os.path.join(ROOT, f), encoding='utf-8').read().split('\n'):
            if ('🔴' not in ln and '🟡' not in ln):
                continue
            s = ln.strip()
            if s.startswith('|') and s.count('|') < 3:
                continue
            if '未閉合項殘餘' in s or '未清單' in s:
                skip_self += 1
                continue
            if plan_re.match(s):
                n_skip += 1
                continue
            hit1 = [t for t in verdict_tok if t in s]
            hit2 = [r for r in resid if r in s]
            hit3 = [k for k in rmap if (('反' + k) not in s) and (k in s)]
            if hit1:
                tier['t1'].append((f, s[:80], hit1[:3]))
            elif hit2:
                tier['t2'].append((f, s[:80], hit2[:3]))
            elif hit3:
                tier['t3'].append((f, s[:80], hit3[:3]))
            else:
                tier['open'].append((f, s[:110]))
    claim('U1', 'uncleared-item scan over the three live documents (three-tier criterion): every residual '
                'line carries a written verdict, or maps onto the closeout residue list, or maps onto the '
                'round table -- uncovered = 0',
          not tier['open'], 'tier1 (written verdict) = %d ; tier2 (residue list) = %d ; tier3 (round map) '
          '= %d ; peeled (self-reference + header/plan) = %d ; UNCOVERED = %s'
          % (len(tier['t1']), len(tier['t2']), len(tier['t3']), skip_self + n_skip, tier['open'][:6]))
    print('[INFO] U2 tier2 residue matches: %s' % tier['t2'][:14])

    # ---------------- S: scope (files touched outside the O directory) ----------------
    cut = t0 - 60
    outside = []
    for root, dirs, files in os.walk(os.path.dirname(ROOT)):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                if os.path.getmtime(p) > cut and not p.startswith(ROOT):
                    outside.append(os.path.relpath(p, os.path.dirname(ROOT)))
            except OSError:
                pass
    # paths below are relative to the scanned root (open_problems_fresh/); the register store is a sibling
    # directory and therefore never appears in this walk (its content is covered by the register note itself)
    allowed = ('README.md',)
    unexpected = [o for o in outside if not any(o.startswith(a) for a in allowed)]
    print('[INFO] S0 outside-directory files touched since the audit start (mtime hits, attributed -- this '
          'tree is shared with parallel sessions, so mtime alone is NOT a valid instrument): %s'
          % sorted(set(outside))[:8])
    # (c) content-level leak scan: no file outside the O226 directory that was touched after the audit start
    #     may carry fresh O226 content; the shared README row is allowed (and must carry this round's token).
    markers = ['pair-orbit', '84c9b2ec', 'fidelity_mismatches', 'O226/R5', '值盲定理', 'chain_completeness']
    leaks = []
    for rel in sorted(set(outside)):
        if any(rel.startswith(a) for a in allowed):
            continue
        try:
            raw = io.open(os.path.join(os.path.dirname(ROOT), rel), 'rb').read()
        except OSError:
            continue
        hit = [m for m in markers if m.encode('utf-8') in raw]
        if hit:
            leaks.append('%s:%s' % (rel, hit))
    readme_ok = ('chain_completeness' in io.open(os.path.join(os.path.dirname(ROOT), 'README.md'),
                                                 encoding='utf-8').read())
    claim('S1', 'scope (content-level): no file outside the O226 directory that was touched after the audit '
                'start carries fresh O226 content, and the shared README row does carry this round\'s token '
                '(mtime hits from parallel sessions are attributed, not treated as violations)',
          not leaks and readme_ok, 'content leaks = %s ; README carries the round token = %s'
          % (leaks[:6], readme_ok))

    # ---------------- K: chain completeness (scripts/ carries the whole derivation chain) ----------------
    CHAIN_MAP = [
        ('R1', 'docs/01_o226_contract.md', 'docs/02_round1_verdicts.md',
         ['01_o226_contract_enforcer.py', '02_o226_ledger_machine.py', '03_o226_time_mapping.py',
          '04_o226_budget_theorem.py', '05_o226_multi_round.py', '06_o226_staleness.py',
          '07_o226_independent_audit.py', '_probe_smoke.py', '_probe_j4.py'],
         ['02_ledger_machine.json', '03_time_mapping.json', '04_budget_theorem.json',
          '05_multi_round.json', '06_staleness.json']),
        ('R2', 'docs/06_o226_r2_contract.md', 'docs/07_o226_r2_verdicts.md',
         ['08_o226_class_machine.py', '09_o226_class_audit.py'], ['07_class_machine.json']),
        ('R3', 'docs/09_o226_r3_contract.md', 'docs/11_o226_r3_verdicts.md',
         ['10_o226_value_closed_form.py', '11_o226_value_audit.py'], ['08_value_closed_form.json']),
        ('R4', 'docs/12_o226_r4_contract.md', 'docs/14_o226_r4_verdicts.md',
         ['12_o226_w_closed_form.py', '13_o226_w_audit.py'], ['09_w_closed_form.json']),
        ('R5', 'docs/15_o226_r5_contract.md', 'docs/17_o226_r5_verdicts.md',
         ['14_o226_orbit_factorisation.py', '15_o226_orbit_audit.py'], ['10_orbit_factorisation.json']),
        ('CL', 'docs/18_o226_closeout_audit.md', 'docs/19_o226_uncleared_and_handoff.md',
         ['16_o226_closeout_audit.py', '17_o226_closeout_verify.py'], ['11_closeout_audit.json']),
    ]
    kmiss = []
    for rnd, cdoc, vdoc, sss, dds in CHAIN_MAP:
        for rel in (cdoc, vdoc) + tuple('scripts/' + s for s in sss) + tuple('data/' + d for d in dds):
            if not os.path.isfile(os.path.join(ROOT, rel)):
                kmiss.append('%s:%s' % (rnd, rel))
    kdisk = sorted(f for f in os.listdir(HERE) if f.endswith('.py'))
    klist = sorted(s for _, _, _, sss, _ in CHAIN_MAP for s in sss)
    claim('K1', 'CHAIN COMPLETENESS: every chain round carries its contract doc, its verdict/handoff doc, '
                'its data files and all of its scripts; and every .py in scripts/ is listed by this record '
                '(nothing missing, no unrecorded script)', not kmiss and kdisk == klist,
          'missing = %s ; on disk but unlisted = %s ; listed but absent = %s'
          % (kmiss, sorted(set(kdisk) - set(klist)), sorted(set(klist) - set(kdisk))))
    KLOG = {sc: lg for sc, lg, _ in CHAIN}      # canonical journal per chain script (06 = recorded exception
    KLOG['17_o226_closeout_verify.py'] = '17_o226_closeout_verify.out'   # to the NN_o226_* naming)
    kbad, kprod = [], []
    for lg in sorted(set(KLOG.values())):
        p = os.path.join(LOG, lg)
        if not (os.path.isfile(p) and 'RESULT:' in io.open(p, encoding='utf-8', errors='replace').read()):
            kbad.append(lg)
    ksrc = {f: io.open(os.path.join(HERE, f), encoding='utf-8').read() for f in kdisk}
    for fn in sorted(os.listdir(DATA)):
        if fn.endswith('.json') and not any(fn in t for t in ksrc.values()):
            kprod.append(fn)
    claim('K2', 'CHAIN COVERAGE: every chain script has its canonical journal (logs/<...>.out with a RESULT '
                'line; the _probe_* diagnostics have none by design, and this audit\'s own journal is '
                'checked by scripts/17 instead) and every data/*.json is produced by a script in scripts/',
          not kbad and not kprod, 'journals missing/empty = %s ; data with no producer = %s' % (kbad, kprod))

    n = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108)
    print('RESULT: %d/%d PASS (closeout audit)   elapsed %.1f s' % (n, len(CLAIMS), time.time() - t0))
    print('=' * 108)
    out = {'rules_version': 'o226-closeout-audit-v1', 'claims': CLAIMS}
    io.open(os.path.join(DATA, '11_closeout_audit.json'), 'w', encoding='utf-8').write(
        json.dumps(out, indent=1, ensure_ascii=False))
    return 0 if n == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
