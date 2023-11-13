"""
KATA. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.utils
Purpose: checker interface utilities file for maya operations.
Execute: from checker import utils; utils.FUNCTION()
"""

try:
    import maya.cmds as cmds
    import maya.api.OpenMaya as om2
except: pass    
    
import sys
import inspect
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import messages, progress

def is_in_maya():
    try:
        import maya.cmds as cmds
        return True
    except: 
        return False
    
def get_python_version():
    return sys.version_info[0]     

def get_checker_version():
    from . import core
    return core.CheckerManager.version
    
def delete_workspace_control(name):
    if cmds.workspaceControl(name, query=True, exists=True): 
        cmds.deleteUI(name, ctl=True)
    if cmds.workspaceControlState(name, query=True, exists=True): 
        cmds.workspaceControlState(name, r=True)
    if cmds.window(name, query=True, exists=True): 
        cmds.deleteUI(name)

def get_module_dictionnary(module):
    dict = {}
    for class_string in module.__dict__:
        if callable(getattr(module, class_string)):
            for class_member in inspect.getmembers(module, inspect.isclass):
                if class_string == class_member[0]:
                    methods = []
                    for method_string in class_member[1].__dict__:
                        if callable(getattr(class_member[1], method_string)):
                            if method_string != "__init__": methods.append(method_string)
                    dict[class_string] = methods
    return dict    

def method_to_title(string=None):
    string = string.replace('_get','').replace('_fix','')
    if string is not None and len(string)>0:
        try:
            A = string
            B = ' '.join(A.rsplit('_'))
            C = ' '.join(B.rsplit('-'))
            D = ' '.join(C.rsplit('/'))
            E = ' '.join(D.rsplit('"'))
            F = ' '.join(E.rsplit('  '))
            G = ' '.join(F.rsplit(','))
            string = []
            [string.append(x.capitalize()) for x in G.rsplit(' ')]
            return ' '.join(string)
        except:
            return string
    else: return str(string)  
    

def noneAsList(s=None):
    return [] if s is None else s
    

def select_from_string(string=None, verbose=None):
    array, unknown = [], []
    for node in string.strip('][').split(', '):
        node = node.replace("'","")
        if cmds.objExists(node): array.append(node)
        else:                    unknown.append(node)
        
    if array:       
        cmds.select(clear=True)
        cmds.select(array)
    
    if verbose and unknown:
        nodes_message = ''
        for u in unknown:
            nodes_message = nodes_message + f"{u}\n"
        confirmation = messages.warning(title='Warning', buttons=['Confirm'], message_text='Some nodes does not exists anymore.\nUnable to select all nodes.', detailed_text=nodes_message)


def is_mesh(object=None):
    try: 
        dag = om2.MGlobal.getSelectionListByName(object).getDagPath(0)
        if dag.apiType() == om2.MFn.kTransform:
            try: dag.extendToShape()
            except: pass
        if dag.apiType() == om2.MFn.kMesh: return True
    except: return False
            
def is_transform(object=None):
    try: 
        dag = om2.MGlobal.getSelectionListByName(object).getDagPath(0)
        if dag.apiType() == om2.MFn.kTransform:
            try: dag.extendToShape(); return False
            except: return True
    except: return False
    
def mesh_array(method='scene'):
    array = []
    if method == 'scene':
        for transform in cmds.ls(typ="transform"):
            if is_mesh(transform) and cmds.nodeType(transform) == 'transform': array.append(transform)
    if method == 'selection':
        for transform in cmds.ls(sl=1):
            if is_mesh(transform) and cmds.nodeType(transform) == 'transform':  array.append(transform)
    if method == 'topnode':
        if cmds.ls(sl=1):
            for transform in noneAsList(cmds.listRelatives(cmds.ls(sl=1)[0], allDescendents=True)):
                if is_mesh(transform) and cmds.nodeType(transform) == 'transform':  array.append(transform)
            if is_mesh(cmds.ls(sl=1)[0]) and cmds.nodeType(cmds.ls(sl=1)[0]) == 'transform':  array.append(cmds.ls(sl=1)[0])    
    return array    
    
def transform_array(method='scene'):
    array = []
    if method == 'scene':
        for transform in cmds.ls(typ="transform"):
            if is_transform(transform) and cmds.nodeType(transform) == 'transform': array.append(transform)
    if method == 'selection':
        for transform in cmds.ls(sl=1):
            if is_transform(transform) and cmds.nodeType(transform) == 'transform':  array.append(transform)
    if method == 'topnode':
        if cmds.ls(sl=1):
            for transform in noneAsList(cmds.listRelatives(cmds.ls(sl=1)[0], allDescendents=True)):
                if is_transform(transform) and cmds.nodeType(transform) == 'transform':  array.append(transform)
            if is_transform(cmds.ls(sl=1)[0]) and cmds.nodeType(cmds.ls(sl=1)[0]) == 'transform':  array.append(cmds.ls(sl=1)[0])    
    return array           
    
def list_as_MSelectionList(list=None):
    selection_list = om2.MSelectionList()
    [selection_list.add(object) for object in list]
    return selection_list
    
