import os
from collections import namedtuple

from pygad import GA


class PyraminxGA:
    def __init__(self):
        self._makedir()

    def _is_solved(self, stage: int, *, target: int | None = None, fitness: int | None = None):
        if target:
            return target == PyraminxGA.TARGET[stage - 1]
        if fitness:
            return fitness <= self.max_fitness_solved[stage - 1]
        raise ValueError("Either target or fitness must be provided")

    def _fitness(self, stage: int):
        pyraminx = self.pyraminx.copy()

        def fitness(ga, solution, index):
            match stage:
                case 1:
                    target_function = pyraminx.small_corners_solved
                case 2:
                    target_function = pyraminx.large_corners_solved
                case 3:
                    target_function = pyraminx.middle_pieces_solved
                case 4:
                    target_function = pyraminx.sum_num_colors_on_a_face

            steps = 0
            target = target_function()

            for move in solution:
                if self._is_solved(stage, target=target):
                    break
                pyraminx.move(move)
                target = max(target, target_function())
                steps += 1

            return target - steps

        return fitness

    def _run_stage(self, stage: int, save_dir: str = "data", **kwargs):
        ga = GA(**kwargs)
        ga.run()
        ga.plot_fitness(save_dir=f"{save_dir}/fitness_stage{stage}.png")
        solution, fitness, _ = ga.best_solution()
        return PyraminxGA.StageResult(solution, fitness, ga.generations_completed, self._is_solved(stage, fitness=fitness))

    def run(self, **kwargs):
        common_kwargs = {
            "num_generations": 100,  # [100, 1000]
            "num_parents_mating": 2,  # [2, 5]
            "sol_per_pop": 100,  # [100, 1000]
            "gene_type": str,
            "parent_selection_type": "tournament",
            "keep_elitism": None,
            "crossover_type": "single_point",
            "crossover_probability": 0.7,  # [0.5, 0.9]
            "mutation_type": "random",  # only one gene
            "mutation_probability": 0.05,  # [0.01, 0.1]
            "mutation_by_replacement": False,
            "mutation_percent_genes": 'default',  # based on population size and the number of generations
            "mutation_num_genes": None,  # number of genes in each solution will be randomly selected for mutation, covering mutation_percent_genes
            "on_start": None,
            "on_fitness": None,
            "on_parents": None,
            "on_crossover": None,
            "on_mutation": None,
            "on_generation": None
        }
        stage_kwargs = tuple({"fitness_func": self._fitness(stage=stage), "num_genes": num_genes, "gene_space": gene_space}
                             for stage, (num_genes, gene_space) in enumerate(zip(self.num_genes, PyraminxGA.GENE_SPACES)))

        solved = True
        for stage in range(1, 5):
            self.results.append(self._run_stage(stage, **(common_kwargs | stage_kwargs[stage - 1])))
            if not self._is_solved(stage, fitness=self.results[-1].fitness):
                solved = False
                break

        return solved

    def best_solution(self):
        pass

    def best_solution_generation(self):
        pass

    def _makedir(self):
        os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/..")
        if not os.path.exists("data"):
            os.makedirs("data")