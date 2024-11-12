class Pyraminx(object):
    def __init__(self):
        """
        Initialize the Pyramix object
        The Pyraminx object has 4 faces: L, F, R, D with colors: Y, G, R, B
        Each face has 3 layers: 1, 2, 3

        """

        self.faces = {
            "L": [["Y"], ["Y", "Y", "Y"], ["Y", "Y", "Y", "Y", "Y"]],
            "F": [["G"], ["G", "G", "G"], ["G", "G", "G", "G", "G"]],
            "R": [["R"], ["R", "R", "R"], ["R", "R", "R", "R", "R"]],
            "D": [["B"], ["B", "B", "B"], ["B", "B", "B", "B", "B"]],
        }


def main():
    pyramix = Pyraminx()
    print(pyramix.faces)


if __name__ == "__main__":
    main()
