#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDERL 并行实验结果分析脚本
用于分析多个随机种子实验的结果，生成统计报告和可视化图表
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ParallelResultsAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.experiments = {}
        self.combined_data = None
        
    def load_experiment_data(self):
        """加载所有实验数据"""
        print(f"🔍 扫描实验目录: {self.base_dir}")
        
        if not self.base_dir.exists():
            print(f"❌ 目录不存在: {self.base_dir}")
            return False
        
        # 查找所有实验子目录
        exp_dirs = [d for d in self.base_dir.iterdir() if d.is_dir() and 'seed_' in d.name]
        
        if not exp_dirs:
            print("❌ 未找到实验目录")
            return False
        
        print(f"📁 找到 {len(exp_dirs)} 个实验目录")
        
        for exp_dir in exp_dirs:
            exp_name = exp_dir.name
            print(f"📊 加载实验: {exp_name}")
            
            # 解析实验名称
            parts = exp_name.split('_seed_')
            if len(parts) == 2:
                env_name = parts[0]
                seed = int(parts[1])
            else:
                print(f"⚠️ 无法解析实验名称: {exp_name}")
                continue
            
            # 加载实验数据
            exp_data = self.load_single_experiment(exp_dir, env_name, seed)
            if exp_data:
                self.experiments[exp_name] = exp_data
        
        print(f"✅ 成功加载 {len(self.experiments)} 个实验")
        return len(self.experiments) > 0
    
    def load_single_experiment(self, exp_dir, env_name, seed):
        """加载单个实验的数据"""
        try:
            # 查找CSV文件
            csv_files = {
                'erl_score': exp_dir / 'erl_score.csv',
                'ddpg_score': exp_dir / 'ddpg_score.csv',
                'frame_erl_score': exp_dir / 'frame_erl_score.csv',
                'time_erl_score': exp_dir / 'time_erl_score.csv'
            }
            
            data = {
                'env_name': env_name,
                'seed': seed,
                'directory': str(exp_dir)
            }
            
            # 加载各种分数数据
            for score_type, csv_path in csv_files.items():
                if csv_path.exists():
                    try:
                        df = pd.read_csv(csv_path)
                        if not df.empty:
                            data[score_type] = df
                            # 计算最终性能
                            if 'fitness' in df.columns:
                                data[f'{score_type}_final'] = df['fitness'].iloc[-1]
                                data[f'{score_type}_max'] = df['fitness'].max()
                                data[f'{score_type}_mean'] = df['fitness'].mean()
                    except Exception as e:
                        print(f"⚠️ 加载 {csv_path} 失败: {str(e)}")
            
            # 检查模型文件
            model_files = list(exp_dir.glob('*.pkl'))
            data['model_files'] = [str(f) for f in model_files]
            data['has_models'] = len(model_files) > 0
            
            return data
            
        except Exception as e:
            print(f"❌ 加载实验 {exp_dir.name} 失败: {str(e)}")
            return None
    
    def create_combined_dataframe(self):
        """创建合并的数据框用于分析"""
        if not self.experiments:
            return None
        
        records = []
        
        for exp_name, exp_data in self.experiments.items():
            record = {
                'experiment': exp_name,
                'environment': exp_data['env_name'],
                'seed': exp_data['seed'],
                'has_models': exp_data['has_models']
            }
            
            # 添加各种分数的最终值
            score_types = ['erl_score', 'ddpg_score']
            for score_type in score_types:
                if f'{score_type}_final' in exp_data:
                    record[f'{score_type}_final'] = exp_data[f'{score_type}_final']
                    record[f'{score_type}_max'] = exp_data[f'{score_type}_max']
                    record[f'{score_type}_mean'] = exp_data[f'{score_type}_mean']
            
            records.append(record)
        
        self.combined_data = pd.DataFrame(records)
        return self.combined_data
    
    def generate_statistics_report(self):
        """生成统计报告"""
        if self.combined_data is None:
            self.create_combined_dataframe()
        
        if self.combined_data is None or self.combined_data.empty:
            print("❌ 没有可用的数据进行分析")
            return
        
        print("\n" + "=" * 60)
        print("📊 统计分析报告")
        print("=" * 60)
        
        # 基本信息
        envs = self.combined_data['environment'].unique()
        print(f"🎮 环境数量: {len(envs)}")
        for env in envs:
            env_data = self.combined_data[self.combined_data['environment'] == env]
            print(f"  📂 {env}: {len(env_data)} 个实验")
        
        print(f"🎲 种子范围: {self.combined_data['seed'].min()} - {self.combined_data['seed'].max()}")
        print(f"✅ 成功实验: {self.combined_data['has_models'].sum()}/{len(self.combined_data)}")
        
        # 性能统计
        score_columns = [col for col in self.combined_data.columns if col.endswith('_final')]
        
        if score_columns:
            print("\n📈 性能统计:")
            
            for env in envs:
                env_data = self.combined_data[self.combined_data['environment'] == env]
                print(f"\n🎯 {env}:")
                
                for score_col in score_columns:
                    if score_col in env_data.columns and not env_data[score_col].isna().all():
                        scores = env_data[score_col].dropna()
                        if len(scores) > 0:
                            score_name = score_col.replace('_final', '').upper()
                            print(f"  {score_name}:")
                            print(f"    平均值: {scores.mean():.2f} ± {scores.std():.2f}")
                            print(f"    最大值: {scores.max():.2f}")
                            print(f"    最小值: {scores.min():.2f}")
                            print(f"    中位数: {scores.median():.2f}")
                            
                            # 置信区间
                            if len(scores) > 1:
                                ci = stats.t.interval(0.95, len(scores)-1, 
                                                     loc=scores.mean(), 
                                                     scale=stats.sem(scores))
                                print(f"    95%置信区间: [{ci[0]:.2f}, {ci[1]:.2f}]")
        
        # 保存统计报告
        self.save_statistics_report()
    
    def save_statistics_report(self):
        """保存统计报告到文件"""
        if self.combined_data is None:
            return
        
        report_file = self.base_dir / 'analysis_report.csv'
        self.combined_data.to_csv(report_file, index=False, encoding='utf-8-sig')
        print(f"\n📄 统计报告已保存: {report_file}")
        
        # 保存汇总统计
        summary_file = self.base_dir / 'summary_statistics.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("PDERL 并行实验统计汇总\n")
            f.write("=" * 40 + "\n\n")
            
            envs = self.combined_data['environment'].unique()
            for env in envs:
                env_data = self.combined_data[self.combined_data['environment'] == env]
                f.write(f"环境: {env}\n")
                f.write(f"实验数量: {len(env_data)}\n")
                
                score_columns = [col for col in env_data.columns if col.endswith('_final')]
                for score_col in score_columns:
                    if score_col in env_data.columns and not env_data[score_col].isna().all():
                        scores = env_data[score_col].dropna()
                        if len(scores) > 0:
                            score_name = score_col.replace('_final', '')
                            f.write(f"{score_name}_平均值: {scores.mean():.2f}\n")
                            f.write(f"{score_name}_标准差: {scores.std():.2f}\n")
                            f.write(f"{score_name}_最大值: {scores.max():.2f}\n")
                
                f.write("\n")
        
        print(f"📄 汇总统计已保存: {summary_file}")
    
    def create_visualizations(self):
        """创建可视化图表"""
        if self.combined_data is None or self.combined_data.empty:
            print("❌ 没有可用的数据进行可视化")
            return
        
        print("\n🎨 生成可视化图表...")
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 1. 性能分布箱线图
        self.plot_performance_distribution()
        
        # 2. 种子间性能对比
        self.plot_seed_comparison()
        
        # 3. 学习曲线对比
        self.plot_learning_curves()
        
        # 4. 性能相关性分析
        self.plot_performance_correlation()
        
        print("✅ 可视化图表生成完成")
    
    def plot_performance_distribution(self):
        """绘制性能分布箱线图"""
        score_columns = [col for col in self.combined_data.columns if col.endswith('_final')]
        
        if not score_columns:
            return
        
        envs = self.combined_data['environment'].unique()
        
        fig, axes = plt.subplots(len(score_columns), len(envs), 
                                figsize=(4*len(envs), 4*len(score_columns)))
        
        if len(score_columns) == 1:
            axes = axes.reshape(1, -1)
        if len(envs) == 1:
            axes = axes.reshape(-1, 1)
        
        for i, score_col in enumerate(score_columns):
            for j, env in enumerate(envs):
                env_data = self.combined_data[self.combined_data['environment'] == env]
                scores = env_data[score_col].dropna()
                
                if len(scores) > 0:
                    ax = axes[i, j] if len(score_columns) > 1 else axes[j]
                    
                    # 箱线图
                    bp = ax.boxplot(scores, patch_artist=True)
                    bp['boxes'][0].set_facecolor('lightblue')
                    
                    # 散点图
                    x = np.random.normal(1, 0.04, len(scores))
                    ax.scatter(x, scores, alpha=0.6, color='red', s=20)
                    
                    score_name = score_col.replace('_final', '').upper()
                    ax.set_title(f'{env}\n{score_name} 性能分布')
                    ax.set_ylabel('分数')
                    ax.grid(True, alpha=0.3)
                    
                    # 添加统计信息
                    mean_val = scores.mean()
                    std_val = scores.std()
                    ax.text(0.02, 0.98, f'均值: {mean_val:.1f}\n标准差: {std_val:.1f}', 
                           transform=ax.transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.base_dir / 'performance_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 性能分布图已保存: performance_distribution.png")
    
    def plot_seed_comparison(self):
        """绘制种子间性能对比"""
        score_columns = [col for col in self.combined_data.columns if col.endswith('_final')]
        
        if not score_columns:
            return
        
        envs = self.combined_data['environment'].unique()
        
        for env in envs:
            env_data = self.combined_data[self.combined_data['environment'] == env]
            
            if len(env_data) < 2:
                continue
            
            fig, axes = plt.subplots(1, len(score_columns), 
                                   figsize=(6*len(score_columns), 5))
            
            if len(score_columns) == 1:
                axes = [axes]
            
            for i, score_col in enumerate(score_columns):
                scores = env_data[score_col].dropna()
                seeds = env_data.loc[scores.index, 'seed']
                
                if len(scores) > 0:
                    ax = axes[i]
                    
                    # 条形图
                    bars = ax.bar(range(len(scores)), scores, 
                                 color=plt.cm.viridis(np.linspace(0, 1, len(scores))))
                    
                    # 添加数值标签
                    for j, (bar, score) in enumerate(zip(bars, scores)):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(scores),
                               f'{score:.1f}', ha='center', va='bottom')
                    
                    ax.set_xlabel('实验 (按种子排序)')
                    ax.set_ylabel('分数')
                    score_name = score_col.replace('_final', '').upper()
                    ax.set_title(f'{env} - {score_name} 种子对比')
                    ax.grid(True, alpha=0.3)
                    
                    # 设置x轴标签为种子值
                    ax.set_xticks(range(len(scores)))
                    ax.set_xticklabels([f'Seed {seed}' for seed in seeds], rotation=45)
                    
                    # 添加平均线
                    mean_val = scores.mean()
                    ax.axhline(y=mean_val, color='red', linestyle='--', alpha=0.7, 
                              label=f'平均值: {mean_val:.1f}')
                    ax.legend()
            
            plt.tight_layout()
            plt.savefig(self.base_dir / f'seed_comparison_{env.lower()}.png', 
                       dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📊 种子对比图已保存: seed_comparison_{env.lower()}.png")
    
    def plot_learning_curves(self):
        """绘制学习曲线对比"""
        envs = self.combined_data['environment'].unique()
        
        for env in envs:
            env_experiments = {name: data for name, data in self.experiments.items() 
                             if data['env_name'] == env}
            
            if len(env_experiments) < 2:
                continue
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            score_types = ['erl_score', 'ddpg_score']
            colors = plt.cm.tab10(np.linspace(0, 1, len(env_experiments)))
            
            for i, score_type in enumerate(score_types):
                ax = axes[i]
                
                for j, (exp_name, exp_data) in enumerate(env_experiments.items()):
                    if score_type in exp_data and not exp_data[score_type].empty:
                        df = exp_data[score_type]
                        if 'fitness' in df.columns:
                            # 平滑曲线
                            window = max(1, len(df) // 20)
                            smoothed = df['fitness'].rolling(window=window, center=True).mean()
                            
                            ax.plot(smoothed, color=colors[j], alpha=0.7, 
                                   label=f'Seed {exp_data["seed"]}')
                
                ax.set_xlabel('训练轮次')
                ax.set_ylabel('适应度分数')
                ax.set_title(f'{env} - {score_type.upper()} 学习曲线')
                ax.grid(True, alpha=0.3)
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            plt.savefig(self.base_dir / f'learning_curves_{env.lower()}.png', 
                       dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📈 学习曲线图已保存: learning_curves_{env.lower()}.png")
    
    def plot_performance_correlation(self):
        """绘制性能相关性分析"""
        score_columns = [col for col in self.combined_data.columns 
                        if col.endswith('_final') or col.endswith('_max') or col.endswith('_mean')]
        
        if len(score_columns) < 2:
            return
        
        # 计算相关性矩阵
        corr_data = self.combined_data[score_columns].corr()
        
        # 绘制热力图
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        
        sns.heatmap(corr_data, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        
        plt.title('性能指标相关性分析')
        plt.tight_layout()
        plt.savefig(self.base_dir / 'performance_correlation.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 相关性分析图已保存: performance_correlation.png")
    
    def generate_best_models_report(self):
        """生成最佳模型报告"""
        if self.combined_data is None or self.combined_data.empty:
            return
        
        print("\n🏆 最佳模型报告")
        print("=" * 40)
        
        envs = self.combined_data['environment'].unique()
        best_models = {}
        
        for env in envs:
            env_data = self.combined_data[self.combined_data['environment'] == env]
            
            # 找到ERL分数最高的实验
            if 'erl_score_final' in env_data.columns:
                best_idx = env_data['erl_score_final'].idxmax()
                if not pd.isna(best_idx):
                    best_exp = env_data.loc[best_idx]
                    best_models[env] = {
                        'experiment': best_exp['experiment'],
                        'seed': best_exp['seed'],
                        'erl_score': best_exp['erl_score_final'],
                        'ddpg_score': best_exp.get('ddpg_score_final', 'N/A')
                    }
                    
                    print(f"🎯 {env}:")
                    print(f"  最佳实验: {best_exp['experiment']}")
                    print(f"  种子: {best_exp['seed']}")
                    print(f"  ERL分数: {best_exp['erl_score_final']:.2f}")
                    if 'ddpg_score_final' in best_exp:
                        print(f"  DDPG分数: {best_exp['ddpg_score_final']:.2f}")
                    
                    # 查找模型文件
                    exp_data = self.experiments[best_exp['experiment']]
                    if exp_data['model_files']:
                        print(f"  模型文件: {len(exp_data['model_files'])} 个")
                        for model_file in exp_data['model_files']:
                            print(f"    📄 {Path(model_file).name}")
                    print()
        
        # 保存最佳模型信息
        best_models_file = self.base_dir / 'best_models.json'
        with open(best_models_file, 'w', encoding='utf-8') as f:
            json.dump(best_models, f, indent=2, ensure_ascii=False)
        
        print(f"📄 最佳模型报告已保存: {best_models_file}")
        
        return best_models

def main():
    parser = argparse.ArgumentParser(description='PDERL 并行实验结果分析')
    parser.add_argument('-dir', '--directory', required=True,
                       help='并行实验结果目录')
    parser.add_argument('--no-plots', action='store_true',
                       help='不生成图表')
    parser.add_argument('--stats-only', action='store_true',
                       help='仅生成统计报告')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = ParallelResultsAnalyzer(args.directory)
    
    # 加载数据
    if not analyzer.load_experiment_data():
        print("❌ 无法加载实验数据")
        return
    
    # 生成统计报告
    analyzer.generate_statistics_report()
    
    # 生成最佳模型报告
    analyzer.generate_best_models_report()
    
    # 生成可视化图表
    if not args.stats_only and not args.no_plots:
        try:
            analyzer.create_visualizations()
        except Exception as e:
            print(f"⚠️ 生成图表时出错: {str(e)}")
            print("💡 可以使用 --no-plots 参数跳过图表生成")
    
    print("\n✅ 分析完成！")
    print(f"📁 结果保存在: {analyzer.base_dir}")

if __name__ == '__main__':
    main()