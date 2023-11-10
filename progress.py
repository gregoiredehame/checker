"""
KATA. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.process
Purpose: context manager wrappering Maya's progressWindow functionality.
Execute: from checker import process; process.FUNCTION()
"""

from . import utils
try:
    import maya.cmds as cmds
    import maya.api.OpenMaya as om2
except: pass    
    
import traceback
import logging 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ProgressWindow(object):
    """
    A context manager wrappering Maya's progressWindow functionality.   
    """
    def __init__(self, totalSteps:int, enable=True, title="Applying skinning..."):
        """
        Parameters:
        totalSteps : int : The number of things we're iterating over.
        enable : bool : Default True : set to False to suppress this.
        title : string
        """
        self.progressSteps = 100.0 / totalSteps
        self.progress = 0.0
        self.enable = enable
        self.currentIndex = 0
        self.totalSteps = totalSteps
        self.title = title

    def __enter__(self):
        """
        Enter the context manager, setup the progress window:
        """
        if self.enable:
            cmds.progressWindow(title=self.title,
                              progress=0, minValue=0, maxValue=100,
                              status='Not started yet...',
                              isInterruptable=True )
        return self

    def update(self, info:str) -> bool:
        """
        Call this every loop once the context has been entered.  It detects for
        progress window canceling, and updates the current progress.

        Parameters:
        info : string : Informative text to display

        Return : bool
        """
        ret = True
        if self.enable:
            if cmds.progressWindow( query=True, isCancelled=True ):
                ret = False
            else:
                self.currentIndex += 1
                self.progress += self.progressSteps
                cmds.progressWindow(edit=True, progress=int(self.progress), status='%s/%s : %s'%(self.currentIndex, self.totalSteps, info))
        return ret

    def __exit__(self, exc_type, exc_value, tb) -> bool:
        """
        Called when the context manager is exited, exits the progress window.
        """
        if self.enable:
            cmds.progressWindow(endProgress=True)
        # If False, Raise the last exception if there is one
        if exc_type:
            tbExtract = traceback.extract_tb(tb)
            tbList = traceback.format_list(tbExtract)
            print("\nTraceback:")
            for line in tbList:
                print(line.rstrip())
            om2.MGlobal.displayError(f"Exception: {exc_value}")
        # Raise the last exception:
        return False