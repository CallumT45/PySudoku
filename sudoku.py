def solve(bo):
    find = find_empty(bo)
    if not find:
        return True
    else:
        row, col = find

    for i in range(1, 10):
        if valid(bo, i, (row, col)):
            bo[row][col] = i

            if solve(bo):
                return True

            bo[row][col] = 0

    return False


def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


def draw_board(board):
    for i, line in enumerate(board):
        if i % 3 == 0:
            print("-"*27)
        print(
            f"{line[0]}  {line[1]}  {line[2]} | {line[3]}  {line[4]}  {line[5]} | {line[6]}  {line[7]}  {line[8]}")


if __name__ == "__main__":
    board = [[6, 0, 0, 0, 0, 0, 9, 0, 7], [7, 9, 0, 0, 1, 0, 6, 3, 0], [4, 0, 1, 6, 0, 0, 8, 0, 0], [0, 0, 3, 7, 0, 8, 4, 0, 0], [
        0, 0, 7, 4, 0, 1, 3, 0, 0], [0, 0, 4, 9, 0, 3, 2, 0, 0], [0, 0, 9, 0, 0, 6, 5, 0, 8], [0, 7, 6, 0, 8, 0, 0, 9, 3], [8, 0, 2, 0, 0, 0, 0, 0, 6]]
    draw_board(board)
    solve(board)
    print()
    draw_board(board)
