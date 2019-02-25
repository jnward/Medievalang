# Medievalang Frontend

from ply import yacc
from medievalang_lex import tokens, lexer, is_ID
from medievalang_state import state

#########################################################################
precedence = (
             ('left', 'EQ', 'LE'),
             ('left', 'PLUS', 'MINUS'),
             ('left', 'TIMES', 'DIVIDE'),
             ('right', 'UMINUS', 'NOT'))

#########################################################################
def p_prog(p):
    '''
    program : stmt_list
    '''
    state.AST = p[1]

#########################################################################
def p_stmt_list(p):
    '''
    stmt_list : stmt stmt_list
              | empty
    '''
    if (len(p) == 3):
        p[0] = ('seq', p[1], p[2])
    elif (len(p) == 2):
        p[0] = p[1]

#########################################################################
def p_stmt(p):
    '''
    stmt : A PLAN IS DEVISED TO ID THE CASTLE opt_of opt_formal_args ':' stmt
         | DECLARE ID opt_init opt_end
         | ID IS opt_to exp opt_end
         | ID WATCHES opt_to exp opt_end
         | ID BEGINS opt_to exp opt_end
         | WHO IS ID '?'
         | EXCLAIM THE GALLANTRY OF exp opt_end
         | NOW ',' ID THE CASTLE opt_of opt_actual_args opt_end
         | SEND WORD OF opt_exp opt_end
         | WHILE AS LONG AS exp ellipsis stmt
         | IF exp ellipsis stmt opt_else
         | BLOCK ',' stmt_list ',' ENDBLOCK opt_end
         | FOR ID ASCENDS FROM exp TO exp ellipsis stmt
         | ID opt_prep iterator exp opt_end
    '''
    if p[2] == 'plan':
        p[0] = ('fundecl', p[6], p[10], p[12])
    elif p[1] == 'Meet':
        p[0] = ('declare', p[2], p[3])
    elif is_ID(p[1]) and (p[2] == 'is' or p[2] == 'watches' or p[2] == 'begins'):
        p[0] = ('assign', p[1], p[4])
    elif p[1] == 'Who':
        p[0] = ('get', p[3])
    elif p[1] == 'Exclaim':
        p[0] = ('put', p[5])
    elif p[1] == 'Now':
        p[0] = ('callstmt', p[3], p[7])
    elif p[1] == 'Send':
        p[0] = ('return', p[4])
    elif p[1] == 'For':
        p[0] = ('while', p[5], p[7])
    elif p[1] == 'If':
        p[0] = ('if', p[2], p[4], p[5])
    elif p[1] == 'First':
        p[0] = ('block', p[3])
    elif p[1] == 'While':
        p[0] = ('for', p[2], p[5], p[7], p[9])
    elif is_ID(p[1]) and (p[3] == 'defeats' or p[3] == 'conspires' or p[3] == 'betrays' or p[3] == 'surrenders'):
        p[0] = ('iterator', p[1], p[3], p[4])
    else:
        raise ValueError("unexpected symbol {}".format(p[1]))

#########################################################################

def p_opt_gallantry(p):
    '''
    opt_gallantry : "'" S GALLANTRY
                  | empty
    '''

def p_opt_to(p):
    '''
    opt_to : TO
           | empty
    '''

def p_opt_of(p):
    '''
    opt_of : OF
           | empty
    '''

def p_opt_formal_args(p):
    '''
    opt_formal_args : formal_args
                    | empty
    '''
    p[0] = p[1]

def p_iterator(p):
    '''
    iterator : CONSPIRES opt_prep
             | BETRAYS
             | DEFEATS
             | SURRENDERS opt_prep
    '''
    p[0] = p[1]

def p_formal_args(p):
    '''
    formal_args : ID comma_and formal_args
                | ID
    '''
    if (len(p) == 4):
        p[0] = ('seq', ('id', p[1]), p[3])
    elif (len(p) == 2):
        p[0] = ('seq', ('id', p[1]), ('nil',))

def p_comma_and(p): #used for parameter lists
    '''
    comma_and : ','
              | opt_oxford AND
    '''
    pass

def p_opt_oxford(p):
    '''
    opt_oxford : ','
               | empty
    '''
    pass

def p_opt_init(p):
    '''
    opt_init : '=' exp
             | empty
    '''
    if p[1] == '=':
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_opt_actual_args(p):
    '''
    opt_actual_args : actual_args
                    | empty
    '''
    p[0] = p[1]

def p_actual_args(p):
    '''
    actual_args : exp comma_and actual_args
                | exp
    '''
    if (len(p) == 4):
        p[0] = ('seq', p[1], p[3])
    elif (len(p) == 2):
        p[0] = ('seq', p[1], ('nil',))

def p_opt_exp(p):
    '''
    opt_exp : exp
            | empty
    '''
    p[0] = p[1]

def p_opt_else(p):
    '''
    opt_else : IF NOT ellipsis stmt
             | empty
    '''
    if p[2] == 'not':
        p[0] = p[4]
    else:
        p[0] = p[1]
    

def p_binop_exp(p):
    '''
    exp : exp opt_gallantry PLUS opt_prep exp opt_gallantry 
        | exp opt_gallantry MINUS opt_prep exp opt_gallantry 
        | exp opt_gallantry TIMES opt_prep exp opt_gallantry 
        | exp opt_gallantry DIVIDE opt_prep exp opt_gallantry 
        | exp opt_gallantry EQ opt_prep exp opt_gallantry 
        | exp opt_gallantry LE opt_prep exp opt_gallantry 
    '''
    p[0] = (p[3], p[1], p[5])

def p_opt_prep(p):
    '''
    opt_prep : WITH
             | TO
             | empty
    '''

def p_opt_article(p):
    '''
    opt_article : ALOWER
                | AN
                | THE
                | empty
    '''

def p_integer_exp(p):
    '''
    exp : opt_article INTEGER
    '''
    p[0] = ('integer', int(p[2]))

def p_id_exp(p):
    '''
    exp : ID
    '''
    p[0] = ('id', p[1])

def p_call_exp(p):
    '''
    exp : ID THE CASTLE OF opt_actual_args
    '''

    p[0] = ('callexp', p[1], p[5])
    
def p_uminus_exp(p):
    '''
    exp : MINUS exp %prec UMINUS
    '''
    p[0] = ('uminus', p[2])


def p_not_exp(p):
    '''
    exp : NOT exp
    '''
    p[0] = ('not', p[2])


def p_opt_end(p):
    '''
    opt_end : '.'
            | '!'
            | empty
    '''
    pass


def p_ellipsis(p):
    '''
    ellipsis : '.' '.' '.'
    '''

def p_empty(p):
    '''
    empty :
    '''
    p[0] = ('nil',)


def p_error(t):
    print("Syntax error at '%s'" % t.value)

#########################################################################
# build the parser
#########################################################################
parser = yacc.yacc(debug=False,tabmodule='medievalang_parsetab')

