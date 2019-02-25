##################################################################
'''
support functions for grammars.  grammars are lists of tuples.

for example, the grammar,

exp : + exp exp
    | - exp exp
    | x
    | y
    | z

is represented as,

[('exp',['+','exp','exp']),
 ('exp',['-','exp','exp']), 
 ('exp',['x']), 
 ('exp',['y']), 
 ('exp',['z'])]
 
 and with lookahead sets it becomes,
 
 [('exp', {'+'}, ['+', 'exp', 'exp']),
  ('exp', {'-'}, ['-', 'exp', 'exp']),
  ('exp', {'x'}, ['x']),
  ('exp', {'y'}, ['y']),
  ('exp', {'z'}, ['z'])]

'''
##################################################################
def start_symbol(G):
    first_rule = G[0]
    if len(first_rule) == 2:
        (A,B) = first_rule
        return A
    elif len(first_rule) == 3:
        (A,L,B) = first_rule
        return A

##################################################################
def first_symbol(rule_body):
    return rule_body[0]

##################################################################
def non_terminal_set(G):
    nt = set()
    for r in G:
        if len(r) == 2:
            (A, B) = r
        else:
            (A, L, B) = r
        nt.add(A)
    return nt

##################################################################
def terminal_set(G):
    nt = non_terminal_set(G)
    symbols = []
    for r in G:
        if len(r) == 2:
            (A, B) = r
        else:
            (A, L, B) = r
        symbols.extend(B)
    t = set(symbols) - nt
    return t

##################################################################
def find_matching_rule(GL, N, P):
    for r in GL:
        (A, L, B) = r
        if A == N and P in L:
            return r
        elif A == N and len(L) == 1 and list(L)[0] == "":
            return r
    return None


##################################################################
def right_side_match(G, S):
    for r in G:
        if len(r) == 2:
            (A, B) = r
        else:
            (A, L, B) = r
        if S.match(B):
            return r
    return None

##################################################################
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def match(self, input_list):
        if len(self.items) < len(input_list):
            return False
        l1 = len(input_list)
        l2 = len(self.items)
        ix = l2 - l1
        tos_list = self.items[ix:]
        return tos_list == input_list

    def push_reverse(self, input_list):
        symbol_list = input_list.copy()
        while symbol_list:
            self.push(symbol_list.pop())
    
    def pop(self):
        return self.items.pop()
    
    def popn(self, n):
        for i in range(n):
            self.pop()

    def peek(self):
        return self.items[-1]

    def empty(self):
        return len(self.items) == 0

##################################################################
class InputStream:
    def __init__(self, stream):
        self.stream = stream # has to be a non-empty list of characters
        self.stream.append('eof')
        self.stream_ix = 0

    def pointer(self):
        return self.stream[self.stream_ix]

    def next(self):
        self.stream_ix += 1
        return self.stream[self.stream_ix]

    def end_of_file(self):
        if self.stream[self.stream_ix] == 'eof':
            return True
        else:
            return False

##################################################################
class TokenStream:
    def __init__(self, lexer, stream):
        self.lexer = lexer
        self.lexer.input(stream) # stream is a string
        self.lookahead = self.lexer.token()
    
    def pointer(self):
        return self.lookahead
    
    def next(self):
        self.lookahead = self.lexer.token()
        return self.lookahead
    
    def end_of_file(self):
        # lexer.token() returns None when at EOF
        if not self.lookahead:
            return True
        else:
            return False

##################################################################
# this function will print any AST that follows the
#
#      (TYPE [, child1, child2,...])
#
# tuple format for tree nodes.

def dump_AST(node):
    _dump_AST(node)
    print('')

def _dump_AST(node, level=0):
    
    if isinstance(node, tuple):
        indent(level)
        nchildren = len(node) - 1

        print("(%s" % node[0], end='')
        
        if nchildren > 0:
            print(" ", end='')
        
        for c in range(nchildren):
            _dump_AST(node[c+1], level+1)
            if c != nchildren-1:
                print(' ', end='')
        
        print(")", end='')
    else:
        print("%s" % str(node), end='')

def indent(level):
    print('')
    for i in range(level):
        print('  |',end='')


##################################################################
def assert_match(input, expected):
    if input != expected:
        raise ValueError("Pattern match failed: expected {} but got {}".format(expected, input))

##################################################################


