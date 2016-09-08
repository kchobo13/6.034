from game_api import *
from boards import *
INF = float('inf')

def is_game_over_connectfour(board) :
    "Returns True if game is over, otherwise False."

    chain = board.get_all_chains()
    for chains in chain:
        if len(chains) == 4:
            return True

    for int in xrange(7):
        if board.is_column_full(int):
            continue
        else:
            return False
    return True

def next_boards_connectfour(board) :
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    boardsend = []
    if is_game_over_connectfour(board):
        return boardsend

    for int in xrange(7):
        if board.is_column_full(int):
            continue
        else:
            boardsend.append(board.add_piece(int))

    return boardsend

def endgame_score_connectfour(board, is_current_player_maximizer) :
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    if is_current_player_maximizer:
        return -1000
    return 1000

def endgame_score_connectfour_faster(board, is_current_player_maximizer) :
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    if is_current_player_maximizer:
        return -(1000+ 42-board.count_pieces())
    return 1000+ 42-board.count_pieces()

def heuristic_connectfour(board, is_current_player_maximizer) :
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    chains = board.get_all_chains(current_player=True)
    chains2 = board.get_all_chains(current_player=False)

    count1 = 0
    count2 = 0
    count3 = 0
    for chain in chains:
        if len(chain) == 1:
            count1 += 1
        elif len(chain) == 2:
            count2 += 1
        elif len(chain) == 3:
            count3 += 1

    for chain in chains2:
        if len(chain) == 1:
            count1 += -1
        elif len(chain) == 2:
            count2 += -1
        elif len(chain) == 3:
            count3 += -1

    if is_current_player_maximizer:
        return count1*10 + count2*50 + count3*100
    return -(count1*10 + count2*50 + count3*100)

# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### PART 2 ###########################################
# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""

    stack = [(state, [state])]
    final = []
    count = 0

    while stack:
        add = []
        (node,path) = stack.pop(0)
        count += 1

        if node.is_game_over():
            print count
            final.append((path, node.get_endgame_score(), count))
            continue

        for nextnode in node.generate_next_states():
            add.append((nextnode, path+[nextnode]))
        stack = add + stack

    variable = final[0]
    for state1 in final:
        if state1[1] > variable[1]:
            variable = state1
        elif state1[1] == variable[1]:
            if state1[2] < variable[2]:
                variable = state1
    return variable

def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""

    final = []
    (node, path, count) = (state, [state], 0)
    if node.is_game_over():
        count += 1
        final.append((path, node.get_endgame_score(), count))
    else:
        if maximize == True:
            max = -INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_endgame_search(nextnode, False)
                count += count1
                if value > max:
                    max = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)
            final.append((nextpath1,value1, count))

        else:
            min = INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_endgame_search(nextnode, True)
                count += count1
                if value < min:
                    min = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)

            final.append((nextpath1,value1, count))

    variable = final[0]
    for state1 in final:
        if state1[1] > variable[1]:
            variable = state1
        elif state1[1] == variable[1]:
            if state1[2] < variable[2]:
                variable = state1

    return variable

# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

#pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    "Performs standard minimax search.  Same return type as dfs_maximizing."

    final = []
    (node, path, count) = (state, [state], 0)

    if node.is_game_over():
        count += 1
        if maximize == True:
            final.append((path, node.get_endgame_score(), count))
        else:
            final.append((path, node.get_endgame_score(False), count))

    elif depth_limit == 0:
        count += 1
        if maximize == True:
            final.append((path, heuristic_fn(node.get_snapshot(), True), count))
        else:
            final.append((path, heuristic_fn(node.get_snapshot(), False), count))

    else:
        if maximize == True:
            max = -INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_search(nextnode, heuristic_fn, depth_limit-1, False)
                count += count1
                if value > max:
                    max = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)
            final.append((nextpath1,value1, count))

        else:
            min = INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_search(nextnode, heuristic_fn, depth_limit-1, True)
                count += count1
                if value < min:
                    min = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)

            final.append((nextpath1,value1, count))

    variable = final[0]
    for state1 in final:
        if state1[1] > variable[1]:
            variable = state1
        elif state1[1] == variable[1]:
            if state1[2] < variable[2]:
                variable = state1

    return variable


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1.  Try increasing the value of depth_limit to see what happens:

#pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    "Performs minimax with alpha-beta pruning.  Same return type as dfs_maximizing."

    final = []
    (node, path, count) = (state, [state], 0)

    if node.is_game_over():
        count += 1
        final.append((path, node.get_endgame_score(maximize), count))

    elif depth_limit == 0:
        count += 1
        final.append((path, heuristic_fn(node.get_snapshot(), maximize), count))

    else:
        if maximize == True:
            max = -INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_search_alphabeta(nextnode, alpha, beta, heuristic_fn, depth_limit-1, False)
                count += count1
                if value > max:
                    max = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)
                if alpha < max:
                    alpha = max
                if beta <= alpha:
                    break
            final.append((nextpath1,value1, count))

        else:
            min = INF
            for nextnode in node.generate_next_states():
                (nextpath, value, count1) = minimax_search_alphabeta(nextnode, alpha, beta, heuristic_fn, depth_limit-1, True)
                count += count1
                if value < min:
                    min = value
                    (nextpath1, value1, count2) = (path+nextpath, value, count)
                if beta > min:
                    beta = min
                if beta <= alpha:
                    break
            final.append((nextpath1,value1, count))

    variable = final[0]
    for state1 in final:
        if state1[1] > variable[1]:
            variable = state1
        elif state1[1] == variable[1]:
            if state1[2] < variable[2]:
                variable = state1

    return variable

# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4.  Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

#pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    anytime_value = AnytimeValue()   # TA Note: Use this to store values.
    i = 1

    while i <= depth_limit:
        value = minimax_search_alphabeta(state, -INF, INF, heuristic_fn, i, maximize)
        if anytime_value.get_value() == value:
            break
        anytime_value.set_value(value)
        i += 1
    return anytime_value

# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4.  Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

#progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


#### SURVEY ###################################################

NAME = "Kevin Cho"
COLLABORATORS = "None"
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = "The coding for minimax was pretty interesting"
WHAT_I_FOUND_BORING = "nothing"
SUGGESTIONS = "nothing"


###########################################################
### Ignore everything below this line; for testing only ###
###########################################################

# The following lines are used in the tester. DO NOT CHANGE!

def wrapper_connectfour(board_array, players, whose_turn = None) :
    board = ConnectFourBoard(board_array = board_array,
                             players = players,
                             whose_turn = whose_turn)
    return AbstractGameState(snapshot = board,
                             is_game_over_fn = is_game_over_connectfour,
                             generate_next_states_fn = next_boards_connectfour,
                             endgame_score_fn = endgame_score_connectfour_faster)
