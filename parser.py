import ply.yacc as yacc
from ply import yacc
from lexer import tokens
from character_map import SymbolTable, SymbolTableStack, SymbolTableStorage
import sys
import logging


symbol_stack = SymbolTableStack()
symbol_storage = SymbolTableStorage()
main_table = SymbolTable('global')
symbol_stack.push(main_table)

flag_procedure_function = False
nested_block_counter = 0


precedence = (
    ('nonassoc', 'in', 'neq', 'leq', 'lss', 'geq', 'gtr', 'eql'),
    ('left', 'plus', 'minus', 'or'),
    ('left', 'and', 'div', 'mod', 'times', 'division'),
    ('right', 'not'),
    ('left', 'peroid', 'rbrack', 'lbrack', 'lparen', 'rparen'),
    ('right', 'else')
)


def p_program(p):
    '''
    program_rule : header declarations subprograms comp_statement peroid
    '''
    p[0] = [p[1], p[2], p[3], p[4], p[5]]


def p_header(p):
    '''
    header : program ident semicolon
    '''
    p[0] = [p[1], p[2], p[3]]


def p_declarations(p):
    '''
    declarations : constdefs typedefs vardefs
    '''
    p[0] = [p[1], p[2], p[3]]


def p_constdefs(p):
    '''constdefs :
                 | const constant_defs semicolon
    '''

    mas_data_types = []
    str_data_types = ''

    def getting_data_types(tup):
        for item in tup:
            if isinstance(item, list):
                getting_data_types(item)
            else:
                mas_data_types.append(item)

    def define_data_type(data):
        if data.lower() == 'true' or data.lower() == 'false':
            return 'boolean'
        try:
            int(data)
            return 'integer'
        except ValueError:
            pass
        try:
            float(data)
            return 'real'
        except ValueError:
            pass
        return 'string'

    if len(p) == 4:
        getting_data_types(p[2])
        for mas_data_types_part in mas_data_types:
            str_data_types += str(mas_data_types_part)
        data_types = []
        str_data_types = str_data_types.split(';')
        for str_data_types_part in str_data_types:
            elements = str_data_types_part.split('=')
            nums = elements[0].split(',')
            inner_array = [[num.strip() for num in nums], [elements[1]]]
            data_types.append(inner_array)
        for data_types_part in data_types:
            for data_types_part_part in data_types_part[0]:
                symbol_stack.top().symbols[data_types_part_part] = [data_types_part[1][0], define_data_type(data_types_part[1][0])]

        p[0] = [p[1], p[2], p[3]]
    else:
        p[0] = None


def p_constant_defs(p):
    '''
    constant_defs : constant_defs semicolon ident eql expression
                  | ident eql expression
    '''
    if len(p) == 6:
        p[0] = [p[1], p[2], p[3], p[4], p[5]]
    else:
        p[0] = [p[1], p[2], p[3]]


def p_relop(p):
	'''
	relop : neq
		  | leq
		  | lss
		  | geq
		  | gtr
	'''
	p[0] = p[1]


def p_addop(p):
	'''
	addop : plus
		  | minus
	'''
	p[0] = p[1]


def p_expression(p):
	'''
	expression : expression relop expression
			   | expression eql expression
			   | expression in expression
			   | expression or expression
			   | expression plus expression
			   | expression minus expression
			   | expression and expression
			   | expression div expression
			   | expression mod expression
			   | expression times expression
			   | expression division expression
			   | addop expression
			   | not expression
			   | variable
			   | ident lparen expressions rparen
			   | constant
			   | lparen expression rparen
			   | setexpression
	'''
	if len(p) == 4:
		if p[1] == '(':
			p[0] = p[2]
		else:
			p[0] = [p[2], p[1], p[3]]
	elif len(p) == 3:
		p[0] = [p[1], p[2]]
	elif len(p) == 5:
		p[0] = [p[1], p[2], p[3], p[4]]
	else:
		p[0] = p[1]


def p_variable(p):
	'''
	variable : ident
			 | variable peroid ident
			 | variable lbrack expressions rbrack
	'''
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	elif len(p) == 5:
		p[0] = [p[1], p[2], p[3], p[4]]


def p_expressions(p):
	'''
	expressions : expressions comma expression
				| expression
	'''
	if len(p) == 4:
		p[0] = [p[2], p[1], p[3]]
	else:
		p[0] = p[1]


def p_constant(p):
	'''
	constant : iconst
			 | rconst
			 | bconst
			 | sconst
	'''
	p[0] = p[1]


def p_setexpression(p):
	'''
	setexpression : lbrack elexpressions rbrack
				 | lbrack rbrack
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = [p[1], p[2]]


def p_elexpressions(p):
	'''
	elexpressions : elexpressions comma elexpression
				  | elexpression
	'''
	if len(p) == 4:
		p[0] = [p[2], p[1], p[3]]
	else:
		p[0] = p[1]


def p_elexpression(p):
	'''
	elexpression : expression dotdot expression
				 | expression
	'''
	if len(p) == 4:
		p[0] = [p[2], p[1], p[3]]
	else:
		p[0] = p[1]


def p_typedefs(p):
	'''
	typedefs : type type_defs semicolon
			 |
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = None


