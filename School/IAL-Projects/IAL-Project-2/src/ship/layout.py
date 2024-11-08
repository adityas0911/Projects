import random as rd
from transition.utils import debug_print

class ShipLayout:
    """
    Represents the layout of the ship in the game.

    This class generates and manages the ship's layout, including the placement of open and blocked cells.
    """
    
    def __init__(self, D=40):
        """
        Initialize the ShipLayout.

        Args:
            D (int): The dimension of the square grid representing the ship. Defaults to 40.
        """
        self.D = D
        self.layout = self.create_layout()
        self.open_dead_ends()

    def create_layout(self):
        """
        Create the initial layout of the ship.

        Returns:
            list: A 2D list representing the ship's layout, where 'X' is a blocked cell and 'O' is an open cell.
        """
        ship_layout = [['X' for _ in range(self.D)] for _ in range(self.D)]
        initial_row, initial_col = rd.randint(0, self.D - 1), rd.randint(0, self.D - 1)
        ship_layout[initial_row][initial_col] = 'O'

        while True:
            one_open_neighbor = self.get_one_open_neighbors(ship_layout)
            if not one_open_neighbor:
                break
            row, col = rd.choice(one_open_neighbor)
            ship_layout[row][col] = 'O'
        return ship_layout

    def get_one_open_neighbors(self, ship_layout):
        """
        Find all blocked cells with exactly one open neighbor.

        Args:
            ship_layout (list): The current ship layout.

        Returns:
            list: A list of tuples representing the coordinates of blocked cells with one open neighbor.
        """
        one_open_neighbor = []
        for row in range(self.D):
            for col in range(self.D):
                if ship_layout[row][col] == 'X' and self.count_open_neighbors(ship_layout, row, col) == 1:
                    one_open_neighbor.append((row, col))
        return one_open_neighbor

    def count_open_neighbors(self, ship_layout, row, col):
        """
        Count the number of open neighbors for a given cell.

        Args:
            ship_layout (list): The current ship layout.
            row (int): The row of the cell.
            col (int): The column of the cell.

        Returns:
            int: The number of open neighbors.
        """
        return sum(1 for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)] if 0 <= row+dr < self.D and 0 <= col+dc < self.D and ship_layout[row+dr][col+dc] == 'O')

    def find_dead_ends(self):
        """
        Find all dead ends in the ship layout.

        Returns:
            tuple: A list of dead end coordinates and a dictionary of their blocked neighbors.
        """
        dead_ends = []
        closed_neighbors = {}

        for row in range(self.D):
            for col in range(self.D):
                if self.layout[row][col] == 'O' and self.count_open_neighbors(self.layout, row, col) == 1:
                    dead_ends.append((row, col))
                    closed_neighbors[(row, col)] = self.get_blocked_neighbors(row, col)
        return dead_ends, closed_neighbors

    def get_blocked_neighbors(self, row, col):
        """
        Get the blocked neighbors of a given cell.

        Args:
            row (int): The row of the cell.
            col (int): The column of the cell.

        Returns:
            list: A list of tuples representing the coordinates of blocked neighbors.
        """
        return [(row+dr, col+dc) for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)] if 0 <= row+dr < self.D and 0 <= col+dc < self.D and self.layout[row+dr][col+dc] == 'X']

    def open_dead_ends(self):
        """
        Open up half of the dead ends in the ship layout.
        """
        dead_ends, closed_neighbors = self.find_dead_ends()
        rd.shuffle(dead_ends)
        half_dead_ends = dead_ends[:len(dead_ends)//2]

        for row, col in half_dead_ends:
            neighbors_to_choose = closed_neighbors[(row, col)]
            neighbor_row, neighbor_col = rd.choice(neighbors_to_choose)
            self.layout[neighbor_row][neighbor_col] = 'O'

    def get_layout(self):
        """
        Get the current ship layout.

        Returns:
            list: The 2D list representing the current ship layout.
        """
        return self.layout
    
    def get_fixed_starting_positions(self):
        """
        Get fixed starting positions for the bot and mice.

        Returns:
            tuple: A tuple containing the bot's starting position and a list of mice starting positions.
        """
        open_cells = [(x, y) for x in range(self.D) for y in range(self.D) if self.layout[x][y] == 'O']
        rd.seed(42)  # Use a fixed seed for reproducibility

        bot_position = rd.choice(open_cells)
        open_cells.remove(bot_position)

        mouse_positions = rd.sample(open_cells, 2)
    
        return bot_position, mouse_positions
