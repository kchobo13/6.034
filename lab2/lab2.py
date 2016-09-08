from search import Edge, UndirectedGraph, do_nothing_fn, make_generic_search
import read_graphs

all_graphs = read_graphs.get_graphs()
GRAPH_0 = all_graphs['GRAPH_0']
GRAPH_1 = all_graphs['GRAPH_1']
GRAPH_2 = all_graphs['GRAPH_2']
GRAPH_3 = all_graphs['GRAPH_3']
GRAPH_FOR_HEURISTICS = all_graphs['GRAPH_FOR_HEURISTICS']

#Change this to True if you want to run additional local tests for debugging:
RUN_ADDITIONAL_TESTS = False

#### PART 1: Helper Functions #########################################

def path_length(graph, path):
    if len(path) == 0:
        return 0
    else:
        final_length = 0
        for index in xrange(len(path)-1):
            one_path = graph.get_edge(path[index],path[index+1]).length
            final_length += one_path
        return final_length

def has_loops(path):
    visited = []
    for node in path:
        if node not in visited:
            visited.append(node)
        else:
            return True
    return False


def extensions(graph, path):
    if not isinstance(path,list):
        path = [path]

    final_list = []
    last_node = path[-1]
    neighbors = graph.get_neighbors(last_node)

    for node in neighbors:
        if node in path:
            continue
        if len(path) != 1:
            if node != path[-2]:
                final_list.append(path+[node])
        else:
            final_list.append(path+[node])

    return final_list


def sort_by_heuristic(graph, goalNode, nodes):
    values = []
    final_list = []
    for node in nodes:
        heuristic = graph.get_heuristic_value(node, goalNode)
        values.append((node,heuristic))
        values = sorted(values, key=lambda value: value[0])
        values = sorted(values, key=lambda value: value[1])
    for (node,value) in values:
        final_list.append(node)
    return final_list


# You can ignore the following line.  It allows generic_search (PART 3) to 
# access the extensions and has_loops functions that you defined in PART 1.
generic_search = make_generic_search(extensions, has_loops)  # DO NOT CHANGE

#### PART 2: Search Algorithms #########################################

# Note: Optionally, you may skip to Part 3: Generic Search,
# then complete Part 2 using your answers from Part 3.

#my_dfs_fn = generic_search(*generic_dfs)
#my_dfs_path = my_dfs_fn(GRAPH_2, 'S', 'G')

def dfs(graph, startNode, goalNode):
    return generic_search(*generic_dfs)(graph,startNode,goalNode)

    # if goalNode not in graph.nodes:
    #     return None
    #
    # stack = [(startNode,[startNode])]
    # visited = []
    #
    # while stack:
    #     (node,path) = stack.pop(0)
    #     visited.append(node)
    #     neighboradd = []
    #
    #     for point in graph.get_neighbors(node):
    #         if point in visited:
    #             continue
    #         neighboradd.append((point,path+[point]))
    #     stack = neighboradd+stack
    #
    #     if stack[0][0] == goalNode:
    #         return stack[0][1]


def bfs(graph, startNode, goalNode):
    return generic_search(*generic_bfs)(graph,startNode,goalNode)
    # if goalNode not in graph.nodes:
    #     return None
    #
    # queue = [(startNode,[startNode])]
    # visited = []
    # while queue:
    #     (node,path) = queue.pop(0)
    #     visited.append(node)
    #
    #     for point in graph.get_neighbors(node):
    #         if point in visited:
    #             continue
    #         queue.append((point,path+[point]))
    #
    #         if point == goalNode:
    #             return path + [goalNode]



def hill_climbing(graph, startNode, goalNode):
    return generic_search(*generic_hill_climbing)(graph,startNode,goalNode)


def best_first(graph, startNode, goalNode):
    return generic_search(*generic_best_first)(graph,startNode,goalNode)


def beam(graph, startNode, goalNode, beam_width):
    if goalNode not in graph.nodes:
        return None

    queue = [[startNode]]
    k_level = 1
    while queue:
        path = queue.pop(0)
        if len(path) == k_level:
            for point in graph.get_neighbors(path[-1]):
                if point in path:
                    continue
                queue.append(path+[point])

                if point == goalNode:
                    return path + [goalNode]
        else:
            k_level += 1
            queue = [path] + queue
            sorted_queue = sort_by_heuristics(graph,goalNode,queue)
            queue = []
            for i in xrange(len(sorted_queue)):
                queue.append(sorted_queue[i])
            queue = queue[:beam_width]







