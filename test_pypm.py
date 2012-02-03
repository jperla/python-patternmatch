import pypm
from pypm import patternmatch,a,b,_

patterns = {
    ("Mult", a, b): lambda a,b: ("Num", (extract_num(evalNumeric(a)) * extract_num(evalNumeric(b)))),
    ("Sum", a, b): lambda a,b: ("Num", (extract_num(evalNumeric(a)) + extract_num(evalNumeric(b)))),
    ("Num", a): lambda a: ("Num", a),
}

@patternmatch(patterns)
def evalNumeric(ast):
    pass

seven = ("Sum", ("Num", 3), ("Num", 4))
fourteen = ("Sum", seven, seven,)
ninetyeight = ("Mult", fourteen, seven,)
ninetyeight_again = ("Mult", seven, ("Mult", ("Num", 1), fourteen,),)

def extract_num(ast):
    assert ast[0] == 'Num'
    return ast[1]

def test_simple():
    assert 7 == extract_num(evalNumeric(seven))
    assert 14 == extract_num(evalNumeric(fourteen))
    assert 98 == extract_num(evalNumeric(ninetyeight))
    assert 98 == extract_num(evalNumeric(ninetyeight_again))

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
