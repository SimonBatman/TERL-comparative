import os
import torch
from torch.utils.tensorboard import SummaryWriter
import numpy as np


class TensorBoardTracker:
    """TensorBoard日志记录器，替代CSV文件存储"""
    
    def __init__(self, parameters, log_dir=None):
        """
        初始化TensorBoard记录器
        
        Args:
            parameters: 参数对象
            log_dir: TensorBoard日志目录，如果为None则使用parameters.save_foldername
        """
        self.parameters = parameters
        
        # 设置日志目录
        if log_dir is None:
            self.log_dir = os.path.join(parameters.save_foldername, 'tensorboard_logs')
        else:
            self.log_dir = log_dir
            
        # 创建目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化SummaryWriter
        self.writer = SummaryWriter(log_dir=self.log_dir)
        
        # 记录参数信息
        self._log_hyperparameters()
        
        print(f"📊 TensorBoard日志已启用: {self.log_dir}")
        print(f"💡 查看训练过程: tensorboard --logdir {self.log_dir}")
    
    def _log_hyperparameters(self):
        """记录超参数"""
        hparams = {
            'env_name': self.parameters.env_name,
            'seed': self.parameters.seed,
            'pop_size': self.parameters.pop_size,
            'num_frames': self.parameters.num_frames,
            'batch_size': self.parameters.batch_size,
            'buffer_size': self.parameters.buffer_size,
            'tau': self.parameters.tau,
            'gamma': self.parameters.gamma,
            'mutation_mag': self.parameters.mutation_mag,
        }
        
        # 添加布尔参数
        bool_params = ['use_cuda', 'novelty', 'proximal_mut', 'distil', 'per']
        for param in bool_params:
            if hasattr(self.parameters, param):
                hparams[param] = getattr(self.parameters, param)
        
        # 记录超参数
        self.writer.add_hparams(hparams, {})
    
    def log_training_step(self, step, metrics):
        """
        记录训练步骤的指标
        
        Args:
            step: 训练步数（帧数或游戏数）
            metrics: 指标字典
        """
        for metric_name, value in metrics.items():
            if value is not None:
                self.writer.add_scalar(f'Training/{metric_name}', value, step)
    
    def log_performance(self, step, erl_score, ddpg_reward, best_train_fitness=None):
        """
        记录性能指标
        
        Args:
            step: 步数
            erl_score: ERL测试分数
            ddpg_reward: DDPG奖励
            best_train_fitness: 最佳训练适应度
        """
        if erl_score is not None:
            self.writer.add_scalar('Performance/ERL_Test_Score', erl_score, step)
        
        if ddpg_reward is not None:
            self.writer.add_scalar('Performance/DDPG_Reward', ddpg_reward, step)
        
        if best_train_fitness is not None:
            self.writer.add_scalar('Performance/Best_Train_Fitness', best_train_fitness, step)
    
    def log_losses(self, step, pg_loss=None, bc_loss=None, critic_loss=None):
        """
        记录损失函数
        
        Args:
            step: 步数
            pg_loss: 策略梯度损失
            bc_loss: 行为克隆损失
            critic_loss: 评论家损失
        """
        if pg_loss is not None:
            self.writer.add_scalar('Losses/Policy_Gradient_Loss', pg_loss, step)
        
        if bc_loss is not None:
            self.writer.add_scalar('Losses/Behavior_Cloning_Loss', bc_loss, step)
        
        if critic_loss is not None:
            self.writer.add_scalar('Losses/Critic_Loss', critic_loss, step)
    
    def log_evolution_stats(self, step, elite_ratio, selected_ratio, discarded_ratio, pop_novelty=None):
        """
        记录进化统计信息
        
        Args:
            step: 步数
            elite_ratio: 精英比例
            selected_ratio: 选择比例
            discarded_ratio: 丢弃比例
            pop_novelty: 种群新颖性
        """
        self.writer.add_scalar('Evolution/Elite_Ratio', elite_ratio, step)
        self.writer.add_scalar('Evolution/Selected_Ratio', selected_ratio, step)
        self.writer.add_scalar('Evolution/Discarded_Ratio', discarded_ratio, step)
        
        if pop_novelty is not None:
            self.writer.add_scalar('Evolution/Population_Novelty', pop_novelty, step)
    
    def log_network_weights(self, step, actor_net, critic_net=None):
        """
        记录网络权重分布
        
        Args:
            step: 步数
            actor_net: Actor网络
            critic_net: Critic网络
        """
        # 记录Actor网络权重
        for name, param in actor_net.named_parameters():
            if param.grad is not None:
                self.writer.add_histogram(f'Actor_Weights/{name}', param.data, step)
                self.writer.add_histogram(f'Actor_Gradients/{name}', param.grad.data, step)
        
        # 记录Critic网络权重
        if critic_net is not None:
            for name, param in critic_net.named_parameters():
                if param.grad is not None:
                    self.writer.add_histogram(f'Critic_Weights/{name}', param.data, step)
                    self.writer.add_histogram(f'Critic_Gradients/{name}', param.grad.data, step)
    
    def log_episode_rewards(self, step, rewards):
        """
        记录回合奖励分布
        
        Args:
            step: 步数
            rewards: 奖励列表
        """
        if len(rewards) > 0:
            self.writer.add_histogram('Episode/Reward_Distribution', np.array(rewards), step)
            self.writer.add_scalar('Episode/Mean_Reward', np.mean(rewards), step)
            self.writer.add_scalar('Episode/Max_Reward', np.max(rewards), step)
            self.writer.add_scalar('Episode/Min_Reward', np.min(rewards), step)
    
    def log_custom_metric(self, metric_name, value, step, category='Custom'):
        """
        记录自定义指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            step: 步数
            category: 分类名称
        """
        self.writer.add_scalar(f'{category}/{metric_name}', value, step)
    
    def log_text(self, tag, text, step):
        """
        记录文本信息
        
        Args:
            tag: 标签
            text: 文本内容
            step: 步数
        """
        self.writer.add_text(tag, text, step)
    
    def close(self):
        """关闭TensorBoard writer"""
        if hasattr(self, 'writer'):
            self.writer.close()
            print(f"📊 TensorBoard日志已保存: {self.log_dir}")
    
    def __del__(self):
        """析构函数，确保writer被正确关闭"""
        self.close()


class LegacyCSVTracker:
    """保持向后兼容的CSV记录器"""
    
    def __init__(self, parameters, vars_string, project_string):
        self.vars_string = vars_string
        self.project_string = project_string
        self.foldername = parameters.save_foldername
        self.all_tracker = [[[],0.0,[]] for _ in vars_string]
        self.counter = 0
        self.conv_size = 10
        
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
    
    def update(self, updates, generation):
        """保持原有的CSV更新逻辑"""
        self.counter += 1
        for update, var in zip(updates, self.all_tracker):
            if update == None: continue
            var[0].append(update)

        # Constrain size of convolution
        for var in self.all_tracker:
            if len(var[0]) > self.conv_size: var[0].pop(0)

        # Update new average
        for var in self.all_tracker:
            if len(var[0]) == 0: continue
            var[1] = sum(var[0])/float(len(var[0]))

        if self.counter % 4 == 0:  # Save to csv file
            for i, var in enumerate(self.all_tracker):
                if len(var[0]) == 0: continue
                var[2].append(np.array([generation, var[1]]))
                filename = os.path.join(self.foldername, self.vars_string[i] + self.project_string)
                try:
                    np.savetxt(filename, np.array(var[2]), fmt='%.3f', delimiter=',')
                except:
                    print('Failed to save progress')