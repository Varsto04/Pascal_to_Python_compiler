import re
import sys


class ThreeAddressCodeInstruction:
    def __init__(self, op, arg1, arg2=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        if self.arg2:
            return f'{self.arg1} {self.op} {self.arg2}'
        else:
            if self.arg2 == 0:
                return f'{self.arg1} {self.op} {self.arg2}'
            else:
                return f'{self.op} {self.arg1}'

    def __repr__(self):
        return self.__str__()


class CustomError(Exception):
    pass


class ThreeAddressCodeGeneration:
    def __init__(self, ast: list):
        self.ast = ast
        self.l_junction_counter = 0
        self.general_l_junction_counter = 0
        self.t_counter = 0
        self.three_address_code = {}
        self.three_address_code_part = []
        self.three_address_code_part_copy = []
        self.name_function_procedure = ''
        self.flag_function_procedure = False

    def __dfs(self, ast):
        if ast[0] in ['if', 'for']:
            l_junction_counter = self.l_junction_counter
        for index, item in enumerate(ast):
            if ast[0] == 'if':
                if index == 2:
                    self.__inserting_data_into_L_block(f'L{l_junction_counter}')
                    self.l_junction_counter += 4
                if index == 4:
                    self.__inserting_data_into_L_block(f'L{l_junction_counter + 1}')
                    self.three_address_code_part.append(['goto', f'L{l_junction_counter + 3}'])
                    self.__inserting_data_into_L_block(f'L{self.l_junction_counter}')
                    self.l_junction_counter += 1
                    self.three_address_code_part.append(['goto', f'L{self.l_junction_counter}'])
                    self.__inserting_data_into_L_block(f'L{l_junction_counter + 2}')
            if ast[0] == 'for':
                if index == 3:
                    self.three_address_code_part.append(
                        [ast[1], ':=', ast[2][1]])
                    self.__inserting_data_into_L_block(f'L{l_junction_counter}')
                    self.l_junction_counter += 2
            if isinstance(item, list):
                ast[index] = self.__dfs(item)
            else:
                pass
        if ast[0] in ['+', '-', '/', '*', 'mod', 'div'] and len(ast) == 3:
            if ((isinstance(ast[1], str) and ast[1].count('"') != 0) or isinstance(ast[1], float) or isinstance(ast[1], int)) \
                    and ((isinstance(ast[2], str) and ast[2].count('"') != 0) or isinstance(ast[2], float) or isinstance(ast[2], int)):
                return self.__optimization(ast)
        if ast[0] == '/' and ast[2] in [0, '0']:
            raise CustomError(f"ZeroDivisionError: division by zero in '{ast}'")
        if ast[0] in ['+', '-', '/', '*', 'mod', 'div'] and len(ast) == 3:
            self.t_counter += 1
            time_variable_t = f't{self.t_counter}'
            self.three_address_code_part.append(
                [time_variable_t, ':=', ThreeAddressCodeInstruction(ast[0], ast[1], ast[2])])
            return time_variable_t
        if ast[0] in ['=', '>', '<', '>=', '<='] and len(ast) == 3:
            self.t_counter += 1
            time_variable_t = f't{self.t_counter}'
            self.three_address_code_part.append(
                [time_variable_t, ':=', ThreeAddressCodeInstruction(ast[0], ast[1], ast[2])])
            return time_variable_t
        if ast[0] in ['not', '-'] and len(ast) == 2:
            self.t_counter += 1
            time_variable_t = f't{self.t_counter}'
            self.three_address_code_part.append(
                [time_variable_t, ':=', ThreeAddressCodeInstruction(ast[0], ast[1])])
            return time_variable_t
        if ast[0] in [':=']:
            self.three_address_code_part.append(
                [ast[1], ':=', ast[2]])
            self.t_counter += 1
        if ast[0] == 'if':
            self.__inserting_data_into_L_block(f'L{l_junction_counter + 2}')
            self.three_address_code[f'L{l_junction_counter}'].append(
                ['if', ast[1], 'goto', f'L{l_junction_counter + 1}'])
            self.three_address_code[f'L{l_junction_counter}'].append(
                ['goto', f'L{l_junction_counter + 2}'])
            self.three_address_code[f'L{l_junction_counter + 1}'].append(
                ['goto', f'L{l_junction_counter + 4}'])
            self.three_address_code_part.append(['goto', f'L{l_junction_counter + 3}'])
            self.__inserting_data_into_L_block(f'L{self.l_junction_counter}')
            self.l_junction_counter += 1
        if ast[0] == 'for':
            self.__inserting_data_into_L_block(f'L{self.l_junction_counter}')
            self.three_address_code[f'L{self.l_junction_counter}'].append(
                ['if', ast[1], '<=', ast[2][2], 'goto', f'L{l_junction_counter + 1}'])
            self.three_address_code_part.append(['goto', f'L{l_junction_counter + 2}'])
            self.__inserting_data_into_L_block(f'L{l_junction_counter + 1}')
        if ast[0] == 'function' or ast[0] == 'procedure':
            self.flag_function_procedure = True
            self.name_function_procedure = ast[1]
        if ast[0] == 'begin':
            if self.flag_function_procedure:
                self.three_address_code[self.name_function_procedure] = self.three_address_code_part
                self.flag_function_procedure = False
                self.three_address_code_part = []
            else:
                if len(self.three_address_code_part) > 0:
                    self.__inserting_data_into_L_block(f'L{self.l_junction_counter}')

        return ast

    def __inserting_data_into_L_block(self, name_L_block: str):
        try:
            self.three_address_code[name_L_block].extend(self.three_address_code_part)
            self.three_address_code_part = []
        except KeyError:
            self.three_address_code[name_L_block] = self.three_address_code_part
            self.three_address_code_part = []

    def __optimization(self, ast_part):
        if not ast_part[0] in ['mod', 'div']:
            return eval(f'{ast_part[1]} {ast_part[0]} {ast_part[2]}')
        else:
            if ast_part[0] == 'mod':
                return eval(f'{ast_part[1]} % {ast_part[2]}')
            else:
                return eval(f'{ast_part[1]} // {ast_part[2]}')

    def start(self):
        try:
            self.ast = self.__dfs(self.ast)
            print(self.three_address_code)
        except CustomError as error_message:
            print(f"{error_message}")
            sys.exit()