from medievalang_state import state
from grammar_stuff import assert_match

#much of this code is recycled from Cuppa3

class ReturnValue(Exception):
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return(repr(self.value))

def len_seq(seq_list):

    if seq_list[0] == 'nil':
        return 0

    elif seq_list[0] == 'seq':
        (SEQ, p1, p2) = seq_list

        return 1 + len_seq(p2)

    else:
            raise ValueError("unknown node type: {}".format(seq_list[0]))

def eval_actual_args(args):

    if args[0] == 'nil':
        return ('nil',)

    elif args[0] == 'seq':
        (SEQ, p1, p2) = args

        val = walk(p1)

        return ('seq', val, eval_actual_args(p2))

    else:
        raise ValueError("unknown node type: {}".format(args[0]))

def declare_formal_args(formal_args, actual_val_args):

    if len_seq(actual_val_args) != len_seq(formal_args):
        raise ValueError("actual and formal argument lists do not match")

    if formal_args[0] == 'nil':
        return

    (SEQ, (ID, sym), p1) = formal_args
    (SEQ, val, p2) = actual_val_args

    state.symbol_table.declare_sym(sym, val)

    declare_formal_args(p1, p2)

def handle_call(name, actual_arglist):
    
    (type, val) = state.symbol_table.lookup_sym(name)
    
    if type != 'function':
        raise ValueError("{} is not a function".format(name))

    (FUNVAL, formal_arglist, body, context) = val

    if len_seq(formal_arglist) != len_seq(actual_arglist):
        raise ValueError("function {} expects {} arguments".format(sym, len_seq(formal_arglist)))

    actual_val_args = eval_actual_args(actual_arglist)  
    save_symtab = state.symbol_table.get_config()       

    state.symbol_table.set_config(context)           #static scoping
    state.symbol_table.push_scope()                     
    declare_formal_args(formal_arglist, actual_val_args)

    return_value = None
    try:
        walk(body)
    except ReturnValue as val:
        return_value = val.value

    state.symbol_table.set_config(save_symtab)

    return return_value

def seq(node):
    
    (SEQ, stmt, stmt_list) = node
    assert_match(SEQ, 'seq')
    
    walk(stmt)
    walk(stmt_list)

def nil(node):
    
    (NIL,) = node
    assert_match(NIL, 'nil')
    
    pass

def fundecl_stmt(node):

    try:
        (FUNDECL, name, (NIL,), body) = node
        assert_match(FUNDECL, 'fundecl')
        assert_match(NIL, 'nil')

    except ValueError:
        (FUNDECL, name, arglist, body) = node
        assert_match(FUNDECL, 'fundecl')
        
        context = state.symbol_table.get_config()
        funval = ('funval', arglist, body, context)
        state.symbol_table.declare_fun(name, funval)

    else:
        context = state.symbol_table.get_config()
        funval = ('funval', ('nil',), body, context)
        state.symbol_table.declare_fun(name, funval)

def declare_stmt(node):

    try:
        (DECLARE, name, (NIL,)) = node
        assert_match(DECLARE, 'declare')
        assert_match(NIL, 'nil')

    except ValueError:
        (DECLARE, name, init_val) = node
        assert_match(DECLARE, 'declare')
        
        value = walk(init_val)
        state.symbol_table.declare_sym(name, value)

    else:
        state.symbol_table.declare_sym(name, 0)

def assign_stmt(node):

    (ASSIGN, name, exp) = node
    assert_match(ASSIGN, 'assign')
    
    value = walk(exp)
    state.symbol_table.update_sym(name, ('scalar', value))

def get_stmt(node):

    (GET, name) = node
    assert_match(GET, 'get')

    s = input("Describe " + name + '\'s gallantry! ')
    
    try:
        value = int(s)
    except ValueError:
        raise ValueError("expected an integer value for " + name)
    
    state.symbol_table.update_sym(name, ('scalar', value))

def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'put')
    
    value = walk(exp)
    print("~ {}".format(value))

def call_stmt(node):

    (CALLSTMT, name, actual_args) = node
    assert_match(CALLSTMT, 'callstmt')

    handle_call(name, actual_args)

def return_stmt(node):

    try:
        (RETURN, (NIL,)) = node
        assert_match(RETURN, 'return')
        assert_match(NIL, 'nil')

    except ValueError:
        (RETURN, exp) = node
        assert_match(RETURN, 'return')
        
        value = walk(exp)
        raise ReturnValue(value)

    else:
        raise ReturnValue(None)

def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'while')
    
    value = walk(cond)
    while value != 0:
        walk(body)
        value = walk(cond)

