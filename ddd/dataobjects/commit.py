'''
Created on 22.11.2015

@author: killian
'''

from objects import dddobject,DataObject


@dddobject('commit')
class DddCommit(DataObject):
    def __init__(self,message='',obj=None, user='',timestamp=None):
        self.message=message
        self.obj=obj
        self.user = user
        self.timestamp=timestamp
        DataObject.__init__(self)
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, hashed)
        tmp.update({'message':self.message,
                    'user':self.user,
                    'timestamp':self.timestamp,
                    'obj':self.obj})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.obj.accept(visitor)
        visitor.post_order(self)
            
    