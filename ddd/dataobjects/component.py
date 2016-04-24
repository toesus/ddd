'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject

@dddobject('component')
class DddComponent(DataObject):
    def __init__(self,name='',declarations=None):
        self.name=name
        self.variablescope=0
        if declarations is not None:
            self.declarations=declarations
        else:
            self.declarations=[]
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'name':self.name,
                    'declarations': self.declarations})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        for d in self.declarations:
            d.accept(visitor)
        visitor.post_order(self)