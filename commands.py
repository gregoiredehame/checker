"""
CHECKER. (c)

Author:  Gregoire Dehame
Created: Oct 27, 2023
Module:  checker.commands
Purpose: checker interface commands file for maya operations.
Execute: from checker import utils; utils.FUNCTION()
"""

try:
    import maya.cmds as cmds
    import maya.api.OpenMaya as om2
    import maya.mel as mel
except: pass    
    
import sys
import os
import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import utils, progress

class Tagger(object):
    def __init__(self):
        self._dict = {}

    def __call__(self, name):
        if name not in self._dict:
            self._dict[name] = []
      
        def tags_decorator(func):
            self._dict[name].append(getattr(func, "__name__", str(func)))
            func._tag = name
            return func
        return tags_decorator
    
tag = Tagger()   
 
class Scene():
    def __init__(self, method='scene'):
        self.method = method
        
        
    # -------------     
    @tag('checked')
    def references_get(self, verbose=None, method='scene') -> list:
        references = []
        nodes = utils.noneAsList(cmds.ls(type='reference'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get References: {node}"): return None
                    [references.append(node) if node not in ['sharedReferenceNode', '_UNKNOWN_REF_NODE_'] else None]
        return references
        
    def references_fix(self, verbose=None, method='scene') -> list:
        nodes = self.references_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix References: {node}"): return None
                    try: cmds.lockNode(node, lock=False)
                    except: pass
                    try: cmds.file(referenceNode=node, removeReference=True)
                    except: 
                        try: cmds.delete(node)
                        except: logger.info('- unable to remove "%s".'%node)
        return self.references_get(verbose=None, method=method)  
        
        
    # -------------    
    @tag('checked')    
    def namespaces_get(self, verbose=None, method='scene') -> list:
        namespaces = []
        nodes = utils.noneAsList(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Namespaces: {node}"): return None
                    [namespaces.append(''.join(node.rsplit(':')[-1])) if node not in ['UI','shared'] else None]
        return namespaces
        
    def namespaces_fix(self, verbose=None, method='scene') -> list:
        nodes = self.namespaces_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Namespaces: {node}"): return None
                    try: cmds.lockNode(node, lock=False)
                    except: pass
                    try: cmds.namespace(removeNamespace=node, mergeNamespaceWithRoot=True)
                    except: logger.info(f'- skipping. unable to remove "{node}".')
        return self.namespaces_get(verbose=None, method=method)
      
        
    # -------------     
    @tag('checked')    
    def unknown_nodes_get(self, verbose=None, method='scene') -> list:
        unknown_nodes = []
        nodes = utils.noneAsList(cmds.ls(type='unknown'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unknown Nodes: {node}"): return None
                    unknown_nodes.append(node)
        return unknown_nodes 
        
    def unknown_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.unknown_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unknown Nodes: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except: logger.info('- unable to remove "%s".'%node)  
        return self.unknown_nodes_get(verbose=None, method=method)
     
        
    # ------------- 
    @tag('checked')    
    def unknown_plugins_get(self, verbose=None, method='scene') -> list:
        unknown_plugins = []
        nodes = utils.noneAsList(cmds.unknownPlugin(query=True, list=True))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unknown Plugins: {node}"): return None
                    unknown_plugins.append(node)
        return unknown_plugins 
        
    def unknown_plugins_fix(self, verbose=None, method='scene') -> list:
        nodes = self.unknown_plugins_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unknown Plugins: {node}"): return None
                    try: cmds.unknownPlugin(node, remove=True)
                    except: logger.info('- unable to remove "%s".'%node)
        return self.unknown_plugins_get(verbose=None, method=method)
    
        
    # -------------     
    @tag('checked')    
    def unused_shaders_get(self, verbose=None, method='scene') -> list:
        unused_shaders = []
        nodes = utils.noneAsList(cmds.ls(type='shadingEngine'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unused Shaders: {node}"): return None
                    if node not in ['initialParticleSE', 'initialShadingGroup']:
                        childs = om2.MFnSet(om2.MGlobal.getSelectionListByName(node).getDependNode(0)).getMembers(1)
                        if childs.length() == 0 or str(childs) == "('shaderBallGeomShape1')":
                            unused_shaders.append(node)
        return unused_shaders
        
    def unused_shaders_fix(self, verbose=None, method='scene') -> list:
        nodes = self.unused_shaders_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unused Shaders: {node}"): return None
                    for shader in utils.noneAsList(cmds.listConnections('%s.surfaceShader'%node)):
                        try:
                            cmds.lockNode(shader, lock=False)
                            cmds.delete(shader)
                        except: logger.info('- unable to remove "%s".'%shader)  
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except: logger.info('- unable to remove "%s".'%node) 
        return self.unused_shaders_get(verbose=None,  method=method)
    
    
    # -------------     
    @tag('checked')    
    def unused_nodes_get(self, verbose=None, method='scene') -> list:
        unused_nodes = []
        return unused_nodes
        
    def unused_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.unused_nodes_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unused Nodes: {node}"): return None
        return self.unused_shaders_get(verbose=None,  method=method)    
        
        
    # -------------     
    @tag('checked')    
    def animation_layers_get(self, verbose=None, method='scene') -> list:
        animation_layers = []
        nodes = utils.noneAsList(cmds.ls(type='animLayer'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Animation Layers: {node}"): return None
                    [animation_layers.append(node) if node not in ['defaultLayer','defaultRenderLayer'] else None]
        return animation_layers 
        
    def animation_layers_fix(self, verbose=None, method='scene') -> list:
        nodes = self.animation_layers_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Animation Layers: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except: logger.info('- unable to remove "%s".'%node)
        return self.animation_layers_get(verbose=None,  method=method)
      
        
    # -------------    
    @tag('checked')   
    def display_layers_get(self, verbose=None, method='scene') -> list:
        display_layers = []
        nodes = utils.noneAsList(cmds.ls(type='displayLayer'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Display Layers: {node}"): return None
                    [display_layers.append(node) if node not in ['defaultLayer','defaultRenderLayer'] else None]
        return display_layers 
        
    def display_layers_fix(self, verbose=None, method='scene') -> list:
        nodes = self.display_layers_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Display Layers: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except: logger.info('- unable to remove "%s".'%node)
        return self.display_layers_get(verbose=None,  method=method)
    
        
    # -------------     
    @tag('checked')    
    def render_layers_get(self, verbose=None, method='scene') -> list:
        render_layers = []
        nodes = utils.noneAsList(cmds.ls(type='renderLayer'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Render Layers: {node}"): return None
                    [render_layers.append(node) if node not in ['defaultLayer','defaultRenderLayer'] else None]
        return render_layers 
        
    def render_layers_fix(self, verbose=None, method='scene') -> list:
        nodes = self.render_layers_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Render Layers: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except: logger.info('- unable to remove "%s".'%node)
        return self.render_layers_get(verbose=None,  method=method)
    
    
    # -------------     
    @tag('checked')    
    def script_nodes_get(self, verbose=None, method='scene') -> list:
        script_nodes = []
        nodes = utils.noneAsList(cmds.ls(type='script'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Script Nodes: {node}"): return None
                    if node not in script_nodes and  node not in ['sceneConfigurationScriptNode','uiConfigurationScriptNode']: script_nodes.append(node)
        return script_nodes
        
    def script_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.script_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Script Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.script_nodes_get(verbose=None, method=method)
     
        
    # -------------         
    @tag('checked')    
    def expression_nodes_get(self, verbose=None, method='scene') -> list:
        expression_nodes = []
        nodes = utils.noneAsList(cmds.ls(type='expression'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Expression Nodes: {node}"): return None
                    if node not in expression_nodes: expression_nodes.append(node)
        return expression_nodes
        
    def expression_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.expression_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Expression Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.expression_nodes_get(verbose=None, method=method)  
    
    
    # -------------     
    @tag('checked')    
    def light_editor_nodes_get(self, verbose=None, method='scene') -> list:
        light_editor_nodes = []
        nodes = utils.noneAsList(cmds.ls(type='lightEditor'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Light Editor Nodes: {node}"): return None
                    if node not in light_editor_nodes: light_editor_nodes.append(node)
        return light_editor_nodes
        
    def light_editor_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.light_editor_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Light Editor Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.light_editor_nodes_get(verbose=None, method=method)  
    
    
    # -------------     
    @tag('checked')    
    def time_editor_nodes_get(self, verbose=None, method='scene') -> list:
        time_editor_nodes = []
        nodes = [node_type for node_type in cmds.allNodeTypes() if node_type.startswith("timeEditor")]
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Time Editor Nodes: {node}"): return None
                    for node in utils.noneAsList(cmds.ls(type=node)):
                        if node not in time_editor_nodes:
                            time_editor_nodes.append(node)
        return time_editor_nodes
        
    def time_editor_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.time_editor_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Time Editor Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.time_editor_nodes_get(verbose=None, method=method)  
    
    
    # -------------     
    @tag('checked')    
    def cache_nodes_get(self, verbose=None, method='scene') -> list:
        cache_nodes = []
        nodes = [node_type for node_type in cmds.allNodeTypes() if node_type in ['cacheBlend','cacheFile']]
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Cache Nodes: {node}"): return None
                    for node in utils.noneAsList(cmds.ls(type=node)):
                        if node not in cache_nodes:
                            cache_nodes.append(node)
        return cache_nodes
        
    def cache_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.cache_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Cache Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.cache_nodes_get(verbose=None, method=method)     
    
    
    # -------------     
    @tag('checked')    
    def dag_nodes_get(self, verbose=None, method='scene') -> list:
        dag_nodes = []
        nodes = [node_type for node_type in cmds.allNodeTypes() if node_type in ['dagContainer','dagNode']]
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Dag Nodes: {node}"): return None
                    for node in utils.noneAsList(cmds.ls(type=node)):
                        if node not in dag_nodes:
                            dag_nodes.append(node)
        return dag_nodes
        
    def dag_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.dag_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Dag Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.dag_nodes_get(verbose=None, method=method)  
    
    
    # -------------     
    @tag('checked')    
    def hypershade_nodes_get(self, verbose=None, method='scene') -> list:
        hypershade_nodes = []
        nodes = cmds.ls('*hyperShade*')
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Hypershade Nodes: {node}"): return None
                    if node not in hypershade_nodes: hypershade_nodes.append(node)
        return hypershade_nodes
        
    def hypershade_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.hypershade_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Hypershade Nodes: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.hypershade_nodes_get(verbose=None, method=method)            
    
    
    # -------------    
    @tag('checked')    
    def poly_nodes_get(self, verbose=None, method='scene') -> list:
        poly_nodes = []
        nodes = [node_type for node_type in cmds.allNodeTypes() if node_type.startswith("poly")]
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Poly Nodes: {node}"): return None
                    for poly in utils.noneAsList(cmds.ls(type=node)):
                        if poly not in poly_nodes:
                            poly_nodes.append(poly)
        return poly_nodes
        
    def poly_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.poly_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Poly Nodes: {node}"): return None
                    try: cmds.lockNode(node, lock=False)
                    except: pass
                    try: cmds.delete(node)
                    except:logger.info('- unable to remove "%s".'%node) 
        return self.poly_nodes_get(verbose=None, method=method)
    
    
    # -------------    
    @tag('checked')    
    def xgen_nodes_get(self, verbose=None, method='scene') -> list:
        xgen_nodes = []
        nodes = [node_type for node_type in cmds.allNodeTypes() if node_type.startswith("xgm")]
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get XGen Nodes: {node}"): return None
                    for poly in utils.noneAsList(cmds.ls(type=node)):
                        if poly not in poly_nodes: poly_nodes.append(poly)
        return poly_nodes
        
    def xgen_nodes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.xgen_nodes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix XGen Nodes: {node}"): return None
                    try: cmds.lockNode(node, lock=False)
                    except: pass
                    try: cmds.delete(node)
                    except:logger.info('- unable to remove "%s".'%node) 
        return self.xgen_nodes_get(verbose=None, method=method)    
        
        
    # -------------     
    @tag('checked')    
    def cameras_get(self, verbose=None, method='scene') -> list:
        cameras_nodes = []
        nodes = utils.noneAsList(cmds.ls(type='camera'))
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Cameras: {node}"): return None
                    if node not in ['frontShape', 'perspShape', 'sideShape', 'topShape']:
                        try:
                            transform = cmds.listRelatives(node, parent=True)[0]
                            if transform not in cameras_nodes: cameras_nodes.append(transform)
                        except:
                            if node not in cameras_nodes: cameras_nodes.append(node)
        return cameras_nodes
        
    def cameras_fix(self, verbose=None, method='scene') -> list:
        nodes = self.cameras_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Cameras: {node}"): return None
                    try: 
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node) 
        return self.cameras_get(verbose=None, method=method)            



class Objects():
    def __init__(self):
        pass 
        
        
    # -------------         
    @tag('checked')    
    def contruction_history_get(self, verbose=None, method='scene') -> list:
        history = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Contruction History: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if cmds.nodeType(shape) == 'mesh':
                            uncorrect_hist = []
                            for hist in utils.noneAsList(cmds.listHistory(shape)): 
                                if cmds.nodeType(hist) not in ['mesh', 'groupId', 'GroupId', 'shadingEngine', 'objectSet', 'textureEditorIsolateSelectSet']:
                                    if hist not in uncorrect_hist: uncorrect_hist.append(hist)
                            if len(uncorrect_hist) > 1: 
                                print(uncorrect_hist)
                                if shape not in history: history.append(shape)
        return history
        
    def contruction_history_fix(self, verbose=None, method='scene') -> list:
        nodes = self.contruction_history_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Contruction History: {node}"): return None
                    cmds.delete(node, constructionHistory=True)
        return self.contruction_history_get(verbose=None, method=method)
    
    
    # -------------  
    @tag('checked')     
    def poly_display_get(self, verbose=None, method='scene') -> list:
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Poly Display: {node}"): return None
                    cmds.polySoftEdge(node, a=180, constructionHistory=False)
        cmds.polyOptions(colorShadedDisplay=False, displayVertex=False, displayCenter=False, displayTriangle=False, displayBorder=False, 
                         displayMapBorder=False, displayCreaseEdge=False, displayCreaseVertex=False, displaySubdComps=False, displayWarp=False,
                         displayNormal=False,  displayUVs=False, displayUVTopology=False, point=False, facet=False, pointFacet=False, allEdges=True,
                         softEdge=False, hardEdge=False, displayGeometry=True, backCulling=True, wireBackCulling=False, hardBack=False, fullBack=False,
                         backCullVertex=True, gl=True)
                             
        return []    
    
    
    # -------------  
    @tag('checked')     
    def intermediate_objects_get(self, verbose=None, method='scene') -> list:
        intermediate_objects = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Intermediate Objects: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if cmds.ls(shape, intermediateObjects=True) and node not in intermediate_objects: intermediate_objects.append(node)  
        return intermediate_objects
        
        
    # -------------           
    def freeze_transformations_get(self, verbose=None, method='scene') -> list:
        unfrozen_transforms = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unfrozen Transformations: {node}"): return None
                    translation = cmds.xform(node, query=True, worldSpace=True, translation=True)
                    rotation = cmds.xform(node, query=True, worldSpace=True, rotation=True)
                    scale = cmds.xform(node, query=True, worldSpace=True, scale=True)
                    if translation != [0.0, 0.0, 0.0] or rotation != [0.0, 0.0, 0.0] or scale != [1.0, 1.0, 1.0]:
                        unfrozen_transforms.append(node)
        return unfrozen_transforms
        
    def freeze_transformations_fix(self, verbose=None, method='scene') -> list:
        nodes = self.freeze_transformations_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unfrozen Transformations: {node}"): return None
                    [cmds.setAttr(f"{node}.{attr}", lock=False) for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']]
                    cmds.makeIdentity(f"{node}", apply=True, translate=True, rotate=True, scale=True, normal=False)  
                    cmds.delete(node, constructionHistory=True) 
        return self.freeze_transformations_get(verbose=None, method=method)
    
    
    # -------------  
    @tag('checked') 
    def world_pivot_get(self, verbose=None, method='scene') -> list:
        uncentered_pivot = []
        nodes = utils.mesh_array(method) + utils.transform_array()
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Pivot Point: {node}"): return None
                    for attr in ['rpx','rpy','rpz','spx','spy','spz']:
                        if cmds.getAttr(f"{node}.{attr}") != 0:
                            if node not in uncentered_pivot: uncentered_pivot.append(node)
        return uncentered_pivot
        
    def world_pivot_fix(self, verbose=None, method='scene') -> list:
        nodes = self.world_pivot_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Pivot Point: {node}"): return None
                    for attr in ['rpx','rpy','rpz','spx','spy','spz']:
                        cmds.setAttr(f"{node}.{attr}", 0, lock=False) 
        return self.world_pivot_get(verbose=None, method=method)  
        
          
    @tag('checked')   
    # -------------           
    def locked_transformations_get(self, verbose=None, method='scene') -> list:
        locked_transforms = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Locked Transformations: {node}"): return None
                    for attribute in ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','visibility']:
                        if cmds.getAttr(f'{node}.{attribute}', lock=True)       == True  and node not in locked_transforms: locked_transforms.append(node)
                        if cmds.getAttr(f'{node}.{attribute}', keyable=True)    == False and node not in locked_transforms: locked_transforms.append(node)
        return locked_transforms
        
    def locked_transformations_fix(self, verbose=None, method='scene') -> list:
        nodes = self.locked_transformations_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Locked Transformations: {node}"): return None
                    for attribute in ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','visibility']:
                        try:
                            cmds.setAttr(f'{node}.{attribute}', lock=False)
                            cmds.setAttr(f'{node}.{attribute}', channelBox=True)
                            cmds.setAttr(f'{node}.{attribute}', keyable=True)
                        except: logger.info(f'- unable to edit {node}.{attribute} status.')    
        return self.locked_transformations_get(verbose=None, method=method)    
        
        
    # -------------  
    @tag('checked')   
    def locked_normals_get(self, verbose=None, method='scene') -> list:
        locked_normals = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Locked Normals: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if True in cmds.polyNormalPerVertex(f'{shape}.vtx[*]', query=True, freezeNormal=True):
                            locked_normals.append(shape)
                            continue
        return locked_normals                
        
    def locked_normals_fix(self, verbose=None, method='scene') -> list:
        nodes = self.locked_normals_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Locked Normals: {node}"): return None
                    cmds.polyNormalPerVertex(node, unFreezeNormal=True)
        return self.locked_normals_get(verbose=None, method=method)
        
        
    # -------------  
    @tag('checked')     
    def vertex_transforms_get(self, verbose=None, method='scene') -> list:
        vertex_transformed = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Vertex Transformations: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        try:
                            for tweak in cmds.getAttr(f'{shape}.pnts[*]'):
                                for i in tweak:
                                    if abs(i) > 0.000000000000001 and node not in vertex_transformed:
                                            vertex_transformed.append(node)
                        except: pass
        return vertex_transformed    
        
    def vertex_transforms_fix(self, verbose=None, method='scene') -> list:
        nodes = self.vertex_transforms_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Vertex Transformations: {node}"): return None
                    cmds.polyMoveVertex(node, constructionHistory=False)
                    cmds.polySmooth(f"{node}.vtx[*]", divisions=0, constructionHistory=False)
                    mfn = om2.MFnMesh(om2.MGlobal.getSelectionListByName(node).getDagPath(0))
                    for shape in cmds.listRelatives(node, shapes=True, fullPath=True):
                        for i in range(len(mfn.getPoints())):
                            cmds.setAttr(f"{shape}.pnts[{str(i)}].pntx",0)
                            cmds.setAttr(f"{shape}.pnts[{str(i)}].pnty",0)
                            cmds.setAttr(f"{shape}.pnts[{str(i)}].pntz",0)
                    cmds.select(clear=True)
        return self.vertex_transforms_get(verbose=None, method=method)


    # -------------  
    @tag('checked')    
    def duplicated_names_get(self, verbose=None, method='scene') -> list:
        duplicated_names = []
        nodes = utils.mesh_array(method) + utils.transform_array()
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Duplicated Names: {node}"): return None
                    for dag in cmds.ls(nodes, dag=1):
                        if dag.count('|') and dag not in duplicated_names: 
                            if cmds.nodeType(dag) == 'transform': duplicated_names.append(dag)
        return duplicated_names                
                 
    def duplicated_names_fix(self, verbose=None, method='scene') -> list:
        nodes = self.duplicated_names_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Duplicated Names: {node}"): return None
                    new_name = ''.join(node.rsplit('|')[-1])
                    cmds.rename(f"{node}", f"{new_name}__{str(i+1)}")
        return self.duplicated_names_get(verbose=None, method=method)
        
        
    # -------------  
    @tag('checked')     
    def extra_shapes_get(self, verbose=None, method='scene') -> list:
        extra_shapes = []
        nodes = utils.mesh_array(method)
        if nodes:
            array_shapes = []
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Extra Shapes: {node}"): return None
                    for geo in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if cmds.nodeType(geo) in ['mesh','nurbsSurface']:
                            if 'geometryShape' in cmds.nodeType(geo, inherited=True) and geo not in array_shapes: array_shapes.append(geo)
                            if 'nurbsSurface'  in cmds.nodeType(geo, inherited=True) and geo not in array_shapes: array_shapes.append(geo)  
                            if not cmds.listConnections(geo, c=True, shapes=True) and geo not in extra_shapes:
                                extra_shapes.append(geo)          
                                
                            shading_engines = cmds.listConnections(geo, type="shadingEngine")
                            if not shading_engines and geo not in extra_shapes:
                                extra_shapes.append(geo)
                                
                            if shading_engines:
                                does_not_have_shaders = True
                                for sg in shading_engines:
                                    connected_shaders = cmds.listConnections(sg + '.surfaceShader')
                                    if connected_shaders:
                                        does_not_have_shaders = False
                                        
                                if does_not_have_shaders and geo not in extra_shapes:
                                    extra_shapes.append(geo)
                              
            for s in array_shapes:
                if s.count('Orig'):
                    is_deformed = False
                    for h in cmds.listHistory(cmds.listRelatives(s, parent=True, fullPath=True)):
                        if cmds.nodeType(h, inherited=True).count('geometryFilter'): is_deformed=True
                    if is_deformed is False: extra_shapes.append(s)
        return extra_shapes        
        
    def extra_shapes_fix(self, verbose=None, method='scene') -> list:
        nodes = self.extra_shapes_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Extra Shapes: {node}"): return None
                    try: cmds.delete(node)
                    except:logger.info('- unable to remove "%s".'%node) 
        return self.extra_shapes_get(verbose=None, method=method)
            
        
    # -------------  
    @tag('checked')     
    def shapes_names_get(self, verbose=None, method='scene') -> list:
        uncorrect_names = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Shapes Names: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if ''.join(shape.rsplit('|')[-1]) != str(node) + 'Shape' and node not in uncorrect_names:
                            uncorrect_names.append(shape)
        return uncorrect_names                
        
    def shapes_names_fix(self, verbose=None, method='scene') -> list:
        nodes = self.shapes_names_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Shapes Names: {node}"): return None
                    parent = cmds.listRelatives(node, parent=True)[0]
                    cmds.rename(node, f"{parent}Shape")
        return self.shapes_names_get(verbose=None, method=method)
        
        
    # -------------  
    @tag('checked')     
    def locked_transforms_get(self, verbose=None, method='scene') -> list:
        locked_transforms = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Transforms: {node}"): return None
                    for attribute in ['translateX','translateY','translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']:
                        if cmds.getAttr(f"{node}.{attribute}", lock=True) == True and node not in locked_transforms:
                            locked_transforms.append(node)
        return locked_transforms
        
    def locked_transforms_fix(self, verbose=None, method='scene') -> list:
        nodes = self.locked_transforms_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Transforms: {node}"): return None
                    for attribute in ['translateX','translateY','translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']:
                        cmds.setAttr(f"{node}.{attribute}", lock=False, keyable=True)
        return  self.locked_transforms_get(verbose=None, method=method)       
        
        
    # -------------  
    @tag('checked')     
    def empty_groups_get(self, verbose=None, method='scene') -> list:
        empty_groups = []
        nodes = utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Empty Groups: {node}"): return None
                    if not cmds.listRelatives(node, allDescendents=True) and node not in empty_groups:
                        empty_groups.append(node)
        return empty_groups            
        
    def empty_groups_fix(self, verbose=None, method='scene') -> list:
        nodes = self.empty_groups_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Empty Groups: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node)
        return self.empty_groups_get(verbose=None, method=method)
        
        
    # -------------  
    @tag('checked')     
    def constraints_get(self, verbose=None, method='scene') -> list:
        constraints = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            constraints_nodes = ['parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint', 'aimConstraint', 'poleVectorConstraint']
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Constraints: {node}"): return None
                    try:
                        for constraint in utils.noneAsList(cmds.listConnections(node, type="constraint")):
                            if constraint not in constraints: constraints.append(constraint)      
                    except: pass
        return constraints
        
    def constraints_fix(self, verbose=None, method='scene') -> list:
        nodes = self.constraints_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Constraints: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node)
        return self.constraints_get(verbose=None, method=method)  
        
        
    # -------------  
    @tag('checked')     
    def deformers_get(self, verbose=None, method='scene') -> list:
        deformers = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            deformer_list = ['blendShape', 'cluster', 'deltaMush', 'ffd', 'jiggle', 'nonLinear', 'proximityWrap', 'sculpt', 'shrinkWrap', 'skinCluster', 'softMod', 'tension', 'textureDeformer', 'wire', 'wrap']
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Deformers: {node}"): return None
                    history = cmds.listHistory(node, gl=True)
                    try: 
                        for deformer in utils.noneAsList(cmds.ls(history, type=deformer_list)):
                            if deformer not in deformers: deformers.append(deformer)
                    except: pass
        return deformers
        
    def deformers_fix(self, verbose=None, method='scene') -> list:
        nodes = self.deformers_get(verbose=None, method=method) 
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Deformers: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node)
            self.extra_shapes_fix(verbose=None, method=method)            
        return self.deformers_get(verbose=None, method=method) 
        
        
    # -------------  
    @tag('checked')     
    def animation_curves_get(self, verbose=None, method='scene') -> list:
        animation_curves = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Animation Curves: {node}"): return None
                    try:
                        for anim_curve in utils.noneAsList(cmds.listConnections(node, type="animCurve")):
                            if anim_curve not in animation_curves_nodes: animation_curves_nodes.append(anim_curve)       
                    except: pass
        return animation_curves
        
    def animation_curves_fix(self, verbose=None, method='scene') -> list:
        nodes = self.animation_curves_get(verbose=None, method=method) 
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Animation Curves: {node}"): return None
                    try:
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                    except:
                        logger.info('- unable to remove "%s".'%node)           
        return self.animation_curves_get(verbose=None, method=method) 
            
        
    # -------------  
    @tag('checked')     
    def enable_overrides_get(self, verbose=None, method='scene') -> list:
        enable_overrides = []
        nodes = utils.mesh_array(method) + utils.transform_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Enable Overrides: {node}"): return None
                    if cmds.getAttr(f"{node}.overrideEnabled") != 0:
                        if node not in enable_overrides: enable_overrides.append(node)
                    elif cmds.getAttr(f"{node}.overrideDisplayType") != 0:
                        if node not in enable_overrides: enable_overrides.append(node)
                    elif cmds.getAttr(f"{node}.overrideLevelOfDetail") != 0:
                        if node not in enable_overrides: enable_overrides.append(node)
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if cmds.getAttr(f"{shape}.overrideEnabled") != 0:
                            if shape not in enable_overrides: enable_overrides.append(shape)
                        elif cmds.getAttr(f"{shape}.overrideDisplayType") != 0:
                            if shape not in enable_overrides: enable_overrides.append(shape)
                        elif cmds.getAttr(f"{shape}.overrideLevelOfDetail") != 0:
                            if shape not in enable_overrides: enable_overrides.append(shape)
        return enable_overrides
        
    def enable_overrides_fix(self, verbose=None, method='scene') -> list:
        nodes = self.enable_overrides_get(verbose=None, method=method) 
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Enable Overrides: {node}"): return None
                    cmds.setAttr(f"{node}.overrideEnabled", 0)
                    cmds.setAttr(f"{node}.overrideDisplayType", 0)
                    cmds.setAttr(f"{node}.overrideLevelOfDetail", 0)
                    cmds.setAttr(f"{node}.overrideShading", 1)
                    cmds.setAttr(f"{node}.overrideTexturing", 1)
                    cmds.setAttr(f"{node}.overridePlayback", 1)
                    cmds.setAttr(f"{node}.overrideVisibility", 1)
                    cmds.setAttr(f"{node}.overrideRGBColors", 0)
                    cmds.setAttr(f"{node}.overrideColor", 0)
        return self.enable_overrides_get(verbose=None, method=method)            
                    

    # -------------  
    @tag('checked')     
    def smooth_mesh_preview_get(self, verbose=None, method='scene') -> list:
        is_smoothed = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Smoothed Meshs: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True)):
                        for attribute in ['displaySubdComps', 'smoothLevel', 'useSmoothPreviewForRender', 'renderSmoothLevel']:
                            try :cmds.setAttr(f"{shape}.{attribute}", 1)
                            except: pass
                        if cmds.getAttr(f"{shape}.displaySmoothMesh") != 0 and node not in is_smoothed: 
                            is_smoothed.append(node)
        return is_smoothed
        
    def smooth_mesh_preview_fix(self, verbose=None, method='scene') -> list:
        nodes = self.smooth_mesh_preview_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Smoothed Meshs: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True)):
                        cmds.setAttr(f"{shape}.displaySmoothMesh", 0)
        return self.smooth_mesh_preview_get(verbose=None, method=method)
    
    
    # -------------  
    @tag('checked')     
    def smooth_mesh_preview_get(self, verbose=None, method='scene') -> list:
        is_smoothed = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Smoothed Meshs: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True, fullPath=True)):
                        if cmds.getAttr(f"{shape}.displaySmoothMesh")         != 0 and node not in is_smoothed: is_smoothed.append(node)
                        if cmds.getAttr(f"{shape}.displaySubdComps")          != 1 and node not in is_smoothed: is_smoothed.append(node)
                        if cmds.getAttr(f"{shape}.smoothLevel")               != 1 and node not in is_smoothed: is_smoothed.append(node)
                        if cmds.getAttr(f"{shape}.useSmoothPreviewForRender") != 1 and node not in is_smoothed: is_smoothed.append(node)
                        if cmds.getAttr(f"{shape}.renderSmoothLevel")         != 1 and node not in is_smoothed: is_smoothed.append(node)
        return is_smoothed
        
    def smooth_mesh_preview_fix(self, verbose=None, method='scene') -> list:
        nodes = self.smooth_mesh_preview_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Smoothed Meshs: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True)):
                        cmds.setAttr(f"{shape}.displaySmoothMesh", 0)
                        cmds.setAttr(f"{shape}.displaySubdComps", 1)
                        cmds.setAttr(f"{shape}.smoothLevel", 1)
                        cmds.setAttr(f"{shape}.useSmoothPreviewForRender", 1)
                        cmds.setAttr(f"{shape}.renderSmoothLevel", 1)
        return self.smooth_mesh_preview_get(verbose=None, method=method)
        
        
    # -------------
    @tag('checked')     
    def floating_rock_model_tag_get(self, verbose=None, method='scene') -> list:
        is_not_tagged = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Tagged Meshs: {node}"): return None
                    for shape in utils.noneAsList(cmds.listRelatives(node, shapes=True)):
                        if not cmds.attributeQuery('mdl_path', node=shape, exists=True) and node not in is_not_tagged:
                            is_not_tagged.append(node)
        return is_not_tagged
        
    def floating_rock_model_tag_fix(self, verbose=None, method='scene') -> list:
        nodes = self.floating_rock_model_tag_get(verbose=None, method=method)
        if nodes:
            try:
                sys.path.append('X:/Tools/Scripts/Maya/Scripts/frModel/')
                import fr_tag_geo_for_USD.main
                with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                    for i, node in enumerate(nodes):
                        if not prog.update(f"Fix Tagged Meshs: {node}"): return None
                        fr_tag_geo_for_USD.main.fr_tag_geo_for_USD(utils.noneAsList(cmds.listRelatives(node, shapes=True)))
            except Exception as e:
                logger.warning(f'- unable to fix the floating rock meshs tags. {e}')
                
        return self.floating_rock_model_tag_get(verbose=None, method=method)        
    
        
class Topology():
    def __init__(self):
        pass
           
           
    # -------------  
    def triangles_get(self, verbose=None, method='scene') -> list:
        triangles = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                numOfEdges = faceIt.getEdges()
                if len(numOfEdges) == 3:
                    triangles.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                faceIt.next()
            selIt.next()
        return triangles    
        

    # -------------  
    @tag('checked')        
    def ngons_get(self, verbose=None, method='scene') -> list:
        ngons = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                numOfEdges = faceIt.getEdges()
                if len(numOfEdges) > 4:
                    ngons.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                faceIt.next()
            selIt.next()
        return ngons     
           
           
    # -------------  
    @tag('checked')       
    def laminas_faces_get(self, verbose=None, method='scene') -> list:
        laminas = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                laminaFaces = faceIt.isLamina()
                if laminaFaces is True:
                    laminas.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                faceIt.next()
            selIt.next()
        return laminas    

           
    # -------------  
    @tag('checked')        
    def zero_areas_faces_get(self, verbose=None, method='scene') -> list:
        zero_areas_faces = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                faceArea = faceIt.getArea()
                if faceArea <= 0.00000001:
                    zero_areas_faces.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                faceIt.next()
            selIt.next()
        return zero_areas_faces    
        
           
    # -------------  
    @tag('checked')        
    def non_manifolds_edges_get(self, verbose=None, method='scene') -> list:
        none_manifold_edges = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            edgeIt = om2.MItMeshEdge(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not edgeIt.isDone():
                if edgeIt.numConnectedFaces() > 2:
                    none_manifold_edges.append(f"{selIt.getDagPath().fullPathName()}.e[{edgeIt.index()}]")
                edgeIt.next()
            selIt.next()
        return none_manifold_edges
        
           
    # -------------  
    @tag('checked')        
    def zero_length_edges_get(self, verbose=None, method='scene') -> list:
        zero_length_edges = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            edgeIt = om2.MItMeshEdge(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not edgeIt.isDone():
                if edgeIt.length() <= 0.00000001:
                    zero_length_edges.append(f"{selIt.getDagPath().fullPathName()}.e[{edgeIt.index()}]")
                edgeIt.next()
            selIt.next()
        return zero_length_edges
        
        
    # -------------  
    @tag('checked')     
    def hard_edges_get(self, verbose=None, method='scene') -> list:
        hard_edges = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            edgeIt = om2.MItMeshEdge(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not edgeIt.isDone():
                if edgeIt.isSmooth is False and edgeIt.onBoundary() is False:
                    hard_edges.append(f"{selIt.getDagPath().fullPathName()}.e[{edgeIt.index()}]")
                edgeIt.next()
            selIt.next()
        return hard_edges
    
    #def hard_edges_fix(self, verbose=None, method='scene') -> list:
    #    hard_edges = self.hard_edges_get(verbose=None, method=method)
    #    if hard_edges:
    #        meshs = []
    #        for edge in hard_edges:
    #            for m in utils.noneAsList(cmds.polyListComponentConversion(edge, fv=True)):
    #                if m not in meshs: meshs.append(m)
    #        [cmds.polySoftEdge(mesh, a=180, constructionHistory=False) for mesh in meshs]
    #    return self.hard_edges_get(verbose=None, method=method)
           
           
    # -------------  
    @tag('checked')        
    def open_edges_get(self, verbose=None, method='scene') -> list:
        open_edges = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            edgeIt = om2.MItMeshEdge(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())    
            while not edgeIt.isDone():
                if edgeIt.numConnectedFaces() < 2:
                    open_edges.append(f"{selIt.getDagPath().fullPathName()}.e[{edgeIt.index()}]")
                edgeIt.next()
            selIt.next()
        return open_edges
    
    
    # -------------      
    def poles_get(self, verbose=None, method='scene') -> list:
        poles = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            vertexIt = om2.MItMeshVertex(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not vertexIt.isDone():
                if vertexIt.numConnectedEdges() > 5:
                    poles.append(f"{selIt.getDagPath().fullPathName()}.vtx[{vertexIt.index()}]")
                vertexIt.next()
            selIt.next()
        return poles 
    
    
    # -------------  
    @tag('checked')        
    def starlikes_get(self, verbose=None, method='scene') -> list:
        starlikes = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            polyIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not polyIt.isDone():
                if polyIt.isStarlike() is False:
                    starlikes.append(f"{selIt.getDagPath().fullPathName()}.f[{polyIt.index()}]")
                polyIt.next()
            selIt.next()
        return starlikes 
    
    # -------------  
    @tag('checked')        
    def invalid_edges_get(self, verbose=None, method='scene') -> list:
        invalid_edges = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Invalid Edges: {node}"): return None
                    invalid = cmds.polyInfo(node, invalidEdges=True)
                    if invalid:
                        invalid_edges.extend(cmds.ls(invalid, flatten=True))
        return invalid_edges     
    
    def invalid_edges_fix(self, verbose=None, method='scene') -> list:
        nodes = self.invalid_edges_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Invalid Edges: {node}"): return None
                    try: cmds.polyClean(node, cleanEdges=True, constructionHistory=False)
                    except: pass
        return self.invalid_edges_get(verbose=None, method=method)  
    
    
    # -------------  
    @tag('checked')        
    def invalid_vertices_get(self, verbose=None, method='scene') -> list:
        invalid_vertices = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Invalid Vertices: {node}"): return None
                    invalid = cmds.polyInfo(node, invalidVertices=True)
                    if invalid: invalid_vertices.extend(cmds.ls(invalid, flatten=True))
        return invalid_vertices   
        
    def invalid_vertices_fix(self, verbose=None, method='scene') -> list:
        nodes = self.invalid_vertices_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Invalid Vertices: {node}"): return None
                    try: cmds.polyClean(node, cleanVertices=True, constructionHistory=False)
                    except: pass
        return self.invalid_vertices_get(verbose=None, method=method)                   
               
     
class UV():
    def __init__(self):
        pass   
        
        
    # -------------  
    @tag('checked') 
    def empty_uv_get(self, verbose=None, method='scene') -> list:
        empty_uv = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                if faceIt.hasUVs() is False:
                    mesh = selIt.getDagPath().fullPathName()
                    if mesh not in empty_uv: empty_uv.append(mesh)
                    break
                faceIt.next()
            selIt.next()
        return  empty_uv   
        
        
    # -------------  
    @tag('checked')        
    def non_manifolds_uvs_get(self, verbose=None, method='scene') -> list:
        non_manifolds_uvs = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Non Manifolds Uvs: {node}"): return None
                    invalid = cmds.polyInfo(node, nonManifoldUVs=True)
                    if invalid: non_manifolds_uvs.extend(cmds.ls(invalid, flatten=True))
        return non_manifolds_uvs   
        
    def non_manifolds_uvs_fix(self, verbose=None, method='scene') -> list:
        nodes = self.non_manifolds_uvs_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Non Manifolds Uvs: {node}"): return None
                    try: cmds.polyClean(node, cleanUVs=True, constructionHistory=False)
                    except: pass
        return self.non_manifolds_uvs_get(verbose=None, method=method)
            
            
    # -------------  
    @tag('checked')     
    def negative_uv_get(self, verbose=None, method='scene') -> list:
        negative_uv = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                U, V = set(), set()
                try:
                    u, v = faceIt.getUVs()
                    if min(u) < 0 or min(v) < 0:
                        negative_uv.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                    faceIt.next()        
                except:
                    faceIt.next()
            selIt.next()
        return negative_uv
    
        
    # -------------  
    @tag('checked')     
    def multiple_uv_sets_get(self, verbose=None, method='scene') -> list:
        multiple_uv_sets = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            try:
                faceIt = om2.MItMeshPolygon(selIt.getDagPath())
                fn = om2.MFnMesh(selIt.getDagPath())
                if len(fn.getUVSetNames()) > 1:
                    mesh = selIt.getDagPath().fullPathName()
                    if mesh not in multiple_uv_sets: multiple_uv_sets.append(mesh)
                    break
            except: 
                selIt.next()
            selIt.next()
        return multiple_uv_sets
        
        
    # -------------  
    @tag('checked')     
    def missing_uv_sets_get(self, verbose=None, method='scene') -> list:
        missing_uv_sets = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            try:
                faceIt = om2.MItMeshPolygon(selIt.getDagPath())
                fn = om2.MFnMesh(selIt.getDagPath())
                if len(fn.getUVSetNames()) == 0:
                    mesh = selIt.getDagPath().fullPathName()
                    if mesh not in multiple_uv_sets: multiple_uv_sets.append(mesh)
                    break
            except: 
                selIt.next()
            selIt.next()
        return missing_uv_sets
        
        
    # -------------  
    @tag('checked')     
    def multiple_udims_get(self, verbose=None, method='scene') -> list:
        multiple_udims = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            faceIt = om2.MItMeshPolygon(selIt.getDagPath())
            fn = om2.MFnDependencyNode(selIt.getDagPath().node())
            while not faceIt.isDone():
                U, V = set(), set()
                try:
                    UVs = faceIt.getUVs()
                    Us, Vs, = UVs[0], UVs[1]
                    for i in range(len(Us)):
                        U.add(int(Us[i]) if Us[i] > 0 else int(Us[i]) - 1)
                        V.add(int(Vs[i]) if Vs[i] > 0 else int(Vs[i]) - 1)
                    if len(U) > 1 or len(V) > 1:
                        multiple_udims.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                    faceIt.next()
                except:
                    faceIt.next()
            selIt.next()
        return multiple_udims
        
        
    # -------------  
    def flipped_uv_faces_get(self, verbose=None, method='scene') -> list:
        flipped_uv_faces = []
        selIt = om2.MItSelectionList(utils.list_as_MSelectionList(utils.mesh_array(method)))
        while not selIt.isDone():
            try:
                faceIt = om2.MItMeshPolygon(selIt.getDagPath())
                fn = om2.MFnMesh(selIt.getDagPath())
                u, v = fn.getUVs()
                while not faceIt.isDone():
                    poly_verts = fn.getPolygonVertices(faceIt.index())
                    pvc = len(poly_verts)
                    u_coo, v_coo = [], []
                    for vtx in range(pvc):
                        uv_indices = int(fn.getPolygonUVid(faceIt.index(), vtx))
                        u_coo.append(u[uv_indices])
                        v_coo.append(v[uv_indices])   
                    uv_a = [u_coo[0], v_coo[0]]
                    uv_b = [u_coo[1], v_coo[1]]
                    uv_c = [u_coo[2], v_coo[2]]
                    uvAB = om2.MVector([uv_b[0]-uv_a[0], uv_b[1]-uv_a[1]])
                    uvBC = om2.MVector([uv_c[0]-uv_b[0], uv_c[1]-uv_b[1]])
                    if (uvAB ^ uvBC) * om2.MVector(0, 0, 1) < 0:
                        flipped_uv_faces.append(f"{selIt.getDagPath().fullPathName()}.f[{faceIt.index()}]")
                    faceIt.next()
            except:
                selIt.next()
            selIt.next()
        return flipped_uv_faces  
        
        
    # -------------  
    def overlapping_uv_faces_get(self, verbose=None, method='scene') -> list:
        overlapping_uv_faces = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Overlapping UV Faces: {node}"): return None
                    shapes = cmds.listRelatives(node, shapes=True)
                    if shapes:
                        overlapping_uv_faces.extend(utils.noneAsList(cmds.polyUVOverlap("{}.f[*]".format(shapes[0]), overlappingComponents=True)))
        return overlapping_uv_faces
        
        
    # -------------  
    def overlapping_uv_meshs_get(self, verbose=None, method='scene') -> list:
        overlapping_uv_meshs = []
        nodes = utils.mesh_array(method)
        data = {}
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Meshs Per Shaders: {node}"): return None
                    dag = om2.MGlobal.getSelectionListByName(node).getDagPath(0)
                    mfn = om2.MFnMesh(dag.extendToShape())
                    for shader in mfn.getConnectedShaders(0)[0]:
                        shader_name = om2.MFnDependencyNode(shader).name()
                        
                        if shader_name not in list(data.keys()):
                            data[shader_name] = []
                        for child in str(om2.MFnSet(shader).getMembers(1).getSelectionStrings()).replace("(","").replace(")","").replace("'","").replace(",","").rsplit(" "):
                            data[shader_name].extend(cmds.polyListComponentConversion(child, toFace=True))
        if data:
            with progress.ProgressWindow(len(list(data.keys())), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(list(data.keys())):
                    if not prog.update(f"Get Overlapping UV Meshs: {node}"): return None
                    overlapping_uv_meshs.extend(utils.noneAsList(cmds.polyUVOverlap(data[node], overlappingComponents=True)))
                    
        return overlapping_uv_meshs
        

     
class Shaders():
    def __init__(self):
        pass
    
    
    # -------------  
    def assigned_lambert_get(self, verbose=None, method='scene') -> list:
        non_lambert = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Assigned Shader: {node}"): return None
                    dag = om2.MGlobal.getSelectionListByName(node).getDagPath(0)
                    mfn = om2.MFnMesh(dag.extendToShape())
                    if mfn.getConnectedShaders(0):
                        is_lambert = True
                        for engine in mfn.getConnectedShaders(0)[0]:
                            if engine.apiType() == om2.MFn.kShadingEngine:
                                if om2.MFnDependencyNode(engine).name() != 'initialShadingGroup':
                                    is_lambert = None
                        if not is_lambert: non_lambert.append(node)
        return non_lambert
        
    def assigned_lambert_fix(self, verbose=None, method='scene') -> list:
        nodes = self.assigned_lambert_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Assigned Shaders: {node}"): return None
                    cmds.sets(f'{node}', edit=True, forceElement='initialShadingGroup')
        return self.assigned_lambert_get(verbose=None,  method=method)  
        
        
    @tag('checked')    
    # -------------  
    def assigned_faces_shaders_get(self, verbose=None, method='scene') -> list:
        non_assigned_faces_shaders = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unassigned Faces: {node}"): return None
                    dag = om2.MGlobal.getSelectionListByName(node).getDagPath(0)
                    mfn = om2.MFnMesh(dag.extendToShape())
                    for shader in mfn.getConnectedShaders(0)[0]:
                        for child in str(om2.MFnSet(shader).getMembers(1).getSelectionStrings()).replace("(","").replace(")","").replace("'","").replace(",","").rsplit(" "):
                            if child not in ['shaderBallGeomShape1']:
                                if not child.count('.f[') and node not in non_assigned_faces_shaders: non_assigned_faces_shaders.append(node)
        return non_assigned_faces_shaders
        
    def assigned_faces_shaders_fix(self, verbose=None, method='scene') -> list:
        nodes = self.assigned_faces_shaders_get(verbose=None,  method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Unassigned Faces: {node}"): return None
                    dag = om2.MGlobal.getSelectionListByName(node).getDagPath(0)
                    mfn = om2.MFnMesh(dag.extendToShape())
                    for shader in mfn.getConnectedShaders(0)[0]:
                        if shader.apiType() == om2.MFn.kShadingEngine:
                            childs = om2.MFnSet(shader).getMembers(1)
                            new_childs = om2.MSelectionList()
                            for child in str(childs.getSelectionStrings()).replace("(","").replace(")","").replace("'","").replace(",","").rsplit(" "):
                                if child not in ['shaderBallGeomShape1']: 
                                    for face in utils.noneAsList(cmds.polyListComponentConversion(child, toFace=True)): new_childs.add(face)

                            om2.MFnSet(shader).removeMembers(childs)    
                            om2.MFnSet(shader).addMembers(new_childs)
        return self.assigned_faces_shaders_get(verbose=None,  method=method) 
    
    
    @tag('checked')    
    # -------------  
    def non_shaders_assigned_get(self, verbose=None, method='scene') -> list:
        non_shaders = []
        nodes = utils.mesh_array(method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Get Unassigned Meshs: {node}"): return None
                    dag = om2.MGlobal.getSelectionListByName(node).getDagPath(0)
                    mfn = om2.MFnMesh(dag.extendToShape())
                    if len(mfn.getConnectedShaders(0)[0]) == 0:
                        non_shaders.append(node)
        return non_shaders
    
    def non_shaders_assigned_fix(self, verbose=None, method='scene') -> list:
        nodes = self.non_shaders_assigned_get(verbose=None, method=method)
        if nodes:
            with progress.ProgressWindow(len(nodes), enable=verbose if not cmds.about(batch=True) else None , title="Mesh Checker") as prog:
                for i, node in enumerate(nodes):
                    if not prog.update(f"Fix Non Shader Assigned Meshs: {node}"): return None
                    cmds.sets(f'{node}', edit=True, forceElement='initialShadingGroup')
        return self.non_shaders_assigned_get(verbose=None, method=method)  