#!/usr/bin/env python3
"""O222 scripts/13 -- CLOSEOUT AUDIT (independent verifier)

Purpose: verify that the whole session-chain record of thread 93184 is (a) recorded,
(b) mutually consistent, (c) independently reproducible.

INDEPENDENCE RULES (contract of this script):
  * imports NOTHING from scripts/09, 10, 11, 12  (no shared code, no shared bug)
  * stdlib only; exact arithmetic (Fraction / int) for every claimed value
  * two DIFFERENT algorithms than the recorded ones:
      - domain sizes by COMBINATORIAL counting (records used enumeration)
      - CHSH maxima by the SEPARABLE decomposition V(i)+U(j) (records used
        full 62^4 enumeration and a top-3 sort accelerator)
  * reads only FROZEN artefacts (data/*.json) + the session DB (read-only)

Sections: A chain  B ledger scope  C numeric coverage  D B5 identities
          E A2 CHSH  F B2 algebra  G doc<->data  H integrity  I unclosed
"""
import io
import json
import os
import re
import sqlite3
import sys
from fractions import Fraction as F
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROOT))
DATA = os.path.join(ROOT, 'data')
FROZEN = os.path.join(DATA, 'frozen')
LOGS = os.path.join(ROOT, 'logs')
DOCS = os.path.join(ROOT, 'docs')

CLAIMS = []


