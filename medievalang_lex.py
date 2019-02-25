import re
from ply import lex

reserved = {
    'Who'       : 'WHO',
    'Send'      : 'SEND',
    'word'      : 'WORD',
    'Exclaim'   : 'EXCLAIM',
    'gallantry' : 'GALLANTRY',
    'If'        : 'IF',
    'For'       : 'WHILE',
    'not'       : 'NOT',
    'Meet'      : 'DECLARE',
    'conspire'  : 'PLUS',
    'betray'    : 'MINUS',
    'defeat'    : 'TIMES',
    'surrender' : 'DIVIDE',
    'First'     : 'BLOCK',
    'is'        : 'IS',
    'watches'   : 'WATCHES',
    'the'       : 'THE',
    'finally'   : 'ENDBLOCK',
    'and'       : 'AND',
    'to'        : 'TO',
    'with'      : 'WITH',
    'plan'      : 'PLAN',
    'an'        : 'AN',
    'a'         : 'ALOWER',
    'A'         : 'A',
    'the'       : 'THE',
    'devised'   : 'DEVISED',
    'castle'    : 'CASTLE',
    'of'        : 'OF',
    'begins'    : 'BEGINS',
    'as'        : 'AS',
    'long'      : 'LONG',
    'precedes'  : 'LE',
    'abides'    : 'EQ',
    'Now'       : 'NOW',
    's'         : 'S',
    'While'     : 'FOR',
    'ascends'   : 'ASCENDS',
    'from'      : 'FROM',
    'conspires' : 'CONSPIRES',
    'betrays'   : 'BETRAYS',
    'defeats'   : 'DEFEATS',
    'surrenders': 'SURRENDERS'

}

literals = [',','.','=','(',')','{','}', '!', ':', '?', '\'']


#dictionary used to read numbers
digits = {
    'one'   : '1',
    'two'   : '2',
    'three' : '3',
    'four'  : '4',
    'five'  : '5',
    'six'   : '6',
    'seven' : '7',
    'eight' : '8',
    'nine'  : '9',
    'zero'  : '0',
    'dead'      : '0',
    'peasant'   : '1',
    'servant'   : '2',
    'yeoman'    : '3',
    'commoner'  : '4',
    'reeve'     : '5',
    'bailiff'   : '6',
    'vassal'    : '7',
    'noble'     : '8',
    'King'      : '9'
}

tokens = [
          'INTEGER','ID',
          ] + list(reserved.values())


t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    if t.value in digits:
        t.type = 'INTEGER'
        t.value = digits[t.value]
    return t

def is_ID(s):
    m = re.match(r'[a-zA-Z_][a-zA-Z_0-9]*', s)
    
    if s in list(reserved.keys()):
        return False
    elif m and len(m.group(0)) == len(s):
        return True
    else:
        return False

def t_INTEGER(t):
    r'[0-9]+'
    return t

def t_COMMENT(t):
    r'//.*'
    pass

def t_NEWLINE(t):
    r'\n'
    pass

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

# build the lexer
lexer = lex.lex(debug=0)

