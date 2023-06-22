import sys
from lexicalAnalyzer import lexer


class Token:
    def __init__(self, tipo_token, valor):
        self.type = tipo_token
        self.value = valor


def createTokens(data):
    tokens = []
    for token in data:
        tokens.append(Token(token['type'], token['lexeme']))
    return tokens


class Nodo:
    def __init__(self, value=None, data=None):
        self.valor = value
        self.branchs = data if data else []

    def add_branch(self, branch):
        self.branchs.append(branch)


class SyntacticAnlyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.indice_token_actual = 0
        self.errores = []

    def analisis_sintactico(self):
        nodo_programa = self.programa()
        if self.getTokenActual().type != 'ERROR':
            self.error("Token inesperado al final del programa.")
        return nodo_programa

    def getTokenActual(self):
        if self.indice_token_actual < len(self.tokens):
            return self.tokens[self.indice_token_actual]
        else:
            return Token('ERROR', '')

    def nextToken(self):
        self.indice_token_actual += 1

    def error(self, mensaje):
        getTokenActual = self.getTokenActual()
        mensaje_error = f"Error de sintaxis: {getTokenActual.type}, valor: {getTokenActual.value}: {mensaje}"
        self.errores.append(mensaje_error)

    def programa(self):
        nodo_lista_declaracion = self.lista_declaracion()
        return Nodo('<programa>', [nodo_lista_declaracion])

    def lista_declaracion(self):
        nodo_lista_declaracion = Nodo('-lista_declaracion')
        while self.getTokenActual().type != 'ERROR':
            if self.getTokenActual().value in ['int', 'void', 'float']:
                nodo_declaracion = Nodo('-declaracion')
                nodo_decl = self.declaracion()
                nodo_lista_declaracion.add_branch(nodo_decl)
            elif self.getTokenActual().value in ['if', 'while', 'do', 'cout', 'cin', 'until']:
                nodo_declaracion = Nodo('-declaracion')
                nodo_lista_declaracion.add_branch(nodo_declaracion)
                nodo_do = self.lista_sentencias()
                nodo_declaracion.add_branch(nodo_do)
            elif self.getTokenActual().type == 'ID':
                nodo_declaracion = Nodo('-declaracion')
                nodo_lista_declaracion.add_branch(nodo_declaracion)
                nodo_do = self.lista_sentencias()
                nodo_declaracion.add_branch(nodo_do)
            self.nextToken()
        return nodo_lista_declaracion

    def declaracion(self):
        nodo_declaracion = Nodo('-declaracion')
        if self.getTokenActual().value in ['int', 'void', 'float']:
            tipo_variable = self.getTokenActual().value  # Obtener el tipo de variable
            self.nextToken()
            if self.getTokenActual().type == 'ID':
                nodo_tipo = Nodo(
                    '-tipo', [Nodo(tipo_variable)])
                nodo_declaracion_variable = Nodo(
                    '', [nodo_tipo])
                while self.getTokenActual().type == 'ID':
                    nodo_identificador = Nodo(
                        '', [Nodo(self.getTokenActual().value)])
                    nodo_declaracion_variable.add_branch(nodo_identificador)
                    self.nextToken()
                    if self.getTokenActual().value == ',':
                        self.nextToken()
                nodo_declaracion.add_branch(nodo_declaracion_variable)
                if self.getTokenActual().value == ';':
                    self.nextToken()
                    if self.getTokenActual().value in ['int', 'float', 'void']:
                        self.indice_token_actual = self.indice_token_actual - 1
                    else:
                        self.indice_token_actual = self.indice_token_actual - 1
                else:
                    self.error(
                        f"Se esperaba ';' en {self.getTokenActual().value}.")
            else:
                self.error(
                    f"Se esperaba un ID en {self.getTokenActual().value}.")
        else:
            self.error(
                f"Declaración inválida {self.getTokenActual().value}.")
        return nodo_declaracion

    def lista_sentencias(self):
        nodo_lista_sentencias = Nodo('-sentencias')
        while self.getTokenActual().type != 'ERROR' and self.getTokenActual().value != 'end':
            if self.getTokenActual().value in ['if', 'while', 'do', 'cin', 'cout', 'ID']:
                nodo_sent = Nodo('-sentencia')
                nodo_lista_sentencias.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            elif self.getTokenActual().value in ['int', 'float']:
                nodo_sent = Nodo('-declaracion')
                nodo_lista_sentencias.add_branch(nodo_sent)
                nodo_sentencia = self.declaracion()
                nodo_sent.add_branch(nodo_sentencia)
            elif self.getTokenActual().type in ['ID']:
                nodo_sent = Nodo('-sentencia')
                nodo_lista_sentencias.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            else:
                self.error(
                    f"Sentencia inválida en {self.getTokenActual().value}.")
                self.nextToken()
        return nodo_lista_sentencias

    def sentencia(self):
        if self.getTokenActual().value == 'if':
            return self.seleccion()
        elif self.getTokenActual().value == 'while':
            return self.iteracion()
        elif self.getTokenActual().value == 'do':
            return self.repeticion()
        elif self.getTokenActual().value == 'cin':
            return self.sent_in()
        elif self.getTokenActual().value == 'cout':
            return self.sent_out()
        elif self.getTokenActual().type == 'ID':
            return self.asignacion()
        else:
            self.error(
                f"Sentencia inválida en {self.getTokenActual().value}.")
            self.nextToken()

    def asignacion(self):
        nodo_asignacion = Nodo('-asignacion')
        nodo_identificador = Nodo(
            '', [Nodo(self.getTokenActual().value)])
        nodo_asignacion.add_branch(nodo_identificador)
        self.nextToken()
        if self.getTokenActual().value in ['=', '+=', '-=', '*=', '/=', '%=']:
            nodo_asignacion_op = Nodo(
                '', [Nodo(self.getTokenActual().value)])
            nodo_asignacion.add_branch(nodo_asignacion_op)
            self.nextToken()
            nodo_sent_expresion = self.sent_expresion()
            nodo_asignacion.add_branch(nodo_sent_expresion)
        else:
            self.error(
                f"Operador de asignación inválido en {self.getTokenActual().value}.")
        return nodo_asignacion

    def sent_expresion(self):
        nodo_sent_expresion = Nodo('-expresion')
        if self.getTokenActual().value != ';':
            nodo_expresion = self.expresion()
            nodo_sent_expresion.add_branch(nodo_expresion)
        if self.getTokenActual().value == ';':
            self.nextToken()
        else:
            self.error(
                f"Se esperaba ';' en {self.getTokenActual().value}.")
        return nodo_sent_expresion

    def expresion(self):
        nodo_expresion = Nodo('-expresion')
        nodo_expresion_simple_1 = self.expresion_simple()
        nodo_expresion.add_branch(nodo_expresion_simple_1)
        if self.getTokenActual().value in ['<=', '<', '>', '>=', '==', '!=']:
            nodo_relacion_op = Nodo(
                '-relacion', [Nodo(self.getTokenActual().value)])
            nodo_expresion.add_branch(nodo_relacion_op)
            self.nextToken()
            nodo_expresion_simple_2 = self.expresion_simple()
            nodo_expresion.add_branch(nodo_expresion_simple_2)
        return nodo_expresion

    def seleccion(self):
        nodo_seleccion = Nodo('-seleccion')
        self.nextToken()
        nodo_if = Nodo('if')
        nodo_seleccion.add_branch(nodo_if)
        nodo_expresion = self.expresion()
        nodo_seleccion.add_branch(nodo_expresion)
        while self.getTokenActual().type in ['ID'] or self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while', 'int', 'float']:
            nodo_sent = Nodo('-sentencia')
            nodo_seleccion.add_branch(nodo_sent)
            if self.getTokenActual().type in ['ID']:
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            if self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while']:
                nodo_sent = Nodo('-sentencia')
                nodo_seleccion.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
        if self.getTokenActual().value == 'else':
            nodo_else = Nodo('else')
            nodo_sent = Nodo('-sentencia')
            nodo_seleccion.add_branch(nodo_else)
            nodo_else.add_branch(nodo_sent)
            self.nextToken()
            nodo_sentencia_else = self.sentencia()
            nodo_sent.add_branch(nodo_sentencia_else)
        if self.getTokenActual().value == 'end':
            nodo_end = Nodo('end')
            nodo_seleccion.add_branch(nodo_end)
            self.nextToken()
        else:
            self.error(
                f"Se esperaba 'end' en {self.getTokenActual().value}.")
        return nodo_seleccion

    def iteracion(self):
        nodo_iteracion = Nodo('-iteracion')
        nodo_while = Nodo('while')
        nodo_iteracion.add_branch(nodo_while)
        self.nextToken()
        nodo_expresion = self.expresion()
        nodo_iteracion.add_branch(nodo_expresion)
        if self.getTokenActual().value == '{':
            self.nextToken()
        else:
            self.error(
                f"Se esperaba 'llave' en {self.getTokenActual().value}.")
        while self.getTokenActual().type in ['ID'] or self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while', 'int', 'float']:
            nodo_sent = Nodo('-sentencia')
            nodo_iteracion.add_branch(nodo_sent)
            if self.getTokenActual().type in ['ID']:
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            if self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while']:
                nodo_sent = Nodo('-sentencia')
                nodo_iteracion.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
        if self.getTokenActual().value == '}':
            self.nextToken()
        else:
            self.error(
                f"Se esperaba 'llave cerrada' en {self.getTokenActual().value}.")
        return nodo_iteracion

    def repeticion(self):
        nodo_repeticion = Nodo('-repeticion')
        nodo_do = Nodo('do')
        nodo_repeticion.add_branch(nodo_do)
        self.nextToken()
        while self.getTokenActual().type in ['ID'] or self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while', 'int', 'float']:
            if self.getTokenActual().type in ['ID']:
                nodo_sent = Nodo('-sentencia')
                nodo_repeticion.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            if self.getTokenActual().value in ['cout', 'cin', 'if', 'do', 'while']:
                nodo_sent = Nodo('-sentencia')
                nodo_repeticion.add_branch(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.add_branch(nodo_sentencia)
            else:
                nodo_declaracion = self.declaracion()
                nodo_repeticion.add_branch(nodo_declaracion)
        if self.getTokenActual().value == 'until':
            nodo_until = Nodo('until')
            nodo_repeticion.add_branch(nodo_until)
            self.nextToken()
            nodo_expresion = self.expresion()
            nodo_repeticion.add_branch(nodo_expresion)
            if self.getTokenActual().value == ';':
                self.nextToken()
            else:
                self.error(
                    f"Se esperaba ';' en {self.getTokenActual().value}.")
        else:
            self.error(
                f"Se esperaba 'until' en {self.getTokenActual().value}.")
        return nodo_repeticion

    def sent_in(self):
        nodo_sent_in = Nodo('')
        nodo_in = Nodo('cin')
        nodo_sent_in.add_branch(nodo_in)
        self.nextToken()
        if self.getTokenActual().type == 'ID':
            nodo_identificador = Nodo(
                '', [Nodo(self.getTokenActual().value)])
            nodo_sent_in.add_branch(nodo_identificador)
            self.nextToken()
        else:
            self.error(f"Se esperaba un ID en {self.getTokenActual().value}.")
        if self.getTokenActual().value == ';':
            self.nextToken()
        else:
            self.error(f"Se esperaba ';' en {self.getTokenActual().value}.")
        return nodo_sent_in

    def sent_out(self):
        nodo_sent_out = Nodo('')
        nodo_cout = Nodo('cout')
        nodo_sent_out.add_branch(nodo_cout)
        self.nextToken()
        nodo_expresion = self.expresion()
        nodo_sent_out.add_branch(nodo_expresion)
        if self.getTokenActual().value == ';':
            self.nextToken()
        else:
            self.error(
                f"Se esperaba ';' en {self.getTokenActual().value}.")
        return nodo_sent_out

    def expresion_simple(self):
        nodo_expresion_simple = Nodo('')
        nodo_termino_1 = self.termino()
        nodo_expresion_simple.add_branch(nodo_termino_1)
        while self.getTokenActual().value in ['+', '-', '++', '--']:
            # nodo_suma_op = Nodo(
            #     '-suma', [Nodo(self.getTokenActual().value)])
            nodo_suma_op = Nodo('',[Nodo(self.getTokenActual().value)])
            nodo_expresion_simple.add_branch(nodo_suma_op)
            self.nextToken()
            nodo_termino_2 = self.termino()
            nodo_expresion_simple.add_branch(nodo_termino_2)
        return nodo_expresion_simple

    def termino(self):
        nodo_termino = Nodo('')
        nodo_factor_1 = self.factor()
        nodo_termino.add_branch(nodo_factor_1)
        while self.getTokenActual().value in ['*', '/', '%']:
            nodo_mult_op = Nodo(
                '', [Nodo(self.getTokenActual().value)])
            nodo_termino.add_branch(nodo_mult_op)
            self.nextToken()
            nodo_factor_2 = self.factor()
            nodo_termino.add_branch(nodo_factor_2)
        return nodo_termino

    def factor(self):
        nodo_factor = Nodo('-factor')
        if self.getTokenActual().value == '(':
            self.nextToken()
            nodo_expresion = self.expresion()
            nodo_factor.add_branch(nodo_expresion)
            if self.getTokenActual().value == ')':
                self.nextToken()
            else:
                self.error(
                    f"Se esperaba ')' en {self.getTokenActual().value}.")
        elif self.getTokenActual().type in ['INTEGER', 'FLOAT']:
            nodo_numero = Nodo('', [Nodo(self.getTokenActual().value)])
            nodo_factor.add_branch(nodo_numero)
            self.nextToken()
        elif self.getTokenActual().type == 'ID':
            nodo_identificador = Nodo(
                '', [Nodo(self.getTokenActual().value)])
            nodo_factor.add_branch(nodo_identificador)
            self.nextToken()
        else:
            self.error(
                f"Factor inválido en {self.getTokenActual().value}.")
            self.nextToken()
        return nodo_factor


def generar_arbol_sintaxis(nodo, indent=''):
    arbol_str = f"{indent}{nodo.valor}\n"
    for branch in nodo.branchs:
        arbol_str += generar_arbol_sintaxis(branch, indent + '  ')
    return arbol_str


def generateTree():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            contents = f.read()
        tokens, errors = lexer(contents)
        data = createTokens(tokens)
        arbol_sintactico = SyntacticAnlyzer(data)
        sintactico = arbol_sintactico.analisis_sintactico()
        print(generar_arbol_sintaxis(sintactico))
        # Generar árbol sintáctico en un archivo de texto
        with open(f'{sys.argv[1].split(".")[0]}_tree.txt', 'w') as archivo:
            archivo.write(generar_arbol_sintaxis(sintactico))

        # Guardar errores sintácticos en otro archivo
        with open(f'{sys.argv[1].split(".")[0]}_errors_syntactic.txt', 'w') as archivo:
            for error in arbol_sintactico.errores:
                archivo.write(error + '\n')
    else:
        print('Proporcione el archivo a analizar ...')


generateTree()
