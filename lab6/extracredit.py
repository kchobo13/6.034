# 6.034 Lab 6 2015: Neural Nets & SVMs

from nn_problems import *
from svm_problems import *
from math import e

#### NEURAL NETS ###############################################################

# Wiring a neural net

nn_half = [1]

nn_angle = [2,1]

nn_cross = [2,2,1]

nn_stripe = [3,1]

nn_hexagon = [6,1]

# Optional problem; change TEST_NN_GRID to True to test locally
TEST_NN_GRID = False
nn_grid = []

# Helper functions
def stairstep(x, threshold=0):
    "Computes stairstep(x) using the given threshold (T)"
    if x >= threshold:
        return 1
    else:
        return 0

def sigmoid(x, steepness=1, midpoint=0):
    "Computes sigmoid(x) using the given steepness (S) and midpoint (M)"
    return 1/ (1+ e**(-steepness*(x-midpoint)))


def accuracy(desired_output, actual_output):
    "Computes accuracy. If output is binary, accuracy ranges from -0.5 to 0."
    return -0.5*(desired_output-actual_output)**2

# Forward propagation
def forward_prop(net, input_values, threshold_fn=stairstep):
    """Given a neural net and dictionary of input values, performs forward
    propagation with the given threshold function to compute binary output.
    This function should not modify the input net.  Returns a tuple containing:
    (1) the final output of the neural net
    (2) a dictionary mapping neurons to their immediate outputs"""
    new_net = net.topological_sort()
    values = input_values
    dictionary = {}
    for neuron in new_net:
        sum = 0
        for wire in net.get_incoming_wires(neuron):
            if wire.startNode in values.keys():
                sum += (values[wire.startNode] * wire.weight)
            else:
                sum += wire.startNode * wire.weight
        output = threshold_fn(sum)
        dictionary[neuron] = output
        values[neuron] = output

    return (dictionary[new_net[-1]], dictionary)




# Backward propagation
def calculate_deltas(net, input_values, desired_output):
    """Computes the update coefficient (delta_B) for each neuron in the
    neural net.  Uses sigmoid function to compute output.  Returns a dictionary
    mapping neuron names to update coefficient (delta_B values)."""
    (final, outputs) = forward_prop(net, input_values, sigmoid)
    new_net = net.topological_sort()
    new_net.reverse()
    dictionary = {}

    for neuron in new_net:
        output = outputs[neuron]
        if neuron == new_net[0]:
            delta = output * (1-output) * (desired_output - output)

        else:
            sigma = 0
            for wire in net.get_wires(neuron):
                sigma += wire.weight * dictionary[wire.endNode]
            delta = output * (1-output) * sigma

        dictionary[neuron] = delta
    return dictionary


def update_weights(net, input_values, desired_output, r=1):
    """Performs a single step of back-propagation.  Computes delta_B values and
    weight updates for entire neural net, then updates all weights.  Uses
    sigmoid function to compute output.  Returns the modified neural net, with
    updated weights."""
    delta_B = calculate_deltas(net, input_values, desired_output)
    (final, outputs) = forward_prop(net, input_values, sigmoid)

    for wire in net.get_wires():
        if wire.endNode != 'OUT':
            if wire.startNode in input_values.keys():
                wire.weight += r * input_values[wire.startNode] * delta_B[wire.endNode]
            else:
                wire.weight += r * int(wire.startNode) * delta_B[wire.endNode]
    return net


def back_prop(net, input_values, desired_output, r=1, accuracy_threshold=-.001):
    """Updates weights until accuracy surpasses minimum_accuracy.  Uses sigmoid
    function to compute output.  Returns a tuple containing:
    (1) the modified neural net, with trained weights
    (2) the number of iterations (that is, the number of weight updates)"""
    (final, outputs) = forward_prop(net, input_values, sigmoid)
    iteration = 0
    while accuracy(desired_output, final) <= accuracy_threshold:
        update_weights(net, input_values, desired_output,r)
        (final, outputs) = forward_prop(net, input_values, sigmoid)
        iteration += 1

    return (net, iteration)


#### SUPPORT VECTOR MACHINES ###################################################

# Vector math
def dot_product(u, v):
    """Computes dot product of two vectors u and v, each represented as a tuple
    or list of coordinates.  Assume the two vectors are the same length."""
    sum = 0
    for i in xrange(len(u)):
        sum += u[i]*v[i]
    return sum
def norm(v):
    "Computes length of a vector v, represented as a tuple or list of coords."
    sum = 0
    for i in xrange(len(v)):
        sum += v[i]**2

    return sum**(0.5)

# Equation 1
def positiveness(svm, point):
    "Computes the expression (w dot x + b) for the given point"
    return dot_product(svm.boundary.w, point.coords) + svm.boundary.b

def classify(svm, point):
    """Uses given SVM to classify a Point.  Assumes that point's classification
    is unknown.  Returns +1 or -1, or 0 if point is on boundary"""
    if positiveness(svm, point) >0:
        return 1
    elif positiveness(svm, point) < 0:
        return -1
    else:
        return 0

# Equation 2
def margin_width(svm):
    "Calculate margin width based on current boundary."
    return 2/(norm(svm.boundary.w))

# Equation 3
def check_gutter_constraint(svm):
    """Returns the set of training points that violate one or both conditions:
        * gutter constraint (positiveness == classification for support vectors)
        * training points must not be between the gutters
    Assumes that the SVM has support vectors assigned."""
    list = []
    for point in svm.training_points:
        if point in svm.support_vectors:
            if point.classification != positiveness(svm, point):
                list.append(point)

        if positiveness(svm, point) < 1 and positiveness(svm, point) > -1:
            list.append(point)

    return set(list)

# Equations 4, 5
def check_alpha_signs(svm):
    """Returns the set of training points that violate either condition:
        * all non-support-vector training points have alpha = 0
        * all support vectors have alpha > 0
    Assumes that the SVM has support vectors assigned, and that all training
    points have alpha values assigned."""
    list = []
    for point in svm.training_points:
        if point not in svm.support_vectors:
            if point.alpha != 0:
                list.append(point)
        else:
            if point.alpha <= 0:
                list.append(point)
    return set(list)

def check_alpha_equations(svm):
    """Returns True if both Lagrange-multiplier equations are satisfied,
    otherwise False.  Assumes that the SVM has support vectors assigned, and
    that all training points have alpha values assigned."""

    vector = []
    sum4 = 0
    for point in svm.training_points:
        vector.append(scalar_mult(point.classification * point.alpha, point.coords))
        sum4 += point.classification* point.alpha
    sum = vector.pop(0)
    for point in vector:
        sum = vector_add(sum, point)

    if sum4 == 0:
        if sum == svm.boundary.w:
            return True

    return False


# Classification accuracy
def misclassified_training_points(svm):
    """Returns the set of training points that are classified incorrectly
    using the current decision boundary."""
    list = []
    for point in svm.training_points:
        if classify(svm,point) != point.classification:
            list.append(point)

    return set(list)

#### SURVEY ####################################################################

NAME = 'Kevin Cho'
COLLABORATORS = 'none'
HOW_MANY_HOURS_THIS_LAB_TOOK = 3
WHAT_I_FOUND_INTERESTING = 'everything was interesting'
WHAT_I_FOUND_BORING = 'nothing really'
SUGGESTIONS = 'none '


nn_extra_credit