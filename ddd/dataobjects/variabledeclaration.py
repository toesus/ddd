'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject
from variabledefinition import DddVariableDef

@dddobject('declaration')
class DddVariableDecl(DataObject):
    def __init__(self,scope='local',definition=None,condition=None):
        if not definition:
            self.definition=DddVariableDef()
        else:
            self.definition=definition
        self.scope=scope
        self.condition=condition
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'scope':self.scope,
                    'condition':self.condition,
                    'definition':self.definition})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.definition.accept(visitor)
        visitor.post_order(self)