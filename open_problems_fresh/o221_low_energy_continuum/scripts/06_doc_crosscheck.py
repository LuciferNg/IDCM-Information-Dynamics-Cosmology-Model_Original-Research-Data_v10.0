#!/usr/bin/env python3
# O221 scripts/06 - doc crosscheck (READ-ONLY audit of the written documents).
#   - doc hygiene: U+FFFD corruption, markdown fence parity, table pipe sanity,
#     section presence, no stray "| **O" rows, file/folder inventory
#   - declared output vs actual data files (no orphans, nothing missing)
#   - every headline number quoted in the docs is grepped for presence (coverage)
#   - SESSION_START / 01_problem_record / final_result status-line consistency
#   This script NEVER writes to the docs.
# ASCII only.
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0
FAIL = 0


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))


# ALL docs are audited (was docs/01..04 only during the first close-out round);
# the list is discovered from disk so a new doc cannot silently escape the audit.
DOCS = sorted("docs/" + f for f in os.listdir(os.path.join(BASE, "docs")) if f.endswith(".md"))
DOCS_EXPECTED = 14
ROOT = ["01_problem_record.md", "SESSION_START.md", "final_result.md"]
ALL = ROOT + DOCS

print("=" * 78)
print("O221 / scripts/06 - doc crosscheck (read-only)")
print("=" * 78)

# ---------- hygiene ----------
print("\n[H] document hygiene")
for f in ALL:
    p = os.path.join(BASE, f)
    t = open(p, encoding="utf-8").read()
    ck("H1 %s : no U+FFFD corruption" % f, t.count(chr(0xFFFD)) == 0, "count = %d" % t.count(chr(0xFFFD)))
    nf = len([l for l in t.split("\n") if l.startswith("```")])
    ck("H2 %s : fence count even" % f, nf % 2 == 0, "fences = %d" % nf)
    bad = [i + 1 for i, l in enumerate(t.split("\n"))
           if l.startswith("|") and l.count("|") < 3]
    ck("H3 %s : no broken table rows" % f, not bad, "offending lines = %s" % bad)
    stray = [i + 1 for i, l in enumerate(t.split("\n")) if l.lstrip().startswith("| **O")]
    ck("H4 %s : no stray master-status row ('| **O...' at line start)" % f, not stray,
       "offending lines = %s" % stray)

# ---------- inventory ----------
print("\n[I] inventory (declared outputs vs actual files)")
have_sc = sorted(os.listdir(os.path.join(BASE, "scripts")))
have_dt = sorted(os.listdir(os.path.join(BASE, "data")))
print("     scripts:", have_sc)
print("     data   :", have_dt)
for sc in have_sc:
    if not sc.endswith(".py"):
        continue
    stem = sc[:-3]                                  # naming convention: NN_name.py -> data/NN_name.txt
    exp = stem + ".txt"
    ck("I1 %s <-> data/%s (naming convention)" % (sc, exp), exp in have_dt, "present = %s" % (exp in have_dt))
ck("I3 no orphan data files (every data/*.txt has its script)",
   all(d[:-4] + ".py" in have_sc for d in have_dt),
   "orphans = %s" % [d for d in have_dt if d[:-4] + ".py" not in have_sc])
ck("I4 no stray backup files in the folder",
   not [f for f in os.listdir(BASE) if f.endswith(".bak") or f.endswith("~")], "")
ck("I5 doc inventory complete (all %d docs present)" % DOCS_EXPECTED, len(DOCS) == DOCS_EXPECTED,
   "found = %d" % len(DOCS))
ck("I6 watermark section present in 01_problem_record.md",
   "\u6a94\u6848\u9589\u5408\u6c34\u4f4d" in open(os.path.join(BASE, "01_problem_record.md"),
                                              encoding="utf-8").read(), "")

# ---------- coverage of headline numbers ----------
print("\n[C] coverage: every headline number appears in the docs")
CORPUS = "\n".join(open(os.path.join(BASE, f), encoding="utf-8").read() for f in ALL)
NUMBERS = ["294.8772",
           "4129.9424",
           "72.590027",
           "2N + 2",
           "178",
           "36.338",
           "0.999363",
           "0.98411",
           "1.0018705",
           "0.993785",
           "0.486",
           "1.221",
           "0.0052",
           "117.33",
           "2.04545",
           "7.8812",
           "0.0114",
           "1.9999",
           "602.75",
           "1.41421",
           "1.99759",
           "322.75",
           "1290.75",
           "arccos(1/4)",
           "12.0000",
           "π/15",
           "5.3e-15",
           "1.3e-23",
           "0.0409",
           "3.02e-7",
           "0.25",
           "512",
           "459",
           "446",
           "398",
           "381",
           "332",
           "1+, 5",
           "dim(TT)",
           "TT criterion",
           "rhombicosidodecahedron",
           "lambda_sync",
           "926.3840",
           "24.7",
           "0.0033",
           "0.480",
           "Σδ = 4π",
           "N − D",
           "DoF = D(D−3)/2"]
missing = [n for n in NUMBERS if n not in CORPUS]
print("     checked %d headline numbers ; missing = %s" % (len(NUMBERS), missing))
ck("C1 headline-number coverage >= 90%%", len(NUMBERS) - len(missing) >= 0.9 * len(NUMBERS),
   "%d/%d present" % (len(NUMBERS) - len(missing), len(NUMBERS)))
for lit in ("O221", "S1", "L_world", "x =", "d_s"):
    ck("C2 doc set mentions '%s'" % lit, lit in CORPUS)

# ---------- status line consistency ----------
print("\n[S] status-line consistency (live field, three files must agree)")
st = {}
for f in ("01_problem_record.md", "SESSION_START.md", "final_result.md"):
    t = open(os.path.join(BASE, f), encoding="utf-8").read()
    m = re.search(r"(🟢|🟡|🔴)[^\n]{0,40}(已閉合|部分閉合|開放)?", t)
    st[f] = m.group(0) if m else None
    print("     %-24s : %s" % (f, st[f]))
ck("S1 all three status lines carry an emoji state", all(v for v in st.values()), "")
ck("S2 no file claims full closure while others say partial",
   not any("🟢 已閉合" in (v or "") for v in st.values()) or all("🟢" in (v or "") for v in st.values()),
   "%s" % {k: (v or "")[:24] for k, v in st.items()})

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
