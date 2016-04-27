'''
Created on 24.04.2016

@author: killian
'''

from objects import dddobject,DataObject
from datatype import DddDatatype
    
@dddobject('definition')
class DddVariableDef(DataObject):
    def __init__(self,name='',datatype=None,min=0,max=0,displayformat='',dimensions=None,calibrationaccess='none'):
        self.name=name
        if not datatype:
            self.datatype=DddDatatype()
        else:
            self.datatype=datatype
        self.min=min
        self.max=max
        self.displayformat=displayformat
        self.dimensions=dimensions
        self.calibrationaccess=calibrationaccess
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'name':self.name,
                    'min':self.min,
                    'max':self.max,
                    'displayformat':self.displayformat,
                    'dimensions':self.dimensions,
                    'datatype':self.datatype,
                    'calibrationaccess':self.calibrationaccess})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.datatype.accept(visitor)
        visitor.post_order(self)