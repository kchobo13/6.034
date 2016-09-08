# 6.034 Lab 7 2015: Boosting (Adaboost)

from math import log as ln
INF = float('inf')

# Helper function for pick_best_classifier and adaboost
def fix_roundoff_error(inp, n=15):
    """inp can be a number, a list of numbers, or a dict whose values are numbers.
    * If inp is a number: Rounds the number to the nth decimal digit to reduce
        previous Python roundoff error.  Returns a float.
    * If inp is a list of numbers: Rounds each number as above.  Does not modify
        the original list.
    * If inp is a dictionary whose values are numbers: Rounds each value as
        above.  Does not modify the original dictionary."""
    fix_val = lambda val: round(abs(val),n)*[-1,1][val>=0]
    if isinstance(inp, list): return map(fix_val, inp)
    if isinstance(inp, dict): return {key: fix_val(inp[key]) for key in inp}
    return fix_val(inp)


#### BOOSTING (ADABOOST) #######################################################

def initialize_weights(training_points):
    """Assigns every training point a weight equal to 1/N, where N is the number
    of training points.  Returns a dictionary mapping points to weights."""
    length = float(len(training_points))
    weights = {}
    for point in training_points:
        weights[point] = float(1.0/length)
    return weights

def calculate_error_rates(point_to_weight, classifier_to_misclassified):
    """Given a dictionary mapping training points to their weights, and another
    dictionary mapping classifiers to the training points they misclassify,
    returns a dictionary mapping classifiers to their error rates."""
    dictionary = {}
    for classifier in classifier_to_misclassified.keys():
        points = classifier_to_misclassified[classifier]
        weight = 0
        for point in points:
            weight += point_to_weight[point]
        dictionary[classifier] = weight

    return dictionary

def pick_best_classifier(classifier_to_error_rate, use_smallest_error=True):
    """Given a dictionary mapping classifiers to their error rates, returns the
    best* classifier.  Best* means 'smallest error rate' if use_smallest_error
    is True, otherwise 'error rate furthest from 1/2'."""
    if use_smallest_error == True:
        weight = INF
        classifierstring = None
        for classifier in classifier_to_error_rate:
            if classifier_to_error_rate[classifier] < weight:
                weight = fix_roundoff_error(classifier_to_error_rate[classifier])
                classifierstring = classifier
            elif classifier_to_error_rate[classifier] == weight:
                list = sorted([classifier, classifierstring])
                classifierstring = list[0]
        return classifierstring
    else:
        weight = 0.5
        classifierstring = None
        for classifier in classifier_to_error_rate:
            compare = abs(classifier_to_error_rate[classifier] - 0.5)
            compare2 = abs(weight - 0.5)
            compare = fix_roundoff_error(compare)
            compare2 = fix_roundoff_error(compare2)
            if compare > compare2:
                weight = fix_roundoff_error(classifier_to_error_rate[classifier])
                classifierstring = classifier
            elif compare == compare2:
                list = sorted([classifier, classifierstring])
                classifierstring = list[0]
        return classifierstring


def calculate_voting_power(error_rate):
    """Given a classifier's error rate (a number), returns the voting power
    (aka alpha, or coefficient) for that classifier."""
    if error_rate == 0:
        return INF
    elif error_rate == 1:
        return -INF
    else:
        return 0.5 * ln((1-error_rate)/error_rate)

def is_good_enough(H, training_points, classifier_to_misclassified,
                   mistake_tolerance=0):
    """Given an overall classifier H, a list of all training points, a
    dictionary mapping classifiers to the training points they misclassify, and
    a mistake tolerance (the maximum number of allowed misclassifications),
    returns False if H misclassifies more points than the tolerance allows,
    otherwise True.  H is represented as a list of (classifier, voting_power)
    tuples."""


    misclassified = 0
    for point in training_points:
        alpha = 0
        for (classy, vote) in H:
            if point in classifier_to_misclassified[classy]:
                alpha -= vote
            else:
                alpha += vote
        if alpha <=0:
            misclassified += 1

    if misclassified <= mistake_tolerance:
        return True
    else:
        return False


def update_weights(point_to_weight, misclassified_points, error_rate):
    """Given a dictionary mapping training points to their old weights, a list
    of training points misclassified by the current weak classifier, and the
    error rate of the current weak classifier, returns a dictionary mapping
    training points to their new weights.  This function is allowed (but not
    required) to modify the input dictionary point_to_weight."""
    for point in point_to_weight.keys():
        if point in misclassified_points:
            point_to_weight[point] *= 0.5 * 1/error_rate
        else:
            point_to_weight[point] *= 0.5 * 1/(1-error_rate)

    return point_to_weight

def adaboost(training_points, classifier_to_misclassified,
             use_smallest_error=True, mistake_tolerance=0, max_num_rounds=INF):
    """Performs the Adaboost algorithm for up to max_num_rounds rounds.
    Returns the resulting overall classifier H, represented as a list of
    (classifier, voting_power) tuples."""
    H = []
    weights = initialize_weights(training_points)
    rounds = 0
    while (max_num_rounds > rounds):
        error_rates = calculate_error_rates(weights, classifier_to_misclassified)
        h = pick_best_classifier(error_rates, use_smallest_error)
        if fix_roundoff_error(error_rates[h]) == 0.5:
            break
        voting_power = calculate_voting_power(error_rates[h])
        H.append((h,voting_power))
        rounds += 1
        if (is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance)):
            break
        weights = update_weights(weights,classifier_to_misclassified[h], error_rates[h])
    return H



#### SURVEY ####################################################################

NAME ='Kevin Cho'
COLLABORATORS = "None"
HOW_MANY_HOURS_THIS_LAB_TOOK = 2
WHAT_I_FOUND_INTERESTING = "The boosting seemed like a hard concept but breaking it down like this makes is so much easier to understand"
WHAT_I_FOUND_BORING = "nothing"
SUGGESTIONS = "none"
