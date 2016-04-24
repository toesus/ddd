'''
Created on 24.04.2016

@author: killian
'''
from objects import dddobject,DataObject
from conversions import DddConversion


@dddobject('datatype')
class DddDatatype(DataObject):
    def __init__(self,basetype='',bitsize=8,signed=False,conversion=None,unit='-',constant=False):
        self.basetype=basetype
        self.bitsize=bitsize
        self.signed=signed
        if not conversion:
            self.conversion=DddConversion(type='1to1')
        else:
            self.conversion=conversion
        self.unit=unit
        self.constant=constant
        typenames={'integer':{8:'int8',
                              16:'int16',
                              32:'int32'},
                   'float':{ 32:'single',
                              64:'double'}}
        self.name=typenames[basetype][bitsize]
        if signed:
            self.name='s'+self.name
        else:
            self.name='u'+self.name
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'basetype':self.basetype,
                    'bitsize':self.bitsize,
                    'signed':self.signed,
                    'unit':self.unit,
                    'constant':self.constant,
                    'conversion':self.conversion})
        return tmp
    
    def get_name(self):
        return self.name.upper()+'_'+self.conversion.get_name()
    
    def source_name(self):
        if self.constant:
            return 'const '+self.name
        else:
            return self.name
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.conversion.accept(visitor)
        visitor.post_order(self)