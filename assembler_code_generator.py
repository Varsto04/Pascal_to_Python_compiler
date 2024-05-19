class AssemblerCodeGeneration:
    def __init__(self, three_address_code: dict, name_file: str, symbol_table: dict):
        self.three_address_code = three_address_code
        self.name_file = name_file
        self.symbol_table = symbol_table

    def __generate(self):
        with open(f'{self.name_file}.asm', 'w') as file:
            data_section = '.data\n'
            const_section = '.const\n'
            for name_table in self.symbol_table:
                for name_ident in self.symbol_table[name_table].symbols:
                    type_variable = self.symbol_table[name_table].symbols[name_ident][1]
                    value_variable = self.symbol_table[name_table].symbols[name_ident][0]
                    if type_variable != 'function' and value_variable == None:
                        if type_variable == 'integer' or type_variable == 'real':
                            data_section += f'\t{name_ident} dq 0\n'
                        elif type_variable == 'boolean':
                            data_section += f'\t{name_ident} db 0\n'
                        elif type_variable == 'string':
                            data_section += f'\t{name_ident} .asciz ""\n'
                    elif value_variable != None:
                        if type_variable == 'integer' or type_variable == 'real':
                            const_section += f'\t{name_ident} dq {value_variable}\n'
                        elif type_variable == 'boolean':
                            const_section += f'\t{name_ident} db {value_variable}\n'
                        elif type_variable == 'string':
                            const_section += f'\t{name_ident} .asciz {value_variable}\n'
            file.write(data_section)
            file.write(const_section)

        # for key, value in three_address_code.items():

    def start(self):
        self.__generate()
