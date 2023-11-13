"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.printter
Purpose: printter core pyside2 standalone interface file.
Execute: from checker import printter; printter.FUNCTION()
"""

from PySide2 import QtCore, QtGui, QtWidgets
import inspect

GREY = QtGui.QColor(43, 43, 43)


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self._code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self._code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._code_editor.lineNumberAreaPaintEvent(event)


class PrintTextEdit(QtWidgets.QPlainTextEdit):
    is_first = False
    pressed_keys = list()

    indented = QtCore.Signal(object)
    unindented = QtCore.Signal(object)
    commented = QtCore.Signal(object)
    uncommented = QtCore.Signal(object)

    def __init__(self):
        super(PrintTextEdit, self).__init__()

        self.indented.connect(self.do_indent)
        self.unindented.connect(self.undo_indent)
        self.commented.connect(self.do_comment)
        self.uncommented.connect(self.undo_comment)

    def clear_selection(self):
        pos = self.textCursor().selectionEnd()
        self.textCursor().movePosition(pos)

    def get_selection_range(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return 0, 0

        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()

        cursor.setPosition(start_pos)
        start_line = cursor.blockNumber()
        cursor.setPosition(end_pos)
        end_line = cursor.blockNumber()

        return start_line, end_line

    def remove_line_start(self, string, line_number):
        cursor = QtGui.QTextCursor(
            self.document().findBlockByLineNumber(line_number))
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = cursor.selectedText()
        if text.startswith(string):
            cursor.removeSelectedText()
            cursor.insertText(text.split(string, 1)[-1])

    def insert_line_start(self, string, line_number):
        cursor = QtGui.QTextCursor(
            self.document().findBlockByLineNumber(line_number))
        self.setTextCursor(cursor)
        self.textCursor().insertText(string)

    def keyPressEvent(self, event):
        """
        Extend the key press event to create key shortcuts
        """
        self.is_first = True
        self.pressed_keys.append(event.key())
        start_line, end_line = self.get_selection_range()

        # enter commands
        if event.key() == QtCore.Qt.Key_Enter:
            return
        # indent event
        if event.key() == QtCore.Qt.Key_Tab and (end_line - start_line):
            lines = range(start_line, end_line+1)
            self.indented.emit(lines)
            return

        # un-indent event
        elif event.key() == QtCore.Qt.Key_Backtab:
            lines = range(start_line, end_line+1)
            self.unindented.emit(lines)
            return

        super(PrintTextEdit, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.is_first:
            self.process_multi_keys(self.pressed_keys)

        self.is_first = False
        if self.pressed_keys:
            self.pressed_keys.pop()
        
        # auto close "
        if event.key() == QtCore.Qt.Key_ParenLeft:
            self.textCursor().insertText(')')
            self.moveCursor(QtGui.QTextCursor.Left)
            return
        # auto close '
        if event.key() == QtCore.Qt.Key_Apostrophe:
            self.textCursor().insertText("'") 
            self.moveCursor(QtGui.QTextCursor.Left)
            return
        # auto close (
        if event.key() == QtCore.Qt.Key_QuoteDbl:
            self.textCursor().insertText('"')
            self.moveCursor(QtGui.QTextCursor.Left)
            return
        
        if event.key() == QtCore.Qt.Key_Return:
            block_line = self.textCursor().blockNumber() - 1
            text_line = self.document().findBlockByLineNumber(block_line).text()
            for i in range(len(text_line) - len(text_line.lstrip())):
                self.textCursor().insertText('\t')
                
            if text_line.endswith(':'):
                self.textCursor().insertText('\t')    
            return
            
        super(PrintTextEdit, self).keyReleaseEvent(event)

    def process_multi_keys(self, keys):
        # toggle comments indent event
        if keys == [QtCore.Qt.Key_Control, QtCore.Qt.Key_Slash]:
            pass

    def do_indent(self, lines):
        for line in lines:
            self.insert_line_start('\t', line)

    def undo_indent(self, lines):
        for line in lines:
            self.remove_line_start('\t', line)

    def do_comment(self, lines):
        for line in lines:
            pass

    def undo_comment(self, lines):
        for line in lines:
            pass


class Editor(PrintTextEdit):
    def __init__(self):
        super(Editor, self).__init__()
        self.line_number_area = LineNumberArea(self)

        self.font = QtGui.QFont()
        self.font.setFamily("Consolas")
        self.font.setStyleHint(QtGui.QFont.Monospace)
        self.font.setPointSize(9)
        self.setFont(self.font)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        
        self.tab_size = 2
        self.setTabStopWidth(self.tab_size * self.fontMetrics().width(' '))
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num *= 0.1
            digits += 1

        space = 30 + self.fontMetrics().width('9') * digits
        return space
    
    def resizeEvent(self, e):
        super(Editor, self).resizeEvent(e)
        cr = self.contentsRect()
        width = self.line_number_area_width()
        rect = QtCore.QRect(cr.left(), cr.top(), width, cr.height())
        self.line_number_area.setGeometry(rect)

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), GREY)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number)
                painter.setPen(GREY.lighter(250))
                width = self.line_number_area.width() - 25
                height = self.fontMetrics().height()
                painter.drawText(0, top, width, height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            width = self.line_number_area.width()
            self.line_number_area.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def highlight_current_line(self):
        extra_selections = list()
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = GREY.lighter(135)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)