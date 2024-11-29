from Pyraminx import Pyraminx
from PyraminxGA import PyraminxGA


def main():
    pga = PyraminxGA()
    pga.run()
    print(pga.best_solution())
    print(pga.best_solution_generation())


if __name__ == "__main__":
    main()
