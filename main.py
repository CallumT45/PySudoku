from cogs.sudokuImage import SudokuImage
from cogs.sudoku import solve, board_valid, draw_board

import concurrent.futures as cf
from functools import partial
import time


def pool_process(cells, Su):
    print("Reading in data")
    # creates empty board
    board = [[0 for i in range(9)] for i in range(9)]
    i = 0
    # for each cell, run ocr and get value then set the value of that cell equal to returned value
    with cf.ProcessPoolExecutor() as executor:
        for number, value in zip(cells, executor.map(Su.pop_board, cells)):
            board[i//9][i % 9] = value
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
    conv = {'0': 5, '1': 10}
    print(
        f"You have selected an accuracy setting of {accuracy}! Expected run time is {conv.get(accuracy)} seconds")
    PATH = ""
    if clipboard == "N":
        PATH = input("Please enter the image path\n")
    return clipboard == 'Y', int(accuracy), PATH


def main(clipboard, accuracy, PATH):
    tp = time.time()
    Su = SudokuImage(PATH, accuracy, clipboard)
    lines = Su.get_lines()
    cells = Su.get_inters(lines)
    pool_process(cells, Su)
    print("Overall Time:", int(time.time()-tp), " seconds")


if __name__ == "__main__":
    clipboard, accuracy, PATH = setup()
    main(clipboard, accuracy, PATH)
