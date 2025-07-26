import os
import torch
from torch.utils.tensorboard import SummaryWriter
import numpy as np


class TensorBoardTracker:
    """TensorBoard logger, replaces CSV file storage"""
    
    def __init__(self, parameters, log_dir=None):
        """
        Initialize TensorBoard logger
        
        Args:
            parameters: Parameter object
            log_dir: TensorBoard log directory, uses parameters.save_foldername if None
        """
        self.parameters = parameters
        
        # Set log directory
        if log_dir is None:
            self.log_dir = os.path.join(parameters.save_foldername, 'tensorboard_logs')
        else:
            self.log_dir = log_dir
            
        # Create directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize SummaryWriter
        self.writer = SummaryWriter(log_dir=self.log_dir)
        
        # Log hyperparameters
        self._log_hyperparameters()
        
        print(f"[TensorBoard] Logging enabled: {self.log_dir}")
        print(f"[INFO] View training progress: tensorboard --logdir {self.log_dir}")
    
    def _log_hyperparameters(self):
        """Log hyperparameters"""
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
        
        # Add boolean parameters
        bool_params = ['use_cuda', 'novelty', 'proximal_mut', 'distil', 'per']
        for param in bool_params:
            if hasattr(self.parameters, param):
                hparams[param] = getattr(self.parameters, param)
        
        # Log hyperparameters
        self.writer.add_hparams(hparams, {})
    
    def log_training_step(self, step, metrics):
        """
        Log training step metrics
        
        Args:
            step: Training step (frames or episodes)
            metrics: Metrics dictionary
        """
        for metric_name, value in metrics.items():
            if value is not None:
                self.writer.add_scalar(f'Training/{metric_name}', value, step)
    
    def log_performance(self, step, erl_score, ddpg_reward, best_train_fitness=None):
        """
        Log performance metrics
        
        Args:
            step: Step number
            erl_score: ERL test score
            ddpg_reward: DDPG reward
            best_train_fitness: Best training fitness
        """
        if erl_score is not None:
            self.writer.add_scalar('Performance/ERL_Test_Score', erl_score, step)
        
        if ddpg_reward is not None:
            self.writer.add_scalar('Performance/DDPG_Reward', ddpg_reward, step)
        
        if best_train_fitness is not None:
            self.writer.add_scalar('Performance/Best_Train_Fitness', best_train_fitness, step)
    
    def log_losses(self, step, pg_loss=None, bc_loss=None, critic_loss=None):
        """
        Log loss functions
        
        Args:
            step: Step number
            pg_loss: Policy gradient loss
            bc_loss: Behavior cloning loss
            critic_loss: Critic loss
        """
        if pg_loss is not None:
            self.writer.add_scalar('Losses/Policy_Gradient_Loss', pg_loss, step)
        
        if bc_loss is not None:
            self.writer.add_scalar('Losses/Behavior_Cloning_Loss', bc_loss, step)
        
        if critic_loss is not None:
            self.writer.add_scalar('Losses/Critic_Loss', critic_loss, step)
    
    def log_evolution_stats(self, step, elite_ratio, selected_ratio, discarded_ratio, pop_novelty=None):
        """
        Log evolution statistics
        
        Args:
            step: Step number
            elite_ratio: Elite ratio
            selected_ratio: Selection ratio
            discarded_ratio: Discard ratio
            pop_novelty: Population novelty
        """
        self.writer.add_scalar('Evolution/Elite_Ratio', elite_ratio, step)
        self.writer.add_scalar('Evolution/Selected_Ratio', selected_ratio, step)
        self.writer.add_scalar('Evolution/Discarded_Ratio', discarded_ratio, step)
        
        if pop_novelty is not None:
            self.writer.add_scalar('Evolution/Population_Novelty', pop_novelty, step)
    
    def log_network_weights(self, step, actor_net, critic_net=None):
        """
        Log network weight distributions
        
        Args:
            step: Step number
            actor_net: Actor network
            critic_net: Critic network
        """
        # Log Actor network weights
        for name, param in actor_net.named_parameters():
            if param.grad is not None:
                self.writer.add_histogram(f'Actor_Weights/{name}', param.data, step)
                self.writer.add_histogram(f'Actor_Gradients/{name}', param.grad.data, step)
        
        # Log Critic network weights
        if critic_net is not None:
            for name, param in critic_net.named_parameters():
                if param.grad is not None:
                    self.writer.add_histogram(f'Critic_Weights/{name}', param.data, step)
                    self.writer.add_histogram(f'Critic_Gradients/{name}', param.grad.data, step)
    
    def log_episode_rewards(self, step, rewards):
        """
        Log episode reward distribution
        
        Args:
            step: Step number
            rewards: Reward list
        """
        if len(rewards) > 0:
            self.writer.add_histogram('Episode/Reward_Distribution', np.array(rewards), step)
            self.writer.add_scalar('Episode/Mean_Reward', np.mean(rewards), step)
            self.writer.add_scalar('Episode/Max_Reward', np.max(rewards), step)
            self.writer.add_scalar('Episode/Min_Reward', np.min(rewards), step)
    
    def log_custom_metric(self, metric_name, value, step, category='Custom'):
        """
        Log custom metrics
        
        Args:
            metric_name: Metric name
            value: Metric value
            step: Step number
            category: Category name
        """
        self.writer.add_scalar(f'{category}/{metric_name}', value, step)
    
    def log_text(self, tag, text, step):
        """
        Log text information
        
        Args:
            tag: Tag
            text: Text content
            step: Step number
        """
        self.writer.add_text(tag, text, step)
    
    def close(self):
        """Close TensorBoard writer"""
        if hasattr(self, 'writer'):
            self.writer.close()
            print(f"[TensorBoard] Logs saved: {self.log_dir}")
    
    def __del__(self):
        """Destructor, ensures writer is properly closed"""
        self.close()


class LegacyCSVTracker:
    """Legacy CSV tracker for backward compatibility"""
    
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
        """Maintain original CSV update logic"""
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