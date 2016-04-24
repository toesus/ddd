'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject

@dddobject('project')
class DddProject(DataObject):
    def __init__(self,name='',components=None):
        self.name=name
        if components is not None:
            self.components = components
        else:
            self.components = []
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'name':self.name,
                    'components':self.components})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        for c in self.components:
            c.accept(visitor)
        visitor.post_order(self)