'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject

@dddobject('project')
class DddProject(DataObject):
    def __init__(self,name='',components=None,memorysections=None):
        self.name=name
        if components is not None:
            self.components = components
        else:
            self.components = []
        self.memorysections=memorysections
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'name':self.name,
                    'components':self.components,
                    'memorysections':self.memorysections})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        for c in self.components:
            c.accept(visitor)
        for m in self.memorysections:
            m.accept(visitor)
        visitor.post_order(self)