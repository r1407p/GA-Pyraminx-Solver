import os
from collections import namedtuple

from pygad import GA


class PyraminxGA:
    def __init__(self):
        self._makedir()

    def _run_stage(self, stage: int, save_dir: str = "data", **kwargs):
        ga = GA(**kwargs)
        ga.run()
        ga.plot_fitness(save_dir=f"{save_dir}/fitness_stage{stage}.png")
        solution, fitness, _ = ga.best_solution()
        return PyraminxGA.StageResult(solution, fitness, ga.generations_completed, self._is_solved(stage, fitness=fitness))

    def best_solution(self):
        pass

    def best_solution_generation(self):
        pass

    def _makedir(self):
        os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/..")
        if not os.path.exists("data"):
            os.makedirs("data")
