from ply import lex


class Symbol:
    def __init__(self):
        self.reserved = (
            'begin', 'end', 'if', 'then', 'else',
            'while', 'do', 'repeat', 'until', 'procedure', 'to', 'downto', 'for', 'in', 'with',
            'write', 'read', 'call', 'function',
            'var', 'const', 'odd', 'type', 'of', 'set', 'record', 'forward',
            'and', 'or', 'not',
            'div', 'mod',
            'program',
            'integer', 'string', 'boolean', 'real', 'array',
        )
        self.tokens = self.reserved+(
            'nul', 'plus', 'minus', 'times', 'division',
            'eql', 'neq', 'lss', 'geq', 'gtr', 'leq',
            'lparen', 'rparen', 'comma', 'semicolon', 'peroid', 'colon', 'lbrack', 'rbrack', 'dotdot',
            'becomes', 'ident',
            'iconst', 'sconst', 'bconst', 'rconst',
        )

symbol = Symbol()
tokens = symbol.tokens


t_plus = r'\+'
t_minus = r'-'
t_times = r'\*'
t_division = r'/'
t_eql = r'='
t_neq = r'<>'
t_leq = r'<='
t_lss = r'<'
t_geq = r'>='
t_gtr = r'>'
t_lparen = r'\('
t_rparen = r'\)'
t_lbrack = r'\['
t_rbrack = r'\]'
t_comma = r','
t_peroid = r'\.'
t_dotdot = r'\.\.'
t_semicolon = r';'
t_colon = r':'
t_becomes = r':='
reserved_map = {}


def t_rconst(t):
    r'\d+\.\d+'
    # r'(\-)*[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t


def t_iconst(t):
    r'\d+'
    # r'(\-)*[0-9]+'
    t.value = int(t.value)
    return t


def t_sconst(t):
    r'\".*?\"'
    return t


def t_bconst(t):
    r'True|False'
    return t


def t_ident(t):
    r'[A-Za-z_][\w_]*'
    for r in symbol.reserved:
        reserved_map[r] = r
    t.type = reserved_map.get(t.value, "ident")
    return t


t_ignore = " \t"


def t_comment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


def getScanner(data_file):
    scanner = lex.lex()
    scanner.input(data_file)

    return scanner
