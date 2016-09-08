from constraint_api import *
from test_problems import get_pokemon_problem

#### PART 1: WRITE A DEPTH-FIRST SEARCH CONSTRAINT SOLVER

def has_empty_domains(csp):
    "Returns True if the problem has one or more empty domains, otherwise False"
    condition = False
    for key in csp.domains.keys():
        if len(csp.domains[key]) == 0:
            condition = True
    return condition

def check_all_constraints(csp):
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    assigned_value = csp.assigned_values
    answer = True
    for variableAssigned in assigned_value.keys():
        constraints = csp.constraints_between(variableAssigned, None)
        for c1 in constraints:
            if c1.var2 in assigned_value.keys():
                if not c1.check(assigned_value[variableAssigned],assigned_value[c1.var2]):
                    answer = False
    return answer


def solve_constraint_dfs(problem) :
    """Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values), and
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple."""

    stack = [problem]
    count = 0

    while stack:
        element = stack.pop(0)
        count += 1

        if has_empty_domains(element):
            continue
        if not check_all_constraints(element):
            continue


        if not element.unassigned_vars:
            return (element.assigned_values, count)
        else:
            copy_list = []
            first = element.pop_next_unassigned_var()
            for value in element.get_domain(first):
                element_new = element.copy()
                element_new.set_assigned_value(first, value)
                copy_list.append(element_new)

            for i in xrange(len(copy_list)):
                 stack.insert(i,copy_list[i])

    return (None, count)


#### PART 2: DOMAIN REDUCTION BEFORE SEARCH

def eliminate_from_neighbors(csp, var) :
    """Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp.  Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None."""

    constraints = csp.constraints_between(None, var)
    modified = []
    for con1 in constraints:
        variable2 = con1.var1
        domain1 = csp.get_domain(var)
        domain2 = csp.get_domain(variable2)

        remove = []
        for value1 in domain2:
            count = 0
            for value2 in domain1:
                if con1.check(value1,value2):
                    break
                count += 1

            if count == len(domain1):
                remove.append(value1)

        if len(remove) != 0:
            for v in remove:
                domain2.remove(v)

            modified.append(variable2)
            if len(domain2) == 0:
                return None
    return sorted(modified)

def domain_reduction(csp, queue=None):
    """Uses constraints to reduce domains, modifying the original csp.
    If queue is None, initializes propagation queue by adding all variables in
    their default order.  Returns a list of all variables that were dequeued,
    in the order they were removed from the queue.  Variables may appear in the
    list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None."""
    if queue == None:
        queue = csp.get_all_variables()
    answer = []
    while queue:
        var = queue.pop(0)
        answer.append(var)

        modified = eliminate_from_neighbors(csp,var)
        if modified == None:
            return None

        add = []
        for element in modified:
            if element not in queue:
                add.append(element)
        add = sorted(add)
        for element in add:
            queue.append(element)
    return answer


def solve_constraint_dfs_domain_reduction(problem):
    domain_reduction(problem)
    return solve_constraint_dfs(problem)

# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with dfs if you DON'T use domain reduction before solving it?

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

ANSWER_1 = solve_constraint_dfs(get_pokemon_problem())[1]

# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with dfs if you DO use domain reduction before solving it?

ANSWER_2 = solve_constraint_dfs_domain_reduction(get_pokemon_problem())[1]


#### PART 3: PROPAGATION THROUGH REDUCED DOMAINS

def solve_constraint_propagate_reduced_domains(problem) :
    """Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs."""

    stack = [problem]
    count = 0
    while stack:
        element = stack.pop(0)
        count += 1

        if has_empty_domains(element):
            continue
        if not check_all_constraints(element):
            continue

        if not element.unassigned_vars:
            return (element.assigned_values, count)
        else:
            copy_list = []
            first = element.pop_next_unassigned_var()
            for value in element.get_domain(first):
                element_new = element.copy()
                element_new.set_assigned_value(first, value)
                domain_reduction(element_new, [first])
                copy_list.append(element_new)


            stack = copy_list + stack


    return (None,count)

# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with propagation through reduced domains? (Don't use domain reduction
#    before solving it.)

ANSWER_3 = solve_constraint_propagate_reduced_domains(get_pokemon_problem())[1]


#### PART 4: PROPAGATION THROUGH SINGLETON DOMAINS

def domain_reduction_singleton_domains(csp, queue=None) :
    """Uses constraints to reduce domains, modifying the original csp.
    Only propagates through singleton domains.
    Same return type as domain_reduction."""
    if queue == None:
        queue = csp.get_all_variables()
    answer = []
    while queue:
        var = queue.pop(0)
        answer.append(var)

        modified = eliminate_from_neighbors(csp,var)
        if modified == None:
            return None

        add = []
        for element in modified:
            if element not in queue:
                add.append(element)
        add = sorted(add)
        for element in add:
            if len(csp.get_domain(element)) == 1:
                queue.append(element)
    return answer

