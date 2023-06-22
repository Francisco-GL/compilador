import sys
from lexicalAnalyzer import lexer


class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def __str__(self, nivel=0):
        resultado = " " * nivel + "└── (" + self.valor + ")\n"
        for hijo in self.hijos:
            resultado += hijo.__str__(nivel + 1)
        return resultado

index = 0

def analisis_sintactico(tokens):
    arbol = programa(tokens)
    return arbol

def getTokenActual(tokens):
    if index < len(tokens):
        return index
    else:
        return len(tokens)

def programa(tokens):
    # print(tokens)
    nodo_programa = Nodo("programa")
    nodo_lista_declaracion = lista_declaracion(tokens)
    nodo_programa.agregar_hijo(nodo_lista_declaracion)
    if tokens and tokens[0]['lexeme'] != "end":
        nodo_sentencia = sentencia(tokens)
        nodo_programa.agregar_hijo(nodo_sentencia)
    return nodo_programa


def lista_declaracion(tokens):
    nodo_lista_declaracion = Nodo("lista-declaracion")
    # while index < len(tokens):
    #     if tokens[index]['lexeme'] in ['int', 'float', 'void']:

    while tokens and tokens[0]['lexeme'] not in ["end", "else", "until", "then"]:
        if tokens[0]['type'] == "KEYWORD":
            nodo_declaracion = declaracion(tokens)
            nodo_lista_declaracion.agregar_hijo(nodo_declaracion)
        else:
            break
    return nodo_lista_declaracion


def declaracion(tokens):
    nodo_declaracion = Nodo("declaracion")
    if tokens[0]['type'] == "KEYWORD":
        nodo_declaracion_variable = declaracion_variable(tokens)
        nodo_declaracion.agregar_hijo(nodo_declaracion_variable)
    else:
        nodo_lista_sentencias = lista_sentencias(tokens)
        nodo_declaracion.agregar_hijo(nodo_lista_sentencias)
    return nodo_declaracion


def declaracion_variable(tokens):
    nodo_declaracion_variable = Nodo("declaracion-variable")
    if tokens[0]['type'] == "KEYWORD":
        nodo_tipo = Nodo(tokens.pop(0)['lexeme'])
        nodo_declaracion_variable.agregar_hijo(nodo_tipo)

        while tokens and tokens[0]['lexeme'] != ";":
            if tokens[0]['lexeme'] == ",":
                tokens.pop(0)  # Ignorar la coma
            else:
                nodo_variable = variable(tokens)
                nodo_declaracion_variable.agregar_hijo(nodo_variable)

        if tokens and tokens[0]['lexeme'] == ";":
            nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
            nodo_declaracion_variable.agregar_hijo(nodo_punto_y_coma)
    else:
        variable_actual = tokens[0]['lexeme']
        if verificar_declaracion(tokens, variable_actual):
            # Error: Variable no declarada previamente pero cumple con la condición de tener una declaración de tipo
            nodo_error = Nodo("ERROR: Variable no declarada previamente")
        else:
            # Error: Variable no declarada previamente ni con declaración de tipo
            nodo_error = Nodo(
                "ERROR: Variable no declarada previamente ni con declaración de tipo")

        nodo_declaracion_variable.agregar_hijo(nodo_error)

        # Se omiten los tokens hasta el siguiente punto y coma para continuar el análisis
        while tokens and tokens[0]['lexeme'] != ";":
            tokens.pop(0)
        if tokens and tokens[0]['lexeme'] == ";":
            nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
            nodo_declaracion_variable.agregar_hijo(nodo_punto_y_coma)

    return nodo_declaracion_variable


def variable(tokens):
    nodo_variable = Nodo("variable")
    nodo_identificador = Nodo(tokens.pop(0)['lexeme'])
    nodo_variable.agregar_hijo(nodo_identificador)

    if tokens and tokens[0]['lexeme'] == "=":
        nodo_asignacion = Nodo(tokens.pop(0)['lexeme'])
        nodo_variable.agregar_hijo(nodo_asignacion)

        nodo_expresion = expresion(tokens)
        nodo_variable.agregar_hijo(nodo_expresion)
    return nodo_variable


