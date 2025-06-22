# Pascal to Python compiler
# RU
## Этот проект представляет собой компилятор для подмножества языка Pascal, написанный на языке Python. Компилятор разработан с использованием библиотеки PLY для лексического и синтаксического анализа.

### Функциональные возможности

Компилятор выполняет следующие функции:
- Лексический анализ
- Синтаксический анализ
- Семантический анализ
- Оптимизация кода
- Генерация промежуточного представления (трехадресный код)
- Генерация ассемблерного кода для x86-64

### Структура файлов

| Файл                                 | Описание                                               |
|--------------------------------------|--------------------------------------------------------|
| `main.py`                            | Запуск программы                                       |
| `lexer.py`                           | Регулярные выражения для создания токенов              |
| `parser.py`                          | Грамматика для создания AST из токенов                 |
| `character_map.py`                   | Таблица символов                                       |
| `semantic_analysis.py`               | Семантический анализ                                   |
| `three_address_code_generation.py`   | Генерация трехадресного кода из AST                    |
| `three_address_code_optimisation.py` | Оптимизация кода                                       |
| `assembler_code_generator.py`        | Генерация ассемблерного кода из трехадресного кода     |

### Процесс компиляции

Компиляция включает следующие этапы:

1. **Лексический анализ** (`lexer.py`): 
   - Определение токенов с помощью регулярных выражений.
   - Создание лексического анализатора.

2. **Синтаксический анализ** (`parser.py`):
   - Определение грамматики языка.
   - Создание узлов AST.
   - Построение AST из токенов.

3. **Таблица символов** (`character_map.py`):
   - Создание и хранение таблиц символов во время синтаксического анализа.

4. **Семантический анализ** (`semantic_analysis.py`):
   - Проверка семантической правильности программы.

5. **Генерация промежуточного представления** (`three_address_code_generation.py`):
   - Рекурсивный обход AST для генерации трехадресного кода.

6. **Оптимизация кода** (`three_address_code_optimisation.py`):
   - Слияние простых математических выражений.
   - Удаление неиспользуемых функций и кода.
   - Замена констант.

7. **Генерация ассемблерного кода** (`assembler_code_generator.py`):
   - Преобразование трехадресного кода в ASM x86-64.

### Особенности входного языка

- Операторные скобки.
- Игнорируется индентация.
- Комментарии любой длины.
- Поддержка функций.
- Операторы: присваивание (:=), арифметические (*, /, +, -, >, <, >=, <=, =, <>), логические (and, or, not), условные (if, if-else), циклы (while, for), базовый вывод (строковый литерал, переменная).
- Типы: 32-битные целые, 32-битные с плавающей запятой, строки, булевы.

### Выходные данные

При успешной компиляции компилятор генерирует файл с ассемблерным кодом для x86-64, использующим инструкции SSE/SSE2.

---

# EN

## This project is a compiler for a subset of the Pascal programming language, implemented in Python. It utilizes the PLY library for lexical and syntactic analysis.

### Features

The compiler performs the following functions:
- Lexical analysis
- Syntax analysis
- Semantic analysis
- Code optimization
- Generation of intermediate representation (three-address code)
- Generation of x86-64 assembly code

### File Structure

| File                                 | Description                                            |
|--------------------------------------|--------------------------------------------------------|
| `main.py`                            | Program launch                                         |
| `lexer.py`                           | Regular expressions for token creation                 |
| `parser.py`                          | Grammar for creating AST from tokens                   |
| `character_map.py`                   | Symbol table                                           |
| `semantic_analysis.py`               | Semantic analysis                                      |
| `three_address_code_generation.py`   | Generation of three-address code from AST              |
| `three_address_code_optimisation.py` | Code optimization                                      |
| `assembler_code_generator.py`        | Generation of assembly code from three-address code    |

### Compilation Process

The compilation process involves the following stages:

1. **Lexical Analysis** (`lexer.py`):
   - Token definition using regular expressions.
   - Creation of the lexical analyzer.

2. **Syntax Analysis** (`parser.py`):
   - Definition of the language grammar.
   - Creation of AST nodes.
   - Building the AST from tokens.

3. **Symbol Table** (`character_map.py`):
   - Creation and storage of symbol tables during syntax analysis.

4. **Semantic Analysis** (`semantic_analysis.py`):
   - Checking the semantic correctness of the program.

5. **Intermediate Representation Generation** (`three_address_code_generation.py`):
   - Recursive traversal of the AST to generate three-address code.

6. **Code Optimization** (`three_address_code_optimisation.py`):
   - Merging simple mathematical expressions.
   - Removing unused functions and code.
   - Replacing constants.

7. **Assembly Code Generation** (`assembler_code_generator.py`):
   - Converting three-address code to x86-64 assembly code.

### Input Language Features

- Statement brackets.
- Indentation is ignored.
- Comments of any length.
- Support for function calls.
- Operators: assignment (:=), arithmetic (*, /, +, -, >, <, >=, <=, =, <>), logical (and, or, not), conditional (if, if-else), loops (while, for), basic output (string literal, variable).
- Types: 32-bit integers, 32-bit floats, strings, booleans.

### Output

Upon successful compilation, the compiler generates an assembly code file for x86-64, utilizing SSE/SSE2 instructions.
