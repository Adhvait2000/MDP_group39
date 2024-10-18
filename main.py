from Simulator.simulator_mgr import *


if __name__ == "__main__":
    # run_simulator()  # run_minimal(False)
    # run_minimal(False)

    # data_from_rpi = [x, y, f, obstacle_id]  // f = either -90 0 90 180, 0 means EAST, 90 means NORTH, 180 means LEFT ...
    obstacles_random = [[100, 70, 180, 0], [130, 20, 0, 1], [190, 90, 180, 2], [170, 180, -90, 3], [70, 120, 90, 4], [10, 180, -90, 5]]
    obstacles_from_sample_arena_blackboard = [[10, 180, -90, 1],[60, 120, 90, 2],[150, 160, 180, 3],[190, 90, 180, 4],[130, 20, 0, 5]]

    obstacles_from_rules_for_task_wk89_word = [[50, 90, -90, 1], [70, 140, 180, 2], [120, 90, 0, 3], [150, 150, -90, 4], [150, 40, 180, 5]]
    obstacle_data = [[105, 75,180, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3], [75, 125, 90, 4], [15, 185, -90, 5]]
    # test = [[70,90,0,1],[110, 130, 0, 2], [150, 60, 90, 3], [180, 140, 180, 4], [70, 170, 0, 5] ]
    # test2 = [[20,20,0,1],[50, 70, 0, 2], [100, 40, 0, 3], [20, 110, 0, 4], [110, 100, 0, 5] ]
    test4 = [[100, 70, 90, 0], [130, 20, 0, 1], [190, 90, 180, 2], [170, 180, -90, 3], [70, 120, 90, 4], [10, 180, -90, 5]]
    test5 = [[110, 80, 90, 0], [140, 30, 0, 1], [170, 100, 180, 2], [180, 190, -90, 3], [80, 130, 90, 4], [20, 190, -90, 5]]
    
    wk_simulator_w_obstacles(test5)
    # wk_simulator_w_obstacles(obstacles_from_sample_arena_blackboard)

    # wk_simulator_w_obstacles(obstacle_data)
    # wk_real_run(False)

"""
    1. from simulator_mgr
    2. class AlgoSimulator(obs)
    3. in either self.execute or self.render()
        - self.robot.brain.plan_path()

"""