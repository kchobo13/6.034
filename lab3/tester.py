# Fall 2015 6.034 Lab 3: Games

import xmlrpclib
import traceback
import sys
import os
import tarfile

from game_api import (AbstractGameState, ConnectFourBoard, is_class_instance,
                      always_zero)
from toytree import (ToyTree, toytree_is_game_over, toytree_generate_next_states,
                     toytree_endgame_score_fn, toytree_heuristic_fn)
from lab3 import (is_game_over_connectfour, next_boards_connectfour,
                  endgame_score_connectfour)

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from key import USERNAME as username, PASSWORD as password, XMLRPC_URL as server_url
except ImportError:
    print "Error: Can't find your 'key.py' file!  Please go download one from"
    print "<https://ai6034.mit.edu/labs/key.py>"
    sys.exit(1)

def test_summary(dispindex, ntests):
    return "Test %d/%d" % (dispindex, ntests)

def show_result(testsummary, testcode, correct, got, expected, verbosity):
    """ Pretty-print test results """
    if correct:
        if verbosity > 0:
            print "%s: Correct." % testsummary
        if verbosity > 1:
            print_testcode(testcode)
            print
    else:
        print "%s: Incorrect." % testsummary
        print_testcode(testcode)
        print "Got:     ", got
        print "Expected:", expected

def print_testcode(testcode):
    if isinstance(testcode, (tuple, list)) and len(testcode) >= 3:
        print '\t', testcode[2]
    else:
        print '\t', testcode

def show_exception(testsummary, testcode):
    """ Pretty-print exceptions (including tracebacks) """
    print "%s: Error." % testsummary
    print "While running the following test case:"
    print_testcode(testcode)
    print "Your code encountered the following error:"
    traceback.print_exc()
    print


def get_lab_module():
    # Try the easy way first
    try:
        from tests import lab_number
    except ImportError:
        lab_number = None

    if lab_number != None:
        lab = __import__('lab%s' % lab_number)
        return lab

    lab = None

    for labnum in xrange(10):
        try:
            lab = __import__('lab%s' % labnum)
        except ImportError:
            pass

    if lab == None:
        raise ImportError, "Cannot find your lab; or, error importing it.  Try loading it by running 'python labN.py' (for the appropriate value of 'N')."

    if not hasattr(lab, "LAB_NUMBER"):
        lab.LAB_NUMBER = labnum

    return lab


# encode/decode objects
def encode_AGS(ags):
    return [ags.snapshot, ags.is_game_over_fn, ags.generate_next_states_fn,
            ags.endgame_score_fn]
def decode_AGS(snapshot, is_game_over_fn, generate_next_states_fn,
               endgame_score_fn):
    return AbstractGameState(snapshot, is_game_over_fn, generate_next_states_fn,
                             endgame_score_fn)

def encode_C4B(board):
    return [board.board_array, board.players, board.whose_turn,
            board.prev_move_string]
def decode_C4B(board_array, players, whose_turn, prev_move_string):
    board = ConnectFourBoard(board_array, players, whose_turn)
    board.prev_move_string = prev_move_string
    return board

def encode_ToyTree(tree):
    if tree.children:
        return [tree.label, tree.score, map(encode_ToyTree, tree.children)]
    return [tree.label, tree.score, list()]
def decode_ToyTree(args):
    label, score, children_encoded = args
    tree = ToyTree(label, score)
    if children_encoded:
        tree.children = map(decode_ToyTree, children_encoded)
    return tree

# decode functions received from server
def l_valuate(board, player): return len(sum(board.get_all_chains(player),[]))
def density(board, player) : return sum([abs(index-3)
                                         for row in board.board_array
                                         for (piece, index) in zip(row, range(board.num_cols))
                                         if piece and (piece == 1) == (board.count_pieces() + player) % 2])
def lambda_density_heur(board, maximize):
    return ([-1,1][maximize] * (density(board, False) - density(board, True)
            + 2*l_valuate(board,True) - 3*l_valuate(board, False)))
def lambda_minus_heur(board, maximize):
    return [-1,1][maximize] * (l_valuate(board,True) - l_valuate(board, False))

def lambda_tree_negate(tree, is_max): return [-1,1][is_max] * tree.score

def lambda_child_score(tree, is_max):
    if not tree.children:
        return tree.score
    return tree.children[0].score

function_dict = {'is_game_over_connectfour': is_game_over_connectfour,
                 'next_boards_connectfour': next_boards_connectfour,
                 'endgame_score_connectfour': endgame_score_connectfour,
                 'toytree_is_game_over': toytree_is_game_over,
                 'toytree_generate_next_states': toytree_generate_next_states,
                 'toytree_endgame_score_fn': toytree_endgame_score_fn,
                 'toytree_heuristic_fn': toytree_heuristic_fn,
                 'lambda_density_heur': lambda_density_heur,
                 'lambda_minus_heur': lambda_minus_heur,
                 'lambda_tree_negate': lambda_tree_negate,
                 'lambda_child_score': lambda_child_score,
                 'always_zero': always_zero}


