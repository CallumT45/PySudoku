from sudokuImage import SudokuImage
from functools import partial
import time
from sudoku import solve

import concurrent.futures as cf


def draw_board(board):
    for i, line in enumerate(board):
        if i % 3 == 0:
            print("-"*27)
        print(
            f"{line[0]}  {line[1]}  {line[2]} | {line[3]}  {line[4]}  {line[5]} | {line[6]}  {line[7]}  {line[8]}")


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
    print("\nSolving board\n")
    solve(board)
    draw_board(board)


if __name__ == "__main__":
    tp1 = time.time()
    # Su = SudokuImage(False, "images/web_sudoku.PNG")
    Su = SudokuImage("images/fuzzy_sudoku.jpg", 0, False)
    # Su = SudokuImage(True, "", accuracy=0)
    lines = Su.get_lines()
    cells = Su.get_inters(lines)
    pool_process(cells)
    print("Overall Time:", int(time.time()-tp1))


# ocr crop should be dynamic
# need to add timeout
# need to add a return if 20 lines not found
# need to add check that niput board is correct
