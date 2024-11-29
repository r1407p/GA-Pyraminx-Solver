from pprint import pprint
import copy
import random

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
        self.shuffle_moves = []

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

    def shuffle(self, num_moves=24):
        """
        Shuffle the Pyraminx object by executing n random
        """
        for _ in range(num_moves):
            move = random.choice(["L", "R", "U", "B", 'l', 'r', 'u', 'b']) + random.choice(["", "'"])
            self.shuffle_moves.append(move)
            self.move(move)

        return self.copy()

    def multi_move(self, moves):
        """
        Execute a sequence of moves on the Pyraminx object.
        """
        for move in moves:
            self.move(move)
        return self.copy()

    def mixture_moves(self, move):
        """
        Execute a sequence of moves on the Pyraminx object.
        """
        # E(R U’ R’), F(L’ U L), G(B U’ B’), H(B’ U B), I(R’ U R), J(L U’ L’), U, U’
        # X(R U’ R’ U’ R U’ R’), Y(R U R’ U R U R’), Z(R’ L R L’ U L’ U’ L), U, U’

        if move == "E":
            return self.multi_move(["R", "U'", "R'"])
        elif move == "F":
            return self.multi_move(["L'", "U", "L"])
        elif move == "G":
            return self.multi_move(["B", "U'", "B'"])
        elif move == "H":
            return self.multi_move(["B'", "U", "B"])
        elif move == "I":
            return self.multi_move(["R'", "U", "R"])
        elif move == "J":
            return self.multi_move(["L", "U'", "L'"])
        elif move == "X":
            return self.multi_move(["R", "U'", "R'", "U'", "R", "U'", "R'"])
        elif move == "Y":
            return self.multi_move(["R", "U", "R'", "U", "R", "U", "R'"])
        elif move == "Z":
            return self.multi_move(["R'", "L", "R", "L'", "U", "L'", "U'", "L"])
        else:
            return self.multi_move([move])

    def small_corners_solved(self):
        """
        Returns True if the small corners are solved
        """
        correspondings = [
            [[('L',(0,0)), ('L',(1,1))], [('F',(0,0)), ('F',(1,1))], [('R',(0,0)), ('R',(1,1))]],
            [[('L',(2,3)), ('L',(2,4))], [('F',(2,0)), ('F',(2,1))], [('D',(2,0)), ('D',(2,1))]],
            [[('F',(2,3)), ('F',(2,4))], [('D',(2,3)), ('D',(2,4))], [('R',(2,0)), ('R',(2,1))]],
            [[('L',(2,0)), ('L',(2,1))], [('D',(0,0)), ('D',(1,1))], [('R',(2,3)), ('R',(2,4))]]
            
        ]
        matches = 0
        for corresponding in correspondings:
            matched = True
            for coners in corresponding:
                colors = [self.faces[face][cord[0]][cord[1]] for face, cord in coners]
                if len(set(colors)) != 1:
                    matched = False
                    break
            if matched:
                matches += 1
        return matches

    def large_corners_solved(self):
        solved = 0
        cornors = [(0,0),(1,1),(2,0),(2,1),(2,3),(2,4)]
        for face in self.faces:
            colors = [self.faces[face][cord[0]][cord[1]] for cord in cornors]
            if len(set(colors)) == 1:
                solved += 1
        return solved

    def middle_pieces_solved(self):
        solved = 0
        if self.faces["F"][2][2] == self.faces["F"][2][3] and self.faces["D"][2][2] == self.faces["D"][2][3]:
            solved += 1
        if self.faces["L"][2][2] == self.faces["L"][2][3] and self.faces["D"][1][2] == self.faces["D"][2][4]:
            solved += 1
        if self.faces["R"][2][2] == self.faces["R"][1][0] and self.faces["D"][2][2] == self.faces["D"][2][0]:
            solved += 1
        return solved

    def sum_num_colors_on_a_face(self):
        colors_in_faces = {}
        for face in self.faces:
            print(face)
            colors = set()
            for layer in self.faces[face]:
                for pixel in layer:
                    colors.add(pixel)
            colors_in_faces[face] = colors
        return [len(colors) for face, colors in colors_in_faces.items()]
        
def main():
    pyraminx = Pyraminx()
    pprint(pyraminx.faces)
    pyraminx.display()

    print("Shuffling...")
    pyraminx.shuffle()
    pyraminx.display()

    
    while True:
        move = input("Enter move: ")
        if move == "q":
            break
        pyraminx.move(move, display=True)
        pyraminx.display()



if __name__ == "__main__":
    main()
