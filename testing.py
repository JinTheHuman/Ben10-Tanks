board = input().split()

width = int(board[0])
height = int(board[1])
numF = int(board[2])

fireworks = []
for i in range(0, numF):
    firework = input().split()

    fireworks.append([int(firework[0]), int(firework[1])])


board = []
for x in range(0, width):
    board.append([])
    for y in range(0, height):
        board[x].append('.')

for x, y in fireworks:
    board[x][y] = "x"
    for dust_y in range(0, y):
        for dust_x in range(x - (y - dust_y), x + (y - dust_y) + 1):
            if 0 <= dust_x < width:
                if board[dust_x][dust_y] == '.':
                    board[dust_x][dust_y] = '+'


for y in reversed(range(0, height)):
    for x in range(0, width):
        print(board[x][y], end='')
    print()


'''
....................
......x.............
.....+++............
....+++++...........
...+++++++..........
..+++++++++.........
.+++++++++++........
+++++++++++++.......
'''