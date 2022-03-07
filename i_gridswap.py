#!/usr/bin/python3
import mortoray_path_finding as mpf
import math
import random
from mortoray_path_finding import maze

class MyFinder(mpf.draw.Finder):
    """Integrate into the simple UI """
    def __init__(self):

        # grid size
        self.size_x = 12
        self.size_y = 12

        # number of monte carlo simulations, increase for larger grids
        self.num_iters = 500

        # void_spaces = [[1, 6], [5, 5], [9, 10], [10, 2]] # set initial list of void spaces
        void_spaces = []

        self.maze1, self.void_spaces = mpf.maze.create_grid( self.size_x, self.size_y, void_spaces)

        self.nboard = self.maze1.board
        self.start = self.maze1.start
        self.void_spaces = void_spaces
        self.neighbours = [ [-1,0], [1,0], [0,-1], [0,1] ]

        # mark the start for the UI
        self.nboard.at( self.start ).mark = maze.CellMark.Start

        self.set_board(self.maze1.board)

        self.path = None

        self.screen_x = ''
        self.screen_y = ''
        self.display = ''

    def set_screen(self,screen_x,screen_y):
        self.screen_x = screen_x
        self.screen_y = screen_y

    def set_display(self,display):
        self.display = display
        self.set_caption("Gridswap Solver 2.0")

    def set_caption(self,caption):
        self.display.set_caption(caption)

    def step(self):
        self.solve()

    def mouse_click(self,pos):
        print("mouse was clicked at:",pos)
        x,y = self.mouse_pos_to_x_y(pos)

        print("toggle cell at x,y = %s" % [x,y])

        if [x,y] == [0,0]:
            return

        if [x,y] in self.void_spaces:
            self.void_spaces.remove([x,y])
        else:
            self.void_spaces += [[x,y]]


        self.maze1, self.void_spaces = mpf.maze.create_grid( self.size_x, self.size_y, self.void_spaces)
        self.set_board(self.maze1.board)

        # solve as soon as 4 black squares are activated?
        # if len(self.void_spaces) == 4:
        #     self.set_caption("Solving...")
        #     self.solve()

        self.run()

    def mouse_pos_to_x_y(self,pos):
        x = math.floor( pos[0] / self.screen_x * self.size_x )
        y = math.floor( pos[1] / self.screen_y * self.size_y )
        print(x,y)
        return x,y

    def reset(self):
        self.void_spaces = []
        self.maze1, self.void_spaces = mpf.maze.create_grid( self.size_x, self.size_y, self.void_spaces)
        self.set_board(self.maze1.board)
        self.set_path(None)

    def solve(self):
        current_length = 0
        longest_path_found = []

        self.theoretical_max_score = self.size_x * self.size_y - len(self.void_spaces)
        fully_solved = False

        if not longest_path_found:
            for i in range(1,self.num_iters+1):
                if i % 10 == 0:
                    self.set_caption("Solving: %s" % i)
                    print(i,end=" ")
                # print("%s %s" % (i,current_length))

                path_list = self.make_path()
                # print("%s %s" % (i,len(path_list)))

                if len(path_list) > current_length:
                    current_length = len(path_list)
                    longest_path_found = path_list
                    print("%s %s" % (i,current_length))
                    # self.set_caption("%s %s" % (i,current_length))
                    # print("longest_path_found = %s" % longest_path_found)

                if len(longest_path_found) == self.theoretical_max_score:
                    print("fully solved")
                    fully_solved = True
                    current_length = len(path_list)
                    longest_path_found = path_list
                    break

                # break

        print("longest path found = %s" % len(longest_path_found))

        path = []
        for item in longest_path_found:
            path.append(self.maze1.board.at(item))

        print("rendering...")

        self.set_path(path)

        if fully_solved:
            self.set_caption("Gridswap Solver: SOLVED! longest_path_found = %s" % len(longest_path_found))
        else:
            self.set_caption("Gridswap Solver: incomplete solution found: longest_path_found = %s" % len(longest_path_found))

    def make_path(self):
        path_list = [self.start]

        # (x,y) offsets from current cell
        # neighbours = [ [-1,0], [1,0], [0,-1], [0,1] ] # moved to top to optimise it slightly
        for index in range(0,self.theoretical_max_score+1):
            cur_pos = path_list[index]

            possible_neighbours = []

            for neighbour in self.neighbours:
                ncell_pos = maze.add_point(cur_pos, neighbour)

                if not self.nboard.is_valid_point(ncell_pos):
                    continue

                if ncell_pos in path_list:
                    continue

                if ncell_pos in self.void_spaces:
                    continue

                possible_neighbours.append(ncell_pos)
                # path_list.append(ncell_pos)

            # print(possible_neighbours)
            if not possible_neighbours:
                break

            # "The node with the fewest possible moves on the next action provided that it is at least one"
            # print(possible_neighbours)
            moves_next_turn = []
            for index, possible_neighbour in enumerate(possible_neighbours):
                # print(possible_neighbour)
                moves = 0
                for neighbour in self.neighbours:
                    neigh_of_neigh = maze.add_point(possible_neighbour, neighbour)
                    if not self.nboard.is_valid_point(neigh_of_neigh):
                        continue
                    if neigh_of_neigh in path_list:
                        continue
                    if neigh_of_neigh in self.void_spaces:
                        continue
                    if neigh_of_neigh == cur_pos:
                        continue
                    moves += 1
                moves_next_turn.append(moves)

            # print(moves_next_turn)
            for index, item in enumerate(moves_next_turn):
                if item == 0:
                    moves_next_turn[index] = 999

            min_indexes = [i for i, x in enumerate(moves_next_turn) if x == min(moves_next_turn)]
            index = random.choice(min_indexes)

            # next_cell = random.choice(possible_neighbours)
            # next_cell = possible_neighbours[0]
            next_cell = possible_neighbours[index]

            path_list.append(next_cell)
            # print(path_list)

        return path_list

header_text = """Keys:
    Left - Solve
    Right - Solve
    Space - Solve
    R - Reset
    Esc - Exit"""
print( header_text )

finder = MyFinder()
finder.run()
