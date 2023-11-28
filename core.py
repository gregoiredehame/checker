"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.core
Purpose: checker core pyside2 standalone interface file.
Execute: from checker import core; core.FUNCTION()
"""

from functools import partial
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

import time
import importlib
import logging
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import utils, commands, printter, highlighter

class CheckerManager(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """ project manager interface class.
            Args:
                //
    """
    title = "Model Checker"
    version = "0.2.3"
    studio = 'Floating Rock'
    
    def __init__(self, parent=None):
        super(CheckerManager, self).__init__(parent=parent)
        
        self.clr_process = '222, 165, 91'
        self.clr_positive = '73, 103, 123'
        self.clr_negative = '153, 102, 102'
        self.all_run_actions = {}
        self.all_fix_actions = {}
        
        self.icons = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        self.setObjectName(f"{CheckerManager.title}")
        self.setWindowTitle(f"{CheckerManager.title} {CheckerManager.version}")
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(-10, -10, -10, -10)
        
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setContentsMargins(0,0,0,0)
        self.main_frame.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        self.grid_layout = QtWidgets.QGridLayout(self.main_frame)
        self.grid_layout.setContentsMargins(-10, 25, -10, -10)
        
        self.menu_bar = QtWidgets.QMenuBar(self.main_frame)
        self.preferences = self.menu_bar.addMenu("Preferences")
        self.preferences.setTearOffEnabled(True)
        
        self.method_1 = QtWidgets.QAction("Selected Objects")
        self.method_2 = QtWidgets.QAction("Selected Top Node")
        self.method_3 = QtWidgets.QAction("Scene")
        self.method_1.setCheckable(True)
        self.method_2.setCheckable(True)
        self.method_3.setCheckable(True)
        self.method_group = QtWidgets.QActionGroup(self.preferences)
        self.method_group.addAction(self.method_1)
        self.method_group.addAction(self.method_2)
        self.method_group.addAction(self.method_3)
        self.method_3.setChecked(True)
        self.verbose =  QtWidgets.QAction("Verbose", checkable=True)
        self.verbose.setChecked(True)
        self.success =  QtWidgets.QAction("Show Success", checkable=True)
        self.errors =  QtWidgets.QAction("Show Errors", checkable=True)
        self.nodes =  QtWidgets.QAction("Show Nodes", checkable=True)
        self.time =  QtWidgets.QAction("Show Time", checkable=True)
        self.success.setChecked(True)
        self.errors.setChecked(True)
        self.nodes.setChecked(True)
        self.time.setChecked(True)
        
        self.show_failed =  QtWidgets.QAction("Selection Warnings", checkable=True)
        self.show_failed.setChecked(True)
        self.auto_erase =  QtWidgets.QAction("Auto Erase Report", checkable=True)
        self.auto_erase.setChecked(True)
        
        self.preferences.addAction(self.method_1)
        self.preferences.addAction(self.method_2)
        self.preferences.addAction(self.method_3)
        self.preferences.addSection('Results')
        self.preferences.addAction(self.verbose)
        self.preferences.addAction(self.success)
        self.preferences.addAction(self.errors)
        self.preferences.addAction(self.nodes)
        self.preferences.addAction(self.time)
        self.preferences.addSection('Options')
        self.preferences.addAction(self.show_failed)
        self.preferences.addAction(self.auto_erase)

        self.bar_widget = QtWidgets.QWidget()
        self.bar_layout = QtWidgets.QGridLayout(self.bar_widget)
        self.bar_layout.setContentsMargins(0,0,0,0)
        self.bar_layout.setRowStretch(0, 0)
        self.bar_layout.setRowStretch(1, 0)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(10)
        self.progress_count = QtWidgets.QLabel("[1/2]")
        self.progress_label = QtWidgets.QLabel("Showing Progress")
        self.progress_bar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.progress_count.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.progress_label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.progress_count.setMinimumHeight(20)
        self.progress_label.setMinimumHeight(20)
        self.bar_layout.addWidget(self.progress_bar, 0 , 0)
        self.bar_layout.addWidget(self.progress_count, 1 , 0, QtCore.Qt.AlignLeft)
        self.bar_layout.addWidget(self.progress_label, 1 , 0, QtCore.Qt.AlignRight)
        
        self.left_scroll_panel = QtWidgets.QWidget()
        self.left_scroll_panel.setContentsMargins(2,2,2,2)
        self.left_scroll_panel_layout = QtWidgets.QFormLayout(self.left_scroll_panel)
        self.left_scroll_panel_layout.setContentsMargins(10,10,15,10)
        self.left_scroll_area = QtWidgets.QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        self.left_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.left_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.left_scroll_area.setWidget(self.left_scroll_panel)
        
        module = utils.get_module_dictionnary(commands)
        for key in list(module.keys()):
            if key != 'Tagger':
                key_frame = QtWidgets.QFrame()
                key_frame.setContentsMargins(0,5,0,0)
                key_frame.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
                key_layout = QtWidgets.QFormLayout(key_frame)
                key_layout.addWidget(self.group_box(key, module[key]))
                self.left_scroll_panel_layout.addWidget(key_frame)
        
        self.print_editor = printter.Editor()
        self.print_editor.setReadOnly(True)
        highlighter.PythonHighlighter(self.print_editor.document())
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.left_scroll_area)
        self.splitter.addWidget(self.print_editor)
        self.splitter.setHandleWidth(8)
        
        self.bot_widget = QtWidgets.QWidget()
        self.bot_layout = QtWidgets.QGridLayout(self.bot_widget)
        self.bot_layout.setContentsMargins(0,0,0,0)
        self.run_button = QtWidgets.QPushButton("Run")
        self.fix_button = QtWidgets.QPushButton("Fix")
        self.cln_button = QtWidgets.QPushButton("Clean Report")
        self.cln_button.clicked.connect(partial(self.clean_report))
        self.run_button.clicked.connect(partial(self.run_all))
        self.fix_button.clicked.connect(partial(self.fix_all))
        self.run_button.setMinimumHeight(25)
        self.fix_button.setMinimumHeight(25)
        self.cln_button.setMinimumHeight(25)
        self.bot_layout.addWidget(self.run_button, 0 , 0)
        self.bot_layout.addWidget(self.fix_button, 0 , 1)
        self.bot_layout.addWidget(self.cln_button, 0 , 2)
        
        #self.grid_layout.addWidget(self.bar_widget, 0 ,0, QtCore.Qt.AlignTop)
        self.grid_layout.addWidget(self.splitter)
        self.grid_layout.addWidget(self.bot_widget, 2, 0, QtCore.Qt.AlignBottom)
        self.grid_layout.setRowStretch(0,1)
        self.grid_layout.setRowStretch(1,0)
        #self.grid_layout.setRowStretch(2,0)
        
        self.main_layout.addWidget(self.main_frame)
        self.setLayout(self.main_layout)

        
    def group_box(self, title=None, childrens=None):
        frame = QtWidgets.QFrame()
        frame.setContentsMargins(10,10,10,10)
        frame.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        box = QtWidgets.QGroupBox(f"  {title}  ")
        vbox = QtWidgets.QVBoxLayout(frame)
        vbox.setSpacing(1)
        vbox.addStretch(1)
        
        section_run, section_fix = {}, {}
        section_run[title] = []
        section_fix[title] = []
        sections = {}
        
        radios_widget = QtWidgets.QWidget()
        radios_layout = QtWidgets.QGridLayout(radios_widget)
        radios_layout.setContentsMargins(0,0,0,10)
        activate = QtWidgets.QRadioButton("All")
        desactivate = QtWidgets.QRadioButton("None")
        presets = QtWidgets.QRadioButton(CheckerManager.studio)
        presets.setChecked(True)
        radios_layout.addWidget(activate, 0 , 1, QtCore.Qt.AlignCenter) 
        radios_layout.addWidget(desactivate, 0 , 2, QtCore.Qt.AlignCenter) 
        radios_layout.addWidget(presets, 0 , 3, QtCore.Qt.AlignCenter) 
        vbox.addWidget(radios_widget)
        for children in childrens:
            if children.endswith('_get'):
                is_default_value = True if children in commands.tag._dict['checked'] else False
                children_widget = QtWidgets.QWidget()
                children_widget.setStyleSheet("background-color: rgb(73, 73, 73);")
                children_widget.setMaximumHeight(35)
                children_layout = QtWidgets.QGridLayout(children_widget)
                children_layout.setContentsMargins(-10,0,0,0)
                children_label = QtWidgets.QLabel(utils.method_to_title(children))
                children_label.setMinimumWidth(125)
                children_label.setMinimumHeight(25)
                children_label.setEnabled(is_default_value)
                children_layout.addWidget(children_label, 0 , 0, QtCore.Qt.AlignLeft)
                children_layout.setColumnStretch(0, 1)
                children_check = QtWidgets.QCheckBox()
                children_check.setChecked(is_default_value)
                children_layout.addWidget(children_check, 0 , 1, QtCore.Qt.AlignLeft)
                children_run = QtWidgets.QPushButton("Run")
                children_run.setMinimumWidth(40)
                children_run.setMinimumHeight(25)
                children_run.setEnabled(is_default_value)
                children_run.setStyleSheet("background-color: rgb(93, 93, 93);")
                children_layout.addWidget(children_run, 0 , 2, QtCore.Qt.AlignLeft)
                children_sel = QtWidgets.QPushButton("Select Error Nodes")
                children_sel.setToolTip('')
                children_sel.setMinimumHeight(25)
                children_sel.setStyleSheet("background-color: rgb(93, 93, 93);")
                children_sel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                children_sel.setEnabled(False)
                children_sel.clicked.connect(partial(self.select_error_nodes, children_sel))
                children_layout.setColumnStretch(3, 1)
                children_layout.addWidget(children_sel, 0 , 3)
                if children.replace('_get','_fix') in childrens:
                    children_fix = QtWidgets.QPushButton("Fix")
                    children_fix.setStyleSheet("background-color: rgb(93, 93, 93);")
                    children_fix.setEnabled(False)
                    section_fix[title].append([children.replace('_get','_fix'), children_widget, children_run, children_sel, children_fix])
                    children_fix.clicked.connect(partial(self.single_fix, clsmethod=title, methods=[children.replace('_get','_fix'), children_widget, children_run, children_sel, children_fix], sections=section_fix[title]))
                    children_fix.setMinimumWidth(40)
                else:
                    children_fix = QtWidgets.QLabel("")
                    children_fix.setEnabled(False)
                    children_fix.setMinimumWidth(44)
                children_fix.setMinimumHeight(25)
                children_layout.addWidget(children_fix, 0 , 4, QtCore.Qt.AlignLeft)  
                section_run[title].append([children, children_check, children_widget, children_run, children_sel, children_fix])
                children_run.clicked.connect(partial(self.single_run, clsmethod=title, methods=[children, children_check, children_widget, children_run, children_sel, children_fix], sections=section_run[title]))
                sections[children] = [children_widget, children_label, children_check, children_run, children_sel, children_fix]
                vbox.addWidget(children_widget)
                children_check.stateChanged.connect(partial(self.change_check_status, widget=children_widget, label=children_label, check=children_check, run=children_run, sel=children_sel, fix=children_fix))
                self.all_run_actions[children] = [title, children, children_check, children_widget, children_run, children_sel, children_fix]
                self.all_fix_actions[children] = [title, children.replace('_get','_fix'), children_widget, children_run, children_sel, children_fix]
                
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QGridLayout(buttons_widget)
        buttons_layout.setContentsMargins(0,10,0,0)
        run_button = QtWidgets.QPushButton(f"Run {title}")
        fix_button = QtWidgets.QPushButton(f"Fix {title}")
        run_button.clicked.connect(partial(self.section_run, clsmethod=title, methods=section_run[title], sections=sections))
        fix_button.clicked.connect(partial(self.section_fix, clsmethod=title, methods=section_fix[title], sections=sections))
        run_button.setStyleSheet("background-color: rgb(93, 93, 93);")
        fix_button.setStyleSheet("background-color: rgb(93, 93, 93);")
        run_button.setMinimumHeight(25)
        fix_button.setMinimumHeight(25)
        run_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        fix_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        buttons_layout.addWidget(run_button, 0 , 1) 
        buttons_layout.addWidget(fix_button, 0 , 2) 
        vbox.addWidget(buttons_widget)
        
        activate.toggled.connect(lambda x:self.change_section_status(activate=activate, desactivate=desactivate, presets=presets, sections=sections, run_button=run_button, fix_button=fix_button))
        desactivate.toggled.connect(lambda x:self.change_section_status(activate=activate, desactivate=desactivate, presets=presets, sections=sections, run_button=run_button, fix_button=fix_button))
        presets.toggled.connect(lambda x:self.change_section_status(activate=activate, desactivate=desactivate, presets=presets, sections=sections, run_button=run_button, fix_button=fix_button))
        
        box.setLayout(vbox)
        return box    
    
    
    def change_check_status(self, event, widget, label, check, run, sel, fix):
        if event == 0: 
            [x.setEnabled(False) for x in [label, run, sel, fix]]
            widget.setStyleSheet("background-color: rgb(73, 73, 73);")
        else:
            [x.setEnabled(True)  for x in [label, run]]
    
    
    def change_section_status(self, activate, desactivate, presets, sections, run_button, fix_button):
        for key in list(sections.keys()):
            widget, label, check, run, sel, fix = sections[key]
            widget.setStyleSheet("background-color: rgb(73, 73, 73);")
            if activate.isChecked():
                [x.setEnabled(True)  for x in [label, run]]; [x.setEnabled(False) for x in [sel, fix]]; check.setChecked(True)       
            elif desactivate.isChecked():
                [x.setEnabled(False) for x in [label, run, sel, fix]]; check.setChecked(False)
            elif presets.isChecked():
                if key in commands.tag._dict['checked']:
                    [x.setEnabled(True)  for x in [label, run]]; [x.setEnabled(False) for x in [sel, fix]]; check.setChecked(True)
                else:
                    [x.setEnabled(False) for x in [label, run, sel, fix]]; check.setChecked(False)       
            
        
    def single_run(self, clsmethod=None, methods=None, sections=None):
        if self.auto_erase.isChecked():
            self.clean_report()

        commands_reload = importlib.reload(commands)
        method, checkbox, widget, run_button, sel_button, fix_button = methods
        class_import = getattr(commands_reload, clsmethod)
        if hasattr(class_import, method):
            class_import = class_import()
            if checkbox.isChecked():
                widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                start_time = time.perf_counter()
                func = getattr(class_import, method)
                errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                if len(errors) == 0:
                    widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                    [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                    sel_button.setToolTip('')
                else:
                    widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                    [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                    sel_button.setToolTip(str(errors))
                
                self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))
    
    
    def single_fix(self, clsmethod=None, methods=None, sections=None):
        if self.auto_erase.isChecked():
            self.clean_report()
            
        commands_reload = importlib.reload(commands)
        method, widget, run_button, sel_button, fix_button = methods
        class_import = getattr(commands_reload, clsmethod)
        if hasattr(class_import, method):
            class_import = class_import()
            if fix_button.isEnabled():
                widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                start_time = time.perf_counter()
                func = getattr(class_import, method)
                errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                if len(errors) == 0:
                    widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                    [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                    sel_button.setToolTip('')
                else:
                    widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                    [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                    sel_button.setToolTip(str(errors))
                    
                self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))
                    

    def section_run(self, clsmethod=None, methods=None, sections=None):
        if self.auto_erase.isChecked():
            self.clean_report()
            
        commands_reload = importlib.reload(commands)
        for method, checkbox, widget, run_button, sel_button, fix_button in methods:
            class_import = getattr(commands_reload, clsmethod)
            if hasattr(class_import, method):
                class_import = class_import()
                if checkbox.isChecked():
                    widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                    start_time = time.perf_counter()
                    func = getattr(class_import, method)
                    errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                    if len(errors) == 0:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                        [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip('')
                    else:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                        [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip(str(errors))
                        
                    self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))
                
   
    def section_fix(self, clsmethod=None, methods=None, sections=None):
        if self.auto_erase.isChecked():
            self.clean_report()
            
        commands_reload = importlib.reload(commands)
        for method, widget, run_button, sel_button, fix_button in methods:
            class_import = getattr(commands_reload, clsmethod)
            if hasattr(class_import, method):
                class_import = class_import()
                if fix_button.isEnabled():
                    widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                    start_time = time.perf_counter()
                    func = getattr(class_import, method)
                    errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                    if len(errors) == 0:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                        [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip('')
                    else:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                        [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip(str(errors))
                        
                    self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))       
                        
    
    def run_all(self):
        if self.auto_erase.isChecked():
            self.clean_report()
            
        commands_reload = importlib.reload(commands)  
        for key in list(self.all_run_actions.keys()):
            clsmethod, method, checkbox, widget, run_button, sel_button, fix_button = self.all_run_actions[key]
            class_import = getattr(commands_reload, clsmethod)
            if hasattr(class_import, method):
                class_import = class_import()
                if checkbox.isChecked():
                    widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                    start_time = time.perf_counter()
                    func = getattr(class_import, method)
                    errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                    if len(errors) == 0:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                        [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip('')
                    else:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                        [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip(str(errors))
                        
                    self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))
                
        
    def fix_all(self):
        if self.auto_erase.isChecked():
            self.clean_report()
            
        commands_reload = importlib.reload(commands)    
        for key in list(self.all_fix_actions.keys()):
            clsmethod, method, widget, run_button, sel_button, fix_button = self.all_fix_actions[key]
            class_import = getattr(commands_reload, clsmethod)
            if hasattr(class_import, method):
                class_import = class_import()
                if fix_button.isEnabled():
                    widget.setStyleSheet(f"background-color: rgb({self.clr_process});")
                    start_time = time.perf_counter()
                    func = getattr(class_import, method)
                    errors = utils.noneAsList(func(verbose=self.verbose.isChecked(), method=self.query_method()))
                    if len(errors) == 0:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_positive});")
                        [bttn.setEnabled(False) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip('')
                    else:
                        widget.setStyleSheet(f"background-color: rgb({self.clr_negative});")
                        [bttn.setEnabled(True) for bttn in [sel_button, fix_button]]
                        sel_button.setToolTip(str(errors))
                        
                    self.add_print_editor(function=utils.method_to_title(method), errors=errors, time=(time.perf_counter() - start_time))
    
    
    def select_error_nodes(self, *args):
        utils.select_from_string(args[0].toolTip(), verbose=self.show_failed.isChecked())


    def add_print_editor(self, function=None, errors=None, time=None):
        if len(errors) == 0:
            if self.success.isChecked():
                if self.time.isChecked():
                    self.print_editor.appendPlainText(f"[ SUCCESS ] {function} (%fs)"%time)
                else:
                    self.print_editor.appendPlainText(f"[ SUCCESS ] {function}")
        else:
            if self.errors.isChecked():
                if self.time.isChecked():
                    self.print_editor.appendPlainText(f"[ ERROR ] {function} (%fs)"%time)
                else:
                    self.print_editor.appendPlainText(f"[ ERROR ] {function}")
                if self.nodes.isChecked():    
                    [self.print_editor.appendPlainText(f" - '{error}'") for error in errors]
    
    
    def query_method(self):
        if   self.method_1.isChecked(): return 'selection'
        elif self.method_2.isChecked(): return 'topnode'
        elif self.method_3.isChecked(): return 'scene'
        
        
    def clean_report(self):
        self.print_editor.clear()