def p_type_defs(p):
	'''
	type_defs : type_defs semicolon ident eql type_def
			  | ident eql type_def
	'''
	if len(p) == 6:
		p[0] = [p[1], p[2], p[3], p[4], p[5]]
	else:
		p[0] = [p[1], p[2], p[3]]


def p_type_def(p):
	'''
	type_def : array lbrack dims rbrack of typename
			 | set of typename
			 | record fields end
			 | lparen identifiers rparen
			 | limit dotdot limit
	'''
	if len(p) == 7:
		p[0] = [p[1], p[2], p[3], p[4], p[5], p[6]]
	elif len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	elif len(p) == 4 and p[1] == 'record':
		p[0] = [p[1], p[2], p[3]]
	elif len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	elif len(p) == 4:
		p[0] = [p[2], p[1], p[3]]


def p_dims(p):
	'''
	dims : dims comma limits
		 | limits
	'''
	if len(p) == 4:
		p[0] = [p[2], p[1], p[3]]
	else:
		p[0] = p[1]


def p_limits(p):
	'''
	limits : limit dotdot limit
		   | ident
	'''
	if len(p) == 4:
		p[0] = [p[2], p[1], p[3]]
	else:
		p[0] = p[1]


def p_limit(p):
	'''
	limit : addop iconst
		  | addop ident
		  | iconst
		  | sconst
		  | bconst
		  | ident
	'''
	if len(p) == 3:
		p[0] = [p[1], p[2]]
	else:
		p[0] = p[1]


def p_typename(p):
	'''
		typename : standard_type
		'''
	# '''
	# typename : standard_type
	# 		  | ident
	# '''
	p[0] = p[1]


def p_standard_type(p):
	'''
	standard_type : integer
				  | real
				  | boolean
				  | string
	'''
	p[0] = p[1]


def p_fields(p):
	'''
	fields : field
		   | fields semicolon field
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = [p[1], p[2], p[3]]


def p_field(p):
	'''
	field : identifiers colon typename
	'''
	p[0] = [p[1], p[2], p[3]]


def p_identifiers(p):
	'''
	identifiers : ident
				| identifiers comma ident
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = [p[1], p[2], p[3]]


def p_vardefs(p):
	'''
	vardefs : var variable_defs semicolon
			|
	'''

	mas_data_types = []
	str_data_types = ''

	def getting_data_types(tup):
		for item in tup:
			if isinstance(item, list):
				getting_data_types(item)
			else:
				mas_data_types.append(item)

	if len(p) == 4:
		getting_data_types(p[2])
		for mas_data_types_part in mas_data_types:
			str_data_types += mas_data_types_part
		data_types = []
		str_data_types = str_data_types.split(';')
		for str_data_types_part in str_data_types:
			elements = str_data_types_part.split(':')
			nums = elements[0].split(',')
			inner_array = [[num.strip() for num in nums], [elements[1]]]
			data_types.append(inner_array)

		for data_types_part in data_types:
			for data_types_part_part in data_types_part[0]:
				symbol_stack.top().symbols[data_types_part_part] = [None, data_types_part[1][0]]

		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = None


def p_variable_defs(p):
	'''
	variable_defs : identifiers colon typename
				  | variable_defs semicolon identifiers colon typename
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = [p[1], p[2], p[3], p[4], p[5]]


def p_subprograms(p):
	'''
	subprograms : subprograms subprogram semicolon
				|
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = None


def p_subprogram(p):
	'''
	subprogram : sub_header semicolon forward
			   | sub_header semicolon declarations subprograms comp_statement
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = [p[1], p[2], p[3], p[4], p[5]]


def p_sub_header(p):
	'''
	sub_header : function ident formal_parameters colon standard_type
			   | procedure ident formal_parameters
			   | function ident
	'''
	if len(p) == 6:
		p[0] = [p[1], p[2], p[3], p[4], p[5]]
	elif len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	elif len(p) == 2:
		p[0] = [p[1], p[2]]

	global flag_procedure_function
	flag_procedure_function = True

	mas_data_types = []
	str_data_types = ''

	def getting_data_types(tup):
		for item in tup:
			if isinstance(item, list):
				getting_data_types(item)
			else:
				mas_data_types.append(item)

	if len(p) == 4 or len(p) == 6:
		data_types = []
		data_types_arguments = []
		if len(p) == 6:
			getting_data_types(p[3][1])
			for mas_data_types_part in mas_data_types:
				if mas_data_types_part != None:
					str_data_types += mas_data_types_part
			str_data_types = str_data_types.split(';')
			for str_data_types_part in str_data_types:
				elements = str_data_types_part.split(':')
				nums = elements[0].split(',')
				inner_array = [[num.strip() for num in nums], [elements[1]]]
				data_types.append(inner_array)

			for subarr in data_types:
				first_array_length = len(subarr[0])
				second_array_value = subarr[1][0]
				for i in range(first_array_length):
					data_types_arguments.append(second_array_value)

		if p[1] == 'function':
			number_function_arguments = sum(len(arr[0]) for arr in data_types)
			symbol_stack.top().symbols[p[2]] = [None, 'function', number_function_arguments, p[5], data_types_arguments]
		else:
			symbol_stack.top().symbols[p[2]] = [None, 'procedure']

		new_table = SymbolTable(p[2])
		symbol_stack.push(new_table)

		for data_types_part in data_types:
			for data_types_part_part in data_types_part[0]:
				symbol_stack.top().symbols[data_types_part_part] = [None, data_types_part[1][0]]


def p_formal_parameters(p):
	'''
	formal_parameters : lparen parameter_list rparen
					  |
	'''
	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = None


def p_parameter_list(p):
	'''
	parameter_list : parameter_list semicolon pass identifiers colon typename
				   | pass identifiers colon typename
	'''
	if len(p) == 7:
		p[0] = [p[1], p[2], p[3], p[4], p[5], p[6]]
	else:
		p[0] = [p[1], p[2], p[3], p[4]]


def p_pass(p):
	'''
	pass : var
		 |
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = None