def solve_constraint_propagate_singleton_domains(problem) :
    """Solves the problem using depth-first search with forward checking and
    propagation through singleton domains.  Same return type as
    solve_constraint_dfs."""
    stack = [problem]
    count = 0
    while stack:
        element = stack.pop(0)
        count += 1

        if has_empty_domains(element):
            continue
        if not check_all_constraints(element):
            continue

        if not element.unassigned_vars:
            return (element.assigned_values, count)
        else:
            copy_list = []
            first = element.pop_next_unassigned_var()
            for value in element.get_domain(first):
                element_new = element.copy()
                element_new.set_assigned_value(first, value)
                domain_reduction_singleton_domains(element_new, [first])
                copy_list.append(element_new)


            stack = copy_list + stack


    return (None,count)


# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with propagation through singleton domains? (Don't use domain reduction
#    before solving it.)

ANSWER_4 = solve_constraint_propagate_singleton_domains(get_pokemon_problem())[1]


#### PART 5: FORWARD CHECKING

def propagate(enqueue_condition_fn, csp, queue=None) :
    """Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced.  Same return type as domain_reduction."""
    if queue == None:
        queue = csp.get_all_variables()
    answer = []
    while queue:
        var = queue.pop(0)
        answer.append(var)

        modified = eliminate_from_neighbors(csp,var)
        if modified == None:
            return None

        add = []
        for element in modified:
            if element not in queue:
                add.append(element)
        add = sorted(add)

        for element in add:
            if enqueue_condition_fn(csp, element):
                queue.append(element)
    return answer

def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True

def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    if len(csp.get_domain(var)) == 1:
        return True
    return False

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### PART 6: GENERIC CSP SOLVER

def solve_constraint_generic(problem, enqueue_condition=None) :
    """Solves the problem, calling propagate with the specified enqueue
    condition (a function).  If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs."""
    stack = [problem]
    count = 0
    while stack:
        element = stack.pop(0)
        count += 1

        if has_empty_domains(element):
            continue
        if not check_all_constraints(element):
            continue

        if not element.unassigned_vars:
            return (element.assigned_values, count)
        else:
            copy_list = []
            first = element.pop_next_unassigned_var()
            for value in element.get_domain(first):
                element_new = element.copy()
                element_new.set_assigned_value(first, value)
                if enqueue_condition != None:
                    propagate(enqueue_condition, element_new, [first])
                copy_list.append(element_new)


            stack = copy_list + stack


    return (None,count)

# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking, but no propagation? (Don't use domain
#    reduction before solving it.)

ANSWER_5 = solve_constraint_generic(get_pokemon_problem(), condition_forward_checking)[1]


#### PART 7: DEFINING CUSTOM CONSTRAINTS

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    if m == n + 1 or m == n - 1:
        return True
    return False

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    if not constraint_adjacent(m, n):
        return True
    return False

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    answer = []
    for index1 in xrange(len(variables)):
        for index2 in xrange(len(variables)):
            if index1 < index2:
                answer.append(Constraint(variables[index1], variables[index2], constraint_different))

    return answer

#### PART 8: MOOSE PROBLEM (OPTIONAL)

moose_problem = ConstraintSatisfactionProblem(["You", "Moose", "McCain",
                                               "Palin", "Obama", "Biden"])

# Add domains and constraints to your moose_problem here:


# To test your moose_problem AFTER implementing all the solve_constraint
# methods above, change TEST_MOOSE_PROBLEM to True:
TEST_MOOSE_PROBLEM = False


#### SURVEY ###################################################

NAME = "Kevin Cho"
COLLABORATORS = "None"
HOW_MANY_HOURS_THIS_LAB_TOOK = 3
WHAT_I_FOUND_INTERESTING = "I found out that reusing code is very usefule"
WHAT_I_FOUND_BORING = "nothing"
SUGGESTIONS = "none"


###########################################################
### Ignore everything below this line; for testing only ###
###########################################################

if TEST_MOOSE_PROBLEM:
    # These lines are used in the local tester iff TEST_MOOSE_PROBLEM is True
    moose_answer_dfs = solve_constraint_dfs(moose_problem.copy())
    moose_answer_propany = solve_constraint_propagate_reduced_domains(moose_problem.copy())
    moose_answer_prop1 = solve_constraint_propagate_singleton_domains(moose_problem.copy())
    moose_answer_generic_dfs = solve_constraint_generic(moose_problem.copy(), None)
    moose_answer_generic_propany = solve_constraint_generic(moose_problem.copy(), condition_domain_reduction)
    moose_answer_generic_prop1 = solve_constraint_generic(moose_problem.copy(), condition_singleton)
    moose_answer_generic_fc = solve_constraint_generic(moose_problem.copy(), condition_forward_checking)
    moose_instance_for_domain_reduction = moose_problem.copy()
    moose_answer_domain_reduction = domain_reduction(moose_instance_for_domain_reduction)
    moose_instance_for_domain_reduction_singleton = moose_problem.copy()
    moose_answer_domain_reduction_singleton = domain_reduction_singleton_domains(moose_instance_for_domain_reduction_singleton)
