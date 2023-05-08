from PyQt5.QtCore import QRegExp, Qt
from PyQt5 import uic
import compiler.lexicalAnalyzer as lexicalAnalyzer
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        self.reserved_words = ['main', 'if', 'then', 'else', 'end', 'do',
                               'while', 'repeat', 'until', 'cin', 'cout', 'real', 'int', 'boolean']
        self.symbols = ['++', '--', '*', '/', '%', '<', '<=', '>', '>=', '==',
                        '!=', ':=', '(', ')', '{', '}', '//', '/*', '*/', '+', '-', ',', ';']
        self.keywords_format = QTextCharFormat()
        self.keywords_format.setForeground(QColor(0, 0, 187))
        self.keywords_format.setFontWeight(QFont.Bold)
        self.numbers_format = QTextCharFormat()
        self.numbers_format.setForeground(QColor(255, 0, 0))
        self.comments_format = QTextCharFormat()
        self.comments_format.setForeground(QColor(128, 128, 128))

        self.highlighting_rules = [
            (QRegExp("\\b" + keyword + "\\b"), self.keywords_format) for keyword in self.reserved_words]
        self.highlighting_rules += [
            (QRegExp("\\b[0-9]+\\b"), self.numbers_format),  # Integer numbers
            (QRegExp("\\b[0-9]*\\.[0-9]+\\b"),
             self.numbers_format),  # Real numbers
            (QRegExp("/\\*[^*]*\\*+(?:[^*/][^*]*\\*+)*/"),
             self.comments_format),  # Multi-line comments
            (QRegExp(r"/\*.?\/"), self.comments_format)  # Single line comments
        ]

    def highlightBlock(self, text):
        for rule in self.highlighting_rules:
            expression = rule[0]
            format = rule[1]
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('IDE.ui', self)
        self.menuActions()

        self.plainTextEditCode.textChanged.connect(self.setSavedFlag)
        self.plainTextEditCode.cursorPositionChanged.connect(
            self.updateLineNumber)

        self.highlighter = Highlighter(self.plainTextEditCode.document())
        self.textEditLineNumber.setText('1')

        self.textEditLineNumber.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

    def updateLineNumber(self):
        totalLines = self.plainTextEditCode.document().blockCount()
        lineNumbers = ''.join([str(i+1) + '\n' for i in range(totalLines)])
        self.textEditLineNumber.setText(lineNumbers)

        codeScrollBarValue = self.plainTextEditCode.verticalScrollBar().value()

        self.textEditLineNumber.verticalScrollBar().setValue(codeScrollBarValue)

        lineHeight = self.textEditLineNumber.fontMetrics().height()

        cursorPos = self.plainTextEditCode.textCursor().position()
        cursorBlock = self.plainTextEditCode.document().findBlock(cursorPos)
        cursorRect = self.plainTextEditCode.cursorRect()
        cursorOffset = self.textEditLineNumber.document(
        ).documentLayout().blockBoundingRect(cursorBlock).topLeft().y()
        lineNumberTop = self.textEditLineNumber.document().documentLayout(
        ).blockBoundingRect(self.textEditLineNumber.document().firstBlock()).topLeft().y()
        cursorY = cursorOffset - lineNumberTop + cursorRect.y() + codeScrollBarValue

        lineNumberScrollBarValue = (
            cursorY / lineHeight) - ((self.textEditLineNumber.viewport().height() / 2) / lineHeight)
        lineNumberScrollBarMax = self.textEditLineNumber.verticalScrollBar().maximum()
        lineNumberScrollBarRange = lineNumberScrollBarMax - \
            self.textEditLineNumber.verticalScrollBar().minimum()
        codeScrollBarRange = self.plainTextEditCode.verticalScrollBar(
        ).maximum() - self.plainTextEditCode.verticalScrollBar().minimum()
        if lineNumberScrollBarRange == 0:
            lineNumberScrollBarValue = 0  # Asigna un valor predeterminado
        else:
            lineNumberScrollBarValue = (
                lineNumberScrollBarValue / lineNumberScrollBarRange) * codeScrollBarRange
        self.textEditLineNumber.verticalScrollBar().setValue(int(lineNumberScrollBarValue))

    def menuActions(self):
        self.actionSave_as.setShortcut("Ctrl+Shift+S")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave_all.setShortcut("Ctrl+S")
        self.actionClose.setShortcut("Ctrl+W")
        self.actionSave_as.triggered.connect(self.saveFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave_all.triggered.connect(self.saveChanges)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionLexico.triggered.connect(self.compileLexico)

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")

        if filename:
            with open(filename, "r") as f:
                content = f.read()
                self.plainTextEditCode.setPlainText(content)
            self.saved_flag = True
            self.filename = filename

    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "Archivos de texto (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write(self.plainTextEditCode.toPlainText())
                f.close()
        self.filename = filename
        print(self.filename)

    def saveChanges(self):
        if self.saved_flag:
            return
        if not self.filename:
            self.filename, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Archivos de texto (*.txt)")

        if self.filename:
            with open(self.filename, "w") as f:
                f.write(self.plainTextEditCode.toPlainText())
            self.saved_flag = True

    def setSavedFlag(self):
        self.saved_flag = False

    def closeFile(self):
        self.plainTextEditCode.clear()
        self.plainTextEditCode.setPlainText('')
        self.filename = ''

    # example -> if(x==10){compi1=x*y;} example2 -> if(x==1)x=1;else x=0;end
    def compileLexico(self):
        if not hasattr(self, 'filename'):
            print('Its a fucking new file')
            self.saveFile()
            print(f'regrese {self.filename}')
            if self.filename:
                with open(self.filename, "r") as f:
                    content = f.read()
                self.saved_flag = True
            print(f'content: {content}')
        else:
            print(self.filename)
        self.plainTextEdit_Lexico.setPlainText("")
        self.plainTextEdit_Error.setPlainText("")
        
        input_text = self.plainTextEditCode.toPlainText()
        
        tokens, errors = lexicalAnalyzer.lexer(input_text)
        
        print(errors)
        output_text = ""
        error_text = ''
        for token in tokens:
            output_text += "clave: {}, lexema: {}, fila: {}, columna: {}\n".format(
                token['type'], token['lexeme'], token['row'], token['col'])
        self.plainTextEdit_Lexico.setPlainText(output_text)

        for token in tokens:
            output_text += "clave: {}, lexema: {}, fila: {}, columna: {}\n".format(
                token['type'], token['lexeme'], token['row'], token['col'])
        for error in errors:
            error_text += "Error: {}, fila: {}, columna: {}\n".format(
                error['message'], error['row'], error['col'])
        self.plainTextEdit_Error.setPlainText(error_text)
        fileNameLength = len(self.filename.split('/'))
        fileName = self.filename.split('/')[fileNameLength - 1].split('.')[0]
        with open(f'{fileName}_lexical.txt', 'w') as f:
            f.write(output_text)
        with open(f'{fileName}_lexical_errors.txt', 'w') as f:
            f.write(error_text)
        print(output_text)
        print(f'errors -> {error_text}')


# Main function
if __name__ == "__main__":
    app = QApplication([])
    ide = IDE()
    ide.show()
    app.exec_()
