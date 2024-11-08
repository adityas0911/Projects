import numpy as np

class NeighborCache:
    def __init__(self, grid_size, is_valid_cell):
        self.grid_size = grid_size
        self.is_valid_cell = is_valid_cell
        self.neighbors = self._precompute_neighbors()

    def _precompute_neighbors(self):
        neighbors = {}
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                neighbors[(row, col)] = self._compute_neighbors(row, col)
        return neighbors

    def _compute_neighbors(self, row, col):
        potential_neighbors = [
            (row-1, col), (row+1, col),
            (row, col-1), (row, col+1)
        ]
        return [
            (r, c) for r, c in potential_neighbors
            if self.is_valid_cell(r, c)
        ]

    def get_neighbors(self, row, col):
        return self.neighbors.get((row, col), [])

    def update_cell(self, row, col, is_valid):
        self.neighbors[(row, col)] = self._compute_neighbors(row, col)
        for nr, nc in self.get_neighbors(row, col):
            self.neighbors[(nr, nc)] = self._compute_neighbors(nr, nc)