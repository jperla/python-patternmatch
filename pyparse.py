import string

class ParseException(Exception):
    pass

class ASTNode(object):
    pass

class Join(ASTNode):
    def __init__(self, name, *nodes):
        self.name = name
        self.nodes = nodes

    def parse(self, s, whole=False):
        values = []
        remaining = s
        for n in self.nodes:
            value,remaining = n.parse(remaining)
            if value is not None:
                values.append(value)
            else:
                return None, s
        if len(remaining) == 0 or not whole:
            if self.name is not None:
                return ((self.name,) + tuple(values)), remaining
            else:
                return tuple(values), remaining
        else:
            return None, s


class Keyword(ASTNode):
    def __init__(self, keyword, name=None):
        self.keyword = keyword
        self.name = name

    def parse(self, s, whole=False):
        #TODO: jperla: make whole decorator
        if s[:len(self.keyword)] == list(self.keyword):
            remaining = s[len(self.keyword):]
            if self.name is None:
                return self.keyword, remaining
            else:
                return (self.name, self.keyword), remaining
        else:
            return None, s

class Symbol(ASTNode):
    def __init__(self, value):
        self.name = value

    def parse(self, s, whole=False):
        if len(s) != 1:
            return None, s
        else:
            if len(s) > 0 and s[0] == self.name:
                return self.name, s[1:]
            else:
                return None, s

class ContiguousSymbols(ASTNode):
    def __init__(self, name, symbols):
        self.name = name
        self.symbols = symbols

    def parse(self, s, whole=False):
        #TODO: jperla: ignores whole argument
        i = 0
        while i < len(s) and s[i] in self.symbols:
            i += 1
        if i == 0:
            return None, s
        else:
            return (self.name, ''.join(s[:i])), s[i:]

class AlphaWord(ContiguousSymbols):
    def __init__(self):
        ContiguousSymbols.__init__(self, 'WORD', string.ascii_letters + '.')

    def parse(self, s, whole=False):
        value,remaining = ContiguousSymbols.parse(self, s)
        if value is not None and (len(remaining) == 0 or not whole):
            n,v = value
            return v, remaining
        else:
            return None, s

class Int(ContiguousSymbols):
    def __init__(self):
        ContiguousSymbols.__init__(self, 'Num', '0123456789')

    def parse(self, s, whole=False):
        value,remaining = ContiguousSymbols.parse(self, s)
        if value is not None:
            n,v = value
            return (n, int(v)), remaining
        else:
            return None, s

class Nested(ASTNode):
    def __init__(self, open_='(', close=')', content=None, ignore=None):
        self.open_ = open_
        self.close = close
        self.content = content
        self.ignore = ignore

    def parse(self, s, whole=False):
        # do not do content ignoring (doesn't support parentheses in quotes)
        assert self.ignore == None
        stack = []
        if len(s) > 0 and s[0] == self.open_:
            stack = [s[0]]
            i = 1

            # nested expression, (e.g. look for matching parenthesis)
            while len(stack) > 0 and i < len(s):
                if s[i] == self.open_:
                    stack.append(s[i])
                elif s[i] == self.close:
                    stack.pop()
                i += 1

            if len(stack) == 0:
                inner_tokens, remaining = s[1:i-1], s[i:]
                if self.content is not None:
                    inner_ast, r = self.content.parse(inner_tokens, whole=False)
                    if len(r) == 0:
                        # nested expression found, and 
                        # inner content parsed
                        return inner_ast, remaining
                    else:
                        # inner content of nested expression
                        # does not parse to self.content
                        return None, s
                else:
                    # no content parser, just return raw string/tokens
                    return inner_tokens, remaining
            else:
                # nested expression did not close (e.g. no close parenthesis)
                return None, s
        else:
            # empty string, or first character doesn't open nested expression
            # (e.g. no open parenthesis at beginning)
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

class Repeat(ASTNode):
    def __init__(self, parser):
        self.parser = parser

    def parse(self, s, whole=False):
        parsed = []
        remaining = s
        while remaining is None or len(remaining) > 0:
            ast, remaining = self.parser.parse(remaining, whole=False)
            if ast is not None:
                parsed.append(ast)
            else:
                break
        return tuple(parsed), remaining


class Recursive(ASTNode):
    def update(self, name, p):
        self.name = name
        self.parser = p

    def parse(self, s, whole=False):
        value,remaining = self.parser.parse(s, whole)
        if value is not None:
            if self.name is not None:
                return (self.name, value), remaining
            else:
                return value, remaining
        else:
            return None, s

def parse(p, s, whole=False):
    return p.parse(s, whole)
    

def whitespace_tokenize(s):
    """Accepts a string.
        Returns an array of strings.

        Removes all whitespace and leaves just a stream of characters.
    """
    return [c for c in s if c not in ' \r\n']

# todo: nested parentheses / brackets etc

simple_expression = Recursive()

opsymbol = Any(Symbol('*'), Symbol('+'), Symbol('-'))

operation = Join('OP', Int(), opsymbol, simple_expression)
simple_expression.update('EXPR', Any(operation, Int()))


if __name__=='__main__':
    s = '5334'
    s = '5+3'


