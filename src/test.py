from genericpath import isdir
import os
import random

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from Pyraminx import Pyraminx
from PyraminxGA import PyraminxGA


def test(pyraminx: Pyraminx, mode: PyraminxGA.Mode, num_test: int = 30, accept_ratio: float = 0.9, num_genes: tuple[int, int, int, int] | int = (8, 8, 18, 6), verbose: bool = False, **kwargs):
    default_kwargs = {
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
        "mutation_by_replacement": True,
        "mutation_percent_genes": 'default',  # based on population size and the number of generations
        "mutation_num_genes": None,  # number of genes in each solution will be randomly selected for mutation, covering mutation_percent_genes
        "on_start": PyraminxGA._on_start,
        "on_fitness": None,
        "on_parents": None,
        "on_crossover": None,
        "on_mutation": None,
        "on_generation": PyraminxGA._on_generation
    }

    kwargs = default_kwargs | kwargs
    data_dir = f"data.{num_genes}.{kwargs["crossover_type"]}"
    save_dir = f"{mode}_{kwargs["sol_per_pop"]}"

    print(f"testing {num_genes=} crossover_type={kwargs["crossover_type"]} mode={mode} population_size={kwargs["sol_per_pop"]} ...")

    pga = PyraminxGA(pyraminx=pyraminx, accept_ratio=accept_ratio, num_genes=num_genes, data_dir=data_dir)
    for i in range(num_test):
        print(f"{i} th test ...")
        solved = pga.run(mode=mode, save_dir=save_dir, index=i, verbose=verbose, **kwargs)
        best = pga.best_solution(expand=False)
        best_expanded = PyraminxGA._expand_high_level_moves(best)
        # with open(f"{data_dir}/{save_dir}/pyraminx.txt", "a+") as f:
        #     f.write(f"{i}th run\n"
        #             f"\tis solved: {solved}\n"
        #             f"\tlength of best solution: {len(best)}\n"
        #             f"\tlength of expanded best solution: {len(best_expanded)}\n"
        #             f"\tnumber of generation: {pga.best_solution_generation()}\n")


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def aggregate_test_results(data_dir: str = "data"):
    with open(f"{data_dir}/aggregated.txt", "w+") as aggregated:
        for config in os.listdir(data_dir):
            if os.path.isdir(f"{data_dir}/{config}"):
                with open(f"{data_dir}/{config}/pyraminx.txt", "r") as f:
                    lines = f.readlines()

                parameters = config.split(sep='_')
                if parameters[1] == "SCRATCH":
                    mode = PyraminxGA.Mode.FROM_SCRATCH
                    sol_per_pop = int(parameters[2])
                else:
                    mode = PyraminxGA.Mode.EXPERT
                    sol_per_pop = int(parameters[1])

                aggregated.write(f"{mode=}, {sol_per_pop=:4d}\n")
                aggregated.write(f"\tis_solved = {[line.split(':')[1].strip() == "True" for line in lines if line.startswith('\tis solved:')]}\n")
                aggregated.write(f"\tlen_best_solution = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tlength of best solution:')]}\n")
                aggregated.write(f"\tlen_best_solution_expanded = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tlength of expanded best solution:')]}\n")
                aggregated.write(f"\tnum_generations = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tnumber of generation:')]}\n")


def plot(mode: PyraminxGA.Mode, x, y, x_label: str, y_label: str, data_dir: str = "data"):
    plt.figure(figsize=(10, 8))

    sns.lineplot(x=x, y=y, label=y_label, color="blue", alpha=0.6)

    plt.title(f"{y_label} Accross {x_label}")
    plt.xticks(x)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(f"{data_dir}/{mode}_{x_label}_{y_label}.png")
    plt.close()
