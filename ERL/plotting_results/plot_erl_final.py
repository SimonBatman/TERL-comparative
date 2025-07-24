#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERL实验结果绘图工具 - 最终版本

功能：
- 自动发现和读取TensorBoard数据
- 生成论文格式图表（均值±标准差）
- 自动保存为环境名称的PNG文件
- 支持多环境批量处理

使用方法：
    python plot_erl_final.py --env Reacher-v2
    python plot_erl_final.py --env all  # 处理所有环境
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

def extract_tensorboard_data(log_dir, tag='charts/best_fitness'):
    """
    从TensorBoard日志中提取数据
    """
    try:
        event_acc = EventAccumulator(log_dir)
        event_acc.Reload()
        
        if tag not in event_acc.Tags()['scalars']:
            print(f"警告: 标签 '{tag}' 在 {log_dir} 中不存在")
            return None, None
        
        scalar_events = event_acc.Scalars(tag)
        steps = [event.step for event in scalar_events]
        values = [event.value for event in scalar_events]
        
        return np.array(steps), np.array(values)
    except Exception as e:
        print(f"读取 {log_dir} 失败: {e}")
        return None, None

def auto_discover_experiment_dirs(base_dir):
    """
    自动发现包含TensorBoard数据的实验目录
    """
    experiment_dirs = []
    
    if not os.path.exists(base_dir):
        return experiment_dirs
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            # 检查是否包含TensorBoard事件文件
            for file in os.listdir(item_path):
                if file.startswith('events.out.tfevents'):
                    experiment_dirs.append(item_path)
                    break
    
    return sorted(experiment_dirs)

def interpolate_data(steps, values, target_steps):
    """
    将数据插值到统一的步数网格
    """
    return np.interp(target_steps, steps, values)

def auto_adjust_axis_range(data_matrix):
    """
    自动调整Y轴范围
    """
    y_min = np.min(data_matrix)
    y_max = np.max(data_matrix)
    
    # 添加适当的边距
    if y_min < 0:
        y_min *= 1.1
        y_max *= 0.9 if y_max < 0 else 1.1
    else:
        margin = (y_max - y_min) * 0.1
        y_min = max(0, y_min - margin)
        y_max = y_max + margin
    
    return y_min, y_max

def plot_environment_results(env_name, base_dir, tag='charts/best_fitness', smooth_sigma=10):
    """
    绘制单个环境的实验结果
    
    Args:
        env_name: 环境名称
        base_dir: 实验数据目录
        tag: TensorBoard标签
        smooth_sigma: 平滑参数
    
    Returns:
        bool: 是否成功生成图表
    """
    print(f"\n{'='*60}")
    print(f"处理环境: {env_name}")
    print(f"数据目录: {base_dir}")
    print(f"{'='*60}")
    
    # 设置matplotlib参数
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # 自动发现实验目录
    experiment_dirs = auto_discover_experiment_dirs(base_dir)
    
    if not experiment_dirs:
        print(f"❌ 在 {base_dir} 中没有找到TensorBoard数据")
        return False
    
    print(f"发现 {len(experiment_dirs)} 个实验目录:")
    for i, exp_dir in enumerate(experiment_dirs):
        print(f"  {i+1}. {os.path.relpath(exp_dir, base_dir)}")
    
    # 提取所有实验的数据
    all_steps = []
    all_values = []
    
    for exp_dir in experiment_dirs:
        steps, values = extract_tensorboard_data(exp_dir, tag)
        if steps is not None and values is not None:
            all_steps.append(steps)
            all_values.append(values)
            print(f"✅ 成功加载 {os.path.basename(exp_dir)}: {len(steps)} 个数据点")
    
    if not all_steps:
        print("❌ 没有成功加载任何数据")
        return False
    
    # 找到所有实验的步数范围
    max_steps = max([steps[-1] for steps in all_steps])
    min_steps = min([steps[0] for steps in all_steps])
    
    # 创建统一的步数网格（转换为百万步）
    target_steps = np.linspace(min_steps, max_steps, 1000)
    target_steps_millions = target_steps / 1e6
    
    # 插值所有数据到统一网格
    interpolated_values = []
    for steps, values in zip(all_steps, all_values):
        interp_values = interpolate_data(steps, values, target_steps)
        interpolated_values.append(interp_values)
    
    # 转换为numpy数组
    data_matrix = np.array(interpolated_values)
    
    # 计算统计量
    mean_values = np.mean(data_matrix, axis=0)
    std_values = np.std(data_matrix, axis=0)
    
    # 计算标准差上下界（论文格式：均值±标准差）
    upper_bound = mean_values + std_values
    lower_bound = mean_values - std_values
    
    # 应用高斯平滑
    mean_smooth = gaussian_filter1d(mean_values, sigma=smooth_sigma)
    upper_bound_smooth = gaussian_filter1d(upper_bound, sigma=smooth_sigma)
    lower_bound_smooth = gaussian_filter1d(lower_bound, sigma=smooth_sigma)
    
    # 创建图表
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 绘制标准差区域
    ax.fill_between(target_steps_millions, lower_bound_smooth, upper_bound_smooth, 
                   alpha=0.3, color='red', label='Mean ± Std')
    
    # 绘制平均值曲线
    ax.plot(target_steps_millions, mean_smooth, 
           color='red', linewidth=2.5, label='ERL', zorder=5)
    
    # 设置图表属性
    ax.set_xlabel('Million Steps', fontsize=14)
    ax.set_ylabel('Performance', fontsize=14)
    ax.set_title(f'{env_name}', fontsize=16, fontweight='bold')
    
    # 自动调整坐标轴范围
    ax.set_xlim(0, target_steps_millions[-1])
    y_min, y_max = auto_adjust_axis_range(data_matrix)
    ax.set_ylim(y_min, y_max)
    
    # 设置网格和图例
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片（直接以环境名命名）
    output_file = f'{env_name}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图表释放内存
    
    print(f"✅ 图表已保存: {output_file}")
    
    # 打印统计信息
    print(f"\n=== {env_name} 统计信息 ===")
    print(f"实验数量: {len(all_steps)}")
    print(f"步数范围: {min_steps:,.0f} - {max_steps:,.0f}")
    print(f"数据范围: [{np.min(data_matrix):.2f}, {np.max(data_matrix):.2f}]")
    print(f"最终性能: {mean_smooth[-1]:.2f} ± {std_values[-1]:.2f}")
    print(f"峰值性能: {np.max(mean_smooth):.2f} ± {std_values[np.argmax(mean_smooth)]:.2f}")
    print(f"标准差范围: [{np.min(std_values):.3f}, {np.max(std_values):.3f}]")
    
    return True

