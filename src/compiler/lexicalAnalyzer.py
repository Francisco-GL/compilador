import re
import sys


def lexer(code):
    keywords = ['main', 'if', 'then', 'else', 'end', 'do', 'while',
                'repeat', 'until', 'cin', 'cout', 'real', 'int', 'boolean']
    punctuations = ['(', ')', '{', '}', ',', ';']
    operators = ['+=', '++', '--', '*', '/', '%', '<',
                 '<=', '>', '>=', '==', '!=', ':=', '=', '+', '-']

    keyword_pattern = '|'.join('\\b{}\\b'.format(kw) for kw in keywords)
    id_pattern = '[a-zA-Z][a-zA-Z0-9]*'
    int_pattern = '[0-9]+'
    real_pattern = r'\d+(?:\.\d+)*'
    comment_pattern = r"//.*"
    multiline_comment_pattern = r"/\*.*?\*/"
    operator_pattern = '|'.join(re.escape(op) for op in operators)
    punctuation_pattern = '|'.join(re.escape(p) for p in punctuations)
    ignore_pattern = r'[@%&]'

    left_multiline_comment_pattern = r"/\*"
    right_multiline_comment_pattern = r"\*/"

    pattern = '|'.join(['({})'.format(p) for p in [keyword_pattern,  id_pattern,  real_pattern,  int_pattern,
                                                   comment_pattern,  multiline_comment_pattern,
                                                   punctuation_pattern,  left_multiline_comment_pattern,
                                                   right_multiline_comment_pattern,  operator_pattern,  ignore_pattern]])
    regex = re.compile(pattern)

    tokens = []
    errors = []

    row, col = 1, 1
    inside_multiline_comment = False
    for line in code.split('\n'):
        temp_tokens = []
        temp_errors = []
        for match in regex.finditer(line):
            lexeme = match.group()

            if '/*' in lexeme:
                inside_multiline_comment = True
                continue
            if inside_multiline_comment:
                if '*/' in lexeme:
                    inside_multiline_comment = False
                continue

            if lexeme in operators:
                token_type = 'OPERATOR'

            elif match.group(1):
                token_type = 'KEYWORD'

            elif match.group(2):
                if not validName(lexeme):
                    token_type = 'INVALID_IDENTIFIER'
                    temp_errors.append({
                        'message': '{} is an invalid identifier'.format(lexeme),
                        'row': row,
                        'col': col
                    })
                else:
                    token_type = 'ID'

            elif match.group(3):
                if '.' in lexeme:
                    if validNumber(lexeme):
                        token_type = 'FLOAT'
                    else:
                        token_type = 'INVALID_FLOAT'
                        temp_errors.append({
                            'message': '{} is not a valid float'.format(lexeme),
                            'row': row,
                            'col': col
                        })
                else:
                    token_type = 'INTEGER'
            elif match.group(4):
                token_type = 'INTEGER'

            elif match.group(5):
                continue

            elif match.group(6):
                token_type = 'OPERATOR'

            elif match.group(7):
                token_type = 'PUNCTUATION'

            elif re.match(r'[@%&]', lexeme):
                token_type = 'INVALID_SYMBOL'
                temp_errors.append({
                    'message': '{} is an invalid symbol'.format(lexeme),
                    'row': row,
                    'col': col
                })

            else:
                continue

            if token_type not in ['INVALID_IDENTIFIER', 'INVALID_FLOAT', 'INVALID_SYMBOL']:
                token = {'type': token_type,
                         'lexeme': lexeme, 'row': row, 'col': col}
                temp_tokens.append(token)
            col += len(lexeme)

        tokens.extend(temp_tokens)
        errors.extend(temp_errors)

        if inside_multiline_comment:
            message = 'Expected end of multiline comment'
            temp_errors.append({'message': message, 'row': row, 'col': col})

        row += 1
        col = 1

    return tokens, errors


def validName(name):
    pattern = '^[a-zA-Z][a-zA-Z0-9]*$'
    if re.match(pattern, name):
        return True
    else:
        return False


def validNumber(expresion):
    try:
        float(expresion)
        return True
    except ValueError:
        return False


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
    print(f'errors -> {error_text}')
else:
    print('Proporcione el archivo a analizar ...')
