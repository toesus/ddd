'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject

@dddobject('project')
class DddProject(DataObject):
    def __init__(self,components=None,config=None):
        if components is not None:
            self.components = components
        else:
            self.components = []
        self.config=config
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'components':self.components,
                    'config':self.config})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        for c in self.components:
            c.accept(visitor)
        self.config.accept(visitor)
        visitor.post_order(self)