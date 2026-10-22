#!/usr/bin/env python3
"""O224 scratch/chain_audit.py -- mechanical audit of the SCRIPT CHAIN: which script produces which
artefact, whether every artefact has a producer, and whether every script has a consumer/product.

Read-only: parses sources with ast, resolves the directory constants (HERE/ROOT/DATA/LOGS/...), and
classifies each file path literal as READ or WRITE from the open() mode (plus np.savez/np.load and
shell redirections).  Prints a producer/consumer map and the orphan lists.
"""
import ast
import glob
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)


def resolve(node, consts):
    """Resolve an expression to a path string when possible, else None."""
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
                vals = [a.value if isinstance(a, ast.Constant) else 0 for a in node.right.elts]
                return base % tuple(vals)
            if isinstance(node.right, ast.Constant):
                return base % node.right.value
        except Exception:                                            # noqa: BLE001
            return base
        return base
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        l = resolve(node.left, consts)
        r = resolve(node.right, consts)
        return None if l is None or r is None else l + r
    if isinstance(node, ast.Call):
        nm = getattr(node.func, 'attr', None) or getattr(node.func, 'id', None)
        if nm == 'join':
            parts = [resolve(a, consts) for a in node.args]
            if all(p is not None for p in parts):
                return os.path.join(*parts)
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
    consts = {'HERE': os.path.join(ROOT, 'scripts'), 'ROOT': ROOT,
              'DATA': os.path.join(ROOT, 'data'), 'LOGS': os.path.join(ROOT, 'logs'),
              'FROZEN': os.path.join(ROOT, 'data', 'frozen'),
              'SCRATCH': os.path.join(ROOT, 'scratch')}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            v = resolve(n.value, consts)
            if v is not None:
                consts[n.targets[0].id] = v
    consts.setdefault('HERE', os.path.dirname(os.path.abspath(path)))
    reads, writes = set(), set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        nm = getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
        if nm in ('open',) and n.args:
            p = resolve(n.args[0], consts)
            mode = None
            if len(n.args) > 1:
                mode = n.args[1].value if isinstance(n.args[1], ast.Constant) else ''
            for kw in n.keywords:
                if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                    mode = kw.value.value
            if p and ('/' in p or p.endswith(('.json', '.out', '.npz'))):
                tgt = writes if (isinstance(mode, str) and ('w' in mode or 'a' in mode)) else reads
                tgt.add(p)
        elif nm in ('finish', 'emit', 'dump_json') and n.args:
            p = resolve(n.args[0], consts)
            if p and p.endswith('.json'):
                writes.add(p)
        elif nm == 'savez' and n.args:
            p = resolve(n.args[0], consts)
            if p:
                writes.add(p if p.endswith('.npz') else p + '.npz')
        elif nm == 'load' and n.args:
            p = resolve(n.args[0], consts)
            if p and p.endswith('.npz'):
                reads.add(p)
    return reads, writes


def rel(p):
    return os.path.relpath(p, ROOT) if os.path.isabs(p) else p


scripts = sorted(glob.glob('scripts/*.py')) + sorted(glob.glob('scratch/*.py'))
W = {}
R = {}
for f in scripts:
    try:
        rd, wr = scan(f)
    except Exception as exc:                                         # noqa: BLE001
        print('PARSE FAIL %s: %s' % (f, exc))
        continue
    for p in wr:
        W.setdefault(rel(p), set()).add(f)
    for p in rd:
        R.setdefault(rel(p), set()).add(f)

shells = sorted(glob.glob('scratch/*.sh')) + sorted(glob.glob('scripts/*.sh'))
for f in shells:
    src = io.open(f, encoding='utf-8').read()
    for m in re.finditer(r'>\s*([\w\./\-%]+\.(?:out|json|npz|sha256|log))', src):
        W.setdefault(m.group(1), set()).add(f)
    for m in re.finditer(r'(?<!>)(?:\s|=)((?:data|logs|scratch)/[\w\./\-%\[\]]+)', src):
        if m.group(1) not in W:
            R.setdefault(m.group(1), set()).add(f)

arts = sorted(set(os.path.relpath(p, ROOT) for p in glob.glob('data/**/*', recursive=True)
                  if os.path.isfile(p)) | set(os.path.relpath(p, ROOT)
                                              for p in glob.glob('logs/*') if os.path.isfile(p)))
print('=== PRODUCER MAP (artefact -> writing script)  [%d artefacts, %d scripts]'
      % (len(arts), len(scripts) + len(shells)))
orphan = []
for a in arts:
    if a in ('data/16_r5_manifest.sha256',):
        continue
    exact = W.get(a, set())
    pats = set()
    if not exact:
        for p, ss in W.items():
            if '%' in p:
                try:
                    if re.fullmatch(re.escape(p).replace('%02d', r'\d{2}').replace('%06d', r'\d{6}')
                                    .replace('%d', r'\d+').replace('%s', r'.+'), a):
                        pats |= ss
                except Exception:                                    # noqa: BLE001
                    pass
    who = exact | pats
    if not who:
        orphan.append(a)
    else:
        flag = '' if exact else ' (pattern)'
        print('  %-38s <- %s%s' % (a, ','.join(sorted(who)), flag))
print()
print('=== ORPHAN artefacts (no writer found in scripts/ scratch/)  [%d]' % len(orphan))
for a in sorted(orphan):
    print('  %s   [read by: %s]' % (a, ','.join(sorted(R.get(a, {'-'})))) )
print()
print('=== SCRIPTS with no artefact output (pure reader / library / launcher)')
for f in scripts + shells:
    outs = [p for p, ss in W.items() if f in ss]
    if not outs:
        print('  %-38s reads: %s' % (f, ','.join(sorted({p for p, ss in R.items() if f in ss}))[:80]))
print()
print('=== REVERSE: scripts reading a frozen/external input')
for f in scripts:
    ins = sorted(p for p, ss in R.items() if f in ss and ('frozen' in p or p.count('/') == 1))
    if ins:
        print('  %-38s <- %s' % (f, ', '.join(ins[:6])))
