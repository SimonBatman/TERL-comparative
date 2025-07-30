#!/bin/bash
cd "/workspace/TERL-comparative/pderl"
export PYTHONUNBUFFERED=1
exec python run_pderl.py -env Ant-v2 -seed 10 -logdir parallel_experiments/Ant-v2_20250728_101954/seed_10 -use_tensorboard
