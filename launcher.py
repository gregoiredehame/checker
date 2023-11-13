"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.launcher
Purpose: checker interface standalone launcher file.
Execute: from checker import launcher; launcher.tool_checker()
"""

from . import core, utils

def tool_checker(area=None):
    """ function that will delete existing tool_checker interface, and will launch new one.
            Args:
                area (str): - string area where to launch interface
    """
    window_name = core.CheckerManager.title + 'WorkspaceControl'
    utils.delete_workspace_control(window_name)
    
    window = core.CheckerManager()
    if area and utils.is_in_maya():
        import maya.cmds as cmds
        cmds.setParent(area)
        window.show(dockable=True, area='right', floating=False)
        cmds.workspaceControl(window_name, edit=True, tabToControl=[area, -1], widthProperty="preferred", width=500)
    else:
       window.show(dockable=True, area='right', floating=True) 
    window.raise_()
    