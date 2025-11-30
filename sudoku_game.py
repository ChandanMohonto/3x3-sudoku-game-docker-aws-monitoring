#!/usr/bin/env python3
"""
Sudoku Puzzle Game
A complete implementation with board generation, solving, and interactive gameplay
"""

import random
import copy
import time
from typing import List, Tuple, Optional


class SudokuGame:
    """Main Sudoku game class with board generation, solving, and validation"""

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize Sudoku game

        Args:
            difficulty: Game difficulty - 'easy', 'medium', or 'hard'
        """
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.difficulty = difficulty
        self.moves_count = 0
        self.start_time = None

    def is_valid_move(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing a number at a position is valid according to Sudoku rules

        Args:
            board: The Sudoku board
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)

        Returns:
            True if the move is valid, False otherwise
        """
        # Check row
        for x in range(9):
            if board[row][x] == num:
                return False

        # Check column
        for x in range(9):
            if board[x][col] == num:
                return False

        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False

        return True

    def solve_board(self, board: List[List[int]]) -> bool:
        """
        Solve Sudoku board using backtracking algorithm

        Args:
            board: The Sudoku board to solve

        Returns:
            True if solved, False if unsolvable
        """
        # Find empty cell
        empty = self.find_empty_cell(board)
        if not empty:
            return True  # Board is complete

        row, col = empty

        # Try numbers 1-9
        for num in range(1, 10):
            if self.is_valid_move(board, row, col, num):
                board[row][col] = num

                if self.solve_board(board):
                    return True

                # Backtrack
                board[row][col] = 0

        return False

    def find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """
        Find an empty cell in the board

        Args:
            board: The Sudoku board

        Returns:
            Tuple of (row, col) for empty cell, or None if no empty cells
        """
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def generate_complete_board(self) -> List[List[int]]:
        """
        Generate a complete valid Sudoku board

        Returns:
            A completed 9x9 Sudoku board
        """
        board = [[0 for _ in range(9)] for _ in range(9)]

        # Fill diagonal 3x3 boxes first (they are independent)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    board[box + i][box + j] = nums[i * 3 + j]

        # Solve the rest of the board
        self.solve_board(board)
        return board

    def remove_numbers(self, board: List[List[int]], difficulty: str) -> List[List[int]]:
        """
        Remove numbers from complete board based on difficulty

        Args:
            board: Complete Sudoku board
            difficulty: 'easy', 'medium', or 'hard'

        Returns:
            Sudoku board with numbers removed
        """
        # Determine how many cells to remove based on difficulty
        cells_to_remove = {
            'easy': 30,
            'medium': 40,
            'hard': 50
        }.get(difficulty, 40)

        puzzle = copy.deepcopy(board)
        cells_removed = 0
        attempts = 0
        max_attempts = 100

        while cells_removed < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)

            if puzzle[row][col] != 0:
                backup = puzzle[row][col]
                puzzle[row][col] = 0

                # Verify puzzle still has unique solution
                copy_board = copy.deepcopy(puzzle)
                if self.solve_board(copy_board):
                    cells_removed += 1
                else:
                    puzzle[row][col] = backup

            attempts += 1

        return puzzle

    def generate_puzzle(self):
        """Generate a new Sudoku puzzle"""
        print(f"Generating {self.difficulty} Sudoku puzzle...")
        complete_board = self.generate_complete_board()
        self.solution = copy.deepcopy(complete_board)
        self.board = self.remove_numbers(complete_board, self.difficulty)
        self.start_time = time.time()
        self.moves_count = 0

    def display_board(self, board: Optional[List[List[int]]] = None):
        """
        Display the Sudoku board in a formatted way

        Args:
            board: Board to display (uses self.board if None)
        """
        if board is None:
            board = self.board

        print("\n    1 2 3   4 5 6   7 8 9")
        print("  ┌───────┬───────┬───────┐")

        for i in range(9):
            if i == 3 or i == 6:
                print("  ├───────┼───────┼───────┤")

            row_str = f"{i+1} │ "
            for j in range(9):
                if board[i][j] == 0:
                    row_str += ". "
                else:
                    row_str += f"{board[i][j]} "

                if (j + 1) % 3 == 0:
                    row_str += "│ "

            print(row_str.rstrip())

        print("  └───────┴───────┴───────┘")

    def is_board_complete(self) -> bool:
        """Check if the board is completely filled"""
        for row in self.board:
            if 0 in row:
                return False
        return True

    def is_board_correct(self) -> bool:
        """Check if the current board matches the solution"""
        return self.board == self.solution

    def make_move(self, row: int, col: int, num: int) -> bool:
        """
        Make a move on the board

        Args:
            row: Row number (1-9)
            col: Column number (1-9)
            num: Number to place (1-9 or 0 to clear)

        Returns:
            True if move was successful, False otherwise
        """
        # Convert to 0-indexed
        row -= 1
        col -= 1

        # Validate input
        if not (0 <= row < 9 and 0 <= col < 9):
            print("Error: Row and column must be between 1 and 9")
            return False

        if not (0 <= num <= 9):
            print("Error: Number must be between 0 and 9")
            return False

        # Check if cell is part of original puzzle
        if self.solution[row][col] != 0 and self.board[row][col] != 0:
            original_board = self.remove_numbers(self.solution, self.difficulty)
            if original_board[row][col] != 0:
                print("Error: Cannot modify original puzzle cells")
                return False

        # Make the move
        self.board[row][col] = num
        self.moves_count += 1
        return True

    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """
        Get a hint for the next move

        Returns:
            Tuple of (row, col, number) for a hint, or None if board is complete
        """
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i + 1, j + 1, self.solution[i][j])
        return None

    def play(self):
        """Main game loop"""
        print("\n" + "="*50)
        print("      SUDOKU PUZZLE GAME")
        print("="*50)
        print("\nRules:")
        print("- Fill the 9x9 grid with numbers 1-9")
        print("- Each row must contain all digits 1-9")
        print("- Each column must contain all digits 1-9")
        print("- Each 3x3 box must contain all digits 1-9")
        print("\nCommands:")
        print("- Enter move as: row col number (e.g., '5 3 7')")
        print("- Type 'hint' for a hint")
        print("- Type 'solve' to see the solution")
        print("- Type 'new' to start a new game")
        print("- Type 'quit' to exit")

        self.generate_puzzle()

        while True:
            self.display_board()

            if self.is_board_complete():
                if self.is_board_correct():
                    elapsed_time = int(time.time() - self.start_time)
                    print("\n" + "="*50)
                    print("🎉 CONGRATULATIONS! YOU SOLVED THE PUZZLE! 🎉")
                    print("="*50)
                    print(f"Time taken: {elapsed_time // 60}m {elapsed_time % 60}s")
                    print(f"Total moves: {self.moves_count}")
                    print("\nType 'new' for a new game or 'quit' to exit")
                else:
                    print("\n❌ The board is complete but incorrect. Keep trying!")

            user_input = input("\nYour move: ").strip().lower()

            if user_input == 'quit':
                print("Thanks for playing!")
                break
            elif user_input == 'new':
                difficulty = input("Choose difficulty (easy/medium/hard) [medium]: ").strip().lower()
                if difficulty in ['easy', 'medium', 'hard']:
                    self.difficulty = difficulty
                self.generate_puzzle()
            elif user_input == 'solve':
                print("\nShowing solution...")
                self.display_board(self.solution)
                input("Press Enter to continue...")
            elif user_input == 'hint':
                hint = self.get_hint()
                if hint:
                    print(f"💡 Hint: Try placing {hint[2]} at row {hint[0]}, column {hint[1]}")
                else:
                    print("No hints available - board is complete!")
            else:
                try:
                    parts = user_input.split()
                    if len(parts) == 3:
                        row, col, num = map(int, parts)
                        if not self.make_move(row, col, num):
                            input("Press Enter to continue...")
                    else:
                        print("Invalid input. Use format: row col number (e.g., '5 3 7')")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
                    input("Press Enter to continue...")


def main():
    """Main entry point for the game"""
    print("Welcome to Sudoku!")
    difficulty = input("Choose difficulty (easy/medium/hard) [medium]: ").strip().lower()

    if difficulty not in ['easy', 'medium', 'hard']:
        difficulty = 'medium'

    game = SudokuGame(difficulty)
    game.play()


if __name__ == "__main__":
    main()
