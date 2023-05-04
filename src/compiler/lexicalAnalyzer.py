import re
import sys


def lexer(code):
    keywords = ['main', 'if', 'then', 'else', 'end', 'do', 'while',
                'repeat', 'until', 'cin', 'cout', 'real', 'int', 'boolean']
    punctuations = ['(', ')', '{', '}', ',', ';']
    operators = ['+', '-', '*', '/', '%', '<',
                 '<=', '>', '>=', '==', '!=', ':=']
    tokens = []
    errors = []

    # Define regex patterns
    keyword_pattern = '|'.join('\\b{}\\b'.format(kw) for kw in keywords)
    id_pattern = '[a-zA-Z][a-zA-Z0-9]*'
    int_pattern = '[0-9]+'
    real_pattern = '[0-9]*\\.[0-9]+'
    comment_pattern = '//[^\n]*|/\\*.*?\\*/'
    operator_pattern = '|'.join(re.escape(op) for op in operators)
    punctuation_pattern = '|'.join(re.escape(p) for p in punctuations)

    # Combine all patterns into a single regex
    pattern = '|'.join(['({})'.format(p) for p in [keyword_pattern, id_pattern, int_pattern,
                       real_pattern, comment_pattern, operator_pattern, punctuation_pattern]])
    regex = re.compile(pattern)

    # Start tokenizing
    row, col = 1, 1
    for line in code.split('\n'):
        for match in regex.finditer(line):
            lexeme = match.group()
            if match.group(1):  # Keyword
                token_type = 'KEYWORD'
            elif match.group(2):  # Identifier
                token_type = 'ID'
            elif match.group(3):  # Integer number
                token_type = 'NUMBER'
            elif match.group(4):  # Real number
                token_type = 'NUMBER'
            elif match.group(5):  # Comment
                continue  # Ignore comments
            elif match.group(6):  # Operator
                token_type = 'OPERATOR'
            elif match.group(7):  # Punctuation
                token_type = 'PUNCTUATION'
            else:  # Invalid token
                errors.append({'lexeme': lexeme, 'row': row, 'col': col})

            token = {'type': token_type,
                     'lexeme': lexeme, 'row': row, 'col': col}
            tokens.append(token)

            # Update row and col
            col += len(lexeme)
        row += 1
        col = 1

    return tokens, errors


if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        contents = f.read()
    tokens, errors = lexer(contents)
    output_text = ''
    error_text = ''
    for token in tokens:
        output_text += "clave: {}, lexema: {}, fila: {}, columna: {}\n".format(
            token['type'], token['lexeme'], token['row'], token['col'])
    for error in errors:
        error_text += "Error: {}, fila: {}, columna: {}\n".format(
            error['message'], error['row'], error['col'])
    with open(f'{sys.argv[1].split(".")[0]}_lexical.txt', 'w') as f:
        f.write(output_text)
    with open(f'{sys.argv[1].split(".")[0]}_lexical_errors.txt', 'w') as f:
        f.write(error_text)
    print(output_text)
    print(error_text)
else:
    print('Proporcione el archivo a analizar ...')