def for_stmt(node):

    (FOR, ID, exp1, exp2, code) = node
    start = int(walk(exp1))
    end = int(walk(exp2))


    try:
        state.symbol_table.lookup_sym(ID)
    except:
        state.symbol_table.declare_sym(ID, start)


    for i in range(start, end):
        state.symbol_table.update_sym(ID, ('scalar', i))
        walk(code)

def if_stmt(node):
    
    try:
        (IF, cond, then_stmt, (NIL,)) = node
        assert_match(IF, 'if')
        assert_match(NIL, 'nil')

    except ValueError:
        (IF, cond, then_stmt, else_stmt) = node
        assert_match(IF, 'if')
        
        value = walk(cond)
        
        if value != 0:
            walk(then_stmt)
        else:
            walk(else_stmt)

    else:
        value = walk(cond)
        if value != 0:
            walk(then_stmt)

def block_stmt(node):
    
    (BLOCK, stmt_list) = node
    assert_match(BLOCK, 'block')
    
    state.symbol_table.push_scope()
    walk(stmt_list)
    state.symbol_table.pop_scope()

def iter_stmt(node):
    #this is used for assignment operations
    (ITERATOR, id1, iterate, c2) = node
    v1 = state.symbol_table.lookup_sym(id1)
    v1 = v1[1]
    v2 = walk(c2)

    if iterate == 'conspires':
        v3 = v1 + v2
    elif iterate == 'betrays':
        v3 = v1 - v2
    elif iterate == 'defeats':
        v3 = v1 * v2
    elif iterate == 'surrenders':
        v3 = v1 / v2

    state.symbol_table.update_sym(id1, ('scalar', v3))

def plus_exp(node):
    
    (PLUS,c1,c2) = node
    assert_match(PLUS, 'conspire')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 + v2

def minus_exp(node):
    
    (MINUS,c1,c2) = node
    assert_match(MINUS, 'betray')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 - v2

def times_exp(node):
    
    (TIMES,c1,c2) = node
    assert_match(TIMES, 'defeat')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 * v2

def divide_exp(node):
    
    (DIVIDE,c1,c2) = node
    assert_match(DIVIDE, 'surrender')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 // v2

def eq_exp(node):
    
    (EQ,c1,c2) = node
    assert_match(EQ, 'abides')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return 1 if v1 == v2 else 0

def le_exp(node):
    
    (LE,c1,c2) = node
    assert_match(LE, 'precedes')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return 1 if v1 <= v2 else 0

def integer_exp(node):

    (INTEGER, value) = node
    assert_match(INTEGER, 'integer')
    
    return value

def id_exp(node):
    
    (ID, name) = node
    assert_match(ID, 'id')
    
    (type, val) = state.symbol_table.lookup_sym(name)
    
    if type != 'scalar':
        raise ValueError("{} is not a scalar".format(name))

    return val

def call_exp(node):
    (CALLEXP, name, args) = node
    assert_match(CALLEXP, 'callexp')
    
    return_value = handle_call(name, args)
    
    if return_value is None:
        raise ValueError("No return value from function {}".format(name))
    
    return return_value

def uminus_exp(node):
    
    (UMINUS, exp) = node
    assert_match(UMINUS, 'uminus')
    
    val = walk(exp)
    return - val

def not_exp(node):
    
    (NOT, exp) = node
    assert_match(NOT, 'not')
    
    val = walk(exp)
    return 0 if val != 0 else 1

def paren_exp(node):
    
    (PAREN, exp) = node
    assert_match(PAREN, 'paren')
    
    return walk(exp)

def walk(node):
    type = node[0]
    
    if type in dispatch_dict:
        node_function = dispatch_dict[type]
        return node_function(node)
    else:
        raise ValueError("walk: unknown tree node type: " + type)

dispatch_dict = {
    'seq'     : seq,
    'nil'     : nil,
    'fundecl' : fundecl_stmt,
    'declare' : declare_stmt,
    'assign'  : assign_stmt,
    'get'     : get_stmt,
    'put'     : put_stmt,
    'callstmt': call_stmt,
    'return'  : return_stmt,
    'while'   : while_stmt,
    'if'      : if_stmt,
    'block'   : block_stmt,
    'integer' : integer_exp,
    'id'      : id_exp,
    'callexp' : call_exp,
    'paren'   : paren_exp,
    'conspire'       : plus_exp,
    'betray'       : minus_exp,
    'defeat'       : times_exp,
    'surrender'       : divide_exp,
    'abides'      : eq_exp,
    'precedes'      : le_exp,
    'uminus'  : uminus_exp,
    'not'     : not_exp,
    'for'     : for_stmt,
    'iterator': iter_stmt
}


