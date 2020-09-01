from sudokuImage import SudokuImage

from pprint import pprint
from multiprocessing import Process, Manager
import time
from sudoku import solve


def draw_board(board):
    for i, line in enumerate(board):
        if i % 3 == 0:
            print("-"*27)
        print(
            f"{line[0]}  {line[1]}  {line[2]} | {line[3]}  {line[4]}  {line[5]} | {line[6]}  {line[7]}  {line[8]}")


def pool_process(cells):

    manager = Manager()
    board = manager.list()
    for _ in range(9):
        board.append(manager.list())
    tp1 = time.time()
    p1 = Process(target=Su.pop_board, args=(cells, range(9), board))
    p1.start()

    p2 = Process(target=Su.pop_board, args=(cells, range(9, 18), board))
    p2.start()

    p3 = Process(target=Su.pop_board, args=(cells, range(18, 27), board))
    p3.start()

    p4 = Process(target=Su.pop_board, args=(cells, range(27, 36), board))
    p4.start()

    p5 = Process(target=Su.pop_board, args=(cells, range(36, 45), board))
    p5.start()

    p6 = Process(target=Su.pop_board, args=(cells, range(45, 54), board))
    p6.start()

    p7 = Process(target=Su.pop_board, args=(cells, range(54, 63), board))
    p7.start()

    p8 = Process(target=Su.pop_board, args=(cells, range(63, 72), board))
    p8.start()

    p9 = Process(target=Su.pop_board, args=(cells, range(72, 81), board))
    p9.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    p9.join()

    print('finished main')
    # print(board)
    draw_board(board)
    board = list(map(lambda x: list(x), board))
    # pprint(board)
    solve(board)
    print()
    draw_board(board)
    print("Overall Time:", int(time.time()-tp1))


if __name__ == "__main__":

    Su = SudokuImage("web_sudoku.PNG")
    for size in [7, 5, 3]:
        print(size)
        lines = Su.get_lines(size)
        if len(lines) != 20:
            continue
        cells = Su.get_inters(lines)
        break
    pool_process(cells)
