import os
import random
from itertools import chain

import numpy as np
import pandas as pd
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
        "mutation_num_genes": 1,  # number of genes in each solution will be randomly selected for mutation, covering mutation_percent_genes
        "on_start": PyraminxGA._on_start if verbose else None,
        "on_fitness": None,
        "on_parents": None,
        "on_crossover": None,
        "on_mutation": None,
        "on_generation": PyraminxGA._on_generation if verbose else None
    }

    kwargs = default_kwargs | kwargs
    data_dir = "data/expert" if mode == PyraminxGA.Mode.EXPERT else "data/naive"
    save_dir = f"{kwargs["sol_per_pop"]}"

    print(f"testing mode={mode} population_size={kwargs["sol_per_pop"]} ...")

    pga = PyraminxGA(pyraminx=pyraminx, accept_ratio=accept_ratio, num_genes=num_genes, data_dir=data_dir)
    for i in range(num_test):
        if verbose:
            print(f"{i} th test ...")
        solved = pga.run(mode=mode, save_dir=save_dir, index=i, verbose=verbose, **kwargs)
        best = pga.best_solution(expand=False)
        best_expanded = PyraminxGA._expand_high_level_moves(best)
        with open(f"{data_dir}/{save_dir}/pyraminx.txt", "a+") as f:
            f.write(f"{i}th run\n"
                    f"\tis solved: {solved}\n"
                    f"\tlength of best solution: {len(best)}\n"
                    f"\tlength of expanded best solution: {len(best_expanded)}\n"
                    f"\tnumber of generation: {pga.best_solution_generation()}\n")


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def aggregate_test_results(data_dir: str = "data"):
    with open(f"{data_dir}/aggregated.txt", "w+") as aggregated:
        for config in os.listdir(data_dir):
            if os.path.isdir(f"{data_dir}/{config}"):
                with open(f"{data_dir}/{config}/pyraminx.txt", "r") as f:
                    lines = f.readlines()

                parameters = data_dir.split(sep='/')
                if parameters[-1] == "naive":
                    mode = PyraminxGA.Mode.FROM_SCRATCH
                    sol_per_pop = int(config)
                else:
                    mode = PyraminxGA.Mode.EXPERT
                    sol_per_pop = int(config)

                aggregated.write(f"{mode=}, {sol_per_pop=:4d}\n")
                aggregated.write(f"\tis_solved = {[line.split(':')[1].strip() == "True" for line in lines if line.startswith('\tis solved:')]}\n")
                aggregated.write(f"\tlen_best_solution = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tlength of best solution:')]}\n")
                aggregated.write(f"\tlen_best_solution_expanded = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tlength of expanded best solution:')]}\n")
                aggregated.write(f"\tnum_generations = {[int(line.split(':')[1].strip()) for line in lines if line.startswith('\tnumber of generation:')]}\n")


def plot(x, y, x_label: str, y_label: str, data_dir: str = "data"):
    plt.figure(figsize=(10, 8))

    sns.lineplot(x=x, y=y, label=y_label, color="blue", alpha=0.6)

    plt.title(f"{y_label} Accross {x_label}")
    plt.xticks(x)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(f"{data_dir}/{'-'.join(x_label.split(sep=' '))}_{'-'.join(y_label.split(sep=' '))}.png")
    plt.close()

def multiplot(x, ys, names, x_label: str, y_label: str, data_dir: str = "data"):
    data = pd.DataFrame({"x": tuple(x) * len(names), "y": tuple(chain.from_iterable(ys)), "name": [name for name in names for _ in x]})

    plt.figure(figsize=(10, 8))

    sns.lineplot(data=data, x="x", y="y", hue="name")
    plt.subplots_adjust(bottom=0.2)

    plt.legend(title="Names", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=len(names))

    plt.title(f"{y_label} Accross {x_label}")
    plt.xticks(x)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(f"{data_dir}/{'-'.join(x_label.split(sep=' '))}_{'-'.join(y_label.split(sep=' '))}.png")
    plt.close()
