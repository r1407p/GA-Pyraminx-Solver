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

    def _colorize(self, char):
        """
        Returns the ANSI escape code for the given color character.
        """
        colors = {
            "Y": "\033[93m",  # Yellow
            "G": "\033[92m",  # Green
            "R": "\033[91m",  # Red
            "B": "\033[94m",  # Blue
        }
        reset = "\033[0m"
        return f"{colors.get(char, '')}{char}{reset}"

    def display(self):
        """
        Display the Pyraminx in a triangular format similar to the provided image.
        """

        def format_layer(layer):
            """
            Formats a given layer by centering its elements with padding and applying colorization.
            """
            padding_len = (11 - len(" ".join(layer))) // 2
            padding = " " * padding_len
            return padding + " ".join([self._colorize(c) for c in layer]) + padding

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

    def move(self, move: str, display=False):
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

        self.rotate(move[0].upper(), clockwise, layer, display)

    def __find__switching_trio(self, corner: str, layer: int):
        """
        Find the switching trios for
        the given corner and layer
        Args:
            corner (str): The corner to be rotated
            layer (int): The layer to be rotated
        """
        if corner == "U":
            if layer == 1:
                return [[("F", (0, 0)), ("R", (0, 0)), ("L", (0, 0))]]
            elif layer == 2:
                return [
                    [("F", (0, 0)), ("R", (0, 0)), ("L", (0, 0))],
                    [("F", (1, 0)), ("R", (1, 0)), ("L", (1, 0))],
                    [("F", (1, 1)), ("R", (1, 1)), ("L", (1, 1))],
                    [("F", (1, 2)), ("R", (1, 2)), ("L", (1, 2))],
                ]
        elif corner == "L":
            if layer == 1:
                return [[("F", (2, 0)), ("L", (2, 4)), ("D", (2, 0))]]
            elif layer == 2:
                return [
                    [("F", (2, 0)), ("L", (2, 4)), ("D", (2, 0))],
                    [("F", (1, 0)), ("L", (2, 2)), ("D", (2, 2))],
                    [("F", (2, 1)), ("L", (2, 3)), ("D", (2, 1))],
                    [("F", (2, 2)), ("L", (1, 2)), ("D", (1, 0))],
                ]
        elif corner == "R":
            if layer ==1:
                return [[("F", (2, 4)), ("D", (2, 4)), ("R", (2, 0))]]
            elif layer == 2:
                return [
                    [("F", (2, 4)), ("D", (2, 4)), ("R", (2, 0))],
                    [("F", (1, 2)), ("D", (2, 2)), ("R", (2, 2))],
                    [("F", (2, 3)), ("D", (2, 3)), ("R", (2, 1))],
                    [("F", (2, 2)), ("D", (1, 2)), ("R", (1, 0))]
                ]
        elif corner == "B":
            if layer == 1:
                return [[("R", (2, 4)), ("D", (0, 0)), ("L", (2, 0))]]
            elif layer == 2:
                return [
                    [("R", (2, 4)), ("D", (0, 0)), ("L", (2, 0))],
                    [("R", (1, 2)), ("D", (1, 2)), ("L", (2, 2))],
                    [("R", (2, 3)), ("D", (1, 1)), ("L", (2, 1))],
                    [("R", (2, 2)), ("D", (1, 0)), ("L", (1, 0))]
                ]
            
    def __rotate_face(self, switching_trios: list, clockwise: bool):
        """
        Rotate the given switching trios in the given direction
        Args:
            switching_trios (list): The list of switching trios to be rotated
            clockwise (bool): The direction of the rotation
        """
        for trio in switching_trios:
            faces = [pixel[0] for pixel in trio]
            cord0 = [pixel[1][0] for pixel in trio]
            cord1 = [pixel[1][1] for pixel in trio]
            if clockwise:
                (
                    self.faces[faces[0]][cord0[0]][cord1[0]],
                    self.faces[faces[1]][cord0[1]][cord1[1]],
                    self.faces[faces[2]][cord0[2]][cord1[2]],
                ) = (
                    self.faces[faces[1]][cord0[1]][cord1[1]],
                    self.faces[faces[2]][cord0[2]][cord1[2]],
                    self.faces[faces[0]][cord0[0]][cord1[0]],
                )
            else:
                (
                    self.faces[faces[0]][cord0[0]][cord1[0]],
                    self.faces[faces[1]][cord0[1]][cord1[1]],
                    self.faces[faces[2]][cord0[2]][cord1[2]],
                ) = (
                    self.faces[faces[2]][cord0[2]][cord1[2]],
                    self.faces[faces[0]][cord0[0]][cord1[0]],
                    self.faces[faces[1]][cord0[1]][cord1[1]],
                )

    def rotate(self, corner: str, clockwise: bool, layer: int, display=False):
        """
        Rotate the Pyraminx according to the given move
        
        args:
            corner (str): The corner to be rotated
            clockwise (bool): The direction of the rotation
            layer (int): The layer to be rotated
            display (bool): Whether to display the Pyraminx after the rotation
        
        """
        if display:
            print(f"Rotate {corner} with clockwise={clockwise} and layer={layer}")
        switching_trio = self.__find__switching_trio(corner, layer)
        self.__rotate_face(switching_trio, clockwise)

    def copy(self):
        """
        Create a deep copy of the Pyraminx object.
        """
        return copy.deepcopy(self)

def main():
    pyramix = Pyraminx()
    pprint(pyramix.faces)
    pyramix.display()
    # return 
    while True:
        move = input("Enter move: ")
        if move == "q":
            break
        pyramix.move(move, display=True)
        pyramix.display()


if __name__ == "__main__":
    main()
