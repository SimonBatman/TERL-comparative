#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDERL 并行训练脚本
支持在同一环境下使用不同随机种子进行多个并行实验
"""

import os
import sys
import time
import json
import argparse
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import psutil
except ImportError:
    print("⚠️ psutil 未安装，无法监控系统资源")
    psutil = None

class ParallelTrainer:
    def __init__(self, base_logdir="parallel_experiments"):
        self.base_logdir = base_logdir
        self.processes = []
        self.results = {}
        self.start_time = None
        
    def create_experiment_config(self, env_name, seeds, base_args=None):
        """创建实验配置"""
        if base_args is None:
            base_args = {}
            
        experiments = []
        for seed in seeds:
            exp_name = f"{env_name}_seed_{seed}"
            logdir = os.path.join(self.base_logdir, exp_name)
            
            config = {
                'name': exp_name,
                'env': env_name,
                'seed': seed,
                'logdir': logdir,
                'args': base_args.copy()
            }
            experiments.append(config)
            
        return experiments
    
    def run_single_experiment(self, config):
        """运行单个实验"""
        print(f"🚀 启动实验: {config['name']}")
        
        # 构建命令 - 使用当前Python解释器
        cmd = [
            sys.executable, 'run_pderl.py',
            '-env', config['env'],
            '-seed', str(config['seed']),
            '-logdir', config['logdir']
        ]
        
        # 添加额外参数
        for key, value in config['args'].items():
            if key.startswith('-'):
                cmd.append(key)
                if value is not None:
                    cmd.append(str(value))
            else:
                cmd.extend([f'-{key}', str(value)])
        
        try:
            # 创建日志目录
            os.makedirs(config['logdir'], exist_ok=True)
            
            # 启动进程
            log_file = os.path.join(config['logdir'], 'training.log')
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=os.getcwd(),
                    env=os.environ.copy()  # 继承当前环境变量
                )
            
            # 记录进程信息
            self.processes.append({
                'name': config['name'],
                'process': process,
                'config': config,
                'start_time': time.time(),
                'log_file': log_file
            })
            
            print(f"✅ 实验 {config['name']} 已启动 (PID: {process.pid})")
            
            # 等待进程完成
            return_code = process.wait()
            end_time = time.time()
            
            result = {
                'name': config['name'],
                'return_code': return_code,
                'duration': end_time - self.processes[-1]['start_time'],
                'success': return_code == 0
            }
            
            if return_code == 0:
                print(f"✅ 实验 {config['name']} 完成")
            else:
                print(f"❌ 实验 {config['name']} 失败 (返回码: {return_code})")
                
            return result
            
        except Exception as e:
            print(f"❌ 实验 {config['name']} 启动失败: {str(e)}")
            return {
                'name': config['name'],
                'return_code': -1,
                'duration': 0,
                'success': False,
                'error': str(e)
            }
    
    def monitor_system_resources(self):
        """监控系统资源使用情况"""
        while any(p['process'].poll() is None for p in self.processes if 'process' in p):
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                print(f"📊 系统资源: CPU {cpu_percent:.1f}%, 内存 {memory.percent:.1f}%")
                
                # 检查运行中的进程
                running_count = sum(1 for p in self.processes if 'process' in p and p['process'].poll() is None)
                print(f"🔄 运行中的实验: {running_count}/{len(self.processes)}")
                
                time.sleep(30)  # 每30秒监控一次
                
            except Exception as e:
                print(f"⚠️ 资源监控错误: {str(e)}")
                break
    
    def run_parallel_experiments(self, experiments, max_workers=None):
        """并行运行多个实验"""
        if max_workers is None:
            max_workers = min(len(experiments), os.cpu_count())
            
        print(f"🎯 开始并行训练: {len(experiments)} 个实验, 最大并发数: {max_workers}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # 启动资源监控线程
        monitor_thread = threading.Thread(target=self.monitor_system_resources, daemon=True)
        monitor_thread.start()
        
        # 并行执行实验
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {executor.submit(self.run_single_experiment, config): config 
                              for config in experiments}
            
            for future in as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    result = future.result()
                    self.results[config['name']] = result
                except Exception as e:
                    print(f"❌ 实验 {config['name']} 异常: {str(e)}")
                    self.results[config['name']] = {
                        'name': config['name'],
                        'return_code': -1,
                        'duration': 0,
                        'success': False,
                        'error': str(e)
                    }
        
        total_time = time.time() - self.start_time
        self.generate_summary_report(total_time)
    
    def generate_summary_report(self, total_time):
        """生成总结报告"""
        print("\n" + "=" * 60)
        print("📋 实验总结报告")
        print("=" * 60)
        
        successful = sum(1 for r in self.results.values() if r['success'])
        failed = len(self.results) - successful
        
        print(f"📊 总体结果: {successful}/{len(self.results)} 个实验成功")
        print(f"⏱️ 总耗时: {total_time/3600:.2f} 小时")
        print(f"💻 平均每个实验: {total_time/len(self.results)/60:.1f} 分钟")
        
        print("\n📈 详细结果:")
        for name, result in self.results.items():
            status = "✅" if result['success'] else "❌"
            duration = result['duration'] / 60  # 转换为分钟
            print(f"  {status} {name}: {duration:.1f}分钟")
            
            if not result['success'] and 'error' in result:
                print(f"    错误: {result['error']}")
        
        # 保存详细报告
        report_file = os.path.join(self.base_logdir, 'experiment_report.json')
        os.makedirs(self.base_logdir, exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_experiments': len(self.results),
            'successful': successful,
            'failed': failed,
            'total_time_hours': total_time / 3600,
            'results': self.results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        # 生成模型文件汇总
        self.collect_trained_models()
    
    def collect_trained_models(self):
        """收集训练好的模型文件"""
        print("\n🔍 收集训练好的模型...")
        
        model_summary = []
        
        for name, result in self.results.items():
            if result['success']:
                # 查找模型文件
                exp_dir = None
                for p in self.processes:
                    if p['name'] == name:
                        exp_dir = p['config']['logdir']
                        break
                
                if exp_dir and os.path.exists(exp_dir):
                    model_files = list(Path(exp_dir).glob('*.pkl'))
                    if model_files:
                        model_summary.append({
                            'experiment': name,
                            'directory': exp_dir,
                            'models': [str(f) for f in model_files]
                        })
        
        if model_summary:
            print(f"📁 找到 {len(model_summary)} 个实验的模型文件:")
            for item in model_summary:
                print(f"  📂 {item['experiment']}: {len(item['models'])} 个模型")
                for model in item['models']:
                    print(f"    📄 {os.path.basename(model)}")
        else:
            print("⚠️ 未找到训练好的模型文件")
    
    def stop_all_experiments(self):
        """停止所有正在运行的实验"""
        print("🛑 停止所有实验...")
        
        for p in self.processes:
            if 'process' in p and p['process'].poll() is None:
                try:
                    p['process'].terminate()
                    print(f"🛑 已停止实验: {p['name']}")
                except Exception as e:
                    print(f"❌ 停止实验 {p['name']} 失败: {str(e)}")

def create_preset_configs():
    """创建预设配置"""
    presets = {
        'quick_test': {
            'description': '快速测试 (3个种子, 较少训练步数)',
            'seeds': [1, 2, 3],
            'args': {
                'popsize': 5,
                'rollout_size': 5,
                'num_frames': 50000
            }
        },
        'standard': {
            'description': '标准实验 (5个种子)',
            'seeds': [1, 2, 3, 4, 5],
            'args': {}
        },
        'comprehensive': {
            'description': '全面实验 (10个种子)',
            'seeds': list(range(1, 11)),
            'args': {}
        },
        'custom_seeds': {
            'description': '自定义种子',
            'seeds': [7, 42, 123, 456, 789],
            'args': {}
        },
        'gpu_optimized': {
            'description': 'GPU优化 (5个种子, 适合16G显存, 启用TensorBoard)',
            'seeds': [1, 2, 3, 4, 5],
            'args': {
                'popsize': 10,
                'rollout_size': 10,
                'num_frames': 1000000,
                '-use_cuda': None,
                '-use_tensorboard': None,
                '-log_weights': None
            }
        }
    }
    return presets

def main():
    parser = argparse.ArgumentParser(description='PDERL 并行训练脚本')
    parser.add_argument('-env', '--environment', 
                       help='训练环境名称 (如: Hopper-v2)')
    parser.add_argument('-preset', '--preset', choices=['quick_test', 'standard', 'comprehensive', 'custom_seeds', 'gpu_optimized'],
                       default='standard', help='预设配置')
    parser.add_argument('-seeds', '--seeds', nargs='+', type=int,
                       help='自定义随机种子列表')
    parser.add_argument('-workers', '--max_workers', type=int,
                       help='最大并发数 (默认为CPU核心数)')
    parser.add_argument('-logdir', '--base_logdir', default='parallel_experiments',
                       help='基础日志目录')
    parser.add_argument('--list-presets', action='store_true',
                       help='列出所有预设配置')
    
    # 添加训练参数
    parser.add_argument('-popsize', '--popsize', type=int, help='种群大小')
    parser.add_argument('-rollout_size', '--rollout_size', type=int, help='Rollout大小')
    parser.add_argument('-num_frames', '--num_frames', type=int, help='训练帧数')
    parser.add_argument('-use_cuda', '--use_cuda', action='store_true', help='使用CUDA')
    
    # TensorBoard相关参数
    parser.add_argument('-use_tensorboard', '--use_tensorboard', action='store_true', 
                       help='使用TensorBoard记录训练过程')
    parser.add_argument('-tensorboard_dir', '--tensorboard_dir', type=str,
                       help='TensorBoard日志目录 (默认为实验目录下的tensorboard文件夹)')
    parser.add_argument('-log_weights', '--log_weights', action='store_true',
                       help='记录网络权重到TensorBoard')
    parser.add_argument('-log_freq', '--log_freq', type=int, default=10,
                       help='详细指标记录频率')
    
    args = parser.parse_args()
    
    # 列出预设配置
    if args.list_presets:
        presets = create_preset_configs()
        print("📋 可用的预设配置:")
        for name, config in presets.items():
            print(f"  {name}: {config['description']}")
            print(f"    种子: {config['seeds']}")
            if config['args']:
                print(f"    参数: {config['args']}")
            print()
        return
    
    # 检查必需参数
    if not args.environment:
        parser.error("训练时必须指定环境 (-env/--environment)")
    
    # 创建训练器
    trainer = ParallelTrainer(args.base_logdir)
    
    try:
        # 确定使用的种子
        if args.seeds:
            seeds = args.seeds
            print(f"🎲 使用自定义种子: {seeds}")
        else:
            presets = create_preset_configs()
            preset_config = presets[args.preset]
            seeds = preset_config['seeds']
            print(f"🎲 使用预设 '{args.preset}': {preset_config['description']}")
            print(f"🎲 种子: {seeds}")
        
        # 构建训练参数
        train_args = {}
        if args.popsize:
            train_args['popsize'] = args.popsize
        if args.rollout_size:
            train_args['rollout_size'] = args.rollout_size
        if args.num_frames:
            train_args['num_frames'] = args.num_frames
        if args.use_cuda:
            train_args['-use_cuda'] = None
        
        # TensorBoard参数
        if args.use_tensorboard:
            train_args['-use_tensorboard'] = None
            if args.tensorboard_dir:
                train_args['-tensorboard_dir'] = args.tensorboard_dir
            if args.log_weights:
                train_args['-log_weights'] = None
            if args.log_freq != 10:  # 只有非默认值才添加
                train_args['-log_freq'] = args.log_freq
        
        # 如果使用预设，合并预设参数
        if not args.seeds:
            preset_args = presets[args.preset]['args']
            train_args.update(preset_args)
        
        # 创建实验配置
        experiments = trainer.create_experiment_config(
            args.environment, seeds, train_args
        )
        
        print(f"🎯 环境: {args.environment}")
        print(f"📊 实验数量: {len(experiments)}")
        if train_args:
            print(f"⚙️ 训练参数: {train_args}")
        print()
        
        # 确认开始
        response = input("是否开始并行训练? (y/n): ")
        if response.lower() != 'y':
            print("❌ 已取消")
            return
        
        # 开始并行训练
        trainer.run_parallel_experiments(experiments, args.max_workers)
        
    except KeyboardInterrupt:
        print("\n⚠️ 收到中断信号，正在停止所有实验...")
        trainer.stop_all_experiments()
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        trainer.stop_all_experiments()

if __name__ == '__main__':
    main()