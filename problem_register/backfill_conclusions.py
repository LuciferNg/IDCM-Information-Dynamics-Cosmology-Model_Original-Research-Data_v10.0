#!/usr/bin/env python3
"""backfill_conclusions.py — 由 final_result.md `## 結論` 段回填 conclusion event

特性：
  - idempotent：concl_hash 已存在 ⟹ skip（重跑安全）
  - 只讀 final_result，不改任何 md
  - verdict 由 register state 推斷（closed→closed / partial→partial / 其他 None）
  - refs = final_result.md 本身；origin = O 目錄

用法：
  /usr/bin/python3 problem_register/backfill_conclusions.py [--dry-run] [--limit N]
"""
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OPF = os.path.join(REPO, "open_problems_fresh")

spec = importlib.util.spec_from_file_location("regmod", os.path.join(HERE, "register.py"))
reg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reg)
reg.REPO = REPO

CONC_RE = re.compile(r"^##\s*結論\s*\n(.*?)(?=\n##\s|\Z)", re.S | re.M)
VERDICT = {"closed": "closed", "partial": "partial", "negative": "negative", "falsified": "falsified"}


def extract(path):
    t = open(path, encoding="utf-8").read()
    m = CONC_RE.search(t)
    body = m.group(1) if m else None
    if not body:
        parts = [x.strip() for x in re.split(r"\n\s*\n", t) if x.strip()]
        body = next((x for x in parts if not x.startswith("#")), None)
    if not body:
        return ""
    body = re.sub(r"[*_`>\[\]]", "", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body[:1800]          # note 上限保護（保持 < NOTE_HARD）


def main():
    dry = "--dry-run" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    con = reg.connect()
    state = {r[0]: r[1] for r in con.execute("SELECT pid, state FROM o_problem").fetchall()}
    existing = {r[0] for r in con.execute(
        "SELECT concl_hash FROM event WHERE kind='conclusion' AND concl_hash IS NOT NULL").fetchall()}

    added = skipped = empty = 0
    for fp in sorted(glob.glob(os.path.join(OPF, "o*", "final_result.md"))):
        d = os.path.dirname(fp)
        m = re.match(r"^o(\d+)_", os.path.basename(d))
        if not m:
            continue
        pid = "O%d" % int(m.group(1))
        claim = extract(fp)
        if not claim:
            empty += 1
            continue
        cid = reg.concl_id(claim)
        if cid in existing:
            skipped += 1
            continue
        if limit is not None and added >= limit:
            break
        rel = os.path.relpath(fp, REPO)
        if dry:
            print("[dry] %s %s %s" % (pid, cid, claim[:70]))
        else:
            reg.record(con, "conclusion", pid, verdict=VERDICT.get(state.get(pid)),
                       title=claim, pids=json.dumps([pid], ensure_ascii=False),
                       refs=json.dumps([rel], ensure_ascii=False), concl_hash=cid,
                       supersedes="[]", version="v10.0", origin=os.path.relpath(d, REPO),
                       note=claim)
        existing.add(cid)
        added += 1

    print("backfill: added %d / skipped(existing) %d / empty %d" % (added, skipped, empty))
    return 0


if __name__ == "__main__":
    sys.exit(main())