def branch_and_bound(graph, startNode, goalNode):
    return generic_search(*generic_branch_and_bound)(graph,startNode,goalNode)


def branch_and_bound_with_heuristic(graph, startNode, goalNode):
    return generic_search(*generic_branch_and_bound_with_heuristic)(graph,startNode,goalNode)


def branch_and_bound_with_extended_set(graph, startNode, goalNode):
    return generic_search(*generic_branch_and_bound_with_extended_set)(graph,startNode,goalNode)


def a_star(graph, startNode, goalNode):
    return generic_search(*generic_a_star)(graph,startNode,goalNode)


#### PART 3: Generic Search #######################################

# Define your custom path-sorting functions here.  
# Each path-sorting function should be in this form:

# def my_sorting_fn(graph, goalNode, paths):
#     # YOUR CODE HERE
#     return sorted_paths

def sort_by_heuristics(graph,goalNode, paths):
    sorted_paths =[]
    lengths = []
    for path in paths:
        lengths.append((path,graph.get_heuristic_value(path[-1],goalNode)))

    lengths = sorted(lengths, key=lambda value: value[0])
    sorted_lengths = sorted(lengths, key=lambda value: value[1])

    for (path,length) in sorted_lengths:
        sorted_paths.append(path)
    return sorted_paths


def sort_by_path_length(graph,goalNode,paths):
    sorted_paths = []
    lengths = []
    for path in paths:
        length = path_length(graph,path)
        lengths.append((path,length))

    lengths = sorted(lengths, key=lambda value: value[0])
    sorted_lengths = sorted(lengths, key=lambda value: value[1])

    for (path,length) in sorted_lengths:
        sorted_paths.append(path)
    return sorted_paths

def sort_by_cost(graph,goalNode,paths):
    sorted_paths = []
    lengths = []
    for path in paths:
        length = path_length(graph,path) + graph.get_heuristic_value(path[-1],goalNode)
        lengths.append((path,length))

    lengths = sorted(lengths, key=lambda value: value[0])
    sorted_lengths = sorted(lengths, key=lambda value: value[1])

    for (path,length) in sorted_lengths:
        sorted_paths.append(path)
    return sorted_paths

def break_ties(paths):
    return sorted(paths)

def alphabetical_sort(graph,goalNode,paths):
    return break_ties(paths)


generic_dfs = [alphabetical_sort, True, do_nothing_fn, False]

generic_bfs = [alphabetical_sort, False, do_nothing_fn, False]

generic_hill_climbing = [sort_by_heuristics, True, do_nothing_fn, False]

generic_best_first = [sort_by_heuristics, True, sort_by_heuristics, False]

generic_branch_and_bound = [do_nothing_fn, False, sort_by_path_length, False]

generic_branch_and_bound_with_heuristic = [do_nothing_fn, False, sort_by_cost, False]

generic_branch_and_bound_with_extended_set = [do_nothing_fn, False, sort_by_path_length, True]

generic_a_star = [do_nothing_fn, False, sort_by_cost, True]

# Here is an example of how to call generic_search (uncomment to run):
#my_dfs_fn = generic_search(*generic_dfs)
#my_dfs_path = my_dfs_fn(GRAPH_2, 'S', 'G')
#print my_dfs_path

# Or, combining the first two steps:
#my_dfs_path = generic_search(*generic_dfs)(GRAPH_2, 'S', 'G')
#print my_dfs_path


### OPTIONAL: Generic Beam Search
# If you want to run local tests for generic_beam, change TEST_GENERIC_BEAM to True:
TEST_GENERIC_BEAM = False

# The sort_agenda_fn for beam search takes fourth argument, beam_width:
# def my_beam_sorting_fn(graph, goalNode, paths, beam_width):
#     # YOUR CODE HERE
#     return sorted_beam_agend

generic_beam = [None, None, None, None]

# Uncomment this to test your generic_beam search:
#print generic_search(*generic_beam)(GRAPH_2, 'S', 'G', beam_width=2)


