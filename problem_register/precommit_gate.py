#!/usr/bin/env python3
"""precommit_gate.py — register 鏈完整性 gate（pre-commit hook 用）

檢查 3 項（只針對 register.jsonl；內容零修改）:
  1. APPEND-ONLY：HEAD 版本每一行必須係新版本嘅前綴（禁改舊 rec / 刪事件 / 後插）
  2. HASH CHAIN：每條 hash = sha256(rec 去 hash + "|" + prev_hash)[:16]；prev 必須接上條 hash
  3. SQLITE SYNC：event count + tail hash 與 jsonl 一致（sqlite 存在時）

逃生門：git commit --no-verify（歷史修復時明知會 fail）
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_REL = "problem_register/register.jsonl"


def chain_hash(rec, prev):
    blob = json.dumps({k: v for k, v in rec.items() if k != "hash"},
                      ensure_ascii=False, sort_keys=True) + "|" + (prev or "")
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def head_lines():
    r = subprocess.run(["git", "show", f"HEAD:{JSONL_REL}"],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        return None
    return r.stdout.splitlines()


def main():
    path = os.path.join(REPO, JSONL_REL)
    if not os.path.exists(path):
        print("[gate] register.jsonl 不存在 — skip")
        return 0

    cur = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    errs = []

    # 1) append-only
    old = head_lines()
    if old is not None:
        old = [l for l in old if l.strip()]
        if len(cur) < len(old):
            errs.append(f"APPEND-ONLY: events {len(old)} -> {len(cur)}（事件被刪）")
        else:
            for i in range(len(old)):
                if old[i].strip() != cur[i].strip():
                    errs.append(f"APPEND-ONLY: L{i+1} 內容被改（禁改舊 rec，只能 append）")
                    break

    # 2) hash chain
    prev = None
    for i, ln in enumerate(cur, 1):
        try:
            r = json.loads(ln)
        except Exception as e:
            errs.append(f"HASH: L{i} 壞 JSON: {e}")
            break
        if "hash" not in r:
            errs.append(f"HASH: L{i} 缺 hash（手動 append？）")
            continue
        if chain_hash(r, r.get("prev_hash")) != r["hash"]:
            errs.append(f"HASH: L{i} hash 重算不符（{r.get('pid')} {r.get('kind')}）")
        if prev is not None and r.get("prev_hash") != prev:
            errs.append(f"CHAIN: L{i} prev_hash 未接上條")
        prev = r["hash"]

    # 3) sqlite sync
    db = os.path.join(REPO, "problem_register/register.sqlite")
    if os.path.exists(db):
        try:
            import sqlite3
            con = sqlite3.connect(db)
            n = con.execute("SELECT COUNT(*) FROM event").fetchone()[0]
            tail = con.execute("SELECT hash FROM event ORDER BY id DESC LIMIT 1").fetchone()[0]
            if n != len(cur):
                errs.append(f"SQLITE: event {n} != jsonl {len(cur)}（跑 register.py mirror）")
            if cur and tail != json.loads(cur[-1]).get("hash"):
                errs.append("SQLITE: tail hash 不同步（跑 register.py mirror）")
        except Exception as e:
            errs.append(f"SQLITE: {e}")

    # 4) drift gate（2026-10-24）：agent 改 docs/改名/刪目錄後常見 drift
    #    只擋 HARD DRIFT > 0；逃生 REGISTER_GATE_ALLOW_DRIFT=1
    if os.environ.get("REGISTER_GATE_ALLOW_DRIFT") != "1":
        r = subprocess.run([sys.executable, os.path.join(REPO, "problem_register/register.py"), "check"],
                           capture_output=True, text=True, cwd=REPO)
        m = None
        for line in r.stdout.splitlines():
            if line.startswith("HARD DRIFT:"):
                try:
                    m = int(line.split(":")[1].strip())
                except ValueError:
                    pass
        if m:
            kinds = [l.strip() for l in r.stdout.splitlines() if l.startswith("[") and not l.strip().endswith("] 0")]
            errs.append(f"DRIFT: HARD DRIFT {m} — {', '.join(kinds[:6])}（先 register.py check 修，或 REGISTER_GATE_ALLOW_DRIFT=1）")

    if errs:
        print("\n[register gate] 鏈完整性檢查 FAIL:")
        for e in errs[:12]:
            print("  -", e)
        if len(errs) > 12:
            print(f"  ... +{len(errs)-12} more")
        print("\n修復：register.py check；必要時 --no-verify（並記錄原因）")
        return 1

    print(f"[register gate] OK — {len(cur)} events, chain clean, sqlite synced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
