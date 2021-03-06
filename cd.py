import random
import sys
sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

reserved = {
    'public' : 'PUBLIC',
    'static': 'STATIC',
    'void': 'VOID',
    'main' : 'MAIN',
    'class' : 'CLASS',
    'String' : 'STRING',
    'args' : 'ARGS',
    'int' : 'INT',
    'float' : 'FLOAT',
    'boolean' : 'BOOLEAN',
    'False' : 'FALSE',
    'True' : 'TRUE',
    'if' : 'IF',
    'else' : 'ELSE',
    'private' : 'PRIVATE',
    'protected' : 'PROTECTED',
    'do' : 'DO',
    'while' : 'WHILE',
}

tokens = (
    'NAME', 'NUMBER','REL_EQ', 'REL_NEQ', 'REL_GTEQ', 'REL_LTEQ','MINEQ','PLUSEQ','DIVEQ','MULEQ'
) + tuple(reserved.values());

literals = ['=', '+', '-', '*', '/', '(', ')', '<', '>', '!','{','}' ,';', ':']

# Tokens
# t_multicomment = r'/\*.*\n.*\*/'
t_REL_EQ = r'=='
t_REL_GTEQ = r'>='
t_REL_LTEQ = r'<='
t_REL_NEQ = r'!='
t_MINEQ = r'-='
t_PLUSEQ = r'\+='
t_DIVEQ = r'/='
t_MULEQ = r'\*='
# t_comment = r'//.*'

t_ignore = " \t[]"
def t_comment_ignore(t):
    r"//.*|/\*+[^*]*\*+(?:[^/*][^*]*\*+)*/"


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'NAME')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
count  = 0 
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)



def t_error(t):
    print("Illegal character '%s'"  %t.value)
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

f = open(sys.argv[1],"r")
s=f.read()
print(s.count("\n"));
lexer.input(s)

# Parsing rules

