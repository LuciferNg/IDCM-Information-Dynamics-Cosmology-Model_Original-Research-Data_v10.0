#!/bin/bash
# round-4 close-out chain: determinism (D1-D3) -> re-aggregate -> addendum -> audit
cd /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer || exit 9
P=/usr/bin/python3
$P scripts/11_determinism.py > logs/11_determinism.out 2>&1; echo "exit=$?" >> logs/11_determinism.out
$P scripts/12_n4_global.py --aggregate > logs/12_n4_global.out 2>&1; echo "exit=$?" >> logs/12_n4_global.out
$P scripts/13_party_window.py > logs/13_party_window.out 2>&1; echo "exit=$?" >> logs/13_party_window.out
$P scripts/07_audit.py > logs/07_audit.out 2>&1; echo "exit=$?" >> logs/07_audit.out
echo "CHAIN DONE"
grep -hE "^RESULT" logs/11_determinism.out logs/12_n4_global.out logs/13_party_window.out logs/07_audit.out
