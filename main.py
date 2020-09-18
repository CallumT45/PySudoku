from sudokuImage import SudokuImage
from functools import partial
import time
from sudoku import solve, board_valid, draw_board
import concurrent.futures as cf


def pool_process(cells, Su):
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


def setup():
    clipboard = ""
    while clipboard != 'Y' and clipboard != 'N':
        clipboard = input("Is the image a screen grab? Y/N\n")
    accuracy = ""
    while accuracy != '0' and accuracy != '1':
        accuracy = input("What level of accuracy? 0/1\n")
    PATH = ""
    if clipboard == "N":
        PATH = input("Please enter the image path\n")
    return clipboard == 'Y', int(accuracy), PATH


def main(clipboard, accuracy, PATH):
    tp1 = time.time()
    Su = SudokuImage(PATH, accuracy, clipboard)
    lines = Su.get_lines()
    cells = Su.get_inters(lines)
    pool_process(cells, Su)
    print("Overall Time:", int(time.time()-tp1), " seconds")


if __name__ == "__main__":
    clipboard, accuracy, PATH = setup()
    main(clipboard, accuracy, PATH)
