# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
import sys
import logic
import game
import pprint

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def getGhostStartStates(self):
        """
        Returns a list containing the start state for each ghost.
        Only used in problems that use ghosts (FoodGhostSearchProblem)
        """
        util.raiseNotDefined()

    def terminalTest(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getGoalState(self):
        """
        Returns goal state for problem. Note only defined for problems that have
        a unique goal state such as PositionSearchProblem
        """
        util.raiseNotDefined()

    def result(self, state, action):
        """
        Given a state and an action, returns resulting state and step cost, which is
        the incremental cost of moving to that successor.
        Returns (next_state, cost)
        """
        util.raiseNotDefined()

    def actions(self, state):
        """
        Given a state, returns available actions.
        Returns a list of actions
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()

    def getWidth(self):
        """
        Returns the width of the playable grid (does not include the external wall)
        Possible x positions for agents will be in range [1,width]
        """
        util.raiseNotDefined()

    def getHeight(self):
        """
        Returns the height of the playable grid (does not include the external wall)
        Possible y positions for agents will be in range [1,height]
        """
        util.raiseNotDefined()

    def isWall(self, position):
        """
        Return true if position (x,y) is a wall. Returns false otherwise.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def atLeastOne(expressions) :
    """
    Given a list of logic.Expr instances, return a single logic.Expr instance in CNF (conjunctive normal form)
    that represents the logic that at least one of the expressions in the list is true.
    >>> A = logic.PropSymbolExpr('A');
    >>> B = logic.PropSymbolExpr('B');
    >>> symbols = [A, B]
    >>> atleast1 = atLeastOne(symbols)
    >>> model1 = {A:False, B:False}
    >>> print logic.pl_true(atleast1,model1)
    False
    >>> model2 = {A:False, B:True}
    >>> print logic.pl_true(atleast1,model2)
    True
    >>> model3 = {A:True, B:True}
    >>> print logic.pl_true(atleast1,model2)
    True
    """
    "*** YOUR CODE HERE ***"
    return logic.Expr('|', *expressions)


def atMostOne(expressions) :
    """
    Given a list of logic.Expr instances, return a single logic.Expr instance in CNF (conjunctive normal form)
    that represents the logic that at most one of the expressions in the list is true.
    """
    "*** YOUR CODE HERE ***"
    not_exprs = []
    for expr in expressions:
        not_exprs.append(logic.Expr('~', expr))
    has_zero_trues = logic.Expr('&', *not_exprs)
    return logic.Expr('|', *[has_zero_trues, exactlyOne(expressions)])


def exactlyOne(expressions) :
    """
    Given a list of logic.Expr instances, return a single logic.Expr instance in CNF (conjunctive normal form)
    that represents the logic that exactly one of the expressions in the list is true.
    """
    "*** YOUR CODE HERE ***"
    if len(expressions) == 0:
        return False
    if len(expressions) == 1:
        return expressions
    exprs = []
    for expr in expressions:
        tempExprs = list(expressions)
        tempExprs.remove(expr)
        tempExprs.append(logic.Expr('~', expr))
        tempExprsExpr = logic.Expr('|', *tempExprs)
        exprs.append(tempExprsExpr)
    exprsExpr = logic.Expr('', *exprs)
    return logic.Expr('~', exprsExpr)


def extractActionSequence(model, actions):
    """
    Convert a model in to an ordered list of actions.
    model: Propositional logic model stored as a dictionary with keys being
    the symbol strings and values being Boolean: True or False
    Example:
    >>> model = {"North[3]":True, "P[3,4,1]":True, "P[3,3,1]":False, "West[1]":True, "GhostScary":True, "West[3]":False, "South[2]":True, "East[1]":False}
    >>> actions = ['North', 'South', 'East', 'West']
    >>> plan = extractActionSequence(model, actions)
    >>> print plan
    ['West', 'South', 'North']
    """
    "*** YOUR CODE HERE ***"
    trues = [key for key in model.keys() if model[key]]
    actionDictionary = {}
    maxTimeStep = 0
    for true in trues:
        for action in actions:
            trueName = true.__repr__()
            if action in trueName:
                timeStep = int(trueName[trueName.index("[")+1:trueName.index("]")])
                if timeStep > maxTimeStep:
                    maxTimeStep = timeStep
                actionDictionary[trueName] = timeStep
                continue
    sequence = [None]*(maxTimeStep+1)
    for action in actionDictionary.keys():
        sequence[actionDictionary[action]] = action[:action.index("[")]
    sequence = [s for s in sequence if s is not None]
    return sequence

def positionLogicPlan(problem):
    manhattanDistance = util.manhattanDistance(problem.getStartState(), problem.getGoalState())
    print "Start state", problem.getStartState(), " and end state ", problem.getGoalState()
    for time in range(manhattanDistance, 25):
        print "a"
        exprs = []

        start=problem.getStartState()
        goal=problem.getGoalState()
        exprs.append(logic.PropSymbolExpr("P",start[0],start[1],0))
        exprs.append(logic.PropSymbolExpr("P",goal[0],goal[1],time))

        positions = []
        for x in range(1,problem.getWidth()+1):
            for y in range(1,problem.getHeight()+1):
                if not problem.isWall((x,y)):
                    positionSymbol = logic.PropSymbolExpr("P",x,y,0)
                    positions.append(positionSymbol)
        print "d"
        exactlyOneExpr = exactlyOne(positions)
        print "e"
        if exactlyOneExpr:
            appendToExprs(exprs, exactlyOneExpr)

        for t in range(0,time):
            print "b"
            northSymbol = logic.PropSymbolExpr("North", t)
            southSymbol = logic.PropSymbolExpr("South", t)
            westSymbol = logic.PropSymbolExpr("West", t)
            eastSymbol = logic.PropSymbolExpr("East", t)
            exactlyOneAction = exactlyOne([northSymbol, southSymbol, westSymbol, eastSymbol])
            appendToExprs(exprs, exactlyOneAction)

        for t in range(1, time+1):
            print "c"
            for x in range(1,problem.getWidth()+1):
                for y in range(1,problem.getHeight()+1):
                    if not problem.isWall((x,y)):
                        actions = problem.actions((x,y))
                        prevExprs = []
                        for action in actions:
                            currentStatePropSymbolExpr = logic.PropSymbolExpr("P", x, y, t)
                            prevState = ()
                            if action == 'North':
                                action = 'South'
                                prevState = (x,y+1)
                            elif action == 'South':
                                action = 'North'
                                prevState = (x,y-1)
                            elif action == 'West':
                                action = 'East'
                                prevState = (x-1,y)
                            elif action == 'East':
                                action = 'West'
                                prevState = (x+1,y)
                            actionPropSymbolExpr = logic.PropSymbolExpr(action, t-1)
                            prevStatePropSymbolExpr = logic.PropSymbolExpr("P", prevState[0], prevState[1], t-1)
                            prevExprs.append(logic.Expr("&", actionPropSymbolExpr, prevStatePropSymbolExpr))
                        prevExprsOrred = logic.Expr("|", *prevExprs)
                        iff = logic.Expr("<=>", prevExprsOrred, currentStatePropSymbolExpr)
                        appendToExprs(exprs, iff)
        pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(exprs)
        result = logic.pycoSAT(exprs)
        print result
        if result:
            # pp.pprint(result)
            actions = extractActionSequence(result, ["North", "South", "East", "West"])
            return actions
    util.raiseNotDefined()


def appendToExprs(exprs, rule):
    exprs.append(logic.to_cnf(rule))
    # exprs.append(rule)

def foodLogicPlan(problem):
    """
    Given an instance of a FoodSearchProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

def foodGhostLogicPlan(problem):
    """
    Given an instance of a FoodGhostSearchProblem, return a list of actions that help Pacman
    eat all of the food and avoid patrolling ghosts.
    Ghosts only move east and west. They always start by moving East, unless they start next to
    and eastern wall.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviations
plp = positionLogicPlan
flp = foodLogicPlan
fglp = foodGhostLogicPlan

# Some for the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)
