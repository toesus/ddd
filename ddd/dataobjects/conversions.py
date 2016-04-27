'''
Created on 24.04.2016

@author: killian
'''
import fractions
import math

from objects import dddobject,DataObject


@dddobject('1to1')
class DddConversion(DataObject):
    def __init__(self):
        self.name='1TO1'
    def get_name(self):
        return self.name
    def accept(self,visitor):
        visitor.pre_order(self)
        pass
        visitor.post_order(self)


class DddConversionPow(DddConversion):
    base=0
    basename=''
    def __init__(self,fraction=0,offset=0):
        if not self.base:
            raise NotImplementedError('DddConversionPow should not be used directly')
        self.factor=fractions.Fraction(1)
        self.fraction=fraction
        self.offset=offset
        
        self.name=self.basename+str(fraction)
        if fraction>0:
            self.factor=fractions.Fraction(1,self.base**fraction)
        else:
            self.factor=fractions.Fraction(self.base**(-fraction),1)
            
        if self.offset!=0:
            self.name=self.name+'_OFFS'+str(self.offset)
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'fraction':self.fraction,
                    'offset':self.offset})
        return tmp        
@dddobject('binary')
class DddConversionBin(DddConversionPow):
    base=2
    basename='BIN'

@dddobject('decimal')
class DddConversionDec(DddConversionPow):
    base=10
    basename='DEC'

@dddobject('linear')
class DddConversionLin(DddConversion):
    def __init__(self,numerator=0,denominator=0,offset=0):
        self.numerator=numerator
        self.denominator=denominator
        self.factor=fractions.Fraction(1)
        self.offset=offset
        
        try:
            self.factor=fractions.Fraction(numerator,denominator)
        except TypeError:
            raise Exception("Only Rational Number factors are supported")
        (m,e)=math.frexp(self.factor)
        if m==0.5:
            raise Exception('Linear conversion with power of 2 factor created, switch to a BIN-covnersion')
        else:
            e=math.log10(self.factor)
            if int(e)==e:
                raise Exception('Linear conversion with power of 10 factor created, switch to a DEC-conversion')
        
        self.name='LIN'+str(float(self.factor))
        
        if self.offset!=0:
            self.name=self.name+'_OFFS'+str(self.offset)
                
            
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'numerator':self.numerator,
                    'denominator':self.denominator,
                    'offset':self.offset})
        return tmp
        
@dddobject('stringconversion')
class DddStringConversion(DataObject):
    def __init__(self,name='',table=None):
        self.name=name
        self.table={}
        
        for key in table:
            self.table[int(key)]=table[key]
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'table':self.table,
                    'name':self.name})
        return tmp
    
    def get_name(self):
        return self.name
    def accept(self,visitor):
        visitor.pre_order(self)
        pass
        visitor.post_order(self)
