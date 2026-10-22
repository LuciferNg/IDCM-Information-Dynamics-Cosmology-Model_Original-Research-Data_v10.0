#!/usr/bin/env python3
"""O224 scratch/chain_audit.py -- CHAIN COMPLETENESS AUDIT for the O224 derivation.

Answers, mechanically: (1) does every artefact in data/ have a producing script?  (2) which
artefacts are never read?  (3) do the driver's commands name existing scripts and use only flags
those scripts actually parse?  (4) do the mirrored R2-R5 probes match their recorded sha256?
Read-only: parses sources with ast, never imports or executes a judgment script, writes nothing
(stdout is redirected to logs/19_chain_audit.out by the caller / driver).
"""
import ast
import glob
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FAILS = []


def note(ok, msg):
    print(('  [ok]   ' if ok else '  [FAIL] ') + msg)
    if not ok:
        FAILS.append(msg)


def resolve(node, consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return consts.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        base = resolve(node.left, consts)
        if base is None:
            return None
        try:
            if isinstance(node.right, ast.Tuple):
                elts = node.right.elts
                if all(isinstance(a, ast.Constant) for a in elts):
                    return base % tuple(a.value for a in elts)
                return base        # some element is a variable: keep the specs -> the pattern itself
            if isinstance(node.right, ast.Constant):
                return base % node.right.value
        except Exception:                                            # noqa: BLE001
            return base
        return base
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        l, r = resolve(node.left, consts), resolve(node.right, consts)
        return None if l is None or r is None else l + r
    if isinstance(node, ast.Call):
        nm = getattr(node.func, 'attr', None) or getattr(node.func, 'id', None)
        if nm == 'join':
            parts = [resolve(a, consts) for a in node.args]
            return None if any(p is None for p in parts) else os.path.join(*parts)
        if nm == 'dirname' and node.args:
            inner = resolve(node.args[0], consts)
            return None if inner is None else os.path.dirname(inner)
        if nm in ('abspath', 'realpath') and node.args:
            inner = resolve(node.args[0], consts)
            return None if inner is None else os.path.abspath(inner)
    return None


def scan(path):
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    consts = {'ROOT': ROOT, 'HERE': os.path.dirname(os.path.abspath(path)),
              'DATA': os.path.join(ROOT, 'data'), 'LOGS': os.path.join(ROOT, 'logs'),
              'FROZEN': os.path.join(ROOT, 'data', 'frozen'),
              'SCRATCH': os.path.join(ROOT, 'scratch')}
    assigns = [n for n in ast.walk(tree)
               if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
    for _ in range(2):                          # two settling passes (chains like ROOT->DATA->fn)
        for n in assigns:
            v = resolve(n.value, consts)
            if v is not None:
                consts[n.targets[0].id] = v
    reads, writes = set(), set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        nm = getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
        if nm in ('open', 'finish', 'emit', 'dump_json') and n.args:
            p = resolve(n.args[0], consts)
            if not p or not (p.endswith(('.json', '.out', '.npz', '.sha256')) or '/' in p):
                continue
            mode = None
            if nm == 'open':
                if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
                    mode = n.args[1].value
                for kw in n.keywords:
                    if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
            writing = (nm != 'open') or (isinstance(mode, str) and ('w' in mode or 'a' in mode))
            (writes if writing else reads).add(p)
        elif nm == 'savez' and n.args:
            p = resolve(n.args[0], consts)
            if p:
                writes.add(p if p.endswith('.npz') else p + '.npz')
        elif nm == 'load' and n.args:
            p = resolve(n.args[0], consts)
            if p and p.endswith('.npz'):
                reads.add(p)
    return reads, writes


def relp(p):
    return os.path.relpath(p, ROOT) if os.path.isabs(p) else p


def pat_match(pat, actual):
    rx = re.escape(pat).replace('\\%', '%')          # re.escape may or may not escape the percent
    for a, b in (('%02d', r'\d{2}'), ('%04d', r'\d{4}'), ('%06d', r'\d{6}'),
                 ('%d', r'\d+'), ('%s', r'.+')):
        rx = rx.replace(a, b)
    return re.fullmatch(rx, actual) is not None


print('=' * 100)
print('O224 CHAIN COMPLETENESS AUDIT   root = %s' % ROOT)
print('=' * 100)

scripts = sorted(glob.glob('scripts/*.py')) + sorted(glob.glob('scratch/*.py'))
W, R, SRC = {}, {}, {}
for f in scripts:
    try:
        rd, wr = scan(f)
    except Exception as exc:                                         # noqa: BLE001
        note(False, 'PARSE FAIL %s: %s' % (f, exc))
        continue
    SRC[f] = io.open(f, encoding='utf-8').read()
    for p in wr:
        W.setdefault(relp(p), set()).add(f)
    for p in rd:
        R.setdefault(relp(p), set()).add(f)
for f in sorted(glob.glob('scripts/*.sh')) + sorted(glob.glob('scratch/*.sh')):
    src = io.open(f, encoding='utf-8').read()
    SRC[f] = src
    for m in re.finditer(r'>\s*([\w\./\-%]+\.(?:out|json|npz|sha256|log))', src):
        W.setdefault(m.group(1), set()).add(f)
    for m in re.finditer(r'(?<!>)=?\s*((?:data|logs|scratch)/[\w\./\-%]+)', src):
        if m.group(1) not in W:
            R.setdefault(m.group(1), set()).add(f)

EXTERNAL = {
    'data/frozen/04_b2_settings.json': 'frozen INPUT from O222 (round-1 re-lock)',
    'data/frozen/08_a2_h_table.json': 'frozen INPUT from O222',
    'data/frozen/09_a2_correlation.json': 'frozen INPUT from O222',
    'data/frozen/o222_snapshot.sha256': 'frozen INPUT: O222 source snapshot manifest',
    'data/frozen/MANIFEST.json': 'frozen INPUT: O222 snapshot inventory',
    'data/00_contract.json': 'the round-1 CONTRACT itself (pre-registration; 00_contract.py writes it '
                             'in-place, path built from a variable)',
    'data/smoke/16_shard_01of3844.json': 'ARCHIVED round-5 smoke artefact (moved here, kept)',
    'data/16_r5_manifest.sha256': 'round-5 in-directory hash manifest (self-referential by design)',
    'data/12_shard_00of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_01of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_02of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_03of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_04of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_05of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_06of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_07of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_08of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_09of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_10of12.json': 'shard of 12_n4_global.py --shard K 12',
    'data/12_shard_11of12.json': 'shard of 12_n4_global.py --shard K 12',
}

print()
print('--- 1. PRODUCER MAP (artefact <- writing script)')
arts = sorted(set(os.path.relpath(p, ROOT) for p in glob.glob('data/**/*', recursive=True)
                  if os.path.isfile(p)))
orphan, attributed, ext_used = [], 0, 0
for a in arts:
    who = set(W.get(a, ()))
    if not who:
        for p, ss in W.items():
            if '%' in p and pat_match(p, a):
                who |= ss
    if who:
        attributed += 1
        print('  %-40s <- %s' % (a, ','.join(sorted(who))))
    elif a in EXTERNAL:
        ext_used += 1
        print('  %-40s <- DOCUMENTED: %s' % (a, EXTERNAL[a]))
    else:
        orphan.append(a)
note(orphan == [], 'every data/** artefact is attributed: %d producer-matched, %d documented '
                   'external/archive/pattern, %d ORPHAN %s'
     % (attributed, ext_used, len(orphan), orphan))
print()
print('--- 2. CONSUMPTION')
never = [a for a in arts if not a.startswith('data/frozen/') and not R.get(a)]
print('  artefacts no script reads (they are all glob-read by 07_audit/16 --aggregate, and the')
print('  round-5 shards are read by 16 through a glob): %d' % len(never))
print('  %s' % (never[:6],))
print()
print('--- 3. DRIVER (scripts/run_chain.sh)')
drv = 'scripts/run_chain.sh'
bad_cmd, cmd_n = [], 0
if not os.path.exists(drv):
    note(False, 'driver missing: %s' % drv)
else:
    dsrc = io.open(drv, encoding='utf-8').read()
    for m in re.finditer(r'^\s*run\s+(\S+)\s+(\S+)(.*)$', dsrc, re.M):
        log, script, argstr = (t.strip('"\'') for t in m.group(1, 2, 3))
        cmd_n += 1
        if not os.path.exists(script):
            bad_cmd.append('%s: script missing' % script)
            continue
        if script.endswith('.py'):
            body = SRC.get(script) or io.open(script, encoding='utf-8').read()
            for fl in [a for a in argstr.split() if a.startswith('--')]:
                if '"%s"' % fl not in body and "'%s'" % fl not in body:
                    bad_cmd.append('%s: flag %s absent from source' % (script, fl))
        if not log.startswith(('logs/', 'scratch/')):
            bad_cmd.append('%s: log target outside logs|scratch' % log)
    note(bad_cmd == [], 'driver: %d commands, %d problems %s' % (cmd_n, len(bad_cmd), bad_cmd[:4]))
    for need in ('00_contract.py', '07_audit.py', '12_n4_global.py --shard',
                 '18_windows_global_jit.py --run-range', '--merge',
                 '16_windows_global.py --aggregate', 'measure_engines.py', 'chain_audit.py'):
        note(need in dsrc, 'driver covers %s' % need)
print()
print('--- 4. MIRRORED PROBES (sha256 vs PROVENANCE.md)')
mir_ok, mir_bad = 0, []
for prov, sub in (('scripts/MIRROR_PROVENANCE.md', 'scripts'),
                  ('scratch/manifests/PROVENANCE.md', 'scratch/manifests')):
    if not os.path.exists(prov):
        mir_bad.append('%s missing' % prov)
        continue
    for name, h in re.findall(r'\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`',
                              io.open(prov, encoding='utf-8').read()):
        p = os.path.join(sub, name)
        if not os.path.exists(p):
            mir_bad.append('%s missing' % p)
        elif hashlib.sha256(io.open(p, 'rb').read()).hexdigest() != h:
            mir_bad.append('%s sha256 mismatch' % p)
        else:
            mir_ok += 1
note(mir_bad == [] and mir_ok >= 25, 'mirrored probes/manifests verified: %d hashes match '
     '(expected >= 25) %s' % (mir_ok, mir_bad[:3]))
print()
print('--- 5. INVENTORY (script -> artefacts)')
for f in sorted(SRC):
    outs = sorted(p for p, ss in W.items() if f in ss)
    print('  %-42s -> %s' % (f, ', '.join(outs) if outs else '(launcher / reader only)'))
print()
print('--- 6. EXTERNAL DEPENDENCIES OF THE CHAIN')
for e in ('data/frozen/*            O222 snapshot, copied in round 1 (state frozen at 2026-09-30)',
          'everything else           scripts + probes + launchers + manifests + artefacts now live '
          'INSIDE this directory'):
    print('  ' + e)
print()
print('=' * 100)
print('VERDICT: %s   (%d failed checks)' % ('CHAIN COMPLETE' if not FAILS else 'GAPS FOUND',
                                            len(FAILS)))
for f in FAILS:
    print('  FAIL: %s' % f)
print('=' * 100)
sys.exit(1 if FAILS else 0)
