class SymbolTable:
    def __init__(self, name_table: str):
        self.symbols = {}
        self.name_table = name_table

    def insert_symbol(self, name, value):
        self.symbols[name] = value

    def lookup_symbol(self, name):
        return self.symbols.get(name, None)


class SymbolTableStack:
    def __init__(self):
        self.stack = []

    def push(self, symbol_table):
        self.stack.append(symbol_table)

    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            return None

    def top(self):
        if len(self.stack) > 0:
            return self.stack[-1]
        else:
            return None


class SymbolTableStorage:
    def __init__(self):
        self.storage = {}

    def push(self, name_table, symbol_table):
        self.storage[name_table] = symbol_table