def tipo(tokens):
    nodo_tipo = None
    if tokens[0]['lexeme'] == "int" or tokens[0]['lexeme'] == "float":
        nodo_tipo = Nodo(tokens.pop(0)['lexeme'])
    return nodo_tipo


def verificar_declaracion(tokens, variable):
    for token in tokens:
        if token['lexeme'] == variable:
            index = tokens.index(token)
            # Verificar si hay una declaración de tipo antes de la variable
            for i in range(index-1, -1, -1):
                if tokens[i]['type'] == 'KEYWORD':
                    return True  # Variable declarada correctamente
            return False  # Variable no declarada previamente ni con declaración de tipo

    return False  # Variable no encontrada en los tokens


def lista_sentencias(tokens):
    nodo_lista_sentencias = Nodo("lista-sentencias")
    while tokens and tokens[0]['lexeme'] != "end" and tokens[0]['lexeme'] != "else" and tokens[0]['lexeme'] != "until":
        nodo_sentencia = sentencia(tokens)
        nodo_lista_sentencias.agregar_hijo(nodo_sentencia)
    return nodo_lista_sentencias


def sentencia(tokens):
    nodo_sentencia = Nodo("sentencia")
    print(tokens[0]['lexeme'])
    print(tokens[1]['lexeme'])
    print(tokens[3]['lexeme'])
    if tokens[0]['lexeme'] == "if":
        nodo_seleccion = seleccion(tokens)
        nodo_sentencia.agregar_hijo(nodo_seleccion)
    elif tokens[0]['lexeme'] == "while":
        nodo_iteracion = iteracion(tokens)
        nodo_sentencia.agregar_hijo(nodo_iteracion)
    elif tokens[0]['lexeme'] == "do":
        nodo_repeticion = repeticion(tokens)
        nodo_sentencia.agregar_hijo(nodo_repeticion)
    elif tokens[0]['lexeme'] == "cin":
        nodo_sent_in = sent_in(tokens)
        nodo_sentencia.agregar_hijo(nodo_sent_in)
    elif tokens[0]['lexeme'] == "cout":
        nodo_sent_out = sent_out(tokens)
        nodo_sentencia.agregar_hijo(nodo_sent_out)
    else:
        nodo_asignacion = asignacion(tokens)
        nodo_sentencia.agregar_hijo(nodo_asignacion)
    return nodo_sentencia


def asignacion(tokens):
    nodo_asignacion = Nodo("asignacion")
    if tokens and tokens[0]['type'] == 'ID':
        nodo_variable = Nodo(tokens.pop(0)['lexeme'])
        nodo_asignacion.agregar_hijo(nodo_variable)

        if tokens and tokens[0]['lexeme'] == "=":
            nodo_asignacion_op = Nodo(tokens.pop(0)['lexeme'])
            nodo_asignacion.agregar_hijo(nodo_asignacion_op)

            if tokens:
                nodo_expresion = sent_expresion(tokens)
                nodo_asignacion.agregar_hijo(nodo_expresion)

                # if tokens and tokens[0]['lexeme'] == ";":
                #     nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
                #     nodo_asignacion.agregar_hijo(nodo_punto_y_coma)

                #     # Nueva rama para asignación agregada
                #     if tokens:
                #         nueva_rama = asignacion(tokens)
                #         nodo_asignacion.agregar_hijo(nueva_rama)

                #         # Se ignora el resto de las variables en la asignación actual
                #         while tokens and tokens[0]['lexeme'] != ";":
                #             print(tokens[0]['lexeme'])
                #             tokens.pop(0)

    return nodo_asignacion