def type_decode(arg, lab):
    """
    XMLRPC can only pass a very limited collection of types.
    Frequently, we want to pass a subclass of 'list' in as a test argument.
    We do that by converting the sub-type into a regular list of the form:
    [ 'TYPE', (data) ] (ie., AND(['x','y','z']) becomes ['AND','x','y','z']).
    This function assumes that TYPE is a valid attr of 'lab' and that TYPE's
    constructor takes a list as an argument; it uses that to reconstruct the
    original data type.
    """
    if isinstance(arg, list) and len(arg) >= 1: # There is no future magic for tuples.
        if arg[0] == 'AGS' and isinstance(arg[1], list):
            return decode_AGS(*[type_decode(x, lab) for x in arg[1]])
        elif arg[0] == 'C4B' and isinstance(arg[1], list):
            return decode_C4B(*arg[1])
        elif arg[0] == 'ToyTree' and isinstance(arg[1], list):
            return decode_ToyTree(arg[1]) # This is intentionally different.
        elif arg[0] == 'callable':
            try:
                return function_dict[arg[1]]
            except KeyError:
                error_string = "Error: invalid function name received from server: " + str(arg[1])
                print error_string + ". Please contact a TA if you continue to see this error."
                return error_string
        else:
            return [ type_decode(x, lab) for x in arg ]
    else:
        return arg


def type_encode(arg):
    "Encode classes as lists in a way that can be decoded by 'type_decode'"
    if isinstance(arg, (list, tuple)):
        return [type_encode(a) for a in arg]
    elif is_class_instance(arg, 'AbstractGameState'):
        return ['AGS', map(type_encode, encode_AGS(arg))]
    elif is_class_instance(arg, 'ConnectFourBoard'):
        return ['C4B', encode_C4B(arg)]
    elif is_class_instance(arg, 'ToyTree'):
        return ['ToyTree', encode_ToyTree(arg)]
    elif is_class_instance(arg, 'AnytimeValue'):
        return ['AnytimeValue_history', type_encode(arg.history)]
    elif callable(arg):
        fn_name = arg.__name__
        if fn_name == '<lambda>':
            print (' ** Note: Unfortunately, the online tester is unable to '
                   +'accept lambda functions. To pass the online tests, use '
                   +'named functions instead. **')
        elif fn_name not in function_dict:
            print ('Error: constraint function', fn_name, 'cannot be transmitted '
                   +'to server.  Please use a pre-defined constraint function instead.')
        return ['callable', arg.__name__]
    else:
        return arg


def run_test(test, lab):
    """
    Takes a 'test' tuple as provided by the online tester
    (or generated by the offline tester) and executes that test,
    returning whatever output is expected (the variable that's being
    queried, the output of the function being called, etc)

    'lab' (the argument) is the module containing the lab code.

    'test' tuples are in the following format:
      'id': A unique integer identifying the test
      'type': One of 'VALUE', 'FUNCTION', 'MULTIFUNCTION', or 'FUNCTION_ENCODED_ARGS'
      'attr_name': The name of the attribute in the 'lab' module
      'args': a list of the arguments to be passed to the function; [] if no args.
      For 'MULTIFUNCTION's, a list of lists of arguments to be passed in
    """
    id, mytype, attr_name, args = test

    attr = getattr(lab, attr_name)

    if mytype == 'VALUE':
        return attr
    elif mytype == 'FUNCTION':
        return apply(attr, args)
    elif mytype == 'MULTIFUNCTION':
        return [ run_test( (id, 'FUNCTION', attr_name, FN), lab)
                for FN in type_decode(args, lab) ]
    elif mytype == 'FUNCTION_ENCODED_ARGS':
        return run_test( (id, 'FUNCTION', attr_name, type_decode(args, lab)), lab )
    else:
        raise Exception("Test Error: Unknown TYPE: " + str(mytype)
                        + ".  Please make sure you have downloaded the latest"
                        + "version of the tester script.  If you continue to "
                        + "see this error, contact a TA.")


def test_offline(verbosity=1):
    """ Run the unit tests in 'tests.py' """
    import tests as tests_module

