#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDERL 模型演示脚本
用于展示训练好的PDERL模型在不同环境中的表现
"""

import os
import argparse
import subprocess
from pathlib import Path

def find_model_files(base_dir='.'):
    """查找可用的模型文件"""
    model_files = []
    base_path = Path(base_dir)
    
    # 查找所有.pkl文件
    for pkl_file in base_path.rglob('*.pkl'):
        if 'evo_net' in pkl_file.name or 'actor' in pkl_file.name:
            model_files.append(str(pkl_file))
    
    return model_files

def run_demo(env_name, model_path, render=True, trials=1, seed=7):
    """运行模型演示"""
    cmd = [
        'python', 'play_pderl.py',
        '-env', env_name,
        '-model_path', model_path,
        '-seed', str(seed)
    ]
    
    if render:
        cmd.append('-render')
    
    print(f"🎮 运行演示: {env_name}")
    print(f"📁 模型路径: {model_path}")
    print(f"🎲 随机种子: {seed}")
    print(f"🖥️ 渲染: {'是' if render else '否'}")
    print("-" * 50)
    
    try:
        # 运行多次试验
        total_reward = 0
        for trial in range(trials):
            print(f"\n🔄 试验 {trial + 1}/{trials}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='.')
            
            if result.returncode == 0:
                # 从输出中提取奖励值
                output_text = result.stdout.decode('utf-8') if isinstance(result.stdout, bytes) else result.stdout
                output_lines = output_text.strip().split('\n')
                for line in output_lines:
                    if 'Reward:' in line:
                        reward = float(line.split('Reward:')[1].strip())
                        total_reward += reward
                        print(f"✅ 奖励: {reward:.2f}")
                        break
            else:
                error_text = result.stderr.decode('utf-8') if isinstance(result.stderr, bytes) else result.stderr
                print(f"❌ 错误: {error_text}")
                return None
        
        avg_reward = total_reward / trials if trials > 0 else 0
        print(f"\n📊 平均奖励 ({trials} 次试验): {avg_reward:.2f}")
        return avg_reward
        
    except Exception as e:
        print(f"❌ 运行演示时出错: {e}")
        return None

def interactive_demo():
    """交互式演示模式"""
    print("🎯 PDERL 模型演示工具")
    print("=" * 50)
    
    # 查找可用的模型文件
    model_files = find_model_files()
    
    if not model_files:
        print("❌ 未找到模型文件！")
        print("请先运行训练生成模型文件，或检查以下目录:")
        print("  - demo_test/evo_net.pkl")
        print("  - results/*/evo_net.pkl")
        print("  - */models/*.pkl")
        return
    
    print(f"📁 发现 {len(model_files)} 个模型文件:")
    for i, model_file in enumerate(model_files):
        print(f"  {i+1}. {model_file}")
    
    try:
        choice = int(input("\n请选择模型文件 (输入数字): ")) - 1
        if 0 <= choice < len(model_files):
            selected_model = model_files[choice]
        else:
            print("❌ 无效选择")
            return
    except (ValueError, KeyboardInterrupt):
        print("\n👋 退出")
        return
    
    # 选择环境
    environments = [
        'Hopper-v2',
        'Walker2d-v2', 
        'HalfCheetah-v2',
        'Ant-v2',
        'Swimmer-v2',
        'Reacher-v2'
    ]
    
    print("\n🌍 可用环境:")
    for i, env in enumerate(environments):
        print(f"  {i+1}. {env}")
    
    try:
        env_choice = int(input("\n请选择环境 (输入数字): ")) - 1
        if 0 <= env_choice < len(environments):
            selected_env = environments[env_choice]
        else:
            print("❌ 无效选择")
            return
    except (ValueError, KeyboardInterrupt):
        print("\n👋 退出")
        return
    
    # 其他选项
    try:
        render = input("\n🖥️ 是否渲染? (y/n, 默认y): ").lower().strip()
        render = render != 'n'
        
        trials = input("🔄 试验次数 (默认1): ").strip()
        trials = int(trials) if trials else 1
        
        seed = input("🎲 随机种子 (默认7): ").strip()
        seed = int(seed) if seed else 7
        
    except (ValueError, KeyboardInterrupt):
        print("\n👋 退出")
        return
    
    # 运行演示
    print("\n🚀 开始演示...")
    avg_reward = run_demo(selected_env, selected_model, render, trials, seed)
    
    if avg_reward is not None:
        print(f"\n🎉 演示完成！平均奖励: {avg_reward:.2f}")
    else:
        print("\n❌ 演示失败")

def batch_demo():
    """批量演示模式"""
    print("🔄 批量演示模式")
    print("=" * 50)
    
    # 查找可用的模型文件
    model_files = find_model_files()
    
    if not model_files:
        print("❌ 未找到模型文件！")
        return
    
    # 测试环境列表
    test_environments = ['Hopper-v2', 'Walker2d-v2', 'HalfCheetah-v2']
    
    results = {}
    
    for model_file in model_files:
        print(f"\n📁 测试模型: {model_file}")
        model_results = {}
        
        for env in test_environments:
            print(f"\n🌍 环境: {env}")
            avg_reward = run_demo(env, model_file, render=False, trials=3, seed=7)
            model_results[env] = avg_reward
        
        results[model_file] = model_results
    
    # 打印汇总结果
    print("\n" + "=" * 80)
    print("📊 批量演示结果汇总")
    print("=" * 80)
    
    for model_file, model_results in results.items():
        print(f"\n📁 模型: {Path(model_file).name}")
        for env, reward in model_results.items():
            if reward is not None:
                print(f"  🌍 {env:<15}: {reward:>8.2f}")
            else:
                print(f"  🌍 {env:<15}: {'失败':>8}")

def main():
    parser = argparse.ArgumentParser(description='PDERL 模型演示工具')
    parser.add_argument('-env', help='环境名称', type=str)
    parser.add_argument('-model', help='模型文件路径', type=str)
    parser.add_argument('-trials', help='试验次数', type=int, default=1)
    parser.add_argument('-seed', help='随机种子', type=int, default=7)
    parser.add_argument('-no_render', help='不渲染', action='store_true')
    parser.add_argument('-batch', help='批量测试模式', action='store_true')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_demo()
    elif args.env and args.model:
        # 命令行模式
        render = not args.no_render
        avg_reward = run_demo(args.env, args.model, render, args.trials, args.seed)
        if avg_reward is not None:
            print(f"\n🎉 演示完成！平均奖励: {avg_reward:.2f}")
    else:
        # 交互式模式
        interactive_demo()

if __name__ == '__main__':
    main()