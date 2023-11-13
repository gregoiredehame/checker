"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.messagess
Purpose: pyside2 message box file.
Execute: from checker import messages; messages.FUNCTION()
"""

import os
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtGui import QIcon
from kata import preference
from functools import partial

class MessageBox(QtWidgets.QMessageBox):
    def __init__(self, type, title, buttons, message_text, informative_text, detailed_text, icon):
        super().__init__()
        self.setWindowTitle(title)
        self.setIcon(QtWidgets.QMessageBox.Information)
        if message_text:
            self.setText(message_text)
        if informative_text:
            self.setInformativeText(informative_text)
        if detailed_text:
            self.setDetailedText(detailed_text)
            
        if icon and os.path.exists(icon):
            self.setIconPixmap(icon)
            q_icon = QtGui.QIcon(icon)
            self.setWindowIcon(q_icon)
            
        for i in range(len(buttons)):
            button = self.addButton(buttons[i], QtWidgets.QMessageBox.YesRole)
            
        else:
            if   type == "critical":    self.setIcon(QtWidgets.QMessageBox.Critical)
            elif type == "warning":     self.setIcon(QtWidgets.QMessageBox.Warning)
            elif type == "information": self.setIcon(QtWidgets.QMessageBox.Information)
            elif type == "question":    self.setIcon(QtWidgets.QMessageBox.Question)
            
def critical(title='Critical', buttons=[], message_text=None, informative_text=None, detailed_text=None, icon=None):
    box = MessageBox("critical", title, buttons, message_text, informative_text, detailed_text, icon)
    resp = box.exec_()
    return resp

def warning(title='Warning', buttons=[], message_text=None, informative_text=None, detailed_text=None, icon=None):
    box = MessageBox("warning", title, buttons, message_text, informative_text, detailed_text, icon)
    resp = box.exec_()
    return resp

def information(title='Information', buttons=[], message_text=None, informative_text=None, detailed_text=None, icon=None):
    box = MessageBox("information", title, buttons, message_text, informative_text, detailed_text, icon)
    resp = box.exec_()
    return resp

def question(title='Question', buttons=[], message_text=None, informative_text=None, detailed_text=None, icon=None):
    box = MessageBox("question", title, buttons, message_text, informative_text, detailed_text, icon)
    resp = box.exec_()
    return resp
    
def prompt(title='Prompt', label="", text=""):
    text, validated = QtWidgets.QInputDialog.getText(None, title, label, QtWidgets.QLineEdit.Normal, text)
    return text if validated else None