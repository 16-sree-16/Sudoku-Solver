# sudoku_solver.py
import numpy as np
import copy
import time
from typing import List, Tuple, Optional

class SudokuSolver:
    
    def __init__(self, board: List[List[int]]):
 
 
        self.board = np.array(board, dtype=int)
        self.size = 9
        self.original_board = copy.deepcopy(self.board)
        self.solutions = []
        self.backtracking_count = 0
        
    def is_valid(self, row: int, col: int, num: int) -> bool:

        if num in self.board[row]:
            return False
        
        if num in self.board[:, col]:
            return False
        
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        if num in self.board[box_row:box_row+3, box_col:box_col+3]:
            return False
        
        return True
    
    def find_empty(self) -> Optional[Tuple[int, int]]:

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return None
    
    def solve_backtracking(self) -> bool:

        empty = self.find_empty()
        if not empty:
            return True
        
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                self.backtracking_count += 1
                
                if self.solve_backtracking():
                    return True
                
                self.board[row][col] = 0
        
        return False
    
    def solve_with_heuristics(self) -> bool:

        empty = self.find_best_cell_mrv()
        if not empty:
            return True
        
        row, col = empty
        candidates = self.get_candidates(row, col)
        
        for num in candidates:
            self.board[row][col] = num
            self.backtracking_count += 1
            
            if self.solve_with_heuristics():
                return True
            
            self.board[row][col] = 0
        
        return False
    
    def find_best_cell_mrv(self) -> Optional[Tuple[int, int]]:

        min_candidates = 10
        best_cell = None
        
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    candidates = self.get_candidates(i, j)
                    if len(candidates) < min_candidates:
                        min_candidates = len(candidates)
                        best_cell = (i, j)
                        if min_candidates == 1:
                            return best_cell
        
        return best_cell
    
    def get_candidates(self, row: int, col: int) -> List[int]:

        candidates = []
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                candidates.append(num)
        return candidates
    
    def solve_dancing_links(self) -> bool:

        self.cover = []
        self.build_exact_cover()
        
        solution = self.algorithm_x(self.cover)
        if solution:
            self.apply_solution(solution)
            return True
        return False
    
    def build_exact_cover(self):

        self.cover = []
        self.row_info = []
        
        for row in range(9):
            for col in range(9):
                for num in range(1, 10):
                    if self.board[row][col] == 0 or self.board[row][col] == num:
                        col_row = row * 9 + col
                        col_row_num = row * 9 + (num - 1) + 81
                        col_col_num = col * 9 + (num - 1) + 162
                        col_box_num = ((row // 3) * 3 + (col // 3)) * 9 + (num - 1) + 243
                        
                        self.cover.append({
                            'row': row, 'col': col, 'num': num,
                            'cols': [col_row, col_row_num, col_col_num, col_box_num]
                        })
                        self.row_info.append((row, col, num))
    
    def algorithm_x(self, rows):

        if not rows:
            return []
        
        col_counts = {}
        for row in rows:
            for col in row['cols']:
                col_counts[col] = col_counts.get(col, 0) + 1
        
        if not col_counts:
            return None
        
        min_col = min(col_counts, key=col_counts.get)
        
        for row in rows:
            if min_col in row['cols']:
                solution = [row]
                
                remaining_rows = []
                for r in rows:
                    if not set(r['cols']).intersection(set(row['cols'])):
                        remaining_rows.append(r)
                
                remaining_rows_filtered = []
                cols_to_remove = set(row['cols'])
                for r in remaining_rows:
                    new_cols = [c for c in r['cols'] if c not in cols_to_remove]
                    if new_cols:
                        r_copy = r.copy()
                        r_copy['cols'] = new_cols
                        remaining_rows_filtered.append(r_copy)
                
                sub_solution = self.algorithm_x(remaining_rows_filtered)
                if sub_solution is not None:
                    solution.extend(sub_solution)
                    return solution
        
        return None
    
    def apply_solution(self, solution):
 
        self.board = np.zeros((9, 9), dtype=int)
        for item in solution:
            self.board[item['row']][item['col']] = item['num']
    
    def solve(self, method='backtracking') -> bool:
  
        self.backtracking_count = 0
        self.solutions = []
        
        if method == 'backtracking':
            return self.solve_backtracking()
        elif method == 'mrv':
            return self.solve_with_heuristics()
        elif method == 'dancing_links':
            return self.solve_dancing_links()
        else:
            raise ValueError("Invalid method. Choose 'backtracking', 'mrv', or 'dancing_links'")
    
    def solve_all(self) -> List[np.ndarray]:

        self.solutions = []
        self._solve_all_recursive()
        return self.solutions
    
    def _solve_all_recursive(self):

        empty = self.find_empty()
        if not empty:
            self.solutions.append(copy.deepcopy(self.board))
            return
        
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                self._solve_all_recursive()
                self.board[row][col] = 0
    
    def display(self):

        print("┌─────────┬─────────┬─────────┐")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("├─────────┼─────────┼─────────┤")
            print("│", end=" ")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("│", end=" ")
                print(self.board[i][j] if self.board[i][j] != 0 else ".", end=" ")
            print("│")
        print("└─────────┴─────────┴─────────┘")
    
    def get_stats(self) -> Dict:

        return {
            'backtracking_count': self.backtracking_count,
            'solutions_found': len(self.solutions),
            'board_size': self.size
        }
    
    def is_solved(self) -> bool:

        # Check rows
        for row in self.board:
            if sorted(row) != list(range(1, 10)):
                return False
        
        # Check columns
        for col in range(9):
            if sorted(self.board[:, col]) != list(range(1, 10)):
                return False
        
        # Check boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = self.board[box_row:box_row+3, box_col:box_col+3].flatten()
                if sorted(box) != list(range(1, 10)):
                    return False
        
        return True

class SudokuGenerator:
    
    @staticmethod
    def generate(difficulty='medium') -> List[List[int]]:
 
        solver = SudokuGenerator._create_solved_sudoku()
        
        if difficulty == 'easy':
            cells_to_remove = 30
        elif difficulty == 'medium':
            cells_to_remove = 45
        else:
            cells_to_remove = 55
        
        puzzle = copy.deepcopy(solver.board)
        
        positions = [(i, j) for i in range(9) for j in range(9)]
        import random
        random.shuffle(positions)
        
        for i in range(cells_to_remove):
            row, col = positions[i]
            puzzle[row][col] = 0
        
        return puzzle.tolist()
    
    @staticmethod
    def _create_solved_sudoku() -> SudokuSolver:
        base = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        
        import random
        mapping = list(range(1, 10))
        random.shuffle(mapping)
        mapped = [[mapping[val-1] for val in row] for row in base]
        
        for band in range(3):
            rows = list(range(band*3, band*3 + 3))
            random.shuffle(rows)
            mapped[band*3:band*3+3] = [mapped[i] for i in rows]
        
        return SudokuSolver(mapped)

def sudoku_solver_demo():
    """Demonstrate Sudoku Solver with various methods"""
    
    print("="*50)
    print("SUDOKU SOLVER")
    print("="*50)
    
    puzzle = SudokuGenerator.generate('medium')
    print("\nGenerated Sudoku Puzzle:")
    solver = SudokuSolver(puzzle)
    solver.display()
    
    while True:
        print("\nSolving Methods:")
        print("1. Simple Backtracking")
        print("2. MRV Heuristic (Advanced)")
        print("3. Dancing Links (Algorithm X)")
        print("4. Find All Solutions")
        print("5. Generate New Puzzle")
        print("6. Compare Methods")
        print("7. Exit")
        
        choice = input("\nChoose method: ")
        
        if choice == '1':
            print("\nSolving with Simple Backtracking...")
            start_time = time.time()
            solver = SudokuSolver(puzzle)
            if solver.solve('backtracking'):
                print(f"Solved in {time.time() - start_time:.3f} seconds")
                solver.display()
                print(f"Backtracking steps: {solver.backtracking_count}")
            else:
                print("No solution found!")
        
        elif choice == '2':
            print("\nSolving with MRV Heuristic...")
            start_time = time.time()
            solver = SudokuSolver(puzzle)
            if solver.solve('mrv'):
                print(f"Solved in {time.time() - start_time:.3f} seconds")
                solver.display()
                print(f"Backtracking steps: {solver.backtracking_count}")
            else:
                print("No solution found!")
        
        elif choice == '3':
            print("\nSolving with Dancing Links...")
            start_time = time.time()
            solver = SudokuSolver(puzzle)
            if solver.solve('dancing_links'):
                print(f"Solved in {time.time() - start_time:.3f} seconds")
                solver.display()
            else:
                print("No solution found!")
        
        elif choice == '4':
            print("\nFinding all solutions...")
            start_time = time.time()
            solver = SudokuSolver(puzzle)
            solutions = solver.solve_all()
            print(f"Found {len(solutions)} solutions in {time.time() - start_time:.3f} seconds")
            if solutions:
                print("First solution:")
                solver.display()
        
        elif choice == '5':
            puzzle = SudokuGenerator.generate('medium')
            print("New puzzle generated:")
            solver = SudokuSolver(puzzle)
            solver.display()
        
        elif choice == '6':
            print("\nComparing Methods:")
            print("-" * 40)
            
            for difficulty in ['easy', 'medium', 'hard']:
                print(f"\nDifficulty: {difficulty.upper()}")
                puzzle = SudokuGenerator.generate(difficulty)
                solver = SudokuSolver(puzzle)
                
                methods = ['backtracking', 'mrv', 'dancing_links']
                for method in methods:
                    solver = SudokuSolver(puzzle)
                    start_time = time.time()
                    solver.solve(method)
                    time_taken = time.time() - start_time
                    print(f"  {method}: {time_taken:.4f}s, steps: {solver.backtracking_count}")
        
        elif choice == '7':
            print("Done!")
            break

if __name__ == "__main__":
    sudoku_solver_demo()