#### PART 4: Heuristics ###################################################

def is_admissible(graph, goalNode):
    for node in graph.nodes:
        if graph.get_heuristic_value(node,goalNode) > path_length(graph,a_star(graph,node,goalNode)):
            return False
    return True


def is_consistent(graph, goalNode):
    for edge in graph.edges:
        if edge.length >= abs(graph.get_heuristic_value(edge.startNode, goalNode) - graph.get_heuristic_value(edge.endNode,goalNode)):
            continue
        else:
            return False
    return True


### OPTIONAL: Picking Heuristics
# If you want to run local tests on your heuristics, change TEST_HEURISTICS to True:
TEST_HEURISTICS = False

# heuristic_1: admissible and consistent

[h1_S, h1_A, h1_B, h1_C, h1_G] = [None, None, None, None, None]

heuristic_1 = {'G': {}}
heuristic_1['G']['S'] = h1_S
heuristic_1['G']['A'] = h1_A
heuristic_1['G']['B'] = h1_B
heuristic_1['G']['C'] = h1_C
heuristic_1['G']['G'] = h1_G


# heuristic_2: admissible but NOT consistent

[h2_S, h2_A, h2_B, h2_C, h2_G] = [None, None, None, None, None]

heuristic_2 = {'G': {}}
heuristic_2['G']['S'] = h2_S
heuristic_2['G']['A'] = h2_A
heuristic_2['G']['B'] = h2_B
heuristic_2['G']['C'] = h2_C
heuristic_2['G']['G'] = h2_G


# heuristic_3: admissible but A* returns non-optimal path to G

[h3_S, h3_A, h3_B, h3_C, h3_G] = [None, None, None, None, None]

heuristic_3 = {'G': {}}
heuristic_3['G']['S'] = h3_S
heuristic_3['G']['A'] = h3_A
heuristic_3['G']['B'] = h3_B
heuristic_3['G']['C'] = h3_C
heuristic_3['G']['G'] = h3_G


# heuristic_4: admissible but not consistent, yet A* finds optimal path

[h4_S, h4_A, h4_B, h4_C, h4_G] = [None, None, None, None, None]

heuristic_4 = {'G': {}}
heuristic_4['G']['S'] = h4_S
heuristic_4['G']['A'] = h4_A
heuristic_4['G']['B'] = h4_B
heuristic_4['G']['C'] = h4_C
heuristic_4['G']['G'] = h4_G


#### SURVEY ###################################################

NAME = 'Kevin Cho'
COLLABORATORS = 'Jin Woo Kim'
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = 'Finding out a universal coding process for all the searches was interesting'
WHAT_I_FOUND_BORING = 'nothing was really boring'
SUGGESTIONS = 'so suggestions so far, but it would be good to hint more that students should start on part 3 first'



# Patch for lab2.py
# Paste the following lines into the bottom of your lab2.py:

generic_dfs_sort_new_paths_fn = generic_dfs[0]
generic_bfs_sort_new_paths_fn = generic_bfs[0]
generic_hill_climbing_sort_new_paths_fn = generic_hill_climbing[0]
generic_best_first_sort_new_paths_fn = generic_best_first[0]
generic_branch_and_bound_sort_new_paths_fn = generic_branch_and_bound[0]
generic_branch_and_bound_with_heuristic_sort_new_paths_fn = generic_branch_and_bound_with_heuristic[0]
generic_branch_and_bound_with_extended_set_sort_new_paths_fn = generic_branch_and_bound_with_extended_set[0]
generic_a_star_sort_new_paths_fn = generic_a_star[0]

generic_dfs_sort_agenda_fn = generic_dfs[2]
generic_bfs_sort_agenda_fn = generic_bfs[2]
generic_hill_climbing_sort_agenda_fn = generic_hill_climbing[2]
generic_best_first_sort_agenda_fn = generic_best_first[2]
generic_branch_and_bound_sort_agenda_fn = generic_branch_and_bound[2]
generic_branch_and_bound_with_heuristic_sort_agenda_fn = generic_branch_and_bound_with_heuristic[2]
generic_branch_and_bound_with_extended_set_sort_agenda_fn = generic_branch_and_bound_with_extended_set[2]
generic_a_star_sort_agenda_fn = generic_a_star[2]
