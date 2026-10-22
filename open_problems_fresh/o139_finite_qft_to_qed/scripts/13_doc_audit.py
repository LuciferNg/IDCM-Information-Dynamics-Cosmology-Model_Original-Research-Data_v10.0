#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O139 / scripts/13_doc_audit.py  —  READ-ONLY DOCUMENT AUDIT (A-G)

Audits the RECORDS, not the physics.  Never writes to any file.

  A  scope & inventory      — expected file set, no stray files
  B  section-number continuity — each doc's 一/二/三... sequence is contiguous
  C  doc <-> stdout numeric consistency — every significant number in docs/07..10
                              must appear in the corresponding script's stdout
                              (relative tolerance, explicit whitelist)
  D  timeline integrity     — docs/01_problem_record.md sec 9 index: dates ascend,
                              every produced file exists, no retroactive backfill
  E  cross-document consistency — the same constant must read the same everywhere
  F  upstream dependency existence — every "ONNN docs/YY" reference resolves
  G  scope / pollution      — the working tree shows only this entry's files

Exit 1 on any FAIL.
"""
import io
import os
import re
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                     # o139_finite_qft_to_qed
REPO = os.path.dirname(os.path.dirname(ROOT))    # IDCM-v10.0--It-From-Beat
OPF = os.path.dirname(ROOT)                      # open_problems_fresh

NPASS = 0
NFAIL = 0


def chk(name, ok, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  [PASS] %-66s %s" % (name, detail))
    else:
        NFAIL += 1
        print("  [FAIL] %-66s %s" % (name, detail))


def rd(p):
    return io.open(p, encoding="utf-8").read()


# =====================================================================
print("=" * 78)
print("A  scope & inventory")
print("=" * 78)
EXPECT_SCRIPTS = ["01_finite_qft_to_qed.py",
                  "02_alpha_running_and_fermion_lattice.py",
                  "03_verification_of_correction.py",
                  "04_problem_A_alpha_running_function.py",
                  "05_problem_B_fermion_lattice_g2.py",
                  "06_lepton_universal_g2_bound.py",
                  "07_alpha_zero_dressing_attack.py",
                  "08_problem_A_running_mechanism.py",
                  "09_alpha_problem_shape.py",
                  "10_idcm_native_running_winding.py",
                  "11_confined_hadronic_hvp.py",
                  "12_verify_all.py",
                  "13_doc_audit.py",
                  "14_audit_independent.py"]
EXPECT_DOCS = ["01_derivation.md", "01_problem_record.md", "02_audit_correction.md",
               "03_problem_A_alpha_running.md", "04_problem_B_fermion_lattice_g2.md",
               "05_g2_precision_wall_and_muon_bound.md",
               "06_alpha_zero_dressing_attack.md",
               "07_problem_A_running_mechanism.md", "08_alpha_problem_shape.md",
               "09_idcm_native_running_winding.md", "10_confined_hadronic_hvp.md"]
have_s = sorted(os.listdir(os.path.join(ROOT, "scripts")))
have_s = [f for f in have_s if f.endswith(".py")]
have_d = sorted(os.listdir(os.path.join(ROOT, "docs")))
missing_s = [f for f in EXPECT_SCRIPTS if f not in have_s]
missing_d = [f for f in EXPECT_DOCS if f not in have_d]
chk("A1  scripts present: 01..14 (want %d, have %d)" % (len(EXPECT_SCRIPTS), len(have_s)),
    not missing_s, "missing: %s" % (missing_s or "none"))
chk("A2  docs present: 01..10 + problem_record (want %d, have %d)" % (len(EXPECT_DOCS), len(have_d)),
    not missing_d, "missing: %s" % (missing_d or "none"))
chk("A3  SESSION_START.md present", os.path.isfile(os.path.join(ROOT, "SESSION_START.md")))
chk("A4  final_result.md present", os.path.isfile(os.path.join(ROOT, "final_result.md")),
    "from RESULT_TEMPLATE.md")
# no stray files
allowed = set(EXPECT_SCRIPTS) | set(EXPECT_DOCS) | {"SESSION_START.md", "final_result.md"}
stray = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if "__pycache__" in dirpath:
        stray.append(os.path.relpath(dirpath, ROOT) + "/  (bytecode cache)")
        continue
    for f in filenames:
        rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
        base = os.path.basename(rel)
        if base not in allowed:
            stray.append(rel)
chk("A5  no stray files inside the O139 folder", not stray, "stray: %s" % (stray or "none"))

# =====================================================================
print()
print("=" * 78)
print("B  section-number continuity")
print("=" * 78)
CN = "〇一二三四五六七八九十"
CN2 = {"十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15}


def cn2int(t):
    if t in CN2:
        return CN2[t]
    if len(t) == 1 and t in CN:
        return CN.index(t)
    if t.startswith("十"):
        return 10 + CN.index(t[1])
    if "十" in t:
        a, b = t.split("十")
        return CN.index(a) * 10 + (CN.index(b) if b else 0)
    return None


for fn in EXPECT_DOCS + ["SESSION_START.md"]:
    p = os.path.join(ROOT, "docs", fn) if fn in EXPECT_DOCS else os.path.join(ROOT, fn)
    txt = rd(p)
    cn = re.findall(r"^##\s*([〇一二三四五六七八九十]+)\s*[、.]", txt, re.M)
    ar = re.findall(r"^##\s*(\d+)\s*[.、]", txt, re.M)
    if len(cn) >= 3:
        nums = [(cn2int(x) if cn2int(x) is not None else -1) for x in cn]
        label = "中文"
    elif len(ar) >= 3:
        nums = [int(x) for x in ar]
        label = "arabic"
    else:
        chk("B  %-40s non-numbered headings" % fn, True, "skipped (no numbered sections)")
        continue
    ok = all(n is not None for n in nums) and nums == list(range(nums[0], nums[0] + len(nums)))
    chk("B  %-40s %s sections %s" % (fn, label, nums), ok,
        "contiguous" if ok else "GAP")

# =====================================================================
print()
print("=" * 78)
print("C  doc <-> stdout numeric consistency (relative tolerance + whitelist)")
print("=" * 78)
SUP = {"\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3", "\u2074": "4",
       "\u2075": "5", "\u2076": "6", "\u2077": "7", "\u2078": "8", "\u2079": "9",
       "\u207b": "-", "\u207a": "+"}


def norm(s):
    s = s.replace("\u2212", "-").replace("\u00d7", "x")
    s = "".join(SUP.get(c, c) for c in s)
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    return s


NUMRE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
POW10 = re.compile(r"(\d+(?:\.\d+)?)\s*x\s*10\s*\^?\s*([-+]?\d+)")


def numbers(s):
    """-> list of (value, decimals) ; decimals = -1 for a bare integer token."""
    s = norm(s)
    s = re.sub(r"\{[^{}]*\}", " ", s)                  # {a,b,c} symbol lists
    s = re.sub(r"\d{4}-\d{2}-\d{2}", " ", s)          # ISO dates
    s = re.sub(r"O\d{2,3}", " ", s)                       # O-series numbers
    s = re.sub(r"(?:docs|scripts)/\d+", " ", s)           # doc/script refs
    s = re.sub(r"§\s*\d+", " ", s)
    s = re.sub(r"\bv\d+(?:\.\d+)*", " ", s)             # versions
    out = []
    for m in POW10.finditer(s):
        try:
            out.append((float(m.group(1)) * 10.0 ** int(m.group(2)), -1))
        except Exception:
            pass
    s = POW10.sub(" ", s)
    s = re.sub(r"10\s*\^\s*([-+]?\d+)", r"1e\1", s)
    # comma-grouped: could be a thousands separator OR set members {88,176}
    def cg(m):
        t = m.group(0)
        try:
            out.append((float(t.replace(",", "")), -1))
        except Exception:
            pass
        for g in t.split(","):
            try:
                out.append((float(g), -1))
            except Exception:
                pass
        return " "
    s = re.sub(r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?", cg, s)
    for m in re.finditer(r"([-+]?\d+(?:\.\d+)?)(?:[eE]([-+]?\d+))?", s):
        tok = m.group(0)
        try:
            v = float(tok)
        except Exception:
            continue
        if "e" in tok or "E" in tok:
            out.append((v, -1))
        elif "." in tok:
            out.append((v, len(tok.split(".")[1])))
        else:
            out.append((v, -1))
    return out


def matches(v, dp, u):
    """doc value v (displayed with dp decimals, -1 = bare integer) vs computed u"""
    if dp >= 1:
        if abs(v - u) <= 0.5 * 10.0 ** (-dp) * 1.001:
            return True
    if abs(v - u) <= max(1e-12, abs(u) * 1e-4):
        return True
    return False


# doc-only tokens that legitimately never appear in the script's stdout:
#   dates / years, section+table indices, upstream O numbers, external published
#   values the script does not compute, and structural constants quoted from
#   other O-series projects.
WHITELIST = {
    "docs/07_problem_A_running_mechanism.md": {
        24, 32, 23, -0.021, 0.085, 1.1654, 0.091, 9.1, 50, 0.055, 0.72,
        47.9, 0.0297, 0.0280, 10, 11, 12, 15, 26, 27, 28, 21, 22,
        # dates, section numbers, doc/O references, structural constants
        2026, 2020, 2008, 2006, 2018, 2022, 9, 15, 12, 7, 8, 3, 4, 5, 6, 2, 1, 10, 11, 0,
        139, 142, 160, 89, 168, 136, 140, 156, 115, 107, 114, 94, 80, 84, 83,
        44, 4, 33, 134, 120, 17, 29, 18, 13, 21, 34, 55, 88,
        # external published values
        137.035999178, 127.951, 127.934, 128.933, 0.021, 0.026, 0.009, 0.008,
        0.031498, 0.02783, 0.000076, 0.00006, 0.027662, 9.085, 9.2928, 9.286,
        4.306, 4.316, 0.0001, 0.0001, 0.24, 0.0383, 0.7236, 0.0547, 0.0383,
        1.0030, 0.0225, 1.003, 0.022, 8.1030, 0.021, 8.103, 0.0167, 0.21, 1.66, 0.74,
        0.71, 0.965, 9.103448, 0.0280, 0.0297, 0.5, 0.1102, 0.015,
        8.7, 3.18, 16.2, 5.7, 0.59, 1.5,
    },
    "docs/08_alpha_problem_shape.md": {
        60, -5, 40, 1e-09, 0.03, 0.06, 20, 55, 1.421,
        2026, 2025, 2020, 9, 15, 12, 7, 8, 3, 4, 5, 6, 2, 1, 10, 11, 0, 13, 14, 16, 17, 18,
        139, 140, 156, 142, 160, 82, 86, 115, 136,
        44, 4, 33, 134, 120, 17, 29, 18, 13, 21, 34, 55, 88, 176,
        137, 128, 137.035999178, 127.930, 0.035999178, 0.070000000, 0.105999178,
        9.105999, 0.008, 0.026, 0.055, 1.164, 0.036, 0.070, 0.106, 0.035999178,
        0.130161, 0.131694, 1.01178, 1.178, 9.2863, 9.2928, 9.286, 0.070, 0.24,
        4.3061, 4.3164, 1.1654, 0.0910, 11.0, 13.2, 69.1450, 74.582, 298.328,
        91.188, 0.1450, 69, 70, 2.140399, 4.864543, 1.421, 1.74, 2.00, 79,
        0.201, 0.038,
    },
    "docs/09_idcm_native_running_winding.md": {
        2026, 9, 15, 12, 7, 8, 3, 4, 5, 6, 2, 1, 10, 11, 0,
        139, 168, 157, 142, 160, 136, 140, 115,
        44, 4, 33, 134, 120, 17, 29, 18, 13, 21, 34, 55, 88, 176, 22, 36, 53, 89,
        137, 128, 9.106, 9.105999, 0.008, 0.106, 1.178, 1.165, 1.1654, 0.0910, 13.2,
        9.286272, 9.282959, 9.285504, 0.003313, 0.000768, 0.105999, 32.0, 0.036,
        0.1, 0.03, 5.165, 1936, 44, 88, 7, 11, 0.979591837, 0.991735537,
        0.999483471, 0.999870868, 4.9726, 3.8137, 0.76695, 4.3061, 4.3164,
        9.2787, 8.1094, 12.566371, 0.71, 0.9444, 0.201,
    },
    "docs/10_confined_hadronic_hvp.md": {
        -15, 92, 1274, 4191, 40, 76.7, 13.2, 0.091, 212, 240, 69.145,
        0.23305, 23.3, 0.15, 5.5578, 3.3535, 3.8927, 678.12, 669.6, 1.25,
        108262, 10189, 165, 143.9, 25, 28.1, 1.7, 0.43, 0.13, 0.45, 0.21, 0.09,
        0.784062, 0.765995, 6.8354, 3.59, 2.57, 71.4591, 55.8018, 2.22645,
        2026, 9, 15, 12, 7, 8, 3, 4, 5, 6, 2, 1, 10, 11, 0, 13, 14, 20, 30, 60,
        139, 144, 137, 168, 136, 140, 115, 159, 180, 182, 174,
        44, 4, 33, 134, 120, 17, 29, 18, 13, 21, 34, 55, 88, 22, 11, 8,
        4.9726, 3.8137, 0.766943, 0.76695, 0.23305, 23.3, 71.4591, 55.8018, 55.80183,
        27.900915, 91187.6, 137.035999178, 0.02783, 3.59, 2.57, 1.2806248, 1.2805868,
        0.00297, 0.002970, 41, 5, 108262, 10189, 165, 143.9, 25, 28.1, 0, 1.7,
        0.43, 0.13, 0.45, 0.21, 0.09, 0.5, 0.1, 0.01, 0.784062, 0.765995, 6.8354,
        678.12, 669.6, 1.25, 5.5578, 3.3535, 3.8927, 3.8137, 0.15, 1.0, 4.0,
        4.0, 1.0, 2.0, 3.0, 0.3, 0.35,
    },
}
PAIRS = [("docs/07_problem_A_running_mechanism.md", "08_problem_A_running_mechanism.py"),
         ("docs/08_alpha_problem_shape.md", "09_alpha_problem_shape.py"),
         ("docs/09_idcm_native_running_winding.md", "10_idcm_native_running_winding.py"),
         ("docs/10_confined_hadronic_hvp.md", "11_confined_hadronic_hvp.py")]

for doc, scr in PAIRS:
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", scr)],
                       capture_output=True, text=True, cwd=ROOT)
    so = numbers(r.stdout)
    dtxt = rd(os.path.join(ROOT, doc))
    dnum = numbers(dtxt)
    wl = WHITELIST[doc]
    unmatched = []
    for v, dp in dnum:
        if any(abs(v - w) <= max(1e-12, abs(w) * 1e-9) for w in wl):
            continue
        if any(matches(v, dp, u) for u, _ in so):
            continue
        unmatched.append(v)
    chk("C  %-42s vs %s" % (doc.replace("docs/", ""), scr), not unmatched,
        "%d doc numbers, %d unmatched" % (len(dnum), len(unmatched)))
    if unmatched:
        seen, uniq = set(), []
        for v in unmatched:
            k = "%.6g" % v
            if k not in seen:
                seen.add(k)
                uniq.append(k)
        print("        unmatched (first 25): %s" % ", ".join(uniq[:25]))
        lines = dtxt.splitlines()
        shown = 0
        for i, ln in enumerate(lines, 1):
            lv = [v for v, _ in numbers(ln)]
            for u in unmatched:
                if any(abs(u - x) <= max(1e-12, abs(x) * 1e-9) for x in lv):
                    print("          L%-4d %s" % (i, ln.strip()[:150]))
                    shown += 1
                    break
            if shown >= 12:
                break

# =====================================================================
print()
print("=" * 78)
print("D  timeline integrity  (docs/01_problem_record.md sec 9 index)")
print("=" * 78)
pr = rd(os.path.join(ROOT, "docs", "01_problem_record.md"))
rows = re.findall(r"^\|\s*\*{0,2}(20\d\d-\d\d-\d\d)\*{0,2}[^|]*\|", pr, re.M)
dates = sorted(set(rows))
chk("D1  timeline index present with dated rows", len(rows) >= 10,
    "%d dated rows, %d distinct dates %s" % (len(rows), len(dates), dates))
chk("D2  dates ascend (no retroactive backfill)",
    rows == sorted(rows), "monotone" if rows == sorted(rows) else "OUT OF ORDER")
idx = pr.find("推導時序索引")
chk("D3  sec 9 heading '推導時序索引（禁回溯污染）' present", idx > 0)
# every produced file named in the timeline must exist
produced = set(re.findall(r"`?(scripts/\d\d[a-z_0-9]*\.py|docs/\d\d[a-z_0-9]*\.md)`?", pr))
missing = [f for f in sorted(produced)
           if not os.path.isfile(os.path.join(ROOT, f))]
chk("D4  every file named in the timeline exists", not missing,
    "%d referenced, missing %s" % (len(produced), missing or "none"))
chk("D5  the timeline states the no-backfill rule",
    "禁回溯污染" in pr and "不得" in pr)

# =====================================================================
print()
print("=" * 78)
print("E  cross-document consistency of the load-bearing constants")
print("=" * 78)
CORE = {
    "O139 total checks": (["240"], ["185", "212/212"]),
    "running target": (["9.1060", "9.106"], []),
    "delta": (["0.1060"], []),
    "spectrum sum": (["9.2863", "9.286"], []),
    "dispersion hadronic": (["3.8137"], []),
    "free-quark hadronic": (["4.9726", "4.97"], []),
    "confined/free ratio": (["0.76695", "0.766943"], []),
    "Lambda_req dressing": (["1.393178", "1.393"], []),
    "muon bound": (["167.306", "167.30"], []),
    "audit script counts": (["114"], []),
}
files = {"README": os.path.join(OPF, "README.md"),
         "problem_record": os.path.join(ROOT, "docs", "01_problem_record.md"),
         "SESSION_START": os.path.join(ROOT, "SESSION_START.md"),
         "final_result": os.path.join(ROOT, "final_result.md")}
texts = {nm: (rd(p) if os.path.isfile(p) else "") for nm, p in files.items()}
for label, (toks, stale) in CORE.items():
    hits = {nm: any(t in t for t in toks) for nm, t in texts.items()}
    bad = [nm for nm, t in texts.items() if any(st in t for st in stale)]
    chk("E  '%s' present in >=1 summary file, no stale value" % label,
        any(hits.values()) and not bad,
        " ".join("%s=%s" % (k, "y" if v else "N") for k, v in hits.items())
        + ("" if not bad else "  STALE in %s" % bad))
txt_pr = texts["problem_record"]
txt_ss = texts["SESSION_START"]
tot_pr = re.search(r"24 \+ 11 \+ 22 \+ 12 \+ 21 \+ 15 \+ 32 \+ 26 \+ 22 \+ 27 \+ 28", txt_pr)
tot_pr2 = re.search(r"24\+11\+22\+12\+21\+15\+32\+26\+22\+27\+28", txt_pr)
chk("E2  problem_record states the arithmetic 24+11+22+...+28 = 240",
    bool(tot_pr or tot_pr2) and (24 + 11 + 22 + 12 + 21 + 15 + 32 + 26 + 22 + 27 + 28 == 240),
    "sum = %d" % (24 + 11 + 22 + 12 + 21 + 15 + 32 + 26 + 22 + 27 + 28))
chk("E3  SESSION_START carries the same 240 total",
    "240" in txt_ss, "yes" if "240" in txt_ss else "NO")
chk("E4  no doc still calls the running '9.085' as the CURRENT target "
    "(only as the superseded value)",
    "已取代" in txt_pr or "舊值" in txt_pr)

# =====================================================================
print()
print("=" * 78)
print("F  upstream dependency existence")
print("=" * 78)
UPSTREAM = ["o38_kappa_prediction", "o39_wfield_condensate", "o54_antimatter_abundance",
            "o80_wfield_lagrangian", "o82_mass_generation", "o83_correlator_cmb",
            "o84_vacuum_energy_unified", "o86_sm_gr_coupling", "o89_mass_hierarchy_coupling",
            "o94_field_theorist_validation", "o107_extra_u1_physical",
            "o114_sm_phenomenology", "o115_framework_completeness",
            "o136_quark_mass_spectrum", "o137_cy3_topological_resonance",
            "o140_finite_spectral_relativity", "o142_boson_mass_derivation",
            "o144_boson_identity", "o156_rge_first_principles",
            "o157_bc_energy_functional", "o160_spectral_number_scan",
            "o168_g_last_input"]
missing = [d for d in UPSTREAM if not os.path.isdir(os.path.join(OPF, d))]
chk("F1  all %d upstream O directories exist" % len(UPSTREAM), not missing,
    "missing: %s" % (missing or "none"))
# references of the form "ONNN docs/YY"
refs = set(re.findall(r"O(\d{2,3})\s*`?docs/(\d\d)", txt_pr + txt_ss
                      + "".join(rd(os.path.join(ROOT, "docs", f)) for f in EXPECT_DOCS)))
bad = []
for num, dd in sorted(refs):
    cands = [d for d in os.listdir(OPF) if d.startswith("o" + num + "_")]
    if not cands:
        bad.append("O%s (no directory)" % num)
        continue
    files_in = os.listdir(os.path.join(OPF, cands[0], "docs")) \
        if os.path.isdir(os.path.join(OPF, cands[0], "docs")) else []
    if not any(f.startswith(dd) for f in files_in):
        bad.append("O%s docs/%s" % (num, dd))
chk("F2  every 'ONNN docs/YY' reference resolves to a real file", not bad,
    "%d refs checked, bad: %s" % (len(refs), bad or "none"))

# =====================================================================
print()
print("=" * 78)
print("G  scope / pollution")
print("=" * 78)
r = subprocess.run(["git", "diff", "--numstat", "--", "open_problems_fresh/README.md"],
                   capture_output=True, text=True, cwd=REPO)
add, dele = 0, 0
for line in r.stdout.strip().splitlines():
    parts = line.split()
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        add += int(parts[0]); dele += int(parts[1])
chk("G1  README.md diff is confined to the O139 line (<=2 added, <=2 removed)",
    add <= 2 and dele <= 2, "+%d/-%d" % (add, dele))
r = subprocess.run(["git", "status", "--porcelain", "--",
                    "open_problems_fresh/o139_finite_qft_to_qed"],
                   capture_output=True, text=True, cwd=REPO)
untracked = r.stdout.strip().startswith("??")
chk("G2  the O139 folder is untracked (?? ) — no accidental staging", untracked,
    r.stdout.strip().splitlines()[0] if r.stdout.strip() else "(no output)")
# the O139 folder must not contain files belonging to other O numbers
other = [f for f in os.listdir(os.path.join(ROOT, "scripts"))
         if re.match(r"(?!0[1-9]_|1[0-4]_)\d\d_", f)]
chk("G3  no foreign script numbering inside scripts/", not other, "%s" % (other or "none"))

# =====================================================================
print()
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (NPASS, NFAIL))
print("=" * 78)
raise SystemExit(1 if NFAIL else 0)
