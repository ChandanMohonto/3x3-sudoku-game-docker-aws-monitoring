#!/usr/bin/env python3
"""
Web-based Sudoku Puzzle Game using Flask
Access via browser on port 5000
"""

from flask import Flask, render_template, jsonify, request
import random
import copy
from typing import List, Tuple, Optional

app = Flask(__name__)

# Store game sessions (in production, use Redis or database)
games = {}


class SudokuGame:
    """Sudoku game logic"""

    def __init__(self, difficulty: str = "medium"):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.difficulty = difficulty
        self.moves_count = 0

    def is_valid_move(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing a number is valid"""
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
        """Solve using backtracking"""
        empty = self.find_empty_cell(board)
        if not empty:
            return True

        row, col = empty

        for num in range(1, 10):
            if self.is_valid_move(board, row, col, num):
                board[row][col] = num

                if self.solve_board(board):
                    return True

                board[row][col] = 0

        return False

    def find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find empty cell"""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def generate_complete_board(self) -> List[List[int]]:
        """Generate complete valid board"""
        board = [[0 for _ in range(9)] for _ in range(9)]

        # Fill diagonal boxes
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    board[box + i][box + j] = nums[i * 3 + j]

        self.solve_board(board)
        return board

    def remove_numbers(self, board: List[List[int]], difficulty: str) -> List[List[int]]:
        """Remove numbers based on difficulty"""
        cells_to_remove = {
            'easy': 35,
            'medium': 45,
            'hard': 55
        }.get(difficulty, 45)

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

                copy_board = copy.deepcopy(puzzle)
                if self.solve_board(copy_board):
                    cells_removed += 1
                else:
                    puzzle[row][col] = backup

            attempts += 1

        return puzzle

    def generate_puzzle(self):
        """Generate new puzzle"""
        complete_board = self.generate_complete_board()
        self.solution = copy.deepcopy(complete_board)
        self.board = self.remove_numbers(complete_board, self.difficulty)
        self.initial_board = copy.deepcopy(self.board)
        self.moves_count = 0

    def make_move(self, row: int, col: int, num: int) -> dict:
        """Make a move and return result"""
        # Check if cell is part of initial puzzle
        if self.initial_board[row][col] != 0:
            return {
                'success': False,
                'message': 'Cannot modify original puzzle cells'
            }

        # Make the move
        self.board[row][col] = num
        self.moves_count += 1

        # Check if board is complete
        if self.is_board_complete():
            if self.is_board_correct():
                return {
                    'success': True,
                    'message': 'Congratulations! You solved the puzzle!',
                    'complete': True
                }
            else:
                return {
                    'success': True,
                    'message': 'Board is complete but has errors',
                    'complete': False
                }

        return {
            'success': True,
            'message': 'Move made successfully'
        }

    def is_board_complete(self) -> bool:
        """Check if board is full"""
        for row in self.board:
            if 0 in row:
                return False
        return True

    def is_board_correct(self) -> bool:
        """Check if board matches solution"""
        return self.board == self.solution

    def get_hint(self) -> Optional[dict]:
        """Get a hint"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return {
                        'row': i,
                        'col': j,
                        'value': self.solution[i][j]
                    }
        return None


# Flask routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start new game"""
    data = request.json
    difficulty = data.get('difficulty', 'medium')
    session_id = str(random.randint(10000, 99999))

    game = SudokuGame(difficulty)
    game.generate_puzzle()
    games[session_id] = game

    return jsonify({
        'session_id': session_id,
        'board': game.board,
        'initial_board': game.initial_board,
        'difficulty': difficulty
    })


@app.route('/api/make_move', methods=['POST'])
def make_move():
    """Make a move"""
    data = request.json
    session_id = data.get('session_id')
    row = data.get('row')
    col = data.get('col')
    value = data.get('value')

    if session_id not in games:
        return jsonify({'error': 'Invalid session'}), 400

    game = games[session_id]
    result = game.make_move(row, col, value)

    return jsonify({
        **result,
        'board': game.board,
        'moves': game.moves_count
    })


@app.route('/api/get_hint', methods=['POST'])
def get_hint():
    """Get a hint"""
    data = request.json
    session_id = data.get('session_id')

    if session_id not in games:
        return jsonify({'error': 'Invalid session'}), 400

    game = games[session_id]
    hint = game.get_hint()

    if hint:
        return jsonify(hint)
    else:
        return jsonify({'message': 'No hints available'})


@app.route('/api/check_board', methods=['POST'])
def check_board():
    """Check if board is correct"""
    data = request.json
    session_id = data.get('session_id')

    if session_id not in games:
        return jsonify({'error': 'Invalid session'}), 400

    game = games[session_id]

    # Count errors
    errors = []
    for i in range(9):
        for j in range(9):
            if game.board[i][j] != 0 and game.board[i][j] != game.solution[i][j]:
                errors.append({'row': i, 'col': j})

    return jsonify({
        'correct': len(errors) == 0,
        'errors': errors,
        'error_count': len(errors)
    })


@app.route('/api/solve', methods=['POST'])
def solve():
    """Show solution"""
    data = request.json
    session_id = data.get('session_id')

    if session_id not in games:
        return jsonify({'error': 'Invalid session'}), 400

    game = games[session_id]

    return jsonify({
        'solution': game.solution
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
