from lexer import getScanner
from parser import getTree_and_symbolTable
import sys
import copy
from semantic_analysis import SemanticAnalysis
from three_address_code_generation import ThreeAddressCodeGeneration
from three_address_code_optimisation import Optimisation


def reading_data_file(address):
    with open(address, 'r') as file:
        data_file = file.read()
        if data_file.count('end.') != 0 and len(data_file) > 4:
            data_file = data_file.split('end.')[0] + 'end.'
    return data_file


def build_tree(root):
    return '\n'.join(_build_tree(root))


def _build_tree(node):
    if not isinstance(node, list):
        yield str(node)
        return

    values = [_build_tree(n) for n in node]
    if len(values) == 1:
        yield from build_lines('──', '  ', values[0])
        return

    start, *mid, end = values
    yield from build_lines('┬─', '│ ', start)
    for value in mid:
        yield from build_lines('├─', '│ ', value)
    yield from build_lines('└─', '  ', end)


def build_lines(first, other, values):
    yield first + next(values)
    for value in values:
        yield other + value


def main():
    name_file = str(input('File name: '))
    data_file = reading_data_file(name_file)

    print()
    print('----Receiving tokens from Lex----')
    tokens = getScanner(data_file)
    tokens_print = copy.copy(tokens)
    for token in tokens_print:
        print(token)

    ast, symbol_table = getTree_and_symbolTable(data_file)
    print()
    print('----Retrieving Symbol Tables----')
    for name_table in symbol_table:
        print(symbol_table[name_table].symbols, name_table)
    constants = {}
    functions = []
    for name_table in symbol_table:
        for name_ident in symbol_table[name_table].symbols:
            if symbol_table[name_table].symbols[name_ident][0] is not None:
                constants[name_ident] = symbol_table[name_table].symbols[name_ident][0]
            elif symbol_table[name_table].symbols[name_ident][1] == 'function':
                functions.append(name_ident)

    print()
    print('----Retrieving AST----')
    print(ast)
    print(build_tree(ast))

    print()
    print('----Semantic Analysis----')
    semantic_analysis = SemanticAnalysis(ast, symbol_table, list(constants.keys()), functions)
    semantic_analysis.start()

    print()
    print('----Receiving three-address code----')
    three_address_code_generation = ThreeAddressCodeGeneration(ast, functions, constants)
    three_address_code = three_address_code_generation.start()
    function_call_tracking = three_address_code_generation.function_call_tracking
    for key, value in three_address_code.items():
        print(key)
        for key2, value2 in value.items():
            print("\t", key2)
            for value_part in value2:
                print("\t", "\t", value_part)

    print()
    print('----Optimised three-address code----')
    three_address_code_optimisation = Optimisation(three_address_code, function_call_tracking)
    three_address_code_optimisation.start()


if __name__ == '__main__':
    main()