def get_available_environments(runs_dir='../runs'):
    """
    获取所有可用的环境
    """
    environments = []
    if os.path.exists(runs_dir):
        for item in os.listdir(runs_dir):
            item_path = os.path.join(runs_dir, item)
            if os.path.isdir(item_path):
                # 检查是否包含实验数据
                if auto_discover_experiment_dirs(item_path):
                    environments.append(item)
    return sorted(environments)

def clean_old_results():
    """
    清理旧的结果文件和文件夹
    """
    print("\n🧹 清理旧的结果文件...")
    
    # 要删除的文件夹
    folders_to_remove = ['Ant-v2', 'HalfCheetah-v2', 'Reacher-v2', 'Hopper-v2', 'Swimmer-v2', 'Walker2d-v2']
    
    # 要删除的文件
    files_to_remove = [
        'demo_enhanced_plotting.py',
        'demo_paper_format.py', 
        'test_confidence_interval.py',
        'plot_reacher_results.py'
    ]
    
    removed_count = 0
    
    # 删除文件夹
    for folder in folders_to_remove:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"✅ 删除文件夹: {folder}")
            removed_count += 1
    
    # 删除文件
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ 删除文件: {file}")
            removed_count += 1
    
    # 删除缓存文件夹
    if os.path.exists('__pycache__'):
        import shutil
        shutil.rmtree('__pycache__')
        print(f"✅ 删除缓存文件夹: __pycache__")
        removed_count += 1
    
    if removed_count > 0:
        print(f"🎉 清理完成，共删除 {removed_count} 个项目")
    else:
        print("ℹ️  没有找到需要清理的文件")

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='ERL实验结果绘图工具 - 最终版本')
    parser.add_argument('--env', type=str, default='all',
                       help='环境名称 (如: Reacher-v2) 或 "all" 处理所有环境')
    parser.add_argument('--tag', type=str, default='charts/best_fitness',
                       help='TensorBoard标签名')
    parser.add_argument('--smooth', type=float, default=10,
                       help='高斯平滑参数')
    parser.add_argument('--clean', action='store_true',
                       help='清理旧的结果文件')
    parser.add_argument('--runs_dir', type=str, default='../runs',
                       help='实验数据根目录')
    
    args = parser.parse_args()
    
    print("ERL实验结果绘图工具 - 最终版本")
    print("=" * 50)
    print("📋 输出格式: 均值±标准差")
    print("📊 文件格式: PNG (高分辨率)")
    print("📁 命名规则: 直接以环境名命名")
    
    # 清理旧文件（如果指定）
    if args.clean:
        clean_old_results()
    
    # 检查依赖
    try:
        import tensorboard
        import scipy
        print("\n✅ 依赖检查通过")
    except ImportError as e:
        print(f"\n❌ 缺少依赖: {e}")
        print("请安装: pip install tensorboard scipy")
        return
    
    # 获取要处理的环境
    if args.env == 'all':
        environments = get_available_environments(args.runs_dir)
        if not environments:
            print(f"\n❌ 在 {args.runs_dir} 中没有找到任何环境数据")
            return
        print(f"\n🎯 发现 {len(environments)} 个环境: {environments}")
    else:
        environments = [args.env]
        print(f"\n🎯 处理指定环境: {args.env}")
    
    # 处理每个环境
    success_count = 0
    total_count = len(environments)
    
    for env in environments:
        base_dir = os.path.join(args.runs_dir, env)
        success = plot_environment_results(
            env_name=env,
            base_dir=base_dir,
            tag=args.tag,
            smooth_sigma=args.smooth
        )
        if success:
            success_count += 1
    
    # 总结
    print(f"\n{'='*60}")
    print(f"🎉 处理完成: {success_count}/{total_count} 个环境成功")
    
    if success_count > 0:
        print(f"\n📊 生成的图表特点:")
        print(f"- 红色实线: ERL平均性能")
        print(f"- 浅蓝色区域: 标准差范围 (Mean ± Std)")
        print(f"- 文件格式: PNG (300 DPI)")
        print(f"- 命名规则: {environments[0] if len(environments) == 1 else '环境名'}.png")
        
        print(f"\n📝 论文写作建议:")
        print(f"- 描述: '结果以均值±标准差的形式报告'")
        print(f"- 图例: '误差线表示标准差'")
        print(f"- 统计: 包含实验次数和性能范围")

if __name__ == "__main__":
    main()