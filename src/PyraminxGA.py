from pygad import GA


class PyraminxGA:
    def __init__(self):
        pass

    def run_stage(self, stage: int, save_dir: str = "data", **kwargs):
        ga = GA(**kwargs)
        ga.run()
        ga.plot_fitness(save_dir=f"{save_dir}/fitness_stage{stage}.png")

    def best_solution(self):
        pass

    def best_solution_generation(self):
        pass

    def run(self):
        pass
