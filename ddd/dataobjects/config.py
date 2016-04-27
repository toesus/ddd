'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject

@dddobject('config')
class DddConfig(DataObject):
    def __init__(self,memorysections=None,conditionheader=''):
        self.conditionheader=conditionheader
        self.memorysections=memorysections
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'memorysections':self.memorysections,
                    'conditionheader':self.conditionheader})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        for m in self.memorysections:
            m.accept(visitor)
        visitor.post_order(self)