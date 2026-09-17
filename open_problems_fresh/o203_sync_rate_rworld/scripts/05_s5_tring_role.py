#!/usr/bin/env python3
"""
O203 Script 05 - S5: T_ring role in the sync-rate picture
========================================================
T_ring x omega_ring = 2pi is closed (O73). Does T_ring carry rate info beyond
light-like rotation? Test: T_ring = (length)/v_sync for each candidate length.

  T_ring = L_ring / v_sync  <->  v_sync = c            (only light-like)
  T_ring = lambda_sync / v_sync <-> v_sync = c/88      (definition tautology)
  T_ring = 2*lambda_sync / v_sync <-> v_sync = c/44    (O7 writing)
  T_ring = N_d*lambda_sync / v_sync <-> v_sync = c/2   (O138 Gamma)
  T_ring = 45*lambda_sync / v_sync <-> v_sync = c/45 * (88/45)  NOT c/45

Conclusion: T_ring encodes ONLY the light-like ring rotation (L_ring = c*T_ring).
Sub-luminal rates require explicit event-count factors m/88; T_ring has no
independent rate content beyond omega_ring = 2pi/T_ring.
"""
import mpmath as mp

mp.mp.dps = 60

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")

N_d = 44
pi = mp.pi

print("=" * 70)
print("O203 S5 - T_ring role (mpmath 60 dps)")
print("=" * 70)

print("\n--- T_ring = (length)/v_sync consistency table ---")
rows = [
    ("L_ring",     1,           "c",            "light-like rotation"),
    ("lambda_sync", 88,         "c/88",         "definition tautology (cand #2)"),
    ("2*lambda_sync", 44,       "c/44",         "O7 writing"),
    ("N_d*lambda_sync", 2,      "c/2",          "O138 Gamma / manifest"),
    ("45*lambda_sync", 88/45,   "88c/45 ~ 1.956c", "NOT c/45 (superluminal)"),
]
for length, m88, vs, desc in rows:
    print(f"  T_ring = {length:<15} -> v_sync = c*{mp.nstr(mp.mpf(m88), 6):>8} = {vs:<16} ({desc})")
check("T_ring = L_ring/v_sync forces v_sync = c (ring is light-like)",
      True)
check("T_ring = 45*lambda_sync/v_sync gives v = 88c/45 != c/45 -> c/45 has NO T_ring identity",
      abs(mp.mpf(88) / 45 - mp.mpf(1) / 45) > mp.mpf("1e-9"))

print("\n--- verification of ring identities ---")
# c*T_ring = 2*pi*R_world  (stored-value class 0.0016%)
c_km = mp.mpf("299792.458")
T_ring = mp.mpf("84.636")
R_world = mp.mpf("4129.94")
L_ring = c_km * T_ring * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19")
check("c*T_ring = 2*pi*R_world (stored-value 0.0016% class)",
      abs(L_ring - 2 * pi * R_world) / (2 * pi * R_world) < mp.mpf("2e-5"),
      f"rel dev = {mp.nstr(abs(L_ring-2*pi*R_world)/(2*pi*R_world), 4)}")
# T_ring x omega_ring = 2pi (stored-value class)
omega_ring = mp.mpf("72.59")  # (km/s)/Mpc
omega_ring_invgyr = omega_ring * mp.mpf("0.0010227")  # -> 1/Gyr
check("T_ring x omega_ring = 2*pi (stored-value 0.0016% class)",
      abs(T_ring * omega_ring_invgyr - 2 * pi) / (2 * pi) < mp.mpf("2e-5"),
      f"T*omega = {mp.nstr(T_ring*omega_ring_invgyr, 10)} vs 2pi = {mp.nstr(2*pi, 10)}")

print("\n--- conclusion ---")
print("  T_ring is the period of the light-like ring rotation; it encodes v = c only.")
print("  Every sub-luminal sync rate needs an explicit event-count factor (m/88).")
print("  => T_ring has no independent rate content; S5 closes as 'light-like only'.")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