precedence = (
    ('left','='),
    ('left','REL_EQ','REL_NEQ'),
    ('left', '<','>','REL_GTEQ', 'REL_LTEQ'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS','!'),
)

# dictionary of names
symbol_table = dict()
names = {}
start = 'start'

def p_start(p):
    ''' start : PUBLIC CLASS NAME '{' main_body '}'
              | PRIVATE CLASS NAME '{' main_body '}'
              | PROTECTED CLASS NAME '{' main_body '}'
              | CLASS NAME '{' main_body '}'
              | main_body '''

def p_main_body(p):
    ''' main_body : PUBLIC STATIC VOID MAIN '(' STRING ARGS ')' '{' body '}' 
                  | body '''

def p_body(p):
    ''' body : statements '''

def p_statements(p):
    ''' statements : statements statement 
                   | '''

def p_statement_do_while(p):
    ''' statement : DO '{' statements '}' WHILE '(' expression ')' ';' '''

def p_else_if_block(p):
    ''' else_if : ELSE IF '(' expression ')' '{' statements '}' else_if
                | ELSE IF '(' expression ')' statement else_if 
                | ELSE '{' statements '}' 
                | ELSE statement
                | '''

def p_statement_if(p):
    ''' statement : IF '(' expression ')' '{' statements '}' else_if
                  | IF '(' expression ')' statement else_if '''

# def p_statement_if_else(p):
#     ''' statement : IF '(' expression ')' '{' statements '}' ELSE '{' statements '}' 
#                   | IF '(' expression ')' statement ELSE '{' statements '}' '''
       

def p_statement_declare(p):
    ''' statement : INT NAME ';'
                  | FLOAT NAME ';'
                  | BOOLEAN NAME ';' '''
    if p[1] == "int" :
        names[p[2]] = 0
    elif p[1] == "float":
        names[p[2]] = 0.0
    elif p[1] == "boolean":
        names[p[2]] = "False"
    symbol_table[p[2]][3] = p[1]
    symbol_table[p[2]][5] = names[p[2]]

def p_statement_assign(p):
    '''statement : NAME "=" expression ';'
                 | INT NAME "=" expression ';'
                 | FLOAT NAME "=" expression ';'
                 | BOOLEAN NAME "=" TRUE ';'
                 | BOOLEAN NAME "=" FALSE ';' '''
    if p[2] == "=":
        if (type(p[3]) == bool ):
            if symbol_table[p[1]][3] == "boolean":
                names[p[1]] = p[3]
                symbol_table[p[1]][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
        if (type(p[3]) == int ) :
            if symbol_table[p[1]][3] == "int":
                names[p[1]] = p[3]
                symbol_table[p[1]][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
        if ( type(p[3]) == float ) :
            if symbol_table[p[1]][3] == "float":
                names[p[1]] = p[3]
                symbol_table[p[1]][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
    else:
        names[p[2]] = p[4]
        symbol_table[p[2]][5] = names[p[2]]
        symbol_table[p[2]][3] = p[1]


def p_statement_expr(p):
    '''statement : expression ";" '''
    print(p[1])

def p_expr_boolean(p):
    '''expression : TRUE
                  | FALSE '''
    p[0] = p[1]

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]

def p_statement_relational(p):
    '''expression : expression '>' expression
                 | expression '<' expression''' 
    if p[2] == '>':
        p[0] = (p[1] > p[3])
    elif p[2] == '<':
        p[0] = (p[1] < p[3])

def p_relop(p):
    '''expression : expression REL_EQ expression
              | expression REL_NEQ expression
                      | expression REL_GTEQ expression
              | expression REL_LTEQ expression'''
    if p[2] == "==" :
        p[0] = (p[1] == p[3])
    elif p[2] == "!=" : 
        p[0] = (p[1] != p[3])
    elif p[2] == "<=" : 
        p[0] = (p[1] <= p[3])
    elif p[2] == ">=" :
        p[0] = (p[1] >= p[3])
   

def p_operation_equals(p):
    '''statement : NAME MINEQ expression ";"
                 | NAME PLUSEQ expression ";"
                 | NAME DIVEQ expression ";"
                 | NAME MULEQ expression ";" '''
    if p[2] == '+=':
        names[p[1]] = names[p[1]] + p[3]
        symbol_table[p[1]][5] = names[p[1]]
    elif p[2] == '-=':
        names[p[1]] = names[p[1]] - p[3]
        symbol_table[p[1]][5] = names[p[1]]
    elif p[2] == '/=':
        names[p[1]] = names[p[1]] / p[3]
        symbol_table[p[1]][5] = names[p[1]]
    elif p[2] == '*=':
        names[p[1]] = names[p[1]] * p[3]
        symbol_table[p[1]][5] = names[p[1]]

def p_expression_not(p):
    '''expression : '!' expression'''
    p[0] = not (p[2])

def p_expression_uminus(p):
    '''expression : '-' expression %prec UMINUS'''
    p[0] = -p[2]

def p_expression_group(p):
    '''expression : '(' expression ')' '''
    p[0] = p[2]


def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]


def p_expression_name(p):
    '''expression : NAME'''
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        error_line_no = p.lineno - s.count("\n")-1
        print("Syntax error at line number '%s'" % error_line_no)
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()

scope_level = 0
#while 1:
while True:
    tok = lex.token()
    if not tok:
        # print(tok)
        # print(symbol_table) 
        break
    else:
        token = (tok.type, tok.value, tok.lineno)
        print(token)
        if tok.type == '(' or tok.type == '{':
            scope_level = scope_level + 1
        if tok.type == ')' or tok.type == '}':
            scope_level = scope_level - 1
        if scope_level == 0:
            scope = "global"
        else:
            scope = "scope" + str(scope_level )
        if tok.type == 'NAME':
             try: 
                token = [tok.type,tok.value,tok.lineno,"int",scope,names[tok.value]]
                symbol_table[tok.value] = token
             except KeyError:
                 token =  [tok.type,tok.value,tok.lineno,"identifier",scope,tok.value]
             symbol_table[tok.value] = token

yacc.parse(s)
# print("Here")
print(symbol_table)