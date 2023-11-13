"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.highlighter
Purpose: checker highlighter pyside2 standalone interface file.
Execute: from checker import highlighter; highlighter.FUNCTION()
"""

from PySide2 import QtCore, QtGui, QtWidgets

def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    if type == 'plain text':
        _foreground = QtGui.QColor(212,212,212)
    elif type == 'selected text':
        _foreground = QtGui.QColor(255,255,255)
    elif color == 'keyword': 
        _foreground = QtGui.QColor(197,134,192)
    elif color == 'builtin': 
        _foreground = QtGui.QColor(220,220,170)
    elif color == 'string':
        _foreground = QtGui.QColor(206,145,120)
    elif color == 'docstring':
        _foreground = QtGui.QColor(128,128,128)
    elif color == 'number':
        _foreground = QtGui.QColor(181,206,168)
    elif color == 'class':
        _foreground = QtGui.QColor(102,201,135)
    elif color == 'method':
        _foreground = QtGui.QColor(86,156,214)
    elif color == 'comment':
        _foreground = QtGui.QColor(96,139,78)
    elif color == 'decorator':
        _foreground = QtGui.QColor(102,201,135)
    elif color == 'operator':
        _foreground = QtGui.QColor(212,212,212)
    elif color == 'self':
        _foreground = QtGui.QColor(156,220,254)
    elif color == 'command':
        _foreground = QtGui.QColor(86,156,214)
    elif color == 'valid':
        _foreground = QtGui.QColor(86,214,86)
    elif color == 'unvalid':
        _foreground = QtGui.QColor(214,86,86)
        

    else:
        _foreground = QtGui.QColor()
        _foreground.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_foreground)
    
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('keyword', 'bold'),
    'builtin': format('builtin'),
    'operator': format('operator'),
    'decorator': format('decorator','italic'),
    'brace': format('darkGray'),
    'class': format('class'),
    'method': format('method'),
    'string': format('string'),
    'docstring': format('docstring', 'italic'),
    'comment': format('comment'),
    'self': format('self'),
    'number': format('number'),
    'command': format('command'),
    'valid': format('valid', 'bold'),
    'unvalid': format('unvalid', 'bold'),
}


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """
    Syntax highlighter for the Python language.
    """
    valid = ['SUCCESS']
    unvalid = ['ERROR']
    
    
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        # Multi-line strings (expression, flag, style)
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['docstring'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['docstring'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['valid'])
                  for w in PythonHighlighter.valid]
        rules += [(r'\b%s\b' % w, 0, STYLES['unvalid'])
                  for w in PythonHighlighter.unvalid]    
                           
        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),
            
            # '.' followed by an identifier
            (r'\.(\w+)\(', 1, STYLES['command']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['method']),
            
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['class']),


            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),
            
            # From '@' until a newline
            (r'@[^\n]*', 0, STYLES['decorator']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """
        Apply syntax highlighting to the given block of text.
        """
        self.tripleQuoutesWithinStrings = []
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            if index >= 0:
                # if there is a string we check
                # if there are some triple quotes within the string
                # they will be ignored if they are matched again
                if expression.pattern() in [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]:
                    innerIndex = self.tri_single[0].indexIn(text, index + 1)
                    if innerIndex == -1:
                        innerIndex = self.tri_double[0].indexIn(text, index + 1)

                    if innerIndex != -1:
                        tripleQuoteIndexes = range(innerIndex, innerIndex + 3)
                        self.tripleQuoutesWithinStrings.extend(tripleQuoteIndexes)

            while index >= 0:
                # skipping triple quotes within strings
                if index in self.tripleQuoutesWithinStrings:
                    index += 1
                    expression.indexIn(text, index)
                    continue

                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """
        Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # skipping triple quotes within strings
            if start in self.tripleQuoutesWithinStrings:
                return False
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
