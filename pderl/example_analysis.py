#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDERL 结果分析示例
演示如何使用可视化工具进行训练结果分析
"""

from visualize_results import (
    load_csv_data, 
    print_summary_stats, 
    plot_training_curves,
    plot_selection_stats,
    compare_experiments
)
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def analyze_training_progress(result_dir):
    """分析训练进展"""
    print(f"\n=== 分析训练进展: {Path(result_dir).name} ===")
    
    # 加载ERL得分数据
    erl_file = Path(result_dir) / 'erl_score.csv'
    if erl_file.exists():
        data = load_csv_data(erl_file)
        
        # 计算学习效率
        if len(data) > 1:
            total_improvement = data['y'].iloc[-1] - data['y'].iloc[0]
            total_games = data['x'].iloc[-1] - data['x'].iloc[0]
            efficiency = total_improvement / (total_games / 1000)  # 每1000游戏的改进
            
            print(f"📈 学习效率: {efficiency:.2f} 分数/千游戏")
            print(f"🎯 总体改进: {total_improvement:.2f} 分数")
            
            # 检测收敛
            window_size = min(10, len(data) // 4)
            if window_size > 1:
                rolling_std = data['y'].rolling(window=window_size).std()
                convergence_threshold = data['y'].max() * 0.02  # 2%的变化阈值
                
                converged_points = rolling_std[rolling_std < convergence_threshold]
                if len(converged_points) > 0:
                    convergence_game = data.iloc[converged_points.index[0]]['x']
                    print(f"🔄 收敛点: 第 {convergence_game:.0f} 游戏")
                else:
                    print("🔄 尚未收敛")
            
            # 分析训练阶段
            analyze_training_phases(data)
    
    return data

def analyze_training_phases(data):
    """分析训练的不同阶段"""
    print("\n📊 训练阶段分析:")
    
    total_games = len(data)
    
    # 早期阶段 (前25%)
    early_end = total_games // 4
    early_data = data.iloc[:early_end]
    early_improvement = early_data['y'].iloc[-1] - early_data['y'].iloc[0] if len(early_data) > 1 else 0
    
    # 中期阶段 (25%-75%)
    mid_start = early_end
    mid_end = total_games * 3 // 4
    mid_data = data.iloc[mid_start:mid_end]
    mid_improvement = mid_data['y'].iloc[-1] - mid_data['y'].iloc[0] if len(mid_data) > 1 else 0
    
    # 后期阶段 (后25%)
    late_data = data.iloc[mid_end:]
    late_improvement = late_data['y'].iloc[-1] - late_data['y'].iloc[0] if len(late_data) > 1 else 0
    
    print(f"  🌱 早期阶段改进: {early_improvement:.2f}")
    print(f"  🚀 中期阶段改进: {mid_improvement:.2f}")
    print(f"  🎯 后期阶段改进: {late_improvement:.2f}")
    
    # 判断训练状态
    if late_improvement > 0:
        print("  ✅ 训练仍在改进")
    elif abs(late_improvement) < data['y'].std() * 0.1:
        print("  🔄 训练已收敛")
    else:
        print("  ⚠️ 训练可能过拟合")

def compare_rl_vs_evolution(result_dir):
    """比较强化学习和进化算法的贡献"""
    print(f"\n=== RL vs Evolution 分析: {Path(result_dir).name} ===")
    
    result_path = Path(result_dir)
    
    # 加载数据
    erl_data = load_csv_data(result_path / 'erl_score.csv')
    ddpg_data = load_csv_data(result_path / 'ddpg_score.csv')
    
    if erl_data is not None and ddpg_data is not None:
        # 计算相关性（需要对齐数据点）
        # 这里简化处理，实际应用中可能需要更复杂的对齐逻辑
        erl_final = erl_data['y'].iloc[-1]
        ddpg_final = ddpg_data['y'].iloc[-1]
        
        print(f"🎮 ERL 最终得分: {erl_final:.2f}")
        print(f"🤖 DDPG 最终奖励: {ddpg_final:.2f}")
        
        # 分析改进趋势
        erl_trend = erl_data['y'].iloc[-5:].mean() - erl_data['y'].iloc[:5].mean()
        ddpg_trend = ddpg_data['y'].iloc[-5:].mean() - ddpg_data['y'].iloc[:5].mean()
        
        print(f"📈 ERL 改进趋势: {erl_trend:.2f}")
        print(f"📈 DDPG 改进趋势: {ddpg_trend:.2f}")

def analyze_selection_strategy(result_dir):
    """分析选择策略效果"""
    print(f"\n=== 选择策略分析: {Path(result_dir).name} ===")
    
    result_path = Path(result_dir)
    
    # 加载选择数据
    elite_data = load_csv_data(result_path / 'elite_selection.csv')
    selected_data = load_csv_data(result_path / 'selected_selection.csv')
    discarded_data = load_csv_data(result_path / 'discarded_selection.csv')
    
    if all(data is not None for data in [elite_data, selected_data, discarded_data]):
        print(f"🏆 平均精英比例: {elite_data['y'].mean():.3f}")
        print(f"✅ 平均选择比例: {selected_data['y'].mean():.3f}")
        print(f"❌ 平均丢弃比例: {discarded_data['y'].mean():.3f}")
        
        # 分析选择策略的稳定性
        elite_std = elite_data['y'].std()
        print(f"📊 精英选择稳定性 (标准差): {elite_std:.3f}")
        
        if elite_std < 0.05:
            print("  ✅ 选择策略稳定")
        else:
            print("  ⚠️ 选择策略波动较大")

def generate_performance_report(result_dir):
    """生成性能报告"""
    print(f"\n{'='*50}")
    print(f"🎯 PDERL 性能报告: {Path(result_dir).name}")
    print(f"{'='*50}")
    
    # 基础统计
    print_summary_stats(result_dir)
    
    # 详细分析
    analyze_training_progress(result_dir)
    compare_rl_vs_evolution(result_dir)
    analyze_selection_strategy(result_dir)
    
    print(f"\n{'='*50}")
    print("📋 报告完成")
    print(f"{'='*50}")

def quick_comparison(result_dirs):
    """快速比较多个实验"""
    print("\n🔍 实验快速比较")
    print("-" * 80)
    print(f"{'实验名称':<20} {'最高分数':<12} {'最终分数':<12} {'平均分数':<12} {'改进幅度':<12}")
    print("-" * 80)
    
    for result_dir in result_dirs:
        result_path = Path(result_dir)
        exp_name = result_path.name
        
        erl_file = result_path / 'erl_score.csv'
        if erl_file.exists():
            data = load_csv_data(erl_file)
            if data is not None:
                max_score = data['y'].max()
                final_score = data['y'].iloc[-1]
                avg_score = data['y'].mean()
                improvement = final_score - data['y'].iloc[0] if len(data) > 1 else 0
                
                print(f"{exp_name:<20} {max_score:<12.1f} {final_score:<12.1f} {avg_score:<12.1f} {improvement:<12.1f}")
        else:
            print(f"{exp_name:<20} {'N/A':<12} {'N/A':<12} {'N/A':<12} {'N/A':<12}")
    
    print("-" * 80)

def main():
    """主函数 - 演示各种分析功能"""
    # 示例：分析单个实验
    result_dir = 'results/hopper_pderl'
    
    if Path(result_dir).exists():
        print("🚀 开始 PDERL 结果分析...")
        
        # 生成完整报告
        generate_performance_report(result_dir)
        
        # 生成可视化图表
        print("\n📊 生成可视化图表...")
        plot_training_curves(result_dir, save_plots=True)
        plot_selection_stats(result_dir, save_plots=True)
        
        print("\n✅ 分析完成！")
        print("📁 查看生成的图片文件:")
        print(f"   - {result_dir}/training_curves.png")
        print(f"   - {result_dir}/selection_stats.png")
    else:
        print(f"❌ 结果目录不存在: {result_dir}")
        print("请先运行训练或指定正确的结果目录")
    
    # 示例：比较多个实验（如果存在）
    results_dir = Path('results')
    if results_dir.exists():
        subdirs = [str(d) for d in results_dir.iterdir() if d.is_dir()]
        if len(subdirs) > 1:
            print("\n🔍 发现多个实验，进行比较分析...")
            quick_comparison(subdirs)
            
            print("\n📊 生成比较图表...")
            compare_experiments(subdirs)

if __name__ == '__main__':
    main()