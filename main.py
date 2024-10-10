from Simulator.simulator_mgr import *


if __name__ == "__main__":
    # run_simulator()  # run_minimal(False)
    # run_minimal(False)

    # data_from_rpi = [x, y, f, obstacle_id]  // f = either -90 0 90 180, 0 means EAST, 90 means NORTH, 180 means LEFT ...
    obstacles_random = [[105, 75, 180, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3], [75, 125, 90, 4], [15, 185, -90, 5]]
    obstacles_from_sample_arena_blackboard = [
        [15, 185, -90, 0],
        [65, 125, 90, 1],
        [155, 165, 180, 3],
        [195, 95, 180, 4],
        [135, 25, 0, 5],
    ]

    obstacles_from_rules_for_task_wk89_word = [[55, 95, -90, 1], [75, 145, 180, 2], [125, 95, 0, 3], [155, 155, -90, 4], [155, 45, 180, 5]]
    obstacle_data = [[105, 75, 90, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3], [75, 125, 90, 4], [15, 185, -90, 5]]
    # wk_simulator_w_obstacles(obstacles_random)
    # wk_simulator_w_obstacles(obstacles_from_sample_arena_blackboard)

    # wk_simulator_w_obstacles(obstacles_from_rules_for_task_wk89_word)
    wk_real_run(False)

"""
    1. from simulator_mgr
    2. class AlgoSimulator(obs)
    3. in either self.execute or self.render()
        - self.robot.brain.plan_path()

"""