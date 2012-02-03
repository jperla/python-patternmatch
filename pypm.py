#!/usr/bin/env python
"""
Joseph Perla
Python Pattern Matching Library

Brings Haskell and Scala style pattern matching to Python.

Pattern Matching makes it much easier to build compilers, 
    programming languages, optimizers, and language transformers.
"""
import copy
import string
import types
from itertools import izip


# The abstract syntax tree is just a recursive n-tuple
# First element is a string which is the name of the node. Remaining are arguments.


class PatternMatchVar(object):
    """Temporary variables used in pattern matching.
        We want to use these in patterns like Sum(a, b), 
            where a and b are of this class.
    """
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return '<%s>' % self.label

    #todo: should raise exception 
    # if you try to do anything with this directly
    # like compare or add
    # except print string, equality, and isinstance
    # will help other people avoid weird bugs in their code


_ = PatternMatchVar('_')
for asc in string.ascii_lowercase:
    exec('{0} = PatternMatchVar("{0}")'.format(asc))

class UnknownPattern(Exception):
    pass

class ASTException(Exception):
    pass


def pattern_does_match(pattern, ast):
    """Accepts a pattern (an n-tuple with PatternMatchVars, e.g. ("Sum", a, b) ).
        and also accepts an ast, a recursive n-tuple.
        Returns boolean if the pattern matches.  See Haskell.
    """
    for p,a in izip(pattern, ast):
        # should match everywhere except the patterns
        if p != a and not isinstance(p, PatternMatchVar):
            return False
    else:
        return True

def match_and_extract_matched_vars(pattern, ast, matched=None):
    """Accepts a pattern (an n-tuple with PatternMatchVars, e.g. ("Sum", a, b) ).
        and also accepts an ast, a recursive n-tuple.
        Returns a dictionary of variable string name and variable value (a sub-node of the AST).
            This will be used in the recursive call.

        Returns None if it is not a correct pattern match

        This is recursive.
    """
    if matched is None:
        matched = {}

    guard = None
    if len(pattern) == 2 and isinstance(pattern[1], types.LambdaType):
        pattern,guard = pattern

    for p,a in izip(pattern, ast):
        # should match everywhere except the patterns
        if p != a and not isinstance(p, PatternMatchVar):
            if isinstance(p, tuple):
                # recursively take out args
                matched = match_and_extract_matched_vars(p, a, matched)
                # may fail somewhere down the line recursively, then fail
                if matched is None:
                    return None
            else:
                # otherwise, not a match, fail
                return None
        elif p != a:
            assert p.label not in matched, ('Cannot reusing pattern match variables!: %s' % pattern)
            # then p is a PatternMatchVar
            matched[p.label] = a
        elif p == a:
            pass # nothing to do
    else:
        # check that the guard returns true
        if guard:
            def is_guard_correct(m, g):
                v = g(*order_matched(m, g))
                assert isinstance(v, bool), "Guard must return true or false"
                return v
            if not is_guard_correct(matched, guard):
                return None
        return matched

def order_matched(matched, function):
    """Accepts a matched dictionary from string variable name => AST, and a function.
        Looks at function, and figures out the order of the variable names.
        Returns an array of values that can be used by calling function(*array)
    """
    for v in function.func_code.co_varnames:
        if v not in matched:
            raise Exception('Function uses argument not used in pattern: %s' % v)
    return [matched[a] for a in function.func_code.co_varnames]

