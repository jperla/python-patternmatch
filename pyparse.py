class ParseException(Exception):
    pass

class ASTNode(object):
    pass

class Join(ASTNode):
    def __init__(self, name, *nodes):
        self.name = name
        self.nodes = nodes

    def parse(self, s):
        values = []
        remaining = s
        for n in self.nodes:
            value,remaining = n.parse(remaining)
            if value is not None:
                values.append(value)
            else:
                return None, s
        return ((self.name,) + tuple(values)), remaining

class Symbol(ASTNode):
    def __init__(self, value):
        self.name = value

    def parse(self, s):
        if len(s) > 0 and s[0] == self.name:
            return self.name, s[1:]
        else:
            return None, s

class ContiguousSymbols(ASTNode):
    def __init__(self, name, symbols):
        self.name = name
        self.symbols = symbols

    def parse(self, s):
        i = 0
        while i < len(s) and s[i] in self.symbols:
            i += 1
        if i == 0:
            return None, s
        else:
            return (self.name, ''.join(s[:i])), s[i:]

class Int(ContiguousSymbols):
    def __init__(self):
        ContiguousSymbols.__init__(self, 'Num', '0123456789')

    def parse(self, s):
        value,remaining = ContiguousSymbols.parse(self, s)
        if value is not None:
            n,v = value
            return (n, int(v)), remaining
        else:
            return None, s


class Any(ASTNode):
    def __init__(self, *nodes):
        self.nodes = nodes

    def parse(self, s, whole=False):
        for n in self.nodes:
            value,remaining = n.parse(s)
            if value is not None:
                if not whole or remaining == []:
                    return value, remaining
        else:
            return None, s

class Recursive(ASTNode):
    def update(self, name, p):
        self.name = name
        self.parser = p

    def parse(self, s, whole=False):
        value,remaining = self.parser.parse(s, whole)
        if value is not None:
            return (self.name, value), remaining
        else:
            return None, s

def parse(p, s, whole=False):
    return p.parse(s, whole)
    

def whitespace_tokenize(s):
    """Accepts a string.
        Returns an array of strings.

        Removes all whitespace and leaves just a stream of characters.
    """
    return [c for c in s if c != ' ']

# todo: nested parentheses / brackets etc
# todo: proper tests

simple_expression = Recursive()

opsymbol = Any(Symbol('*'), Symbol('+'), Symbol('-'))

operation = Join('OP', Int(), opsymbol, simple_expression)
simple_expression.update('EXPR', Any(operation, Int()))


if __name__=='__main__':
    s = '5334'
    s = '5+3'


