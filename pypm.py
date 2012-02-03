#!/usr/bin/env python
"""
Joseph Perla
Python Pattern Matching Library

Brings Haskell and Scala style pattern matching to Python.

Pattern Matching makes it much easier to build compilers, 
    programming languages, optimizers, and language transformers.
"""

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


a = PatternMatchVar('a')
b = PatternMatchVar('b')
c = PatternMatchVar('c')
d = PatternMatchVar('d')
e = PatternMatchVar('e')
f = PatternMatchVar('f')
_ = PatternMatchVar('_')
UnknownPattern = Exception('Unknown pattern')


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

def check_patterns(patterns):
    """Accepts patterns which are n-tuples of strings and PatternMatchVars.
        Ensures that they are or throws exceptions.
    """
    if not isinstance(patterns, dict):
        raise Exception('Patterns should be a dictionary of n-tuples => functions')

    for p in patterns:
        if not isinstance(p, tuple):
            raise Exception('Pattern should be a tuple.' 
                            'Remember that in Python you have to add a comma'
                            'at the end of singleton tuples.: %s' % p)

        for t in p:
            if not isinstance(t, basestring) and not isinstance(t, PatternMatchVar):
                raise Exception('Patterns must be tuples of strings and PatternMatchVars.'
                                'Did you remember to do "from pypm import a,b,c" ?: %s' % t)

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
            for p in patterns:
                if pattern_does_match(p, ast):
                    # note: this does not work for 
                    # recursive nested expressions!
                    return patterns[p](*ast[1:])
            else:
                # 
                if run_func:
                    return f(ast)
                else:
                    raise UnknownPattern
        return recognize_and_run
    return decorator


# jperla: start with just tuple pattern matching, can add sugar later
# jperla: start with unrecursive pattern matching, add recursive later

