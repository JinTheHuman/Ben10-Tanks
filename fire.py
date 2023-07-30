board = input().split()

width = int(board[0])
height = int(board[1])
numF = int(board[2])

fireworks = []
# fireworksA = []
for i in range(0,numF):
    firework = input().split()
    
    fireworks.append([int(firework[0]), int(firework[1])])

board = []
for x in range(0, width):
    board.append([])
    for y in range(0,height):
        board[x].append('.')

for x,y in fireworks:
    for cy in reversed(range(0, y + 1)):
        dust_x = x + (y - cy)
        for dust_y in reversed(range(0, cy + 1)):
            dy = cy - dust_y
            if (dust_x - dy) < 0:
                break

            if (dust_x - dy) >= width:
                continue
            if board[dust_x - dy][dust_y] == '.':
                board[dust_x - dy][dust_y] = '+'
            else:
                break
        
        dust_x = x + (y - cy) + 1
        for dust_y in reversed(range(0, cy)):
            dy = cy - dust_y
            if (dust_x - dy) < 0:
                break
            
            if (dust_x - dy) >= width:
                continue

            if board[dust_x - dy][dust_y] == '.':
                board[dust_x - dy][dust_y] = '+'
            else:
                break

    board[x][y] = "x"

for y in reversed(range(0, height)):
    for x in range(0, width):
        print(board[x][y], end='')
    print()