#    tests = [ (x[:-8],
#               getattr(tests_module, x),
#               getattr(tests_module, "%s_testanswer" % x[:-8]),
#               getattr(tests_module, "%s_expected" % x[:-8]),
#               "_".join(x[:-8].split('_')[:-1]))
#              for x in tests_module.__dict__.keys() if x[-8:] == "_getargs" ]

    tests = tests_module.get_tests()

    ntests = len(tests)
    ncorrect = 0

    for index, (testname, getargs, testanswer, expected, fn_name, type) in enumerate(tests):
        dispindex = index+1
        summary = test_summary(dispindex, ntests)

        try:
            if callable(getargs):
                getargs = getargs()

            answer = run_test((index, type, fn_name, getargs), get_lab_module())
        except NotImplementedError:
            print "%d: (%s: Function not yet implemented, NotImplementedError raised)" % (dispindex, testname)
            continue
        except Exception:
            show_exception(summary, testname)
            continue

        correct = testanswer(answer)
        show_result(summary, testname, correct, answer, expected, verbosity)
        if correct: ncorrect += 1

    print "Passed %d of %d tests." % (ncorrect, ntests)
    return ncorrect == ntests


def get_target_upload_filedir():
    """ Get, via user prompting, the directory containing the current lab """
    cwd = os.getcwd() # Get current directory.  Play nice with Unicode pathnames, just in case.

    print "Please specify the directory containing your lab."
    print "Note that all files from this directory will be uploaded!"
    print "Labs should not contain large amounts of data; very-large"
    print "files will fail to upload."
    print
    print "The default path is '%s'" % cwd
    target_dir = raw_input("[%s] >>> " % cwd)

    target_dir = target_dir.strip()
    if target_dir == '':
        target_dir = cwd

    print "Ok, using '%s'." % target_dir

    return target_dir

def get_tarball_data(target_dir, filename):
    """ Return a binary String containing the binary data for a tarball of the specified directory """
    data = StringIO()
    file = tarfile.open(filename, "w|bz2", data)

    print "Preparing the lab directory for transmission..."

    file.add(target_dir)

    print "Done."
    print
    print "The following files have been added:"

    for f in file.getmembers():
        print f.name

    file.close()

    return data.getvalue()


def test_online(verbosity=1):
    """ Run online unit tests.  Run them against the 6.034 server via XMLRPC. """
    lab = get_lab_module()

    try:
        server = xmlrpclib.Server(server_url, allow_none=True)
        tests = server.get_tests(username, password, lab.__name__)
    except NotImplementedError: # Solaris Athena doesn't seem to support HTTPS
        print "Your version of Python doesn't seem to support HTTPS, for"
        print "secure test submission.  Would you like to downgrade to HTTP?"
        print "(note that this could theoretically allow a hacker with access"
        print "to your local network to find your 6.034 password)"
        answer = raw_input("(Y/n) >>> ")
        if len(answer) == 0 or answer[0] in "Yy":
            server = xmlrpclib.Server(server_url.replace("https", "http"))
            tests = server.get_tests(username, password, lab.__name__)
        else:
            print "Ok, not running your tests."
            print "Please try again on another computer."
            print "Linux Athena computers are known to support HTTPS,"
            print "if you use the version of Python in the 'python' locker."
            sys.exit(0)

    ntests = len(tests)
    ncorrect = 0

    lab = get_lab_module()

    target_dir = get_target_upload_filedir()

    tarball_data = get_tarball_data(target_dir, "lab%s.tar.bz2" % lab.LAB_NUMBER)

    print "Submitting to the 6.034 Webserver..."

    server.submit_code(username, password, lab.__name__, xmlrpclib.Binary(tarball_data))

    print "Done submitting code."
    print "Running test cases..."

    for index, testcode in enumerate(tests):
        dispindex = index+1
        summary = test_summary(dispindex, ntests)

        try:
            answer = run_test(testcode, get_lab_module())
        except Exception:
            show_exception(summary, testcode)
            continue

        correct, expected = server.send_answer(username, password, lab.__name__, testcode[0], type_encode(answer))
        show_result(summary, testcode, correct, answer, expected, verbosity)
        if correct: ncorrect += 1

    response = server.status(username, password, lab.__name__)
    print response


def make_test_counter_decorator():
    tests = []
    def make_test(getargs, testanswer, expected_val, name = None, type = 'FUNCTION'):
        if name != None:
            getargs_name = name
        elif not callable(getargs):
            getargs_name = "_".join(getargs[:-8].split('_')[:-1])
            getargs = lambda: getargs
        else:
            getargs_name = "_".join(getargs.__name__[:-8].split('_')[:-1])

        tests.append( ( getargs_name,
                        getargs,
                        testanswer,
                        expected_val,
                        getargs_name,
                        type ) )

    def get_tests():
        return tests

    return make_test, get_tests


make_test, get_tests = make_test_counter_decorator()


if __name__ == '__main__':
    if 'submit' in sys.argv:
        test_online()
    elif test_offline():
        if "IDLE" in sys.executable:
            print "submitting and testing online..."
            test_online()
        else:
            print "Local tests passed! Run 'python %s submit' to submit your code and have it graded." % sys.argv[0]

#test_online()