def expresion(tokens):
    nodo_expresion = Nodo("expresion")
    nodo_termino = termino(tokens)
    nodo_expresion.agregar_hijo(nodo_termino)

    while tokens and tokens[0]['lexeme'] in ['+', '-']:
        nodo_operador = Nodo(tokens.pop(0)['lexeme'])
        nodo_termino = termino(tokens)
        nodo_expresion.agregar_hijo(nodo_operador)
        nodo_expresion.agregar_hijo(nodo_termino)

    return nodo_expresion


def termino(tokens):
    nodo_termino = Nodo("termino")
    nodo_factor = factor(tokens)
    nodo_termino.agregar_hijo(nodo_factor)

    while tokens and tokens[0]['lexeme'] in ['*', '/']:
        nodo_operador = Nodo(tokens.pop(0)['lexeme'])
        nodo_factor = factor(tokens)
        nodo_termino.agregar_hijo(nodo_operador)
        nodo_termino.agregar_hijo(nodo_factor)

    return nodo_termino


def factor(tokens):
    nodo_factor = Nodo("factor")

    if tokens:
        if tokens[0]['type'] == 'ID':
            nodo_variable = Nodo(tokens.pop(0)['lexeme'])
            nodo_factor.agregar_hijo(nodo_variable)

        elif tokens[0]['type'] == 'INTEGER' or tokens[0]['type'] == 'FLOAT':
            nodo_valor = Nodo(tokens.pop(0)['lexeme'])
            nodo_factor.agregar_hijo(nodo_valor)

        elif tokens[0]['lexeme'] == "(":
            nodo_parentesis_abierto = Nodo(tokens.pop(0)['lexeme'])
            nodo_expresion = expresion(tokens)
            nodo_parentesis_cerrado = Nodo(tokens.pop(0)['lexeme'])

            nodo_factor.agregar_hijo(nodo_parentesis_abierto)
            nodo_factor.agregar_hijo(nodo_expresion)
            nodo_factor.agregar_hijo(nodo_parentesis_cerrado)

    return nodo_factor


def sent_expresion(tokens):
    nodo_sent_expresion = Nodo("sent-expresion")
    print(tokens[0]['lexeme'])
    if tokens and tokens[0]['lexeme'] != ";":
        # nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
        # nodo_sent_expresion.agregar_hijo(nodo_punto_y_coma)
        nodo_expresion = expresion(tokens)
        nodo_sent_expresion.agregar_hijo(nodo_expresion)
    else:
        nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
        nodo_sent_expresion.agregar_hijo(nodo_punto_y_coma)
    return nodo_sent_expresion


def seleccion(tokens):
    print('entre a sentencia if')
    nodo_seleccion = Nodo("seleccion")
    if tokens and tokens[0]['lexeme'] == "if":
        nodo_if = Nodo(tokens.pop(0)['lexeme'])
        nodo_seleccion.agregar_hijo(nodo_if)
        nodo_expresion = expresion(tokens)
        nodo_seleccion.agregar_hijo(nodo_expresion)
        nodo_sentencia = sentencia(tokens)
        nodo_seleccion.agregar_hijo(nodo_sentencia)
        if tokens and tokens[0]['lexeme'] == "else":
            nodo_else = Nodo(tokens.pop(0)['lexeme'])
            nodo_seleccion.agregar_hijo(nodo_else)
            nodo_sentencia = sentencia(tokens)
            nodo_seleccion.agregar_hijo(nodo_sentencia)
        if tokens and tokens[0]['lexeme'] == "end":
            nodo_end = Nodo(tokens.pop(0)['lexeme'])
            nodo_seleccion.agregar_hijo(nodo_end)
    return nodo_seleccion


def iteracion(tokens):
    nodo_iteracion = Nodo("iteracion")
    if tokens and tokens[0]['lexeme'] == "while":
        nodo_while = Nodo(tokens.pop(0)['lexeme'])
        nodo_iteracion.agregar_hijo(nodo_while)
        nodo_expresion = expresion(tokens)
        nodo_iteracion.agregar_hijo(nodo_expresion)

        if tokens and tokens[0]['lexeme'] == "do":
            nodo_do = Nodo(tokens.pop(0)['lexeme'])
            nodo_iteracion.agregar_hijo(nodo_do)
            nodo_sentencia = sentencia(tokens)
            nodo_iteracion.agregar_hijo(nodo_sentencia)

        if tokens and tokens[0]['lexeme'] == "end":
            nodo_end = Nodo(tokens.pop(0)['lexeme'])
            nodo_iteracion.agregar_hijo(nodo_end)
    return nodo_iteracion


