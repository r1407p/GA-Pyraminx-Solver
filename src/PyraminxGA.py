import os
from collections import namedtuple

from pygad import GA
from Pyraminx import Pyraminx


class PyraminxGA:
    NUM_STAGES = 4
    GENE_SPACES = (["r", "l", "b", "u", "r'", "l'", "b'", "u'"],
                   ["R", "L", "B", "U", "R'", "L'", "B'", "U'"],
                   ["E", "F", "G", "H", "I", "J", "U", "U'"],
                   ["X", "Y", "Z", "U", "U'"])
    TARGET = (4, 4, 3, 4)

    StageResult = namedtuple("StageResult", ["solution", "fitness", "generation", "is_solved"])

    def __init__(self):
        self.pyraminx = Pyraminx()
        self.pyraminx.shuffle()

        self.num_genes = (8, 8, 20, 12)
        self.min_fitness_solved = tuple(target - num_genes for target, num_genes in zip(PyraminxGA.TARGET, self.num_genes))

        self.results = []

        PyraminxGA._makedir()

    def _is_solved_fitness(self, stage: int, fitness: int):
        return self.min_fitness_solved[stage - 1] <= fitness

    @staticmethod
    def _is_solved_target(stage: int, target: int):
        return target == PyraminxGA.TARGET[stage - 1]

    @staticmethod
    def _gene2move(stage: int, move: int):
        return PyraminxGA.GENE_SPACES[stage - 1][move]

    @staticmethod
    def _genes2moves(stage: int, moves: list[int]):
        return tuple(PyraminxGA._gene2move(stage, move) for move in moves)

    @staticmethod
    def _best_target(pyraminx: Pyraminx, stage: int, genes: list[int]):
        pyraminx = pyraminx.copy()

        match stage:
            case 1:
                target_function = pyraminx.small_corners_solved
            case 2:
                target_function = pyraminx.large_corners_solved
            case 3:
                target_function = pyraminx.middle_pieces_solved
            case 4:
                def target_function(): return sum(pyraminx.num_colors_on_a_face())

        steps = 0
        target = target_function()
        for gene in genes:
            if PyraminxGA._is_solved_target(stage, target=target):
                break
            pyraminx.mixture_moves(PyraminxGA._gene2move(stage, gene))
            target = max(target, target_function())
            steps += 1

        return target, steps

    @staticmethod
    def _fitness(pyraminx: Pyraminx, stage: int):
        def fitness(ga, solution, index):
            target, steps = PyraminxGA._best_target(pyraminx, stage, solution)
            return target - steps
        return fitness

    @staticmethod
    def _valid_moves(pyraminx: Pyraminx, stage: int, moves: list[int]):
        _, steps = PyraminxGA._best_target(pyraminx, stage, moves)
        return PyraminxGA._genes2moves(stage, moves[:steps])

    @staticmethod
    def _apply_valid_moves(pyraminx: Pyraminx, stage: int, moves: list[int]):
        valid_moves = PyraminxGA._valid_moves(pyraminx, stage, moves)
        for move in valid_moves:
            pyraminx.mixture_moves(move)
        return valid_moves

    def _run_stage(self, stage: int, save_dir: str = "data", **kwargs):
        ga = GA(**kwargs)
        ga.run()
        ga.plot_fitness(save_dir=f"{save_dir}/fitness_stage{stage}.png")
        solution, fitness, _ = ga.best_solution()
        return PyraminxGA.StageResult(solution, fitness, ga.best_solution_generation, self._is_solved_fitness(stage, fitness=fitness))

    def run(self, **kwargs):
        common_kwargs = {
            "num_generations": 100,  # [100, 1000]
            "num_parents_mating": 2,  # [2, 5]
            "sol_per_pop": 100,  # [100, 1000]
            "gene_type": int,
            "parent_selection_type": "tournament",
            "keep_elitism": 100,
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
        stage_kwargs = tuple({"num_genes": num_genes, "gene_space": range(len(gene_space))}
                             for num_genes, gene_space in zip(self.num_genes, PyraminxGA.GENE_SPACES))

        solved = True
        pyraminx = self.pyraminx.copy()
        for stage in range(1, 5):
            self.results.append(self._run_stage(stage, fitness_func=PyraminxGA._fitness(pyraminx, stage), **(common_kwargs | stage_kwargs[stage - 1] | kwargs)))
            if not self.results[-1].is_solved:
                solved = False
                break
            PyraminxGA._apply_valid_moves(pyraminx, stage, self.results[-1].solution)

        return solved

    def best_solution(self):
        pyraminx = self.pyraminx.copy()
        aggregated_solution = []
        for stage, result in enumerate(self.results, start=1):
            valid_moves = PyraminxGA._apply_valid_moves(pyraminx, stage, result.solution)
            aggregated_solution.extend(valid_moves)
        return aggregated_solution

    def best_solution_generation(self):
        return sum(result.generation for result in self.results)

    @staticmethod
    def _makedir():
        os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/..")
        if not os.path.exists("data"):
            os.makedirs("data")
