import re
from three_address_code_generation import ThreeAddressCodeInstruction
import struct


class AssemblerCodeGeneration:
    def __init__(self, three_address_code: dict, name_file: str, symbol_table: dict):
        self.three_address_code = three_address_code
        self.name_file = name_file
        self.symbol_table = symbol_table
        self.storage_offsets_data_integer_type = {}
        self.storage_offsets_data_real_type = {}
        self.offset_counter_rbp = 0
        self.LCPI_counter = 0
        self.type_storage_temporary_variables = {}
        self.storage_register_operation = {
            ('integer', 'real', '+'): 'addsd',
            ('real', 'integer', '+'): 'addsd',
            ('real', 'real', '+'): 'addsd',
            ('integer', 'integer', '+'): 'add',
            ('integer', 'real', '*'): 'mulsd',
            ('real', 'integer', '*'): 'mulsd',
            ('real', 'real', '*'): 'mulsd',
            ('integer', 'integer', '*'): 'imul',
            ('integer', 'real', '-'): 'subsd',
            ('real', 'integer', '-'): 'subsd',
            ('real', 'real', '-'): 'subsd',
            ('integer', 'integer', '-'): 'sub',
            ('integer', 'real', '/'): 'divsd',
            ('real', 'integer', '/'): 'divsd',
            ('real', 'real', '/'): 'divsd',
            ('integer', 'integer', '/'): 'idiv',
        }
        self.function_greater = '\n\ngreater:\n\tcmp rsi, rdx\n\tsetg al\n\tret'
        self.function_less = '\n\ngreater:\n\tcmp rsi, rdx\n\tsetl al\n\tret'
        self.function_less_or_equal = '\n\ngreater:\n\tcmp rsi, rdx\n\tsetle al\n\tret'
        self.function_greater_or_equal = '\n\ngreater:\n\tcmp rsi, rdx\n\tsetge al\n\tret'
        self.function_equal = '\n\ngreater:\n\tcmp rsi, rdx\n\tsete al\n\tret'
        self.function_not_equal = '\n\ngreater:\n\tcmp rsi, rdx\n\tsetne al\n\tret'

    def __generate(self):
        with open(f'{self.name_file}.asm', 'w') as file:
            data_section = '\n\nsection .data'
            file.write('section .text\n\tglobal _start')

            for key, value in self.three_address_code.items():
                if key == 'main':
                    file.write(f'\n\n_start:')
                else:
                    file.write(f'\n\n_{key}:')
                file.write(f'\n\tpush rbp')
                file.write(f'\n\tmov rbp, rsp')
                self.offset_counter_rbp = 0
                self.storage_offsets_data_integer_type = {}
                self.offset_counter_rbp = 0
                self.storage_offsets_data_real_type = {}
                i = 0
                for key2, value2 in self.three_address_code[key].items():
                    if i != 0:
                        file.write(f'\n_{key2}:')
                    i += 1
                    for value2_part in value2:
                        if value2_part[0] == 'goto':
                            file.write(f'\n\tjmp _{value2_part[1]}')
                        if value2_part[1] == ':=' and re.compile(r't\d+$').match(value2_part[0]) and \
                                value2_part[-1] == 'tmp':
                            if isinstance(value2_part[2], ThreeAddressCodeInstruction):
                                if value2_part[2].op == '+' or value2_part[2].op == '*' or value2_part[2].op == '-':
                                    arg1_type = self.__define_data_type(value2_part[2].arg1)
                                    arg2_type = self.__define_data_type(value2_part[2].arg2)
                                    if arg1_type:
                                        if arg1_type == 'integer':
                                            file.write(f'\n\tmov eax, {value2_part[2].arg1}')
                                        elif arg1_type == 'real':
                                            data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                            binary = struct.pack('f', value2_part[2].arg1)
                                            hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                            data_section += f'\n\tdq {hex_value}'
                                            file.write(f'\n\tmovss xmm0, [LCPI0_{self.LCPI_counter}]')
                                            self.LCPI_counter += 1
                                    else:
                                        arg1_type = self.__getting_data_about_variable(value2_part[2].arg1)
                                        if arg1_type:
                                            if arg1_type[1] == 'integer':
                                                file.write(f'\n\tmov eax, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg1]}]')
                                            elif arg1_type[1] == 'real':
                                                file.write(f'\n\tmovsd xmm0, qword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg1]}]')
                                        else:
                                            pass

                                    arg1_type = self.__define_data_type(value2_part[2].arg1)
                                    if arg2_type:
                                        if arg1_type:
                                            if arg1_type == arg2_type:
                                                if arg2_type == 'integer':
                                                    operation = self.storage_register_operation[(arg1_type, arg2_type, value2_part[2].op)]
                                                    file.write(f'\n\t{operation} eax, {value2_part[2].arg2}')
                                                    self.type_storage_temporary_variables[value2_part[0]] = 'integer'
                                                if arg2_type == 'real':
                                                    data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                    binary = struct.pack('f', value2_part[2].arg2)
                                                    hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                    data_section += f'\n\tdq {hex_value}'
                                                    operation = self.storage_register_operation[
                                                        (arg1_type, arg2_type, value2_part[2].op)]
                                                    file.write(f'\n\t{operation} xmm0, [LCPI0_{self.LCPI_counter}]')
                                                    self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                    self.LCPI_counter += 1
                                            else:
                                                if arg1_type == 'real' and arg2_type == 'integer':
                                                    file.write(f'\n\tcvtsi2sd xmm1, {value2_part[2].arg2}')
                                                    operation = self.storage_register_operation[
                                                        (arg1_type, arg2_type, value2_part[2].op)]
                                                    file.write(f'\n\t{operation} xmm0, xmm1')
                                                    self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                if arg1_type == 'integer' and arg2_type == 'real':
                                                    data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                    binary = struct.pack('f', value2_part[2].arg2)
                                                    hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                    data_section += f'\n\tdq {hex_value}'
                                                    file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                    file.write(f'\n\tmovsd xmm0, [LCPI0_{self.LCPI_counter}]')
                                                    operation = self.storage_register_operation[
                                                        (arg1_type, arg2_type, value2_part[2].op)]
                                                    file.write(f'\n\t{operation} xmm0, xmm1')
                                                    self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                    self.LCPI_counter += 1
                                        else:
                                            arg1_type = self.__getting_data_about_variable(value2_part[2].arg1)
                                            if arg1_type:
                                                if arg1_type[1] == arg2_type:
                                                    if arg2_type == 'integer':
                                                        operation = self.storage_register_operation[
                                                            (arg1_type[1], arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} eax, {value2_part[2].arg2}')
                                                        self.type_storage_temporary_variables[
                                                            value2_part[0]] = 'integer'
                                                    if arg2_type == 'real':
                                                        data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                        binary = struct.pack('f', value2_part[2].arg2)
                                                        hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                        data_section += f'\n\tdq {hex_value}'
                                                        operation = self.storage_register_operation[
                                                            (arg1_type[1], arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, [LCPI0_{self.LCPI_counter}]')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                        self.LCPI_counter += 1
                                                else:
                                                    if arg1_type[1] == 'real' and arg2_type == 'integer':
                                                        file.write(f'\n\tcvtsi2sd xmm1, {value2_part[2].arg2}')
                                                        operation = self.storage_register_operation[
                                                            (arg1_type[1], arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                    elif arg1_type[1] == 'integer' and arg2_type == 'real':
                                                        data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                        binary = struct.pack('f', value2_part[2].arg2)
                                                        hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                        data_section += f'\n\tdq {hex_value}'
                                                        file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                        file.write(f'\n\tmovsd xmm0, [LCPI0_{self.LCPI_counter}]')
                                                        operation = self.storage_register_operation[
                                                            (arg1_type[1], arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                        self.LCPI_counter += 1
                                            else:
                                                if re.compile(r't\d+$').match(value2_part[2].arg1):
                                                    temporary_variable_type = self.type_storage_temporary_variables[value2_part[2].arg1]
                                                    if temporary_variable_type == 'real' and arg2_type == 'real':
                                                        data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                        binary = struct.pack('f', value2_part[2].arg2)
                                                        hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                        data_section += f'\n\tdq {hex_value}'
                                                        operation = self.storage_register_operation[
                                                            (temporary_variable_type, arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, [LCPI0_{self.LCPI_counter}]')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                        self.LCPI_counter += 1
                                                    elif temporary_variable_type == 'real' and arg2_type == 'integer':
                                                        file.write(f'\n\tcvtsi2sd xmm1, {value2_part[2].arg2}')
                                                        operation = self.storage_register_operation[
                                                            (temporary_variable_type, arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                    elif temporary_variable_type == 'integer' and arg2_type == 'real':
                                                        data_section += f'\nLCPI0_{self.LCPI_counter}:'
                                                        binary = struct.pack('f', value2_part[2].arg2)
                                                        hex_value = hex(int.from_bytes(binary, byteorder='little'))
                                                        data_section += f'\n\tdq {hex_value}'
                                                        file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                        file.write(f'\n\tmovsd xmm0, [LCPI0_{self.LCPI_counter}]')
                                                        operation = self.storage_register_operation[
                                                            (temporary_variable_type, arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                        self.LCPI_counter += 1
                                                    elif temporary_variable_type == 'integer' and arg2_type == 'integer':
                                                        operation = self.storage_register_operation[
                                                            (temporary_variable_type, arg2_type, value2_part[2].op)]
                                                        file.write(f'\n\t{operation} eax, {value2_part[2].arg2}')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'integer'
                                    else:
                                        arg2_type = self.__getting_data_about_variable(value2_part[2].arg2)
                                        if arg2_type:
                                            if arg1_type:
                                                if arg1_type == arg2_type[1]:
                                                    if arg2_type[1] == 'integer':
                                                        operation = self.storage_register_operation[
                                                            (arg1_type, arg2_type[1], value2_part[2].op)]
                                                        file.write(f'\n\t{operation} eax, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                        self.type_storage_temporary_variables[
                                                            value2_part[0]] = 'integer'
                                                    if arg2_type[1] == 'real':
                                                        operation = self.storage_register_operation[
                                                            (arg1_type, arg2_type[1], value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                else:
                                                    if arg1_type == 'real' and arg2_type[1] == 'integer':
                                                        file.write(f'\n\tcvtsi2sd xmm1, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                        operation = self.storage_register_operation[
                                                            (arg1_type, arg2_type[1], value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                                    if arg1_type == 'integer' and arg2_type[1] == 'real':
                                                        file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                        file.write(f'\n\tmovsd xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                        operation = self.storage_register_operation[
                                                            (arg1_type, arg2_type[1], value2_part[2].op)]
                                                        file.write(f'\n\t{operation} xmm0, xmm1')
                                                        self.type_storage_temporary_variables[value2_part[0]] = 'real'
                                            else:
                                                arg1_type = self.__getting_data_about_variable(value2_part[2].arg1)
                                                if arg1_type:
                                                    if arg1_type[1] == arg2_type[1]:
                                                        if arg2_type[1] == 'integer':
                                                            operation = self.storage_register_operation[
                                                                (arg1_type[1], arg2_type[1], value2_part[2].op)]
                                                            file.write(f'\n\t{operation} eax, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'integer'
                                                        if arg2_type[1] == 'real':
                                                            operation = self.storage_register_operation[
                                                                (arg1_type[1], arg2_type[1], value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                    else:
                                                        if arg1_type[1] == 'real' and arg2_type[1] == 'integer':
                                                            file.write(f'\n\tcvtsi2sd xmm1, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                            operation = self.storage_register_operation[
                                                                (arg1_type[1], arg2_type[1], value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, xmm1')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                        elif arg1_type[1] == 'integer' and arg2_type[1] == 'real':
                                                            file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                            file.write(f'\n\tmovsd xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                            operation = self.storage_register_operation[
                                                                (arg1_type[1], arg2_type[1], value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, xmm1')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                else:
                                                    if re.compile(r't\d+$').match(value2_part[2].arg1):
                                                        temporary_variable_type = self.type_storage_temporary_variables[
                                                            value2_part[2].arg1]
                                                        if temporary_variable_type == 'real' and arg2_type[1] == 'real':
                                                            operation = self.storage_register_operation[
                                                                (temporary_variable_type, arg2_type[1], value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                        elif temporary_variable_type == 'real' and arg2_type[1] == 'integer':
                                                            file.write(f'\n\tcvtsi2sd xmm1, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                            operation = self.storage_register_operation[
                                                                (temporary_variable_type, arg2_type[1],
                                                                 value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, xmm1')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                        elif temporary_variable_type == 'integer' and arg2_type[1] == 'real':
                                                            file.write(f'\n\tcvtsi2sd xmm1, eax')
                                                            file.write(f'\n\tmovsd xmm0, dword [rbp - {self.storage_offsets_data_real_type[value2_part[2].arg2]}]')
                                                            operation = self.storage_register_operation[
                                                                (temporary_variable_type, arg2_type[1],
                                                                 value2_part[2].op)]
                                                            file.write(f'\n\t{operation} xmm0, xmm1')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'real'
                                                        elif temporary_variable_type == 'integer' and arg2_type[1] == 'integer':
                                                            operation = self.storage_register_operation[
                                                                (temporary_variable_type, arg2_type[1],
                                                                 value2_part[2].op)]
                                                            file.write(f'\n\t{operation} eax, dword [rbp - {self.storage_offsets_data_integer_type[value2_part[2].arg2]}]')
                                                            self.type_storage_temporary_variables[
                                                                value2_part[0]] = 'integer'
                                        else:
                                            pass

                        elif value2_part[1] == ':=':
                            variable_type = self.__getting_data_about_variable(value2_part[0])
                            if variable_type:
                                if variable_type[1] == 'integer':
                                    variable_value_data_type = self.__define_data_type(value2_part[2])
                                    if variable_value_data_type:
                                        file.write(f'\n\tmov dword [rbp - {self.offset_counter_rbp}], {value2_part[2]}')
                                    else:
                                        file.write(f'\n\tmov dword [rbp - {self.offset_counter_rbp}], eax')
                                    self.storage_offsets_data_integer_type[value2_part[0]] = self.offset_counter_rbp
                                    self.offset_counter_rbp += 4
                                if variable_type[1] == 'real':
                                    variable_value_data_type = self.__define_data_type(value2_part[2])
                                    if variable_value_data_type:
                                        file.write(f'\n\tmovss dword [rbp - {self.offset_counter_rbp}], {value2_part[2]}')
                                    else:
                                        file.write(f'\n\tmovss dword [rbp - {self.offset_counter_rbp}], xmm0')
                                    self.storage_offsets_data_real_type[value2_part[0]] = self.offset_counter_rbp
                                    self.offset_counter_rbp += 4
                                else:
                                    pass
            file.write(data_section)

    def __define_data_type(self, data):
        if isinstance(data, float):
            return "real"
        if isinstance(data, int):
            return "integer"
        if str(data) == 'True' or str(data) == 'False':
            return 'boolean'
        if re.compile(r'^"(.*)"$').match(data):
            return 'string'
        return False

    def __getting_data_about_variable(self, name_variable):
        for name_table in self.symbol_table:
            for name_ident in self.symbol_table[name_table].symbols:
                if name_ident == name_variable:
                    return self.symbol_table[name_table].symbols[name_ident]

    def start(self):
        self.__generate()
