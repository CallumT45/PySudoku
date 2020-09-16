from sudokuImage import SudokuImage
from functools import partial
import time
from sudoku import solve, board_valid, draw_board

import concurrent.futures as cf


def pool_process(cells):
    print("Reading in data")
    board = [[0 for i in range(9)] for i in range(9)]
    i = 0
    with cf.ProcessPoolExecutor() as executor:
        for number, value in zip(cells, executor.map(Su.pop_board, cells)):
            board[i//9][i % 9] = value
            # print(i, value)
            i += 1

    draw_board(board)
    if board_valid(board):
        print("\nSolving board\n")
        solve(board)
        draw_board(board)
    else:
        print(
            "Looks like there was an error reading in the data, try using a clearer image")


if __name__ == "__main__":
    tp1 = time.time()
    # Su = SudokuImage(False, "images/web_sudoku.PNG")
    # Su = SudokuImage("images/fuzzy_sudoku.jpg", 0, False)
    Su = SudokuImage("", accuracy=0, clipboard=True)
    lines = Su.get_lines()
    cells = Su.get_inters(lines)
    pool_process(cells)
    print("Overall Time:", int(time.time()-tp1))
