#!/usr/bin/env python3
"""O222/B2 frozen-round ARTIFACT INTEGRITY tool.

Not part of the frozen contract: this never writes inside logs/, data/05_*, data/06_*, scripts/04_*, scripts/05_*.
It only (a) verifies canonical frozen artifacts against data/frozen/MANIFEST.json and
(b) if a canonical artifact was clobbered by a stale background writer, restores it byte-exactly
from its immutable copy (after verifying the copy itself).

Usage:  python3 scripts/07_artifact_integrity.py            # verify only, exit 1 on drift
        python3 scripts/07_artifact_integrity.py --restore  # verify + restore from copies
"""
import hashlib, io, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, 'data', 'frozen', 'MANIFEST.json')

def sha(rel):
    with open(os.path.join(ROOT, rel), 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()

def main():
    argv = sys.argv[1:]
    restore = '--restore' in argv
    with io.open(MAN, encoding='utf-8') as fh:
        man = json.load(fh)
    bad, restored, missing = [], [], []
    for rel, rec in man['artifacts'].items():
        want = rec['sha256']
        if not os.path.exists(os.path.join(ROOT, rel)):
            missing.append(rel); continue
        got = sha(rel)
        if got == want:
            print('OK    %-42s %s  mtime %s' % (rel, got[:16],
                  time.strftime('%H:%M:%S', time.localtime(os.stat(os.path.join(ROOT, rel)).st_mtime))))
            continue
        bad.append((rel, got, want))
        print('DRIFT %-42s %s != %s' % (rel, got[:16], want[:16]))
        copy = rec.get('copy')
        if restore and copy and os.path.exists(os.path.join(ROOT, copy)):
            if sha(copy) == want:
                with open(os.path.join(ROOT, copy), 'rb') as s, open(os.path.join(ROOT, rel), 'wb') as d:
                    d.write(s.read())
                ok = sha(rel) == want
                restored.append(rel)
                print('      restored from %s -> %s' % (copy, 'byte-exact OK' if ok else 'FAILED'))
            else:
                print('      copy hash mismatch, NOT restoring from %s' % copy)
    print('\nmissing=%d drift=%d restored=%d  (manifest round: %s)' % (len(missing), len(bad), len(restored), man.get('round')))
    writers = os.popen("pgrep -af 'scripts/0[456][a-z_]*\\.py|tee logs' | grep -v pgrep | grep -v 07_artifact").read().strip()
    print('live writers:', writers or 'NONE')
    return 1 if (missing or bad) and not restore else 0

if __name__ == '__main__':
    sys.exit(main())
