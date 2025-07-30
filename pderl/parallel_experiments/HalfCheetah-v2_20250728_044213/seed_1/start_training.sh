#!/bin/bash
cd "/workspace/TERL-comparative/pderl"
export PYTHONUNBUFFERED=1
exec python run_pderl.py -env HalfCheetah-v2 -seed 1 -logdir parallel_experiments/HalfCheetah-v2_20250728_044213/seed_1 -use_tensorboard
