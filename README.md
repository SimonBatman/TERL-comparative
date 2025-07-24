# TERL Comparative Study

这是一个关于进化强化学习(Evolutionary Reinforcement Learning)算法的比较研究项目。

## 项目结构

```
TERL-comparative/
├── ERL/                    # ERL (Evolutionary Reinforcement Learning) 实现
├── PDERL/                  # PDERL (Proximal Distilled ERL) 实现  
├── results/                # 实验结果和分析
└── README.md              # 项目说明文档
```

## 算法介绍

### ERL (Evolutionary Reinforcement Learning)
ERL是一种结合了进化算法和强化学习的混合方法，通过进化算法优化策略网络的参数，同时使用强化学习进行策略梯度更新。

### PDERL (Proximal Distilled ERL)
PDERL是ERL的改进版本，引入了：
- 近邻变异(Proximal Mutation)
- 知识蒸馏(Knowledge Distillation) 
- TensorBoard可视化支持
- 并行训练能力

## 快速开始

### ERL
```bash
cd ERL
python run_erl.py --env Hopper-v2
```

### PDERL
```bash
cd PDERL
python run_pderl.py --env Hopper-v2 --use_tensorboard
```

## 实验环境

推荐使用以下环境：
- Python 3.7+
- PyTorch 1.8+
- OpenAI Gym
- MuJoCo

详细的环境配置请参考各子项目的README文件。

## 结果分析

实验结果和性能比较分析请查看 `results/` 目录。

## 贡献

欢迎提交Issue和Pull Request来改进这个比较研究项目。

## 许可证

MIT License
