#!/bin/bash
# round-4 sharded runner: 12 shards over the party-1 ordered pair index
cd /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer || exit 9
mkdir -p logs
for k in $(seq 0 11); do
  /usr/bin/python3 scripts/12_n4_global.py --shard "$k" 12 > "logs/12_shard_$(printf '%02d' "$k").out" 2>&1 &
done
wait
echo "ALL SHARDS DONE exit=$?"
for k in $(seq 0 11); do tail -1 "logs/12_shard_$(printf '%02d' "$k").out"; done
