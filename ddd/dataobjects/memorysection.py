'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject


@dddobject('memorysection')
class DddMemorySection(DataObject):
    def __init__(self,name='',conditions=None):
        self.name=name
        self.conditions=conditions
        print "created "+str(conditions)
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'name':self.name,
                    'conditions':self.conditions})
        return tmp
    def accept(self,visitor):
        visitor.pre_order(self)
        pass
        visitor.post_order(self)