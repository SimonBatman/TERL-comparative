#!/bin/bash
cd "/workspace/TERL-comparative/pderl"
export PYTHONUNBUFFERED=1
exec python run_pderl.py -env HalfCheetah-v2 -seed 10 -logdir parallel_experiments/HalfCheetah-v2_standard_20250729_145817/seed_10 -proximal_mut -distil -use_tensorboard
