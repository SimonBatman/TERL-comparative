#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDERL训练结果可视化脚本
用于分析和可视化CSV格式的训练数据
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_csv_data(file_path):
    """加载CSV数据"""
    try:
        data = pd.read_csv(file_path, header=None, names=['x', 'y'])
        return data
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return None

def plot_training_curves(result_dir, save_plots=True):
    """绘制训练曲线"""
    result_path = Path(result_dir)
    
    if not result_path.exists():
        print(f"结果目录不存在: {result_dir}")
        return
    
    # 定义要绘制的文件和对应的标题
    files_to_plot = {
        'erl_score.csv': ('ERL Score', 'Games', 'Score'),
        'ddpg_score.csv': ('DDPG Reward', 'Frames', 'Reward'),
        'frame_erl_score.csv': ('ERL Score vs Frames', 'Frames', 'Score'),
        'time_erl_score.csv': ('ERL Score vs Time', 'Time (s)', 'Score')
    }
    
    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'PDERL Training Results - {result_path.name}', fontsize=16)
    
    axes = axes.flatten()
    
    for idx, (filename, (title, xlabel, ylabel)) in enumerate(files_to_plot.items()):
        file_path = result_path / filename
        
        if file_path.exists():
            data = load_csv_data(file_path)
            if data is not None:
                axes[idx].plot(data['x'], data['y'], linewidth=2, alpha=0.8)
                axes[idx].set_title(title, fontsize=12)
                axes[idx].set_xlabel(xlabel)
                axes[idx].set_ylabel(ylabel)
                axes[idx].grid(True, alpha=0.3)
                
                # 添加统计信息
                max_score = data['y'].max()
                final_score = data['y'].iloc[-1]
                axes[idx].text(0.02, 0.98, f'Max: {max_score:.1f}\nFinal: {final_score:.1f}', 
                             transform=axes[idx].transAxes, verticalalignment='top',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        else:
            axes[idx].text(0.5, 0.5, f'文件不存在:\n{filename}', 
                          transform=axes[idx].transAxes, ha='center', va='center')
            axes[idx].set_title(title, fontsize=12)
    
    plt.tight_layout()
    
    if save_plots:
        plot_path = result_path / 'training_curves.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"训练曲线已保存到: {plot_path}")
    
    plt.show()

def plot_selection_stats(result_dir, save_plots=True):
    """绘制选择统计信息"""
    result_path = Path(result_dir)
    
    selection_files = {
        'elite_selection.csv': 'Elite',
        'selected_selection.csv': 'Selected', 
        'discarded_selection.csv': 'Discarded'
    }
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    for filename, label in selection_files.items():
        file_path = result_path / filename
        if file_path.exists():
            data = load_csv_data(file_path)
            if data is not None:
                ax.plot(data['x'], data['y'], label=label, linewidth=2, alpha=0.8)
    
    ax.set_title('Selection Statistics Over Training', fontsize=14)
    ax.set_xlabel('Frames')
    ax.set_ylabel('Selection Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_plots:
        plot_path = result_path / 'selection_stats.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"选择统计图已保存到: {plot_path}")
    
    plt.show()

def print_summary_stats(result_dir):
    """打印训练结果摘要统计"""
    result_path = Path(result_dir)
    
    print(f"\n=== 训练结果摘要: {result_path.name} ===")
    
    # ERL Score 统计
    erl_file = result_path / 'erl_score.csv'
    if erl_file.exists():
        data = load_csv_data(erl_file)
        if data is not None:
            print(f"\n📊 ERL Score 统计:")
            print(f"  最高分数: {data['y'].max():.2f}")
            print(f"  最终分数: {data['y'].iloc[-1]:.2f}")
            print(f"  平均分数: {data['y'].mean():.2f}")
            print(f"  标准差: {data['y'].std():.2f}")
            print(f"  总游戏数: {data['x'].iloc[-1]:.0f}")
    
    # DDPG Reward 统计
    ddpg_file = result_path / 'ddpg_score.csv'
    if ddpg_file.exists():
        data = load_csv_data(ddpg_file)
        if data is not None:
            print(f"\n🎯 DDPG Reward 统计:")
            print(f"  最高奖励: {data['y'].max():.2f}")
            print(f"  最终奖励: {data['y'].iloc[-1]:.2f}")
            print(f"  平均奖励: {data['y'].mean():.2f}")
            print(f"  总帧数: {data['x'].iloc[-1]:.0f}")
    
    # 检查info.txt文件
    info_file = result_path / 'info.txt'
    if info_file.exists():
        print(f"\n⚙️ 训练参数信息可查看: {info_file}")

def compare_experiments(result_dirs):
    """比较多个实验结果"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(result_dirs)))
    
    for idx, result_dir in enumerate(result_dirs):
        result_path = Path(result_dir)
        exp_name = result_path.name
        color = colors[idx]
        
        # ERL Score 比较
        erl_file = result_path / 'erl_score.csv'
        if erl_file.exists():
            data = load_csv_data(erl_file)
            if data is not None:
                axes[0].plot(data['x'], data['y'], label=exp_name, 
                           color=color, linewidth=2, alpha=0.8)
        
        # DDPG Reward 比较
        ddpg_file = result_path / 'ddpg_score.csv'
        if ddpg_file.exists():
            data = load_csv_data(ddpg_file)
            if data is not None:
                axes[1].plot(data['x'], data['y'], label=exp_name, 
                           color=color, linewidth=2, alpha=0.8)
    
    axes[0].set_title('ERL Score Comparison')
    axes[0].set_xlabel('Games')
    axes[0].set_ylabel('Score')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_title('DDPG Reward Comparison')
    axes[1].set_xlabel('Frames')
    axes[1].set_ylabel('Reward')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='PDERL训练结果可视化工具')
    parser.add_argument('-dir', '--result_dir', type=str, required=True,
                       help='结果目录路径')
    parser.add_argument('-compare', '--compare_dirs', nargs='+', 
                       help='比较多个实验目录')
    parser.add_argument('--no_save', action='store_true',
                       help='不保存图片文件')
    parser.add_argument('--stats_only', action='store_true',
                       help='只显示统计信息，不绘图')
    
    args = parser.parse_args()
    
    if args.compare_dirs:
        print("比较多个实验结果...")
        compare_experiments(args.compare_dirs)
    else:
        # 打印统计信息
        print_summary_stats(args.result_dir)
        
        if not args.stats_only:
            # 绘制训练曲线
            plot_training_curves(args.result_dir, save_plots=not args.no_save)
            
            # 绘制选择统计
            plot_selection_stats(args.result_dir, save_plots=not args.no_save)

if __name__ == '__main__':
    # 如果直接运行，使用默认参数
    import sys
    if len(sys.argv) == 1:
        # 自动查找results目录
        current_dir = Path('.')
        results_dir = current_dir / 'results'
        
        if results_dir.exists():
            subdirs = [d for d in results_dir.iterdir() if d.is_dir()]
            if subdirs:
                print("发现以下实验结果目录:")
                for i, subdir in enumerate(subdirs):
                    print(f"  {i+1}. {subdir.name}")
                
                try:
                    choice = int(input("请选择要可视化的实验 (输入数字): ")) - 1
                    if 0 <= choice < len(subdirs):
                        selected_dir = subdirs[choice]
                        print(f"\n分析实验: {selected_dir.name}")
                        print_summary_stats(selected_dir)
                        plot_training_curves(selected_dir)
                        plot_selection_stats(selected_dir)
                    else:
                        print("无效选择")
                except (ValueError, KeyboardInterrupt):
                    print("\n退出")
            else:
                print("results目录中没有找到实验结果")
        else:
            print("未找到results目录，请使用命令行参数指定结果目录")
            print("用法: python visualize_results.py -dir <结果目录路径>")
    else:
        main()