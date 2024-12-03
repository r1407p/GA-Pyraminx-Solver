import os
from collections import namedtuple
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pygad import GA

from Pyraminx import Pyraminx


fitnesses = []
global_pyraminx = Pyraminx()
global_pyraminx.faces = {'D': [['Y'], ['G', 'B', 'Y'], ['B', 'G', 'R', 'R', 'R']],
                         'F': [['Y'], ['Y', 'Y', 'B'], ['G', 'Y', 'B', 'B', 'B']],
                         'L': [['R'], ['R', 'R', 'G'], ['R', 'Y', 'B', 'B', 'Y']],
                         'R': [['G'], ['Y', 'G', 'G'], ['G', 'G', 'R', 'R', 'B']]}

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

    # TODO: parameterize PyraminxGA.TARGET
    TARGET = [36, 4, 4, 3, -1]

    StageResult = namedtuple("StageResult", ["solution", "fitness", "generation", "is_solved"])

    def __init__(self, pyraminx: Pyraminx | None = None, accept_ratio: float = 0.9, data_dir: str = "data", **kwargs):
        if pyraminx:
            self.pyraminx = pyraminx
        else:
            self.pyraminx = Pyraminx()
            self.pyraminx.shuffle()

        # for expert mode
        self.num_genes = kwargs.get("num_genes", None)
        self.fitness_accepted = tuple(target * accept_ratio for target in PyraminxGA.TARGET[1:])

        self.results = []

        self.data_dir = data_dir
        PyraminxGA._makedir(data_dir)

    @staticmethod
    def _makedir(dir: str):
        os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/..")
        if not os.path.exists(dir):
            os.makedirs(dir)

    def _is_accepted(self, stage: int, fitness: int):
        return self.fitness_accepted[stage - 1] <= fitness

    @staticmethod
    def _is_solved(stage: int, target: int):
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
                    return sum(max(face) for face in pyraminx.entropy())
                case 1:
                    return pyraminx.small_corners_solved()
                case 2:
                    return pyraminx.large_corners_solved()
                case 3:
                    return pyraminx.middle_pieces_solved()
                case 4:
                    return -max(pyraminx.num_colors_on_a_face())
                case _:
                    return 0

        steps = 0
        target = target_function()
        for move in PyraminxGA._genes2moves(stage, genes):
            if PyraminxGA._is_solved(stage, target=target):
                break
            pyraminx.mixture_moves(move)
            target = max(target, target_function())
            steps += 1

        return target, steps

    @staticmethod
    def _fitness(pyraminx: Pyraminx, stage: int, penalty_scaling: float = 0.01):
        def fitness(ga, solution, index):
            target, steps = PyraminxGA._best_target(pyraminx, stage, solution)
            return target - steps * penalty_scaling
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

    def _run_stage(self, stage: int, save_dir: str = "", index: int = 0, **kwargs):
        ga = GA(suppress_warnings=True, **kwargs)
        ga.run()

        # TODO: plot fitness
        save_dir = f"{self.data_dir}/{save_dir}"
        PyraminxGA._makedir(save_dir)

        fitness_min = tuple(map(np.min, fitnesses))
        fitness_mean = tuple(map(np.mean, fitnesses))
        fitness_max = tuple(map(np.max, fitnesses))

        plt.figure(figsize=(10, 8))
        plt.fill_between(range(len(fitnesses)), fitness_min, fitness_max, color="lightblue", alpha=0.6, label="Range")
        sns.lineplot(x=range(len(fitnesses)), y=fitness_mean, label="Mean", color="blue", alpha=0.6)

        plt.title("Min, Max, and Mean Fitness Across Generations")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.legend(bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.savefig(f"{save_dir}/stage{stage}_{index}.png")
        plt.close()

        fitnesses.clear()

        solution, fitness, _ = ga.best_solution()
        return PyraminxGA.StageResult(solution, fitness, ga.best_solution_generation, self._is_accepted(stage, fitness=fitness))  # type: ignore

    # TODO: review following methods

    @staticmethod
    def _on_start(ga: GA):
        # uncomment for verbose evolution
        pyraminx = global_pyraminx.copy()
        best_solution, _, _ = ga.best_solution()
        valid_moves = PyraminxGA._apply_valid_moves(pyraminx, stage=0, moves=list(best_solution))
        pyraminx.display()
        print(valid_moves)
        print(ga.generations_completed)

    @staticmethod
    def _on_generation(ga: GA):
        fitnesses.append(ga.last_generation_fitness)
        # uncomment for verbose evolution
        if ga.generations_completed % 256 == 0:
            pyraminx = global_pyraminx.copy()

            best_solution, _, _ = ga.best_solution()
            valid_moves = PyraminxGA._apply_valid_moves(pyraminx, stage=0, moves=list(best_solution))
            pyraminx.display()
            print(valid_moves)
            print(ga.generations_completed)

    @staticmethod
    def _expand_high_level_moves(valid_moves: tuple[str, ...]):
        high_level_moves = []
        for move in valid_moves:
            match move:
                case "E":
                    high_level_moves.extend(["R", "U'", "R'"])
                case "F":
                    high_level_moves.extend(["L'", "U", "L"])
                case "G":
                    high_level_moves.extend(["B", "U'", "B'"])
                case "H":
                    high_level_moves.extend(["B'", "U", "B"])
                case "I":
                    high_level_moves.extend(["R'", "U", "R"])
                case "J":
                    high_level_moves.extend(["L", "U'", "L'"])
                case "X":
                    high_level_moves.extend(["R", "U'", "R'", "U'", "R", "U'", "R'"])
                case "Y":
                    high_level_moves.extend(["R", "U", "R'", "U", "R", "U", "R'"])
                case "Z":
                    high_level_moves.extend(["R'", "L", "R", "L'", "U", "L'", "U'", "L"])
                case _:
                    high_level_moves.append(move)
        return high_level_moves


    def run(self, mode: Mode = Mode.EXPERT, save_dir: str = "", index: int = 0, verbose: bool = False, **kwargs):
        # TODO: move num_generations to stage_kwargs
        common_kwargs = {
            "num_generations": 100,  # [100, 1000]
            "num_parents_mating": 2,  # [2, 5]
            "sol_per_pop": 10,  # [100, 1000]
            "gene_type": int,
            "parent_selection_type": "tournament",
            "keep_elitism": 1,
            "crossover_type": "single_point",
            "crossover_probability": 0.7,  # [0.5, 0.9]
            "mutation_type": "random",  # only one gene
            "mutation_probability": 0.05,  # [0.01, 0.1]
            "mutation_by_replacement": False,
            "mutation_percent_genes": 'default',  # based on population size and the number of generations
            "mutation_num_genes": None,  # number of genes in each solution will be randomly selected for mutation, covering mutation_percent_genes
            "on_start": PyraminxGA._on_start,
            "on_fitness": None,
            "on_parents": None,
            "on_crossover": None,
            "on_mutation": None,
            "on_generation": PyraminxGA._on_generation
        }

        self.results.clear()

        pyraminx = self.pyraminx.copy()
        if verbose:
            pyraminx.display()
            print(pyraminx.shuffle_moves)

        self.mode = mode
        match mode:
            case PyraminxGA.Mode.FROM_SCRATCH:
                if not hasattr(self, "num_genes") or not isinstance(self.num_genes, int):
                    self.num_genes = 24
                stage_kwargs = {"num_genes": self.num_genes, "gene_space": range(len(PyraminxGA.GENE_SPACES[0]))}
                self.results.append(self._run_stage(0, fitness_func=PyraminxGA._fitness(pyraminx, 0), save_dir=save_dir, index=index, **(common_kwargs | stage_kwargs | kwargs)))
                valid_moves = PyraminxGA._apply_valid_moves(pyraminx, 0, self.results[-1].solution)
                if verbose:
                    pyraminx.display()
                    print(valid_moves)
            case PyraminxGA.Mode.EXPERT:
                if not hasattr(self, "num_genes") or not isinstance(self.num_genes, tuple):
                    self.num_genes = (8, 8, 18, 6)
                stage_kwargs = tuple({"num_genes": num_genes, "gene_space": range(len(gene_space))}
                                     for num_genes, gene_space in zip(self.num_genes, PyraminxGA.GENE_SPACES[1:]))
                for stage in range(1, 5):
                    self.results.append(self._run_stage(stage, fitness_func=PyraminxGA._fitness(pyraminx, stage), save_dir=save_dir, index=index, **(common_kwargs | stage_kwargs[stage - 1] | kwargs)))
                    valid_moves = PyraminxGA._apply_valid_moves(pyraminx, stage, self.results[-1].solution)
                    if verbose:
                        pyraminx.display()
                        print(valid_moves)
                    if not self.results[-1].is_solved:
                        break

        return sum(map(max, pyraminx.entropy())) == 36

    def best_solution(self, expand: bool = True):
        pyraminx = self.pyraminx.copy()
        aggregated_solution = []
        match self.mode:
            case PyraminxGA.Mode.FROM_SCRATCH:
                aggregated_solution = PyraminxGA._apply_valid_moves(pyraminx, 0, self.results[-1].solution)
            case PyraminxGA.Mode.EXPERT:
                for stage, result in enumerate(self.results, start=1):
                    valid_moves = PyraminxGA._apply_valid_moves(pyraminx, stage, result.solution)
                    if expand and stage > 2:
                        valid_moves = PyraminxGA._expand_high_level_moves(valid_moves)
                    aggregated_solution.extend(valid_moves)
        return tuple(aggregated_solution)

    def best_solution_generation(self):
        return sum(result.generation for result in self.results)

    def best_solution_fitness(self):
        return sum(result.fitness for result in self.results)
