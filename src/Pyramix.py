from pprint import pprint


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

    def display(self):
        """
        Display the Pyraminx in a triangular format similar to the provided image.
        """

        def format_layer(layer):
            return " ".join(layer).center(11)

        print(
            "\n"
            + format_layer(self.faces["L"][0])
            + "  "
            + format_layer(self.faces["F"][0])
            + "  "
            + format_layer(self.faces["R"][0])
        )
        print(
            format_layer(self.faces["L"][1])
            + "  "
            + format_layer(self.faces["F"][1])
            + "  "
            + format_layer(self.faces["R"][1])
        )
        print(
            format_layer(self.faces["L"][2])
            + "  "
            + format_layer(self.faces["F"][2])
            + "  "
            + format_layer(self.faces["R"][2])
        )
        print(" " * 13 + format_layer(self.faces["D"][2]))
        print(" " * 13 + format_layer(self.faces["D"][1]))
        print(" " * 13 + format_layer(self.faces["D"][0]))

    def move(self, move: str):
        """
        Rotate the Pyraminx according to the given move
        The move is a string of the form have 16 possible moves:
        Include the combination of 4 corners(l r u b)
        and 2 layers(lower case and upper case)
        and 2 directions("" and "'")

        Args:
            move (str): The move to be executed
        """

        if len(move) == 1:
            clockwise = True
        elif len(move) == 2:
            clockwise = False
        else:
            raise ValueError("Invalid move")

        if move[0].islower():
            layer = 1
        else:
            layer = 2

        self.rotate(move[0].upper(), clockwise, layer)

    def rotate(self, corner: str, clockwise: bool, layer: int):
        print(f"Rotate {corner} with clockwise={clockwise} and layer={layer}")


def main():
    pyramix = Pyraminx()
    pprint(pyramix.faces)
    pyramix.display()
    pyramix.move("l")
    pyramix.move("L")


if __name__ == "__main__":
    main()
