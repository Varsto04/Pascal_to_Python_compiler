import sys
import re
from lexer import tokens


class CustomError(Exception):
    pass


class SemanticAnalysis:
    def __init__(self, ast: list, symbol_table):
        del ast[0]
        self.ast = ast
        self.symbol_table = symbol_table
        self.last_data_type = ''
        self.name_table = ''
        self.scope_stack = ['global']
        self.declared_variables = [[key for key in self.symbol_table['global'].symbols]]
        self.symbol_table_stack = {}
        self.symbol_table_stack['global'] = self.symbol_table['global'].symbols
        self.constants = []
        self.functions = []
        for name_table in self.symbol_table:
            for name_ident in self.symbol_table[name_table].symbols:
                if self.symbol_table[name_table].symbols[name_ident][0] is not None:
                    self.constants.append(name_ident)
                elif self.symbol_table[name_table].symbols[name_ident][1] == 'function':
                    self.functions.append(name_ident)
        self.all_kinds_data_types_binary_operations = {
            '+': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                  ('string', 'string')),
            '-': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real')),
            '/': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real')),
            '*': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                  ('string', 'string'), ('string', 'integer'), ('integer', 'string')),
            '>': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                  ('string', 'string')),
            '<': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                  ('string', 'string')),
            '<=': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                   ('string', 'string')),
            '>=': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                   ('string', 'string')),
            '=': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                  ('string', 'string')),
            '<>': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real'),
                   ('string', 'string')),
            'and': (('boolean', 'boolean')),
            'or': (('boolean', 'boolean')),
            'mod': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real')),
            'div': (('integer', 'integer'), ('integer', 'real'), ('real', 'integer'), ('real', 'real')),
        }
        self.final_data_types = {
            ('integer', 'real'): 'real',
            ('real', 'integer'): 'real',
            ('integer', 'integer'): 'integer',
            ('real', 'real'): 'real',
            ('string', 'string'): 'string',
            ('string', 'integer'): 'string',
            ('integer', 'string'): 'string',
            ('boolean', 'boolean'): 'boolean',
        }
        self.nested_block_counter = 0
        self.counter_begin = 0
        self.counter_end = 0
        self.flag_function_procedure = False

    def __semantic_analysis(self):
        try:
            self.__dfs(self.ast)
            print('Semantic analysis completed successfully')
        except CustomError as error_message:
            print(f"{error_message}")
            sys.exit()

    def __dfs(self, ast):
        for item in ast:
            if isinstance(item, list):
                self.__dfs(item)
            else:
                if item == 'begin':
                    if self.flag_function_procedure:
                        self.flag_function_procedure = False
                    else:
                        self.counter_begin += 1
                        self.nested_block_counter += 1
                        self.name_table = 'nested_block' + str(self.nested_block_counter)
                        self.scope_stack.append(self.name_table)
                        self.declared_variables.append([key for key in self.symbol_table[self.name_table].symbols])
                        self.symbol_table_stack[self.name_table] = self.symbol_table[self.name_table].symbols
                elif item == 'end':
                    self.counter_end += 1
                    self.scope_stack.pop()
                    self.declared_variables.pop()
                    self.symbol_table_stack.popitem()
                elif item == 'function' or item == 'procedure':
                    self.flag_function_procedure = True
                    self.name_table = ast[1]
                    self.scope_stack.append(self.name_table)
                    self.declared_variables.append([key for key in self.symbol_table[self.name_table].symbols])
                    self.symbol_table_stack[self.name_table] = self.symbol_table[self.name_table].symbols
                if isinstance(item, str):
                    if re.compile(r'[A-Za-z_][\w_]*').match(item) and tokens.count(item) == 0 and \
                            item not in ['writeln', 'readln', 'True', 'False']:
                        if not any(item in array for array in self.declared_variables):
                            raise CustomError(f"NameError: name '{item}' is not defined")
                        if item in self.functions and ast[1] == '(' and ast[-1] == ')':
                            number_arguments_expected = self.__getting_data_about_variable(item)[2]
                            number_arguments_passed = self.__count_elements_without_commas(ast[2])
                            if number_arguments_expected != number_arguments_passed:
                                raise CustomError(f"TypeError: '{number_arguments_passed}' arguments were passed to the '{item}' function, but '{number_arguments_expected}' were expected")
        if ast[0] == '/' and ast[2] == 0:
            raise CustomError(f"ZeroDivisionError: division by zero in '{ast}'")
        if ast[0] in ['+', '-', '/', '*', 'and', 'or', '>', '<', '<=', '>=', '=', '<>', 'mod', 'div', 'not', ':=']:
            self.__data_type_checking(ast)

    def __count_elements_without_commas(self, arr):
        count = 0
        for element in arr:
            if isinstance(element, list):
                count += self.__count_elements_without_commas(element)
            elif element != ',':
                count += 1
        return count

    def __data_type_checking(self, ast_part):
        if ast_part[0] == ':=':
            if self.constants.count(ast_part[1]) != 0:
                raise CustomError(f"TypeError: Variable '{ast_part[1]}' is defined as a constant and cannot be changed")
            variable_type = self.__getting_data_about_variable(ast_part[1])[1]
            if variable_type != self.__define_data_type(ast_part[2]) and \
                    variable_type != 'function' and variable_type != 'procedure':
                raise CustomError(f"TypeError: The variable '{ast_part[1]}' is defined as '{variable_type}', and it is assigned '{ast_part[2]}'")
        elif ast_part[0] == 'not':
            data_type = self.__define_data_type(ast_part[1])
            if data_type != 'boolean':
                raise CustomError(f"TypeError: The 'not' operation only supports the 'boolean' type, and '{ast_part[1]}' was passed with the type '{data_type}'")
        else:
            if len(ast_part) == 2:
                data_type = self.__define_data_type(ast_part[1])
                if data_type != 'integer' and data_type != 'real':
                    raise CustomError(f"TypeError: It is impossible to apply the unary minus operation to '{ast_part[1]}', since the expression is of type '{data_type}'")
            else:
                data_type_1 = self.__define_data_type(ast_part[1])
                data_type_2 = self.__define_data_type(ast_part[2])
                if not self.all_kinds_data_types_binary_operations[ast_part[0]].count(
                        (
                        data_type_1,
                        data_type_2
                        )
                ):
                    raise CustomError(f"TypeError: Incompatible data types. Cannot perform operation between '{ast_part[1]}' and '{ast_part[2]}'")
                if ast_part[0] in ('>', '<', '>=', '<='):
                    self.last_data_type = 'boolean'
                else:
                    self.last_data_type = self.final_data_types[(data_type_1, data_type_2)]

    def __getting_data_about_variable(self, name_variable):
        for name_table in self.symbol_table:
            for name_ident in self.symbol_table[name_table].symbols:
                if name_ident == name_variable:
                    return self.symbol_table[name_table].symbols[name_ident]

    def __define_data_type(self, data):
        if isinstance(data, list):
            return self.last_data_type
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
        if str(data) == 'True' or str(data) == 'False':
            return 'boolean'
        elif re.compile(r'[A-Za-z_][\w_]*').match(str(data)) and tokens.count(str(data)) == 0 and \
                            str(data) not in ['writeln', 'readln', 'True', 'False']:
            return self.__getting_data_about_variable(str(data))[1]
        return 'string'

    def start(self):
        self.__semantic_analysis()
