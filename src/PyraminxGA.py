import os
from collections import namedtuple
from enum import Enum

from pygad import GA

from Pyraminx import Pyraminx


class PyraminxGA:
    class Mode(Enum):
        EXPERT = 0
        FROM_SCRATCH = 1

    NUM_STAGES = 4
    GENE_SPACES = (["r", "l", "b", "u", "r'", "l'", "b'", "u'", "R", "L", "B", "U", "R'", "L'", "B'", "U'"],
                   ["r", "l", "b", "u", "r'", "l'", "b'", "u'"],
                   ["R", "L", "B", "U", "R'", "L'", "B'", "U'"],
                   ["E", "F", "G", "H", "I", "J", "U", "U'"],
                   ["X", "Y", "Z", "U", "U'"])
    TARGET = (0, 4, 4, 3, 4)

    StageResult = namedtuple("StageResult", ["solution", "fitness", "generation", "is_solved"])

    def __init__(self):
        self.pyraminx = Pyraminx()
        self.pyraminx.shuffle()

        self.num_genes = (8, 8, 32, 12)
        self.min_fitness_solved = tuple(target - num_genes * 0.01 for target, num_genes in zip(PyraminxGA.TARGET[1:], self.num_genes))

        self.results = []

        PyraminxGA._makedir()

    def _is_solved_fitness(self, stage: int, fitness: int):
        return self.min_fitness_solved[stage - 1] <= fitness

    @staticmethod
    def _is_solved_target(stage: int, target: int):
        return target == PyraminxGA.TARGET[stage]

    @staticmethod
    def _gene2move(stage: int, move: int):
        return PyraminxGA.GENE_SPACES[stage][move]

    @staticmethod
    def _genes2moves(stage: int, moves: list[int]):
        return tuple(PyraminxGA._gene2move(stage, move) for move in moves)

    @staticmethod
    def _best_target(pyraminx: Pyraminx, stage: int, genes: list[int]):
        pyraminx = pyraminx.copy()

        def target_function():
            match stage:
                case 0:
                    return pyraminx.small_corners_solved() + pyraminx.large_corners_solved() + pyraminx.middle_pieces_solved() + sum(pyraminx.num_colors_on_a_face())
                case 1:
                    return pyraminx.small_corners_solved()
                case 2:
                    return pyraminx.large_corners_solved()
                case 3:
                    return pyraminx.middle_pieces_solved()
                case 4:
                    return sum(pyraminx.num_colors_on_a_face())
                case _:
                    return 0

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
            return target - steps * 0.01
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
        return PyraminxGA.StageResult(solution, fitness, ga.best_solution_generation, self._is_solved_fitness(stage, fitness=fitness))  # type: ignore

    def run(self, mode: Mode = Mode.EXPERT, **kwargs):
        common_kwargs = {
            "num_generations": 10000,  # [100, 1000]
            "num_parents_mating": 2,  # [2, 5]
            "sol_per_pop": 2,  # [100, 1000]
            "gene_type": int,
            "parent_selection_type": "tournament",
            "keep_elitism": 2,
            "crossover_type": "single_point",
            "crossover_probability": 0.7,  # [0.5, 0.9]
            "mutation_type": "random",  # only one gene
            "mutation_probability": 0.1,  # [0.01, 0.1]
            "mutation_by_replacement": True,
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
                             for num_genes, gene_space in zip(self.num_genes, PyraminxGA.GENE_SPACES[1:]))

        pyraminx = self.pyraminx.copy()
        self.results.clear()

        self.mode = mode
        match mode:
            case PyraminxGA.Mode.FROM_SCRATCH:
                stage_kwargs = {"num_genes": 36, "gene_space": range(len(PyraminxGA.GENE_SPACES[0]))}
                self.results.append(self._run_stage(0, fitness_func=PyraminxGA._fitness(pyraminx, 0), **(common_kwargs | stage_kwargs | kwargs)))
            case PyraminxGA.Mode.EXPERT:
                pyraminx.display()
                for stage in range(1, 5):
                    self.results.append(self._run_stage(stage, fitness_func=PyraminxGA._fitness(pyraminx, stage), **(common_kwargs | stage_kwargs[stage - 1] | kwargs)))
                    print(f"{self.results[-1].fitness=}")
                    if not self.results[-1].is_solved:
                        break
                    PyraminxGA._apply_valid_moves(pyraminx, stage, self.results[-1].solution)
                    pyraminx.display()

        return self.results[-1].is_solved

    def best_solution(self):
        pyraminx = self.pyraminx.copy()
        aggregated_solution = []
        match self.mode:
            case PyraminxGA.Mode.FROM_SCRATCH:
                aggregated_solution = PyraminxGA._apply_valid_moves(pyraminx, 0, self.results[-1].solution)
            case PyraminxGA.Mode.EXPERT:
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
