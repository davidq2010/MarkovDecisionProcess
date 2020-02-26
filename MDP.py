from enum import IntEnum
from functools import reduce
import sys

BIG_NEG = -100000000000000

# Build graph
rows = 4
cols = 3

class Action(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

def print_util_graph(graph):
    space = 8
    line_width = space * cols + cols+1
    output = []
    output.append("{:{fill}<{width}}".format('', fill='-', width=line_width) + "\n")
    for i in range(rows):
        line = '|'
        for j in range(cols):
            line += ("{:{width}}".format('', width=space) if graph[i][j] == BIG_NEG
                else "{:^{width}.3f}".format(graph[i][j], width=space))
            line += "|"
        output.append(line + "\n")
        output.append("{:{fill}<{width}}".format('', fill='-', width=line_width) + "\n")

    for i in range(len(output)):
        for j in range(cols):
            if i % 2 == 0 and ((i/2, j) in terminals or ((i-2)/2, j) in terminals):
                start = j*(space+1) + 1
                end = start + space
                new_line = output[i][0:start] + '=' * (space) + output[i][end:]
                output[i] = new_line
    print(''.join(output))

def max_of_neighbors(util_graph, coord):
    new_coords = []
    best_dir = []
    for unit_dir in unit_dirs:
        new_coord = (coord[0] + unit_dir[0], coord[1] + unit_dir[1])
        if in_bounds(new_coord) and new_coord not in blocked:
            new_coords.append(new_coord)
            best_dir.append(unit_dir)
    max_val = max([util_graph[coord[0]][coord[1]] for coord in new_coords])
    filtered_coords = []
    for i in range(len(new_coords)):
        if max_val - 0.0001 <= util_graph[new_coords[i][0]][new_coords[i][1]] <= max_val + 0.0001:
            filtered_coords.append(best_dir[i])
    return set(filtered_coords)

policy_dict = {Action.NORTH: "^",
               Action.EAST: ">",
               Action.SOUTH: "v",
               Action.WEST: "<"}

def print_policy_graph(util_graph):
    #or i in range(rows * 3 + rows + 1)
    space = 8
    line_width = space * cols + cols+1
    output = []
    output.append("{:{fill}<{width}}".format('', fill='-', width=line_width))
    for i in range(rows):
        for j in range(cols):
            if (i, j) in blocked:
                for cell_row in range(3):
                    line = "{:{width}}".format('', width=space) + "|"
                    if j == 0:
                        output.append("|" + line)
                    else:
                        output[cell_row-3] += line
            elif (i, j) in terminals:
                line = "{:{width}}".format('', width=space) + "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-3] += line
                line = "{:^{width}.3f}".format(util_graph[i][j], width=space) + "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-2] += line
                line = "{:{width}}".format('', width=space) + "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-1] += line
            else:
                best_dirs = max_of_neighbors(util_graph, (i, j))
                line = "{:{width}}".format('', width=space)
                if unit_dirs[Action.NORTH] in best_dirs:
                    line = "{:^{width}}".format(policy_dict[Action.NORTH], width=space)
                line += "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-3] += line
                line = "{:{width}}".format('', width=space-1)
                if unit_dirs[Action.WEST] in best_dirs:
                    line = "{:<{width}}".format(policy_dict[Action.WEST], width=space-1)
                if unit_dirs[Action.EAST] in best_dirs:
                    line += policy_dict[Action.EAST]
                else:
                    line += " "
                line += "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-2] += line
                line = "{:{width}}".format('', width=space)
                if unit_dirs[Action.SOUTH] in best_dirs:
                    line = "{:^{width}}".format(policy_dict[Action.SOUTH], width=space)
                line += "|"
                if j == 0:
                    output.append("|" + line)
                else:
                    output[-1] += line
        output.append("{:{fill}<{width}}".format('', fill='-', width=line_width))

    for i in range(len(output)):
        for j in range(cols):
            if i % 4 == 0 and ((i/4, j) in terminals or ((i-4)/4, j) in terminals):
                start = j*(space+1) + 1
                end = start + space
                new_line = output[i][0:start] + '=' * (space) + output[i][end:]
                output[i] = new_line
    print('\n'.join(output))

def in_bounds(coord):
    return (0 <= coord[0] < rows) and (0 <= coord[1] < cols)

def compute_policy_probs(coord, action):
    direction = unit_dirs[action]
    new_coord = (coord[0] + direction[0], coord[1] + direction[1])
    if coord in cell_class["land"]:
        return [(1, new_coord)]
    elif coord in cell_class["water"]:
        west_dir = unit_dirs[Action.WEST]
        west_coord = (coord[0] + west_dir[0], coord[1] + west_dir[1])
        return [(0.75, new_coord), (0.25, west_coord)]

def util_of_action(coord, action):
    direction = unit_dirs[action]
    new_coord = (coord[0] + direction[0], coord[1] + direction[1])
    if not in_bounds(new_coord) or new_coord in blocked:
        return util_graph[coord[0]][coord[1]]
    policy_probs = compute_policy_probs(coord, action)
    util = 0
    for policy_prob in policy_probs:
        util += policy_prob[0] * util_graph[policy_prob[1][0]][policy_prob[1][1]]
    return util

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 MDP.py <initial_reward>")
        exit(1)

    initial_reward = int(sys.argv[1])
    print(initial_reward)

    r_graph = [[initial_reward for j in range(cols)] for i in range(rows)]
    util_graph = [[0 for j in range(cols)] for i in range(rows)]

    # Blank spots; not necessary, just in case I think (bc they're already in blocked)
    util_graph[0][0] = util_graph[3][0] = r_graph[0][0] = r_graph[3][0] = BIG_NEG

    # Terminals
    util_graph[1][0] = r_graph[1][0] = -100
    util_graph[2][0] = r_graph[2][0] = -100

    util_graph[3][1] = r_graph[3][1] = 100

    terminals = set([(1, 0), (2, 0), (3, 1)])
    blocked = set([(0, 0), (3, 0)])

    unit_dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)] # N E S W

    cell_class = {"land": set([(0, 1), (0, 2), (3, 2)]),
                  "water": set([(1, 1), (1, 2), (2, 1), (2, 2)])}

    discount = 1
    count = 0
    while(count < 10):
        for i in range(rows):
            for j in range(cols):
                if (i, j) not in terminals and (i, j) not in blocked:
                    max_util = max([util_of_action((i, j), action)
                        for action in range(len(unit_dirs))])
                    util_of_coord = r_graph[i][j] + discount * max_util
                    util_graph[i][j] = util_of_coord
        count += 1

    print_util_graph(util_graph)
    print_policy_graph(util_graph)
