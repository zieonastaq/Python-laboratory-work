import copy
import random
import os
import readchar


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""

    def __init__(self):
        self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class Labirint:
    IS_GENERATED = False
    WALL_CELL = '#'
    HALL_CELL = ' '
    PLAYER_CELL = 'P'
    START_CELL = 'S'
    FINISH_CELL = 'F'
    WAY_CELL = '.'

    x_dir = [1, 0, 0, -1]
    y_dir = [0, 1, -1, 0]

    def print(self):
        if not self.IS_GENERATED:
            print('didn\'t generated!')
            return
        for i in self.field:
            for j in i:
                print(j, end='')
            print()

    def is_able_to_become_hall(self, i, j, k):
        return 0 < i + 2 * self.x_dir[k] < self.height - 1 and 0 < j + 2 * self.y_dir[k] < self.width - 1 and \
               not self.is_visited[i + 2 * self.x_dir[k]][j + 2 * self.y_dir[k]]

    def generation_dfs(self, i, j):
        self.is_visited[i][j] = True
        for k in random.sample(range(4), 4):
            if self.is_able_to_become_hall(i, j, k):
                self.field[i + self.x_dir[k]][j + self.y_dir[k]] = self.HALL_CELL
                self.generation_dfs(i + 2 * self.x_dir[k], j + 2 * self.y_dir[k])

    def is_able_to_be_visited(self, i, j, k):
        return 0 < i + self.x_dir[k] < self.height - 1 and 0 < j + self.y_dir[k] < self.width - 1 and \
               self.field_copy[i + self.x_dir[k]][j + self.y_dir[k]] == self.HALL_CELL

    def coloring_dfs(self, i, j):
        self.field_copy[i][j] = self.color
        self.is_visited[i][j] = True

        for k in range(4):
            if self.is_able_to_be_visited(i, j, k):
                self.coloring_dfs(i + self.x_dir[k], j + self.y_dir[k])

    def is_able_to_be_vanished_to_connect(self, i, j):
        if self.field_copy[i][j] != self.WALL_CELL:
            return [False, 0, 0]
        elif 1 < i < self.height - 1 and self.field_copy[i - 1][j] != self.field_copy[i + 1][j] and \
                self.field_copy[i - 1][j] != self.WALL_CELL and self.field_copy[i + 1][j] != self.WALL_CELL and \
                1 < j < self.width - 1 and self.field_copy[i][j - 1] != self.field_copy[i][j + 1] and \
                self.field_copy[i][j - 1] != self.WALL_CELL and self.field_copy[i][j + 1] != self.WALL_CELL and \
                random.randint(0, 1) == 0:
            return [True, i - 1, j, i + 1, j]
        elif 1 < i < self.height - 1 and self.field_copy[i - 1][j] != self.field_copy[i + 1][j] and \
                self.field_copy[i - 1][j] != self.WALL_CELL and self.field_copy[i + 1][j] != self.WALL_CELL and \
                1 < j < self.width - 1 and self.field_copy[i][j - 1] != self.field_copy[i][j + 1] and \
                self.field_copy[i][j - 1] != self.WALL_CELL and self.field_copy[i][j + 1] != self.WALL_CELL:
            return [True, i, j - 1, i, j + 1]
        elif 1 < i < self.height - 1 and self.field_copy[i - 1][j] != self.field_copy[i + 1][j] and \
                self.field_copy[i - 1][j] != self.WALL_CELL and self.field_copy[i + 1][j] != self.WALL_CELL:
            return [True, i - 1, j, i + 1, j]
        elif 1 < j < self.width - 1 and self.field_copy[i][j - 1] != self.field_copy[i][j + 1] and \
                self.field_copy[i][j - 1] != self.WALL_CELL and self.field_copy[i][j + 1] != self.WALL_CELL:
            return [True, i, j - 1, i, j + 1]
        return [False, 0, 0]

    def generate_via_dfs(self):
        self.IS_GENERATED = True
        for i in range(1, self.height - 1, 2):
            for j in range(1, self.width - 1, 2):
                if not self.is_visited[i][j]:
                    self.generation_dfs(i, j)

        self.field_copy = copy.deepcopy(self.field)

        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.field_copy[i][j] == self.HALL_CELL:
                    self.coloring_dfs(i, j)
                    self.color += 1

        while self.color > 1:
            flag = True
            for i in range(1, self.height - 1):
                if not flag:
                    break
                for j in range(1, self.width - 1):
                    res = self.is_able_to_be_vanished_to_connect(i, j)
                    if res[0]:
                        self.field[i][j] = self.HALL_CELL
                        flag = False
                        break

            self.color = 0

            self.field_copy = copy.deepcopy(self.field)

            for i in range(1, self.height - 1):
                for j in range(1, self.width - 1):
                    if self.field_copy[i][j] == self.HALL_CELL:
                        self.coloring_dfs(i, j)
                        self.color += 1

    def bfs(self):
        self.field_copy[1][1] = 0
        stack = [[1, 1]]

        while stack:
            u = stack[-1]
            stack.pop()
            for k in range(4):
                if self.field_copy[u[0] + self.x_dir[k]][u[1] + self.y_dir[k]] == self.HALL_CELL:
                    self.field_copy[u[0] + self.x_dir[k]][u[1] + self.y_dir[k]] = self.field_copy[u[0]][u[1]] + 1
                    stack.append([u[0] + self.x_dir[k], u[1] + self.y_dir[k]])

    def solve(self):
        if self.field[1][1] == self.START_CELL:
            print('already solved!')
            return

        self.field_copy = copy.deepcopy(self.field)
        self.bfs()

        u = [self.height - 2, self.width - 2]

        while u != [1, 1]:
            self.field[u[0]][u[1]] = self.WAY_CELL

            for k in range(4):
                if self.field_copy[u[0] + self.x_dir[k]][u[1] + self.y_dir[k]] == self.field_copy[u[0]][u[1]] - 1:
                    u = [u[0] + self.x_dir[k], u[1] + self.y_dir[k]]
                    break

        self.field[1][1] = self.START_CELL
        self.field[self.height - 2][self.width - 2] = self.FINISH_CELL

    def generate_via_minimum_spanning_tree(self):
        self.IS_GENERATED = True
        edges = []

        for i in range(1, self.height - 3, 2):
            for j in range(1, self.width - 3, 2):
                edges.append([random.randint(1, 1600), (i, j), (i + 2, j)])
                edges.append([random.randint(1, 1600), (i, j), (i, j + 2)])

        edges.sort()
        visited = set()

        while edges:
            u = edges[0]
            edges.pop(0)

            if u[1][0] - u[2][0] < 0:
                self.field[u[1][0] + 1][u[1][1]] = self.HALL_CELL
            else:
                self.field[u[1][0]][u[1][1] + 1] = self.HALL_CELL

            visited.add(u[1])
            visited.add(u[2])

            edges1 = []

            for i in edges:
                if not (i[1] in visited and i[2] in visited):
                    edges1.append(i)

            edges = edges1

        self.field_copy = copy.deepcopy(self.field)

        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.field_copy[i][j] == self.HALL_CELL:
                    self.coloring_dfs(i, j)
                    self.color += 1

        while self.color > 1:
            flag = True
            for i in range(1, self.height - 1):
                if not flag:
                    break
                for j in range(1, self.width - 1):
                    res = self.is_able_to_be_vanished_to_connect(i, j)
                    if res[0]:
                        self.field[i][j] = self.HALL_CELL
                        flag = False
                        break

            self.color = 0

            self.field_copy = copy.deepcopy(self.field)

            for i in range(1, self.height - 1):
                for j in range(1, self.width - 1):
                    if self.field_copy[i][j] == self.HALL_CELL:
                        self.coloring_dfs(i, j)
                        self.color += 1

        for i in range(2, self.width - 1, 2):
            if random.randint(0, 2) == 0:
                self.field[self.height - 2][i] = self.HALL_CELL

    def play(self):
        if not self.IS_GENERATED:
            print('didn\'t generated!')
            return

        player_pos = [1, 1]
        self.field[player_pos[0]][player_pos[1]] = self.PLAYER_CELL
        self.field[self.height - 2][self.width - 2] = self.FINISH_CELL
        self.print()

        while player_pos != [self.height - 2, self.width - 2]:
            move = readchar.readkey()
            os.system('cls||clear')

            if move == 'w' and self.field[player_pos[0] - 1][player_pos[1]] != self.WALL_CELL:
                if player_pos == [1, 1]:
                    self.field[player_pos[0]][player_pos[1]] = self.START_CELL
                else:
                    self.field[player_pos[0]][player_pos[1]] = self.HALL_CELL
                player_pos[0] -= 1
            elif move == 'a' and self.field[player_pos[0]][player_pos[1] - 1] != self.WALL_CELL:
                if player_pos == [1, 1]:
                    self.field[player_pos[0]][player_pos[1]] = self.START_CELL
                else:
                    self.field[player_pos[0]][player_pos[1]] = self.HALL_CELL
                player_pos[1] -= 1
            elif move == 's' and self.field[player_pos[0] + 1][player_pos[1]] != self.WALL_CELL:
                if player_pos == [1, 1]:
                    self.field[player_pos[0]][player_pos[1]] = self.START_CELL
                else:
                    self.field[player_pos[0]][player_pos[1]] = self.HALL_CELL
                player_pos[0] += 1
            elif move == 'd' and self.field[player_pos[0]][player_pos[1] + 1] != self.WALL_CELL:
                if player_pos == [1, 1]:
                    self.field[player_pos[0]][player_pos[1]] = self.START_CELL
                else:
                    self.field[player_pos[0]][player_pos[1]] = self.HALL_CELL
                player_pos[1] += 1
            elif move == 'q':
                return

            self.field[player_pos[0]][player_pos[1]] = self.PLAYER_CELL
            self.print()

    def save(self):
        files = os.listdir()
        i = 0
        while str(i) + '.txt' in files:
            i += 1
        file = open(str(i) + '.txt', 'w')
        file.write(str(self.height) + ' ' + str(self.width) + '\n')
        for i in self.field:
            for j in i:
                file.write(j)
            file.write('\n')
        file.close()

    def __init__(self, num=-1):
        random.seed()
        if num != -1:
            self.IS_GENERATED = True
            file = open(str(num) + '.txt')
            self.height, self.width = [int(i) for i in file.readline().split(' ')]
            self.field = [['#'] * self.width for i in range(self.height)]

            for i in range(self.width):
                s = file.readline()
                for j, char in enumerate(s):
                    if char != '\n':
                        self.field[i][j] = char
        else:
            self.width = random.randint(15, 17) * 2 + 1
            self.height = random.randint(15, 17) * 2 + 1

            self.field = [[self.WALL_CELL] * self.width for i in range(self.height)]

            for i in range(1, self.height, 2):
                for j in range(1, self.width, 2):
                    self.field[i][j] = self.HALL_CELL

        self.is_visited = [[False] * self.width for i in range(self.height)]
        self.field_copy = [[]]
        self.color = 0


if __name__ == '__main__':
    a = Labirint()

    while True:
        command = input()

        if command == 'gen dfs':
            a = Labirint()
            a.generate_via_dfs()
        elif command == 'gen tree':
            a = Labirint()
            a.generate_via_minimum_spanning_tree()
        elif command == 'print':
            a.print()
        elif command == 'solve':
            a.solve()
        elif command == 'play':
            a.play()
        elif command == 'save':
            a.save()
        elif command == 'load':
            num = int(input('num of labirint: '))
            a = Labirint(num)
        elif command == 'q':
            break
        else:
            print('unknown command')