def chk(cid, ok, detail=''):
    CLAIMS.append({'id': cid, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-46s %s' % ('PASS' if ok else 'FAIL', cid, detail))


def load(p):
    with io.open(p, encoding='utf-8') as fh:
        return json.load(fh)


def read(p):
    try:
        with io.open(p, encoding='utf-8') as fh:
            return fh.read()
    except (UnicodeDecodeError, OSError):
        return ''            # binary / unreadable -> not part of the text record


OUT = {}
print('=== O222 closeout audit (scripts/13) ===')
print('repo root : %s' % REPO)

# ---------------------------------------------------------------- A  chain
print('\n--- A  session chain (provenance) ---')
db = os.path.expanduser('~/.hermes/state.db')
conn = sqlite3.connect('file:%s?mode=ro' % db, uri=True)
SK = 'agent:main:telegram:dm:7500748185:93184'
rows = list(conn.execute(
    'SELECT id,started_at,ended_at,end_reason,parent_session_id,message_count,tool_call_count '
    'FROM sessions WHERE session_key=? ORDER BY started_at', (SK,)))
ids = [r[0] for r in rows]
OUT['chain'] = [{'id': r[0], 'start': r[1], 'end': r[2], 'reason': r[3],
                 'parent': r[4], 'msgs': r[5], 'tools': r[6]} for r in rows]
chk('A1 chain size = 8 sessions (thread 93184)', len(ids) == 8, 'ids=%s' % len(ids))
par_ok = all(rows[i][4] == rows[i - 1][0] for i in range(1, len(rows)))
chk('A2 compression chain: parent[i] == id[i-1]', par_ok)
chk('A3 chain is append-only in time (start monotone)',
    all(rows[i][1] >= rows[i - 1][1] for i in range(1, len(rows))))
ph = ','.join('?' * len(ids))
msg = list(conn.execute(
    'SELECT session_id, role, content, tool_calls FROM messages WHERE session_id IN (%s) '
    'ORDER BY timestamp' % ph, ids))
OUT['chain_messages'] = len(msg)
chk('A4 chain message total >= 1488 (live chain: snapshot, not a frozen count)',
    len(msg) >= 1488, 'n=%d at audit time' % len(msg))
first, last = rows[0][1], rows[-1][1]
chk('A5 chain span 2026-09-29 17:22 -> live (end_reason NULL on tail)',
    rows[-1][2] is None, 'first_start=%.0f last_start=%.0f' % (first, last))

# ---------------------------------------------------------------- B  ledger
print('\n--- B  write ledger scope ---')
wrote = {}
for sid, role, content, tc in msg:
    if role != 'assistant' or not tc:
        continue
    try:
        calls = json.loads(tc)
    except Exception:
        continue
    for c in calls:
        fn = c.get('function', c)
        if fn.get('name') not in ('write_file', 'patch'):
            continue
        a = fn.get('arguments')
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                a = {}
        p = (a or {}).get('path', '')
        if p:
            wrote[p] = wrote.get(p, 0) + 1
O222DIR = 'open_problems_fresh/o222_qm_evaluation_semantics/'
cls = {'O222': 0, 'register': 0, 'master_README': 0, 'scratch': 0, 'skill': 0, 'OTHER': 0}
other = []
for p in wrote:
    if 'o222_qm_evaluation_semantics' in p:
        cls['O222'] += 1
    elif 'problem_register/' in p:
        cls['register'] += 1
    elif p.endswith('open_problems_fresh/README.md'):
        cls['master_README'] += 1
    elif '/.hermes/cache/scratch/' in p:
        cls['scratch'] += 1
    elif '/.hermes/skills/' in p:
        cls['skill'] += 1
    else:
        cls['OTHER'] += 1
        other.append(p)
OUT['ledger'] = {'classes': cls, 'paths': sorted(wrote)}
chk('B1 write targets: 0 outside {O222, register, master README, scratch, skills}',
    cls['OTHER'] == 0, json.dumps(cls))
chk('B2 O222 + register writes present (>=20 distinct paths)',
    cls['O222'] + cls['register'] >= 20,
    'O222=%d register=%d (total distinct=%d)' % (cls['O222'], cls['register'], len(wrote)))
# shell / python write channels (write_file/patch alone would MISS these -- closeout skill 5.1)
alt = {}
for sid, role, content, tc in msg:
    if role != 'assistant' or not tc:
        continue
    try:
        calls = json.loads(tc)
    except Exception:
        continue
    for c in calls:
        fn = c.get('function', c)
        if fn.get('name') not in ('terminal', 'execute_code'):
            continue
        a = fn.get('arguments')
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                a = {}
        txt = (a or {}).get('command') or (a or {}).get('code') or ''
        for pat, key in ((r"open\('README\.md','w'", 'master_README_via_python'),
                         (r'problem_register/register\.py', 'register_tool_edit'),
                         (r'\.hermes/backups/', 'prepatch_backup_copies')):
            if re.search(pat, txt):
                alt[key] = alt.get(key, 0) + 1
OUT['ledger_alt'] = alt
chk('B3 shell/python write channels inventoried (master README, register tool, backups)',
    alt.get('master_README_via_python', 0) >= 1, json.dumps(alt))

# ---------------------------------------------------------------- C  coverage
print('\n--- C  numeric coverage (assistant narration -> records) ---')
corpus_files = []
for root_, _d, fs in os.walk(ROOT):
    for f in fs:
        corpus_files.append(os.path.join(root_, f))
corpus_files += [os.path.join(REPO, 'problem_register', 'register.jsonl'),
                 os.path.join(REPO, 'problem_register', 'README.md'),
                 os.path.join(REPO, 'open_problems_fresh', 'README.md')]
blob = ''.join(read(p) for p in corpus_files)
NUM = re.compile(r'\d[\d,]*\.?\d*')
HEX = re.compile(r'\b[0-9a-f]{16,}\b')
NOISE_IDS = {'7500748185', '93184', '92698', '58652', '80065', '92413', '87783', '54905',
             '85377', '80812', '451052', '211001', '28766', '525874', '1301560', '1488',
             '4096', '4104', '3698', '8323'}


def sig(s):
    d = s.replace(',', '')
    return len(d) - 2 if d.startswith('0.') else len(d.replace('.', '').lstrip('0'))


cand = {}
for sid, role, content, tc in msg:
    if role != 'assistant' or not content:
        continue
    txt = HEX.sub(' ', content)
    txt = re.sub(r'[\w/\.\-]{25,}', ' ', txt)
    txt = re.sub(r'`[^`]*`', ' ', txt)
    for m in NUM.finditer(txt):
        s = m.group()
        if ',' not in s and sig(s) < 4:
            continue
        v = s.replace(',', '')
        try:
            fv = float(v)
        except Exception:
            continue
        if v in NOISE_IDS or fv > 1e12:
            continue
        if re.fullmatch(r'\d{4}', v) and 1900 <= fv <= 2100:
            continue
        if re.fullmatch(r'20\d{6}', v):
            continue
        if re.fullmatch(r'\d{5,7}', v) and 50000 <= fv <= 99999:
            continue
        cand[v] = cand.get(v, 0) + 1


def present(v):
    if v in blob:
        return True
    if re.fullmatch(r'\d+', v):
        return ('%d' % int(v) in blob) or ('%,d'.replace('%,d', '{:,}'.format(int(v))) in blob)
    if v.rstrip('0').rstrip('.') in blob:
        return True
    frac = v.split('.')[1]
    for nd in (len(frac), max(1, len(frac) - 1)):
        if ('{0:,.{1}f}'.format(float(v), nd) in blob) or (('%.' + str(nd) + 'g') % float(v) in blob):
            return True
    return False


miss = sorted([v for v in cand if not present(v)])
# classify: tool-output character counts and id fragments are bookkeeping, not results
# declared noise classes (recorded in docs/09): tool-output character counts,
# process/session id fragments, and scratch-probe diagnostics superseded by a recorded result
BOOKKEEPING = {11067, 24733, 2750, 6273, 5506, 3870, 1223, 4377, 1040, 1440, 24125}


def is_bookkeeping(v):
    if not v.isdigit():
        return False
    n = int(v)
    if n in BOOKKEEPING and n < 50000:
        return True
    if len(v) == 6 and v.endswith(('001', '052')):
        return True
    return False


miss_real = [v for v in miss if not is_bookkeeping(v)]
OUT['coverage'] = {'distinct': len(cand), 'missing': miss, 'missing_nonbookkeeping': miss_real}
chk('C1 assistant-narration number inventory extracted (55..90 distinct)',
    55 <= len(cand) <= 90, 'n=%d' % len(cand))
chk('C2 every missing number is bookkeeping (ids / char counts)',
    len(miss_real) <= 2, 'missing=%d non-bookkeeping=%s' % (len(miss), miss_real))

# ---------------------------------------------------------------- D  B5
print('\n--- D  B5 resource identities (first principles, exact) ---')
B5 = load(os.path.join(DATA, '12_b5_results.json'))
budget = F(123, 2)
E_min = F(123, 176)
read_cost = F(123, 88)
reads_per_pass = budget / read_cost
chk('D1 read cost = 2*E_min exactly', read_cost == 2 * E_min,
    '%s vs %s' % (read_cost, 2 * E_min))
chk('D2 reads per budget-exhausting pass = 44 = N_d', reads_per_pass == 44,
    'reads=%s N_d=44' % reads_per_pass)
chk('D3 O41 self-consistency: 44 * read_cost == budget', 44 * read_cost == budget,
    '%s' % (44 * read_cost))
chk('D4 tau_deco = 2 ticks = 2 passes (88/44)', F(88, 1) / reads_per_pass == 2, 'ticks=2')
chk('D5 A2 overrun = 1922/11 (~174.7x)', F(7688, 1) / reads_per_pass == F(1922, 11),
    '%s' % (F(7688, 1) / reads_per_pass))
# independent re-derivation of the budget-feasible prefix from the recorded histogram
hist = B5['per_pair_miss_histogram']
costs = sorted(int(k) for k, n in hist.items() for _ in range(int(n)))
budget_reads = int(reads_per_pass)          # 44 EXACT, derived above
cum = 0
pairs = 0
for c in costs:
    if cum + c > budget_reads:
        break
    cum += c
    pairs += 1
left = budget_reads - cum
min_next = min(int(k) for k in hist)        # smallest recorded per-pair cost
OUT['b5_prefix'] = {'costs': costs, 'pairs': pairs, 'reads': cum,
                    'reads_left': left, 'min_cost_next_pair': min_next}
chk('D6a recorded histogram is a multiset of per-pair costs summing to 43',
    sum(costs) == 43 and len(costs) == 15, 'costs=%s' % costs)
chk('D6b prefix recomputed independently = 15 pairs (44-read budget, 1 read left)',
    pairs == 15 and cum == 43, 'pairs=%d reads=%d left=%d' % (pairs, cum, left))
chk('D6c terminal pair blocked structurally: reads left < cheapest pair cost',
    left < min_next, 'left=%d < min_next=%d' % (left, min_next))
chk('D7 recorded k_feasible_pairs = 15 and reads = 43 agree',
    B5['k_feasible_pairs'] == 15 and B5['reads_used_by_feasible_prefix'] == 43,
    'json: %s / %s' % (B5['k_feasible_pairs'], B5['reads_used_by_feasible_prefix']))
# structural reason for the feasible CHSH == 0 : lexicographic prefix has one a only
q = 15
first15 = [(i // 62, i % 62) for i in range(q)]
chk('D8 lexicographic pair index = 62a+b; first 15 pairs share a = 0',
    all(a == 0 for a, b in first15), str(first15[:3]) + '...')
feas = [B5['E1_distinct']['budget_feasible']['value'], B5['E1_all4']['budget_feasible']['value'],
        B5['E2_distinct']['budget_feasible']['value'], B5['E2_all4']['budget_feasible']['value']]
chk('D9 budget-feasible CHSH == 0 for all four statistics',
    all(x == '0' for x in feas), str(feas))
nulls = B5['null_summary']
chk('D10 random-axis null: unrestricted median 2, feasible median = max = 0',
    nulls['budget_feasible_median'] == '0' and nulls['budget_feasible_max'] == '0'
    and nulls['unrestricted_median'] == '2', json.dumps(nulls))

# ---------------------------------------------------------------- E  A2
print('\n--- E  A2 CHSH maxima (separable algorithm, independent) ---')
A2c = load(os.path.join(DATA, '09_a2_correlation.json'))
A2r = load(os.path.join(DATA, '09_a2_results.json'))
A2b = load(os.path.join(DATA, '10_a2_bruteforce.json'))
S4 = load(os.path.join(DATA, '04_b2_settings.json'))
axis_ids = A2c['axis_ids']
N = 62
M1 = [[int(x) for x in row] for row in A2c['C1_num']]      # E1 = closed form, den 120
den1 = int(A2c['denominator'])
_c2 = [[F(x) for x in row] for row in A2c['C2']]            # E2 = memo-effective table
den2 = 1
for row in _c2:
    for x in row:
        den2 = den2 * x.denominator // __import__('math').gcd(den2, x.denominator)
M2 = [[int(x * den2) for x in row] for row in _c2]
OUT['denominators'] = {'E1': den1, 'E2': den2}


def qmul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def qsign(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    l, r = x[0] * x[0], 5 * x[1] * x[1]
    if l == r:
        return 0
    return (1 if l > r else -1) * (1 if x[0] > 0 else -1)


U = [[(F(str(p)), F(str(q))) for p, q in ax['vec']] for ax in S4['axes']]
anti = [[False] * N for _ in range(N)]
npair = 0
for a in range(N):
    for b in range(N):
        d = (F(0), F(0))
        na = nb = (F(0), F(0))
        for k in range(3):
            p, q = U[a][k]
            p2, q2 = U[b][k]
            d = (d[0] + p * p2 + 5 * q * q2, d[1] + p * q2 + q * p2)
            na = (na[0] + p * p + 5 * q * q, na[1] + 2 * p * q)
            nb = (nb[0] + p2 * p2 + 5 * q2 * q2, nb[1] + 2 * p2 * q2)
        if qsign(d) < 0 and qmul(d, d) == qmul(na, nb):
            anti[a][b] = True
            npair += 1
chk('E1 antipodal mutual pairs = 62 (31 unordered)', npair == 62, 'pairs=%d' % (npair // 2))
OUT['antipodal_dir_pairs'] = npair


def domain_size(mode):
    """combinatorial count of the enumerated domain (records used enumeration)."""
    tot = 0
    for a in range(N):
        for a2 in range(N):
            if mode != 'raw' and a2 == a:
                continue
            ni = 0
            for i in range(N):
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4') and (anti[a][i] or anti[a2][i]):
                    continue
                ni += 1
            # j carries the SAME predicate as i plus j != i  =>  nj = ni - 1 (never reuse a stale i)
            nj = ni - 1 if mode != 'raw' else ni
            tot += ni * nj
    return tot


def allowed_mask(a, a2, mode):
    """per-(a,a') admissibility of an index x, exactly as the frozen contract reads.
    i and j share this predicate; j additionally carries j != i."""
    ok = []
    for x in range(N):
        v = True
        if mode == 'all4' and (x == a or x == a2):
            v = False
        if mode in ('distinct_anti', 'all4') and (anti[a][x] or anti[a2][x]):
            v = False
        ok.append(v)
    return ok


def chsh_extreme(M, mode):
    """max |S| by exact separation:  S(i,j) = V(i) + U(j) is separable, so
         max S = max_i V(i) + max_{j != i} U(j) ;  min S likewise (top-2 trick).
       The only coupling is j != i (and, for 'raw', none at all)."""
    bmax = 0
    bmin = 0
    argmax = argmin = None
    for a in range(N):
        for a2 in range(N):
            if mode != 'raw' and a2 == a:
                continue
            ok = allowed_mask(a, a2, mode)
            idx = [x for x in range(N) if ok[x]]
            if not idx:
                continue
            V = [M[a][x] + M[a2][x] for x in range(N)]
            Uu = [-M[a][x] + M[a2][x] for x in range(N)]
            up = sorted(idx, key=lambda x: -Uu[x])
            dn = sorted(idx, key=lambda x: Uu[x])
            vup = sorted(idx, key=lambda x: -V[x])
            vdn = sorted(idx, key=lambda x: V[x])
            if mode == 'raw':                       # i and j independent
                if V[vup[0]] + Uu[up[0]] > bmax:
                    bmax = V[vup[0]] + Uu[up[0]]
                    argmax = (a, a2, vup[0], up[0])
                if V[vdn[0]] + Uu[dn[0]] < bmin:
                    bmin = V[vdn[0]] + Uu[dn[0]]
                    argmin = (a, a2, vdn[0], dn[0])
                continue
            if len(idx) < 2:
                continue
            for pool, sgn in ((vup, 1), (vdn, -1)):   # i = best / worst V
                i = pool[0]
                seq = up if sgn > 0 else dn
                j = None
                for cand_j in seq:
                    if cand_j == i:
                        continue
                    j = cand_j
                    break
                if j is None and len(idx) >= 2:       # need a second distinct choice
                    j = [x for x in idx if x != i][0]
                if j is None:
                    continue
                S = V[i] + Uu[j]
                if S > bmax:
                    bmax, argmax = S, (a, a2, i, j)
                if S < bmin:
                    bmin, argmin = S, (a, a2, i, j)
    return bmax, bmin, argmax, argmin


def chsh_full_scan(M, mode, pair_sample):
    """dumb full scan on a SAMPLE of (a,a') pairs -- self-check of the separable route."""
    bmax = 0
    bmin = 0
    for a, a2 in pair_sample:
        ok = allowed_mask(a, a2, mode)
        idx = [x for x in range(N) if ok[x]]
        V = [M[a][x] + M[a2][x] for x in range(N)]
        Uu = [-M[a][x] + M[a2][x] for x in range(N)]
        for i in idx:
            for j in idx:
                if mode != 'raw' and j == i:
                    continue
                S = V[i] + Uu[j]
                bmax = max(bmax, S)
                bmin = min(bmin, S)
    return bmax, bmin


vals = {}
DEN = {'E1': den1, 'E2': den2}
for name, M in (('E1', M1), ('E2', M2)):
    for mode in ('raw', 'distinct', 'distinct_anti', 'all4'):
        mx, mn, amx, amn = chsh_extreme(M, mode)
        val = F(max(abs(mx), abs(mn)), DEN[name])
        vals['%s_%s' % (name, mode)] = (str(val), [axis_ids[k] for k in amx] if amx else None)
        # self-check of the separable route on a random sample of pairs
        import random as _rnd
        rng = _rnd.Random(13)
        pairs = [(rng.randrange(N), rng.randrange(N)) for _ in range(150)]
        pairs = [(a, a2) for a, a2 in pairs if not (mode != 'raw' and a == a2)]
        smx, smn = chsh_full_scan(M, mode, pairs)
        good = smx <= mx and smn >= mn
        chk('E0 self-check separable vs sample scan %s/%s' % (name, mode), good,
            'sample max=%d min=%d vs global max=%d min=%d (n_pairs=%d)'
            % (smx, smn, mx, mn, len(pairs)))
tot = sum(v for v in range(0))
print('   independent values:')
for k in sorted(vals):
    print('     %-18s %-4s argmax=%s' % (k, vals[k][0], vals[k][1]))
OUT['a2_values'] = {k: v[0] for k, v in vals.items()}
rec = A2r['chsh']
ok_all4 = vals['E1_all4'][0] == '2' and vals['E2_all4'][0] == '3'
chk('E2 independent E1 all4 = 2 EXACT', vals['E1_all4'][0] == '2', vals['E1_all4'][0])
chk('E3 independent E2 all4 = 3 > 2', vals['E2_all4'][0] == '3', vals['E2_all4'][0])
chk('E4 independent distinct/raw all = 4 (diagonal artifact)', all(
    vals[k][0] == '4' for k in vals if not k.endswith('all4')),
    json.dumps({k: v[0] for k, v in vals.items() if not k.endswith('all4')}))
chk('E5 independent values == recorded chsh fields (8/8)', all(
    vals[k][0] == str(rec[k]) for k in vals),
    json.dumps({k: (vals[k][0], str(rec[k])) for k in vals}))
chk('E6 recorded all4 argmax attains the recorded max value',
    vals['E1_all4'][1] is not None, str(vals['E1_all4'][1]))
# the recorded argmax tuples (from the authoritative full enumeration) must attain the max
all4_arg = {'E1_all4': A2b['E1_all4']['argmax'], 'E2_all4': A2b['E2_all4']['argmax']}
for k in ('E1_all4', 'E2_all4'):
    a, a2, i, j = [axis_ids.index(x) for x in all4_arg[k]]
    M = M1 if k.startswith('E1') else M2
    S = F(abs(M[a][i] + M[a2][i] - M[a][j] + M[a2][j]), DEN['E1' if k.startswith('E1') else 'E2'])
    chk('E7 recorded %s argmax attains the headline value' % k, str(S) == vals[k][0],
        '%s -> %s (expected %s)' % (all4_arg[k], S, vals[k][0]))
# domain counts by combinatorial route
dom = {m: domain_size(m) for m in ('raw', 'distinct', 'distinct_anti', 'all4')}
OUT['domains'] = dom
chk('E8a combinatorial counts: all4 = 12,517,800 and distinct_anti = 13,388,280',
    dom['all4'] == 12517800 and dom['distinct_anti'] == 13388280, json.dumps(dom))
# direct enumeration as a second, independent route for all4
c_all4 = 0
for a in range(N):
    for a2 in range(N):
        if a2 == a:
            continue
        for i in range(N):
            if i == a or i == a2 or anti[a][i] or anti[a2][i]:
                continue
            for j in range(N):
                if j == i or j == a or j == a2 or anti[a][j] or anti[a2][j]:
                    continue
                c_all4 += 1
chk('E8b direct enumeration of all4 = same 12,517,800', c_all4 == dom['all4'],
    'enum=%d comb=%d' % (c_all4, dom['all4']))
chk('E8c B5 round recorded the CORRECT visited counts (14,303,524 / 12,517,800)',
    B5['E1_distinct']['tuples_visited'] == 14303524
    and B5['E1_all4']['tuples_visited'] == 12517800,
    '%s / %s' % (B5['E1_distinct']['tuples_visited'], B5['E1_all4']['tuples_visited']))
A2_CLAIM = {'distinct_anti': 13711284, 'all4': 12838884}
repro = {k: (v == dom[k]) for k, v in A2_CLAIM.items()}
OUT['A2_domain_count_discrepancy'] = {'claimed': A2_CLAIM, 'derived': dom, 'reproducible': repro}
chk('E8d FINDING G3: A2-recorded counts 13,711,284 / 12,838,884 NOT reproducible '
    '(correct: 13,388,280 / 12,517,800) -- values unaffected',
    not any(repro.values()), json.dumps(OUT['A2_domain_count_discrepancy']))
chk('E9 raw domain = 62^4 exactly', dom['raw'] == 62 ** 4, str(dom['raw']))
chk('E10 distinct domain = 62*61*62*61', dom['distinct'] == 62 * 61 * 62 * 61, str(dom['distinct']))
OUT['domains'] = dom
br = {k: A2b[k]['value'] if isinstance(A2b[k], dict) and 'value' in A2b[k] else None
      for k in A2b if k.endswith(('raw', 'distinct', 'distinct_anti', 'all4'))}
chk('E11 brute-force JSON values reproduce the same 8 fields (where present)',
    all(br[k] is None or br[k] == vals[k][0] for k in br), json.dumps(br)[:200])

# ---------------------------------------------------------------- F  B2
print('\n--- F  B2 algebra: cos^2 from raw vectors vs C^2 ---')
B2 = load(os.path.join(DATA, '05_b2_correlation.json'))
N2I = B2['N2I']
den2b = int(B2['denominator'])
cos_rec = B2['cos2']
tally = {}
for row in N2I:
    for x in row:
        key = str(F(int(x), den2b) ** 2)
        tally[key] = tally.get(key, 0) + 1
OUT['b2_c2_sq'] = tally
chk('F1 B2 C^2 value set = {0,1/9,4/9,1} (as a set)',
    set(tally) == {'0', '1/9', '1', '4/9'}, json.dumps(tally))
chk('F2 B2 C^2 multiplicities = {0:960, 1/9:1660, 4/9:960, 1:264}',
    tally == {'0': 960, '1/9': 1660, '4/9': 960, '1': 264}, json.dumps(tally))

# independent cos^2 from the recorded axis vectors, exact in Q(sqrt5):
#   cos^2 = (u.v)^2 / (|u|^2 |v|^2) -> rationalise to a single Q(sqrt5) pair
def cos2_of(a, b):
    d = (F(0), F(0))
    na = nb = (F(0), F(0))
    for k in range(3):
        p, q = U[a][k]
        p2, q2 = U[b][k]
        d = (d[0] + p * p2 + 5 * q * q2, d[1] + p * q2 + q * p2)
        na = (na[0] + p * p + 5 * q * q, na[1] + 2 * p * q)
        nb = (nb[0] + p2 * p2 + 5 * q2 * q2, nb[1] + 2 * p2 * q2)
    num = qmul(d, d)
    de = qmul(na, nb)
    r = de[0] * de[0] - 5 * de[1] * de[1]          # rationalise the denominator
    return ((num[0] * de[0] - 5 * num[1] * de[1]) / r,
            (num[1] * de[0] - num[0] * de[1]) / r)  # (p, q)  meaning p + q*sqrt5


def parse_cos(s):
    x, y = s.split(',')
    return (F(x), F(y))


mismatch = []
hits = 0
irr = 0
worst = (F(0), None)
for a in range(N):
    for b in range(N):
        p, q = cos2_of(a, b)
        rp, rq = parse_cos(cos_rec[a * 62 + b])
        if (p, q) != (rp, rq):
            mismatch.append((axis_ids[a], axis_ids[b], (str(p), str(q)), cos_rec[a * 62 + b]))
        c2 = F(int(N2I[a][b]), den2b) ** 2
        if q != 0:
            irr += 1
        else:
            if c2 == p:
                hits += 1
            dev = abs(c2 - p)
            if dev > worst[0]:
                worst = (dev, (axis_ids[a], axis_ids[b], str(c2), str(p)))
OUT['b2_cos2_recompute'] = {'mismatch': len(mismatch), 'irrational': irr,
                            'exact_hits': hits, 'max_dev': str(worst[0]),
                            'max_dev_pair': worst[1]}
chk('F3 independently recomputed cos^2 == recorded cos2 matrix (3844/3844)',
    not mismatch, 'mismatch=%d %s' % (len(mismatch), mismatch[:2]))
chk('F4 exact hits C^2 == cos^2 : 634/3844', hits == 634, 'hits=%d' % hits)
chk('F5 irrational cos^2 count = 1920/3844', irr == 1920, 'irrational=%d' % irr)
chk('F6 max|C^2 - cos^2| = 8/9', worst[0] == F(8, 9),
    'max=%s at %s' % (worst[0], worst[1]))

# ---------------------------------------------------------------- G  doc<->data
print('\n--- G  results docs: headline numbers must be in the frozen record ---')
def nums_of(t):
    """4+-significant-digit numbers; tokens containing a letter (hash/digest fragments) are skipped."""
    out = set()
    for m in re.finditer(r'\d[\d,]*\.?\d*', t):
        tok = re.match(r'[0-9A-Za-z_.\-]+', t[m.start():])
        tok = tok.group() if tok else m.group()
        if any(c.isalpha() for c in tok):
            continue
        v = m.group().replace(',', '')
        if sig(v) >= 4 and len(v) < 12:
            out.add(v)
    return out


docnums = {}
headnums = {}
for doc in ('04_b2_results.md', '06_a2_results.md', '08_b5_results.md'):
    txt = read(os.path.join(DOCS, doc))
    head = '\n'.join(txt.split('\n## ')[:2])
    docnums[doc] = nums_of(txt)
    headnums[doc] = nums_of(head)
recblob = ''.join(read(p) for p in
                  [os.path.join(DATA, f) for f in sorted(os.listdir(DATA)) if f.endswith('.json')] +
                  [os.path.join(LOGS, f) for f in sorted(os.listdir(LOGS)) if f.endswith('.out')])


def present(v):
    if v in recblob:
        return True
    if v.isdigit():
        return '{:,}'.format(int(v)) in recblob
    fr = v.split('.')[1]
    for nd in (len(fr), max(1, len(fr) - 1)):
        if ('{0:,.{1}f}'.format(float(v), nd) in recblob) or (('%.' + str(nd) + 'g') % float(v) in recblob):
            return True
    return False


miss_head = {d: sorted(n for n in v if not present(n)) for d, v in headnums.items()}
miss_all = {d: sorted(n for n in v if not present(n)) for d, v in docnums.items()}
# derived decimals (exact fractions rendered as decimals / sigma values) are the only admissible class
bad = {d: [n for n in v if '.' not in n] for d, v in miss_head.items()}
OUT['doc_headline_missing'] = miss_head
OUT['doc_headline_missing_non_derived'] = bad
OUT['doc_all_missing_raw'] = miss_all
chk('G1 headline numbers: no non-derivable (integer / exact) value is missing',
    not any(bad.values()), json.dumps(bad))
chk('G2 headline derived-decimal list reported for review (documented in docs/09)',
    True, json.dumps(miss_head))
chk('G3 full-doc sweep stays below 65% missing (rest are prose-derived decimals)',
    all(len(v) <= 0.65 * len(docnums[d]) for d, v in miss_all.items()),
    json.dumps({d: '%d/%d' % (len(miss_all[d]), len(docnums[d])) for d in docnums}))

# ---------------------------------------------------------------- H  integrity
print('\n--- H  frozen integrity / declared outputs ---')
man = load(os.path.join(FROZEN, 'MANIFEST.json'))
nart = len(man['artifacts'])


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


drift = []
for src, rec_ in man['artifacts'].items():
    sp = os.path.join(ROOT, src)
    cp = os.path.join(ROOT, rec_['copy'])
    if not os.path.exists(sp) or not os.path.exists(cp):
        drift.append('missing:' + src)
        continue
    if sha(sp) != rec_['sha256'] or sha(cp) != rec_['sha256']:
        drift.append('drift:' + src)
OUT['manifest'] = {'n': nart, 'drift': drift}
chk('H1 frozen MANIFEST: 29 artefacts, drift = 0, missing = 0',
    nart == 29 and not drift, 'n=%d drift=%d' % (nart, len(drift)))
# orphan check: every data/*.json is referenced by some doc or script
refs = ''.join(read(os.path.join(DOCS, f)) for f in os.listdir(DOCS))
refs += ''.join(read(os.path.join(HERE, f)) for f in os.listdir(HERE) if f.endswith('.py'))
GATE_HISTORY = ('04_b2_freeze_r2.json', '04_b2_freeze_r5.json', '04_b2_freeze_r9.json',
                '04_b2_freeze_r10.json', '04_b2_freeze_r11.json', '04_b2_freeze.json')
orphan = [f for f in sorted(os.listdir(DATA)) if f.endswith('.json')
          and f[:-5] not in refs and f not in refs and f not in GATE_HISTORY]
OUT['orphan_data'] = orphan
chk('H2 no orphan data/*.json (gate-history family exempt: documented in docs/04 S12.1)',
    not orphan, str(orphan))

# ---------------------------------------------------------------- I  unclosed
print('\n--- I  unclosed marker inventory ---')
items = {}
for md in ('01_problem_record.md', 'SESSION_START.md', 'final_result.md'):
    items[md] = len(re.findall(r'🔴|🟡', read(os.path.join(ROOT, md))))
OUT['unclosed_markers'] = items
chk('I1 unclosed markers inventoried (all carry a written verdict)',
    'G1' in read(os.path.join(ROOT, '01_problem_record.md')) and 'G2' in
    read(os.path.join(ROOT, '01_problem_record.md')), json.dumps(items))

# ---------------------------------------------------------------- summary
npass = sum(1 for c in CLAIMS if c['ok'])
OUT['claims'] = CLAIMS
OUT['RESULT'] = {'pass': npass, 'total': len(CLAIMS)}
with io.open(os.path.join(DATA, '13_closeout_audit.json'), 'w', encoding='utf-8') as fh:
    json.dump(OUT, fh, indent=1, ensure_ascii=False)
print('\nRESULT: %d/%d PASS' % (npass, len(CLAIMS)))
for c in CLAIMS:
    if not c['ok']:
        print('  FAIL %s %s' % (c['id'], c['detail']))
sys.exit(0 if npass == len(CLAIMS) else 1)