def repeticion(tokens):
    nodo_repeticion = Nodo("repeticion")
    if tokens and tokens[0]['lexeme'] == "do":
        nodo_do = Nodo(tokens.pop(0)['lexeme'])
        nodo_repeticion.agregar_hijo(nodo_do)
        nodo_sentencia = sentencia(tokens)
        nodo_repeticion.agregar_hijo(nodo_sentencia)

        if tokens and tokens[0]['lexeme'] == "while":
            nodo_while = Nodo(tokens.pop(0)['lexeme'])
            nodo_repeticion.agregar_hijo(nodo_while)
            nodo_expresion = expresion(tokens)
            nodo_repeticion.agregar_hijo(nodo_expresion)

        if tokens and tokens[0]['lexeme'] == ";":
            nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
            nodo_repeticion.agregar_hijo(nodo_punto_y_coma)
    return nodo_repeticion


def sent_in(tokens):
    nodo_sent_in = Nodo("sent-in")
    if tokens and tokens[0]['lexeme'] == "cin":
        nodo_cin = Nodo(tokens.pop(0)['lexeme'])
        nodo_sent_in.agregar_hijo(nodo_cin)
        nodo_identificador = Nodo(tokens.pop(0)['lexeme'])
        nodo_sent_in.agregar_hijo(nodo_identificador)
        if tokens and tokens[0]['lexeme'] == ";":
            nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
            nodo_sent_in.agregar_hijo(nodo_punto_y_coma)
    return nodo_sent_in


def sent_out(tokens):
    nodo_sent_out = Nodo("sent-out")
    if tokens and tokens[0]['lexeme'] == "cout":
        nodo_cout = Nodo(tokens.pop(0)['lexeme'])
        nodo_sent_out.agregar_hijo(nodo_cout)
        nodo_expresion = expresion(tokens)
        nodo_sent_out.agregar_hijo(nodo_expresion)
        if tokens and tokens[0]['lexeme'] == ";":
            nodo_punto_y_coma = Nodo(tokens.pop(0)['lexeme'])
            nodo_sent_out.agregar_hijo(nodo_punto_y_coma)
    return nodo_sent_out


def expresion(tokens):
    nodo_expresion = Nodo("expresion")
    nodo_expresion_simple = expresion_simple(tokens)
    nodo_expresion.agregar_hijo(nodo_expresion_simple)
    if tokens and tokens[0]['lexeme'] in ["<=", "<", ">", ">=", "==", "!=", "%"]:
        nodo_relacion_op = Nodo(tokens.pop(0)['lexeme'])
        nodo_expresion.agregar_hijo(nodo_relacion_op)
        nodo_expresion_simple = expresion_simple(tokens)
        nodo_expresion.agregar_hijo(nodo_expresion_simple)
    return nodo_expresion


def expresion_simple(tokens):
    nodo_expresion_simple = Nodo("expresion-simple")
    nodo_termino = termino(tokens)
    nodo_expresion_simple.agregar_hijo(nodo_termino)
    while tokens and tokens[0]['lexeme'] in ["+", "-"]:
        nodo_suma_op = Nodo(tokens.pop(0)['lexeme'])
        nodo_expresion_simple.agregar_hijo(nodo_suma_op)
        nodo_termino = termino(tokens)
        nodo_expresion_simple.agregar_hijo(nodo_termino)
    return nodo_expresion_simple


def generateTree():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            contents = f.read()
        tokens, errors = lexer(contents)
        arbol_sintactico = analisis_sintactico(tokens)
        print(arbol_sintactico)
    else:
        print('Proporcione el archivo a analizar ...')


generateTree()
