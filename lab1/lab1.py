from production import IF, AND, OR, NOT, THEN, DELETE,forward_chain
from data import *

#### Part 1: Multiple Choice #########################################

ANSWER_1 = '2'

ANSWER_2 = 'no'

ANSWER_3 = '2'

ANSWER_4 = '1'

ANSWER_5 = '0'


#### Part 2: Transitive Rule #########################################

transitive_rule = IF( AND('(?x) beats (?y)',
                          '(?y) beats (?z)'),
                      THEN('(?x) beats (?z)') )

# You can test your rule by uncommenting these print statements:
#print forward_chain([transitive_rule], abc_data)
#print forward_chain([transitive_rule], poker_data)
#print forward_chain([transitive_rule], minecraft_data)


#### Part 3: Family Relations #########################################

# Define your rules here:



# Add your rules to this list:
family_rules = [

        IF( AND('person (?x)'),
        THEN( 'self (?x) (?x)'),
        DELETE( 'person (?x)')),

        IF( AND('parent (?x) (?y)'),
        THEN('child (?y) (?x)')),

        IF( AND('parent (?x) (?y)',
            'parent (?x) (?z)',
            NOT('self (?y) (?z)')),
        THEN('sibling (?y) (?z)')),

        IF( AND('parent (?x) (?y)',
                'parent (?z) (?x)'),
            THEN('grandparent (?z) (?y)',
                 'grandchild (?y) (?z)')),

        IF( AND('sibling (?x) (?y)',
                'parent (?x) (?a)',
                'parent (?y) (?b)'),
        THEN('cousin (?a) (?b)'))


    ]

# Uncomment this to test your data on the Simpsons family:
#print forward_chain(family_rules, simpsons_data, verbose=True
# These smaller datasets might be helpful for debugging:
#forward_chain(family_rules, sibling_test_data, verbose=True)
#forward_chain(family_rules, grandparent_test_data, verbose=True)

# The following should generate 14 cousin relationships, representing 7 pairs
# of people who are cousins:
black_family_cousins = [
    relation for relation in
    forward_chain(family_rules, black_data, verbose=False)
    if "cousin" in relation ]

# To see if you found them all, uncomment this line:
#print black_family_cousins


#### Part 4: Backward Chaining #########################################

# Import additional methods for backchaining
from production import PASS, FAIL, match, populate, simplify, variables


def backchain_to_goal_tree(rules, hypothesis):
    goal_tree = OR(hypothesis)
    for rule in rules:
        consequent = rule.consequent()[0]
        matching = match(consequent,hypothesis)
        if matching or matching == {}:
            if isinstance(rule.antecedent(), AND):
                leaf_tree = AND()
                for antecedent in rule.antecedent():
                    if populate(antecedent,matching):
                        leaf_tree.append(backchain_to_goal_tree(rules,populate(antecedent,matching)))
                        goal_tree.append(leaf_tree)
                    else:
                        leaf_tree.append(backchain_to_goal_tree(rules,antecedent))
            elif isinstance(rule.antecedent(), OR):
                leaf_tree = OR()
                for antecedent in rule.antecedent():
                    if populate(antecedent,matching):
                        leaf_tree.append(backchain_to_goal_tree(rules,populate(antecedent,matching)))
                        goal_tree.append(leaf_tree)
                    else:
                        leaf_tree.append(backchain_to_goal_tree(rules,antecedent))
            else:
                goal_tree.append(backchain_to_goal_tree(rules,populate(rule.antecedent(),matching)))

    return simplify(goal_tree)






# Uncomment this to run your backward chainer:
#print backchain_to_goal_tree(zookeeper_rules, 'opus is a penguin')


#### Survey #########################################

NAME = 'Kevin Cho'
COLLABORATORS = "Jin Woo Kim"
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = "It was fun trying to find out the logic behind backwards chaining and implimenting the code"
WHAT_I_FOUND_BORING = 'It was not boring at all'
SUGGESTIONS = 'no suggestions in mind'


###########################################################
### Ignore everything below this line; for testing only ###
###########################################################

# The following lines are used in the tester. DO NOT CHANGE!
transitive_rule_poker = forward_chain([transitive_rule], poker_data)
transitive_rule_abc = forward_chain([transitive_rule], abc_data)
transitive_rule_minecraft = forward_chain([transitive_rule], minecraft_data)
family_rules_simpsons = forward_chain(family_rules, simpsons_data)
family_rules_black = forward_chain(family_rules, black_data)
family_rules_sibling = forward_chain(family_rules, sibling_test_data)
family_rules_grandparent = forward_chain(family_rules, grandparent_test_data)
family_rules_anonymous_family = forward_chain(family_rules, anonymous_family_test_data)
