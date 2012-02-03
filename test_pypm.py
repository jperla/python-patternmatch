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
ninetyeight_again = ("Mult", seven, ("Mult", 1, fourteen,),)

def extract_num(ast):
    assert ast[0] == 'Num'
    return ast[1]

def test_simple():
    assert 7 == extract_num(evalNumeric(seven))
    assert 14 == extract_num(evalNumeric(fourteen))
    #assert 98 == extract_num(evalNumeric(ninetyeight))
    #assert 98 == extract_num(evalNumeric(ninetyeight_again))

def test_error():
    try:  
        evalNumeric(("bla"))
    except pypm.UnknownPattern,e:
        assert True
    else:
        raise Exception('no proper exception raised')

    @patternmatch(patterns, run_func=True)
    def evalNumericRun(ast):
        pass

    try:  
        evalNumericRun(("bla"))
    except:
        assert Exception('exception raised when it should not')
    else:
        assert True 
