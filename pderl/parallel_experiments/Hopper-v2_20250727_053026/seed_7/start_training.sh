#!/bin/bash
cd "/workspace/TERL-comparative/pderl"
export PYTHONUNBUFFERED=1
exec python run_pderl.py -env Hopper-v2 -seed 7 -logdir parallel_experiments/Hopper-v2_20250727_053026/seed_7 -use_tensorboard
