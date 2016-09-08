from classify import *
import math
from collections import Counter

### Data sets for the lab
## You will be classifying data from these sets.
senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')


### Part 1: Nearest Neighbors
## An example of evaluating a nearest-neighbors classifier.
senate_group1, senate_group2 = crosscheck_groups(senate_people)
#evaluate(nearest_neighbors(hamming_distance, 1), senate_group1, senate_group2, verbose=1)

## Write the euclidean_distance function.
## This function should take two lists of integers and
## find the Euclidean distance between them.
## See 'hamming_distance()' in classify.py for an example that
## computes Hamming distances.

def euclidean_distance(list1, list2):
    # this is not the right solution!
    sum = 0
    for i in xrange(max(len(list1), len(list2))):
        inner_difference = list1[i] - list2[i]
        sum += inner_difference**2

    distance = math.sqrt(sum)
    return distance
    #return hamming_distance(list1, list2)

#Once you have implemented euclidean_distance, you can check the results:
#evaluate(nearest_neighbors(euclidean_distance, 1), senate_group1, senate_group2)

## By changing the parameters you used, you can get a classifier factory that
## deals better with independents. Make a classifier that makes at most 3
## errors on the Senate.

my_classifier = nearest_neighbors(euclidean_distance)
#evaluate(my_classifier, senate_group1, senate_group2, verbose=1)

### Part 2: ID Trees
#CongressIDTree(senate_people, senate_votes, homogeneous_disorder)

## Now write an information_disorder function to replace homogeneous_disorder,
## which should lead to simpler trees.

def information_disorder(yes, no):
    n_yes_b = float(len(yes))
    n_no_b = float(len(no))
    n_t = n_yes_b + n_no_b
    disorder_yes = 0.0
    disorder_no = 0.0

    Count_of_Houses_yes = Counter(yes)
    Count_of_Houses_no = Counter(no)

    for house in Count_of_Houses_yes.keys():
        n_bc = float(Count_of_Houses_yes[house])
        disorder_yes += -(n_bc/n_yes_b)* -math.log((n_yes_b)/(n_bc), 2)

    for house in Count_of_Houses_no.keys():
        n_bc = float(Count_of_Houses_no[house])
        disorder_no += -1*(n_bc/n_no_b)*-math.log((n_no_b)/(n_bc), 2)

    total_disorder = ((n_yes_b)/n_t) * (disorder_yes) + ((n_no_b)/n_t) * disorder_no
    return total_disorder


#print CongressIDTree(senate_people, senate_votes, information_disorder)
#evaluate(idtree_maker(senate_votes, homogeneous_disorder), senate_group1, senate_group2)

## Now try it on the House of Representatives. However, do it over a data set
## that only includes the most recent n votes, to show that it is possible to
## classify politicians without ludicrous amounts of information.

def limited_house_classifier(house_people, house_votes, n, verbose = False):
    house_limited, house_limited_votes = limit_votes(house_people,
    house_votes, n)
    house_limited_group1, house_limited_group2 = crosscheck_groups(house_limited)

    if verbose:
        print "ID tree for first group:"
        print CongressIDTree(house_limited_group1, house_limited_votes,
                             information_disorder)
        print
        print "ID tree for second group:"
        print CongressIDTree(house_limited_group2, house_limited_votes,
                             information_disorder)
        print

    return evaluate(idtree_maker(house_limited_votes, information_disorder),
                    house_limited_group1, house_limited_group2)


## Find a value of n that classifies at least 430 representatives correctly.
## Hint: It's not 10.
N_1 = 44
rep_classified = limited_house_classifier(house_people, house_votes, N_1)

## Find a value of n that classifies at least 90 senators correctly.
N_2 = 67
senator_classified = limited_house_classifier(senate_people, senate_votes, N_2)

## Now, find a value of n that classifies at least 95 of last year's senators correctly.
N_3 = 23
old_senator_classified = limited_house_classifier(last_senate_people, last_senate_votes, N_3)


## The standard survey questions.
NAME = 'Kevin Cho'
COLLABORATORS = "None"
HOW_MANY_HOURS_THIS_LAB_TOOK = 1.5
WHAT_I_FOUND_INTERESTING = "Machine Learning has always been my interest so the disorder thing was pretty cool to see"
WHAT_I_FOUND_BORING = "None that I found"
SUGGESTIONS = "Found the lab not too boring and trivial so it seemed great"


## This function is used by the tester; please don't modify it!
def eval_test(eval_fn, group1, group2, verbose = 0):
    """ Find eval_fn in globals(), then execute evaluate() on it """
    # Only allow known-safe eval_fn's
    if eval_fn in [ 'my_classifier' ]:
        return evaluate(globals()[eval_fn], group1, group2, verbose)
    else:
        raise Exception, "Error: Tester tried to use an invalid evaluation function: '%s'" % eval_fn
