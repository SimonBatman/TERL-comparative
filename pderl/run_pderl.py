import numpy as np, os, time, random
from core import mod_utils as utils, agent
from core.tensorboard_tracker import TensorBoardTracker, LegacyCSVTracker
import gym, torch
import argparse
import pickle
from core.operator_runner import OperatorRunner
from parameters import Parameters

parser = argparse.ArgumentParser()
parser.add_argument('-env', help='Environment Choices: (Swimmer-v2) (HalfCheetah-v2) (Hopper-v2) ' +
                                 '(Walker2d-v2) (Ant-v2)', required=True, type=str)
parser.add_argument('-seed', help='Random seed to be used', type=int, default=7)
parser.add_argument('-disable_cuda', help='Disables CUDA', action='store_true')
parser.add_argument('-render', help='Render gym episodes', action='store_true')
parser.add_argument('-sync_period', help="How often to sync to population", type=int)
parser.add_argument('-novelty', help='Use novelty exploration', action='store_true')
parser.add_argument('-proximal_mut', help='Use safe mutation', action='store_true')
parser.add_argument('-distil', help='Use distilation crossover', action='store_true')
parser.add_argument('-distil_type', help='Use distilation crossover. Choices: (fitness) (distance)',
                    type=str, default='fitness')
parser.add_argument('-per', help='Use Prioritised Experience Replay', action='store_true')
parser.add_argument('-mut_mag', help='The magnitude of the mutation', type=float, default=0.05)
parser.add_argument('-mut_noise', help='Use a random mutation magnitude', action='store_true')
parser.add_argument('-verbose_mut', help='Make mutations verbose', action='store_true')
parser.add_argument('-verbose_crossover', help='Make crossovers verbose', action='store_true')
parser.add_argument('-logdir', help='Folder where to save results', type=str, required=True)
parser.add_argument('-opstat', help='Store statistics for the variation operators', action='store_true')
parser.add_argument('-opstat_freq', help='Frequency (in generations) to store operator statistics', type=int, default=1)
parser.add_argument('-save_periodic', help='Save actor, critic and memory periodically', action='store_true')
parser.add_argument('-next_save', help='Generation save frequency for save_periodic', type=int, default=200)
parser.add_argument('-test_operators', help='Runs the operator runner to test the operators', action='store_true')
parser.add_argument('-use_tensorboard', help='Use TensorBoard for logging instead of CSV files', action='store_true')
parser.add_argument('-tensorboard_dir', help='TensorBoard log directory', type=str, default=None)
parser.add_argument('-log_weights', help='Log network weights to TensorBoard', action='store_true')
parser.add_argument('-log_freq', help='Frequency to log detailed metrics', type=int, default=10)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    parameters = Parameters(parser)  # Inject the cla arguments in the parameters object
    
    # 初始化日志记录器
    if parameters.use_tensorboard:
        # 使用TensorBoard记录
        tb_tracker = TensorBoardTracker(parameters, parameters.tensorboard_dir)
        print("📊 使用TensorBoard记录训练过程")
        # 保持CSV兼容性（可选）
        use_csv_backup = False
    else:
        # 使用传统CSV记录
        tb_tracker = None
        use_csv_backup = True
        print("📄 使用CSV文件记录训练过程")
    
    # CSV trackers（用于向后兼容或备份）
    if use_csv_backup or not parameters.use_tensorboard:
        tracker = LegacyCSVTracker(parameters, ['erl'], '_score.csv')
        frame_tracker = LegacyCSVTracker(parameters, ['frame_erl'], '_score.csv')
        time_tracker = LegacyCSVTracker(parameters, ['time_erl'], '_score.csv')
        ddpg_tracker = LegacyCSVTracker(parameters, ['ddpg'], '_score.csv')
        selection_tracker = LegacyCSVTracker(parameters, ['elite', 'selected', 'discarded'], '_selection.csv')
    else:
        tracker = frame_tracker = time_tracker = ddpg_tracker = selection_tracker = None

    # Create Env
    env = utils.NormalizedActions(gym.make(parameters.env_name))
    parameters.action_dim = env.action_space.shape[0]
    parameters.state_dim = env.observation_space.shape[0]

    # Write the parameters to a the info file and print them
    parameters.write_params(stdout=True)

    # Seed
    env.seed(parameters.seed)
    torch.manual_seed(parameters.seed)
    np.random.seed(parameters.seed)
    random.seed(parameters.seed)

    # Tests the variation operators after that is saved first with -save_periodic
    if parameters.test_operators:
        operator_runner = OperatorRunner(parameters, env)
        operator_runner.run()
        exit()

    # Create Agent
    agent = agent.Agent(parameters, env)
    print('Running', parameters.env_name, ' State_dim:', parameters.state_dim, ' Action_dim:', parameters.action_dim)

    next_save = parameters.next_save; time_start = time.time()
    while agent.num_frames <= parameters.num_frames:
        stats = agent.train()
        best_train_fitness = stats['best_train_fitness']
        erl_score = stats['test_score']
        elite_index = stats['elite_index']
        ddpg_reward = stats['ddpg_reward']
        policy_gradient_loss = stats['pg_loss']
        behaviour_cloning_loss = stats['bc_loss']
        population_novelty = stats['pop_novelty']

        # 计算进化统计
        elite = agent.evolver.selection_stats['elite']/agent.evolver.selection_stats['total']
        selected = agent.evolver.selection_stats['selected'] / agent.evolver.selection_stats['total']
        discarded = agent.evolver.selection_stats['discarded'] / agent.evolver.selection_stats['total']
        
        # 控制台输出
        avg_score = tracker.all_tracker[0][1] if tracker and len(tracker.all_tracker[0][0]) > 0 else 0.0
        print('#Games:', agent.num_games, '#Frames:', agent.num_frames,
              ' Train_Max:', '%.2f'%best_train_fitness if best_train_fitness is not None else None,
              ' Test_Score:','%.2f'%erl_score if erl_score is not None else None,
              ' Avg:','%.2f'%avg_score,
              ' ENV:  '+ parameters.env_name,
              ' DDPG Reward:', '%.2f'%ddpg_reward,
              ' PG Loss:', '%.4f' % policy_gradient_loss)
        print()
        
        # TensorBoard记录
        if tb_tracker:
            # 记录性能指标
            tb_tracker.log_performance(
                step=agent.num_frames,
                erl_score=erl_score,
                ddpg_reward=ddpg_reward,
                best_train_fitness=best_train_fitness
            )
            
            # 记录损失
            tb_tracker.log_losses(
                step=agent.num_frames,
                pg_loss=policy_gradient_loss,
                bc_loss=behaviour_cloning_loss
            )
            
            # 记录进化统计
            tb_tracker.log_evolution_stats(
                step=agent.num_frames,
                elite_ratio=elite,
                selected_ratio=selected,
                discarded_ratio=discarded,
                pop_novelty=population_novelty
            )
            
            # 记录时间相关指标
            current_time = time.time() - time_start
            tb_tracker.log_custom_metric('Time_Elapsed_Hours', current_time/3600, agent.num_frames, 'Training')
            tb_tracker.log_custom_metric('Games_Completed', agent.num_games, agent.num_frames, 'Training')
            
            # 定期记录网络权重（可选）
            if parameters.log_weights and agent.num_games % parameters.log_freq == 0:
                if elite_index is not None:
                    tb_tracker.log_network_weights(
                        step=agent.num_frames,
                        actor_net=agent.pop[elite_index].actor,
                        critic_net=agent.rl_agent.critic
                    )
        
        # CSV记录（向后兼容）
        if tracker:
            tracker.update([erl_score], agent.num_games)
            frame_tracker.update([erl_score], agent.num_frames)
            time_tracker.update([erl_score], time.time()-time_start)
            ddpg_tracker.update([ddpg_reward], agent.num_frames)
            selection_tracker.update([elite, selected, discarded], agent.num_frames)

        # Save Policy
        if agent.num_games > next_save:
            next_save += parameters.next_save
            if elite_index is not None:
                torch.save(agent.pop[elite_index].actor.state_dict(), os.path.join(parameters.save_foldername,
                                                                                   'evo_net.pkl'))

                if parameters.save_periodic:
                    save_folder = os.path.join(parameters.save_foldername, 'models')
                    if not os.path.exists(save_folder):
                        os.makedirs(save_folder)

                    actor_save_name = os.path.join(save_folder, 'evo_net_actor_{}.pkl'.format(next_save))
                    critic_save_name = os.path.join(save_folder, 'evo_net_critic_{}.pkl'.format(next_save))
                    buffer_save_name = os.path.join(save_folder, 'champion_buffer_{}.pkl'.format(next_save))

                    torch.save(agent.pop[elite_index].actor.state_dict(), actor_save_name)
                    torch.save(agent.rl_agent.critic.state_dict(), critic_save_name)
                    with open(buffer_save_name, 'wb+') as buffer_file:
                        pickle.dump(agent.rl_agent.buffer, buffer_file)

            print("Progress Saved")
    
    # 训练结束时的清理工作
    if tb_tracker:
        # 记录最终统计信息
        total_time = time.time() - time_start
        tb_tracker.log_text('Training_Summary', 
                           f'Training completed!\n'
                           f'Total frames: {agent.num_frames}\n'
                           f'Total games: {agent.num_games}\n'
                           f'Total time: {total_time/3600:.2f} hours\n'
                           f'Environment: {parameters.env_name}\n'
                           f'Final ERL score: {erl_score:.2f}' if erl_score else 'N/A', 
                           agent.num_frames)
        
        # 关闭TensorBoard writer
        tb_tracker.close()
        print("📊 TensorBoard日志已保存并关闭")
    
    print("🎉 训练完成！")
    if parameters.use_tensorboard and parameters.tensorboard_dir:
        print(f"📈 查看TensorBoard: tensorboard --logdir {parameters.tensorboard_dir}")











