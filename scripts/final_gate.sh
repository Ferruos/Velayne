#!/bin/bash
set -e

source .venv/bin/activate

python -m velayne.scripts.final_gate

if [ $? -eq 0 ]; then
    echo "FINAL GATE PASSED"
else
    echo "FINAL GATE FAILED -- see logs/final_gate.json for details"
fi