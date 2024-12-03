from test import aggregate_test_results, plot, set_seed, test

import numpy as np

from Pyraminx import Pyraminx
from PyraminxGA import PyraminxGA


def main():
    pyraminx = Pyraminx()
    pyraminx.faces = {'D': [['Y'], ['G', 'B', 'Y'], ['B', 'G', 'R', 'R', 'R']],
                      'F': [['Y'], ['Y', 'Y', 'B'], ['G', 'Y', 'B', 'B', 'B']],
                      'L': [['R'], ['R', 'R', 'G'], ['R', 'Y', 'B', 'B', 'Y']],
                      'R': [['G'], ['Y', 'G', 'G'], ['G', 'G', 'R', 'R', 'B']]}

    # pyraminx.display()
    # for move in ("R'", 'U', "b'", "L'", 'l', "r'", "l'", "b'", 'r', "U'", "l'", "u'", "U'", "U'", 'U', "R'", 'r', "b'", "b'", "L'", 'U', "r'", "l'", 'U'):
    #     pyraminx.mixture_moves(move)
    #     pyraminx.display()

    # population_size = range(2, 34, 2)
    # num_genes = (4,4,9,3)
    # crossover_type = "single_point"

    set_seed(42)
    test(pyraminx=pyraminx, mode=PyraminxGA.Mode.FROM_SCRATCH, num_genes=24, verbose=True, num_generations=1024, sol_per_pop=32)

    # for sol_per_pop in population_size:
    #     set_seed(42)
    #     test(pyraminx=pyraminx, mode=PyraminxGA.Mode.EXPERT, num_genes=num_genes, sol_per_pop=sol_per_pop)

    # for sol_per_pop in population_size:
    #     set_seed(42)
    #     test(pyraminx=pyraminx, mode=PyraminxGA.Mode.FROM_SCRATCH, num_genes=12, num_generations=1024, sol_per_pop=sol_per_pop)

    # data_dir = f"data.{num_genes}.{crossover_type}"
    # aggregate_test_results(data_dir=data_dir)

    # testing_results = {}
    # with open(f"{data_dir}/aggregated.txt", "r") as f:
    #     lines = f.readlines()
    #     for i in range(0, len(lines), 5):
    #         mode = PyraminxGA.Mode.EXPERT if "EXPERT" in lines[i] else PyraminxGA.Mode.FROM_SCRATCH
    #         sol_per_pop = int(lines[i].split('=')[2].strip())

    #         is_solved = tuple(map(lambda x: "True" in x, lines[i + 1].removeprefix("\tis_solved = [").removesuffix("]\n").split(', ')))
    #         len_best_solution = tuple(map(int, lines[i + 2].removeprefix("\tlen_best_solution = [").removesuffix("]\n").split(', ')))
    #         len_best_solution = [x for x, solved in zip(len_best_solution, is_solved) if solved]
    #         len_best_solution_expanded = tuple(map(int, lines[i + 3].removeprefix("\tlen_best_solution_expanded = [").removesuffix("]\n").split(', ')))
    #         len_best_solution_expanded = [x for x, solved in zip(len_best_solution_expanded, is_solved) if solved]
    #         num_generations = tuple(map(int, lines[i + 4].removeprefix("\tnum_generations = [").removesuffix("]\n").split(', ')))
    #         num_generations = [x for x, solved in zip(num_generations, is_solved) if solved]

    #         testing_results[(mode, sol_per_pop)] = {
    #             "num_solved": is_solved.count(True),
    #             "mean_len_best_solution": np.mean(len_best_solution) if len_best_solution else sum(num_genes),
    #             "min_len_best_solution": min(len_best_solution) if len_best_solution else sum(num_genes),
    #             "mean_len_best_solution_expanded": np.mean(len_best_solution_expanded) if len_best_solution_expanded else sum(num_genes),
    #             "min_len_best_solution_expanded": min(len_best_solution_expanded) if len_best_solution_expanded else sum(num_genes),
    #             "mean_num_generations": np.mean(num_generations) if num_generations else 100,
    #         }

    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["num_solved"] for sol_per_pop in population_size), x_label="Population Size", y_label="Number of Success", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["mean_len_best_solution"] for sol_per_pop in population_size), x_label="Population Size", y_label="Mean Length of Best Solution", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["min_len_best_solution"] for sol_per_pop in population_size), x_label="Population Size", y_label="Minimum Length of Best Solution", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["mean_len_best_solution_expanded"] for sol_per_pop in population_size), x_label="Population Size", y_label="Mean Length of Expanded Best Solution", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["min_len_best_solution_expanded"] for sol_per_pop in population_size), x_label="Population Size", y_label="Minimum Length of Expanded Best Solution", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.EXPERT, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.EXPERT, sol_per_pop)]["mean_num_generations"] for sol_per_pop in population_size), x_label="Population Size", y_label="Mean Generation to Achieve Best Solution", data_dir=data_dir)
    # plot(mode=PyraminxGA.Mode.FROM_SCRATCH, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.FROM_SCRATCH, sol_per_pop)]["num_solved"] for sol_per_pop in population_size), x_label="Population Size", y_label="Number of Success")
    # plot(mode=PyraminxGA.Mode.FROM_SCRATCH, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.FROM_SCRATCH, sol_per_pop)]["mean_len_best_solution"] for sol_per_pop in population_size), x_label="Population Size", y_label="Mean Length of Best Solution")
    # plot(mode=PyraminxGA.Mode.FROM_SCRATCH, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.FROM_SCRATCH, sol_per_pop)]["mean_num_generations"] for sol_per_pop in population_size), x_label="Population Size", y_label="Mean Generation to Achieve Best Solution")
    # plot(mode=PyraminxGA.Mode.FROM_SCRATCH, x=population_size, y=tuple(testing_results[(PyraminxGA.Mode.FROM_SCRATCH, sol_per_pop)]["min_len_best_solution"] for sol_per_pop in population_size), x_label="Population Size", y_label="Minimum Length of Best Solution")


if __name__ == "__main__":
    main()
