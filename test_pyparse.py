import pyparse

def test_simple():
    s = '5 + 323 - 12 * 18'
    w = pyparse.whitespace_tokenize(s)
    ast,remaining = pyparse.parse(pyparse.simple_expression, w, whole=True)
    assert remaining == []