def check_patterns(patterns):
    """Accepts patterns which are a list of 1-element dictionaries from patterns to lambda functions.
        The patterns are recursive n-tuples of strings and PatternMatchVars.
        Ensures that these types are correct or throw exception.

        !!Feature!!
        Note that pattern keys may be (pattern, guard) 2-tuples where the guard is a lambda function.
    """
    if not isinstance(patterns, tuple) and not isinstance(patterns, list):
        for d in patterns:
            if not isinstance(d, dict) and not len(d) == 1:
                raise Exception('Patterns should be an iterable of 1-item dictionaries: (n-tuple => function)')

    for d in patterns:
        p,f = d.keys()[0], d.values()[0]
        if not isinstance(p, tuple):
            raise Exception('Pattern should be a tuple.  ' 
                            'Remember that in Python you have to add a comma '
                            'at the end of singleton tuples.: {0}'.format(p))

        # patterns can have a guard
        if len(p) == 2 and isinstance(p[1], types.LambdaType):
            p,guard = p
                
        for t in p:
                
            if not isinstance(t, basestring) and not isinstance(t, PatternMatchVar) and not isinstance(t, tuple):
                raise Exception('Patterns must be recursive tuples of strings and PatternMatchVars.  '
                                'Did you remember to do "from pypm import a,b,c" ?: {0}'.format(t))

        if (not isinstance(f, types.LambdaType)):
            raise Exception('Values should be lambda functions')

def check_ast(ast):
    """Accepts an ast which is a recursive n-tuple.
        Ensures that it is or throws exceptions.
    """
    if not isinstance(ast, tuple):
        raise ASTException('AST must be a recursive n-tuple')

def copyfunc(f, newglobals):
    """Accepts a function. Copies its code point but gives it different name/globals/etc.
        Returns a new function.
    """
    t = eval('lambda: None', globals().update(newglobals))
    t.func_code = f.func_code
    t.func_name = f.func_name
    return t

def patternmatch(patterns, run_func=False):
    """Accepts a dictionary representing patterns.  
            The dictionary has keys which are n-tuples representing parts of ASTs.
            The dictionary has values which are lambda functions that 
                accept the variable named parts of the ast.
        Returns a decorator. The decorator should be put on a function that will accept an AST.
        If a pattern does match, it will execute the lambda function appropriately.  See Haskell.
        If no pattern matches, then by default this will raise an Exception.
            The function will only run if no pattern matched and run_func=True in the optional arguments.
    """
    check_patterns(patterns)
    def decorator(f):
        def recognize_and_run(ast):
            check_ast(ast)
            for d in patterns:
                p,tocall = d.keys()[0], d.values()[0]
                matched = match_and_extract_matched_vars(p, ast)
                if matched is not None:
                    # we got a match!
                    return tocall(*order_matched(matched, tocall))
            else:
                # 
                if run_func:
                    return f(ast)
                else:
                    raise UnknownPattern()
        return recognize_and_run
    return decorator

# jperla: start with just tuple pattern matching, can add sugar later
# jperla: add monads to make this easier
# jperla: write a parser
# jperla: make a sophisticated sqrt/+/- etc calculator compiler
# jperla: make a C compiler? Fortran?

if __name__=='__main__':
    def extract_num(ast):
        assert ast[0] == 'Num'
        return ast[1]

    patterns = [
        {(("Sub", ("Num", a), ("Num", b),),
                lambda a,b: a > b): lambda a,b: ("Num", (a - b))},
        {(("Sub", ("Num", a), ("Num", b),),
                lambda a,b: b > a): lambda a,b: ("Num", (b - a))},
        {("Mult", a, b): lambda a,b: ("Num", (extract_num(evalNumeric(a)) * extract_num(evalNumeric(b))))},
        {("Sum", a, b): lambda a,b: ("Num", (extract_num(evalNumeric(a)) + extract_num(evalNumeric(b))))},
        {("Num", a): lambda a: ("Num", a)},
    ]

    @patternmatch(patterns)
    def evalNumeric(ast):
        pass

    seven = ("Sum", ("Num", 3), ("Num", 4))
    fourteen = ("Sum", seven, seven,)
    ninetyeight = ("Mult", fourteen, seven,)
    ninetyeight_again = ("Mult", seven, ("Mult", ("Num", 1), fourteen,),)
    ninety = ("Sub", ("Num", 22), ("Num", 112))

    print evalNumeric(seven)
    print evalNumeric(fourteen)
    print evalNumeric(ninetyeight)
    print evalNumeric(ninetyeight_again)
    print evalNumeric(ninety)