def p_comp_statement(p):
	'''
	comp_statement : begin_rule statements end_rule
	'''

	p[0] = [p[1], p[2], p[3]]


def p_begin_rule(p):
	'''
	begin_rule : begin
	'''

	global flag_procedure_function, nested_block_counter

	if not flag_procedure_function:
		nested_block_counter += 1
		new_table = SymbolTable('nested_block' + str(nested_block_counter))
		symbol_stack.push(new_table)

	p[0] = p[1]


def p_end_rule(p):
	'''
	end_rule : end
	'''

	global flag_procedure_function

	if not flag_procedure_function:
		symbol_storage.push(symbol_stack.top().name_table, symbol_stack.top())
		symbol_stack.pop()
	else:
		flag_procedure_function = False
		symbol_storage.push(symbol_stack.top().name_table, symbol_stack.top())
		symbol_stack.pop()

	p[0] = p[1]


def p_statements(p):
	'''
	statements : statements semicolon statement
			   | statement
	'''

	if len(p) == 4:
		p[0] = [p[1], p[2], p[3]]
	else:
		p[0] = p[1]


def p_statement(p):
	'''
	statement : assignment
			  | if_statement
			  | while_statement
			  | for_statement
			  | with_statement
			  | subprogram_call
			  | io_statement
			  | comp_statement
			  | empty
	'''

	if len(p) > 1:
		p[0] = p[1]
	else:
		p[0] = None


def p_assignment(p):
	'''
	assignment : variable becomes expression
			   | variable becomes sconst
	'''
	p[0] = [p[2], p[1], p[3]]


def p_if_statement(p):
	'''
	if_statement : if expression then statement if_tail
	'''
	p[0] = [p[1], p[2], p[3], p[4]]

	if p[5]:
		p[0].extend(p[5])
	else:
		p[0].append(None)


def p_if_tail(p):
	'''
	if_tail : else statement
	'''
	p[0] = [p[1], p[2]]


def p_if_tail_1(p):
	'''
	if_tail : %prec else
	'''
	p[0] = None


def p_while_statement(p):
	'''
	while_statement : while expression do statement
	'''
	p[0] = [p[1], p[2], p[3], p[4]]


def p_for_statement(p):
	'''
	for_statement : for ident becomes iter_space do statement
	'''
	p[0] = [p[1], p[2], p[4], p[5], p[6]]


def p_iter_space(p):
	'''
	iter_space : expression to expression
	'''
	p[0] = [p[2], p[1], p[3]]


def p_iter_space_1(p):
	'''
	iter_space : expression downto expression
	'''
	p[0] = [p[2], p[1], p[3]]


def p_with_statement(p):
	'''
	with_statement : with variable do statement
	'''
	p[0] = [p[1], p[2], p[3], p[4]]


def p_subprogram_call(p):
	'''
	subprogram_call : ident lparen expressions rparen
					| ident
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = [p[1], p[2], p[3], p[4]]


def p_io_statement(p):
	'''
	io_statement : read lparen read_list rparen
				 | write lparen write_list rparen
	'''
	p[0] = [p[1], p[2], p[3], p[4]]


def p_read_list(p):
	'''
	read_list : read_item
			 | read_list comma read_item
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = [p[1], p[2], p[3]]


def p_read_item(p):
	'''
	read_item : variable
	'''
	p[0] = p[1]


def p_write_list(p):
	'''
	write_list : write_item
			   | write_list comma write_item
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = [p[1], p[2], p[3]]


def p_write_item(p):
	'''
	write_item : expression
			   | string
	'''
	p[0] = p[1]


def p_empty(p):
	'empty :'
	pass


def p_error(t):
	print(f"Syntax error in input, in line {t.lineno}: '{t.value}'!")
	sys.exit()


def getTree_and_symbolTable(data_file):
	parser = yacc.yacc(debug=0)
	ast = parser.parse(data_file, tracking=False)

	symbol_storage.push(symbol_stack.top().name_table, symbol_stack.top())
	symbol_stack.pop()

	return ast, symbol_storage.storage
