import pypm
from pypm import patternmatch,a,b,_
from pypm import anynode,starargs,recurse_ast

def extract_num(ast):
    assert ast[0] == 'Num'
    return ast[1]

patterns = [
    {("Mult", a, b):    lambda a,b: ("Num", (extract_num(evalNumeric(a)) * extract_num(evalNumeric(b))))},
    {("Sum", a, b):     lambda a,b: ("Num", (extract_num(evalNumeric(a)) + extract_num(evalNumeric(b))))},
    {("Num", a):        lambda a: ("Num", a)},

    # absolute subtract; using guards!
    {(("AbsSub", ("Num", a), ("Num", b),),
                        lambda a,b: a > b): lambda a,b: ("Num", (a - b))},
    {(("AbsSub", ("Num", a), ("Num", b),),
                        lambda a,b: b > a): lambda a,b: ("Num", (b - a))},
]

@patternmatch(patterns)
def evalNumeric(ast):
    pass

seven = ("Sum", ("Num", 3), ("Num", 4))
fourteen = ("Sum", seven, seven,)
ninetyeight = ("Mult", fourteen, seven,)
ninetyeight_again = ("Mult", seven, ("Mult", ("Num", 1), fourteen,),)
ninety = ("AbsSub", ("Num", 22), ("Num", 112))

big = ('EXPR',
 ('OP',
  ('Num', 5),
  '+',
  ('EXPR',
   ('OP',
    ('Num', 323),
    '-',
    ('EXPR', ('OP', ('Num', 12), '*', ('EXPR', ('Num', 18))))))))

def is_in_ast(ast, token):
    if ast == token:
        return True
    
    for a in ast:
        if a == token:
            return True
        else:
            if isinstance(a, tuple):
                b = is_in_ast(a, token)
                if b:
                    return True
            else:
                if a == token:
                    return True
    else:
        return False

def depth(ast):
    if isinstance(ast, tuple):
        depths = []
        for a in ast:
            depths.append(depth(a))
        return max(depths)
    else:
        return 0

def test_simple():
    assert 7 == extract_num(evalNumeric(seven))
    assert 14 == extract_num(evalNumeric(fourteen))
    assert 98 == extract_num(evalNumeric(ninetyeight))
    assert 98 == extract_num(evalNumeric(ninetyeight_again))
    assert 90 == extract_num(evalNumeric(ninety))


def test_varargs():
    @patternmatch([
        {('OP', ('Num', a), '*', ('EXPR', ('Num', b))): 
                    lambda a,b: ('Num', a * b)},
        {(anynode, starargs): 
                    lambda anynode,starargs: recurse_ast(evalMinus, anynode, starargs)},
    ])
    def evalMinus(ast):
        pass

    answer = evalMinus(big)
 
    assert not is_in_ast(answer, '*')
    assert is_in_ast(answer, '+')

    assert is_in_ast(answer, 216)
    assert is_in_ast(answer, 5)
    assert is_in_ast(answer, ('Num', 5))
    assert not is_in_ast(answer, (5,))
    assert not is_in_ast(answer, (5,))
    assert not is_in_ast(answer, 18)

class NoProperExceptionRaised(Exception):
    pass

def test_errors():
    try:  
        evalNumeric(('bla'))
    except pypm.ASTException,e:
        assert True
    else:
        raise NoProperExceptionRaised()

    try:
        evalNumeric(('bla',))
    except pypm.UnknownPattern,e:
        assert True
    else:
        raise Exception('no proper exception raised')

    global t
    t = 35
    # test that run func goes through
    @patternmatch(patterns, run_func=True)
    def evalNumericRun(ast):
        global t
        t = 25

    try:  
        evalNumericRun(('bla',))
    except:
        raise NoProperExceptionRaised()
    else:
        assert t == 25 
