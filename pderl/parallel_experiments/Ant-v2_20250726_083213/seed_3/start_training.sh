#!/bin/bash
cd "/workspace/TERL-comparative/pderl"
export PYTHONUNBUFFERED=1
exec python run_pderl.py -env Ant-v2 -seed 3 -logdir parallel_experiments/Ant-v2_20250726_083213/seed_3 -use_tensorboard
