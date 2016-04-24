'''
Created on 22.11.2015

@author: killian
'''
import json
import hashlib
import fractions
import math

class DataObjectFactory:
    classes={}
    def __init__(self):
        self.count = 0
    def create_by_name(self,classname,**kwargs):
        tmp = self.classes[classname](**kwargs)
        self.count += 1
        return tmp
    def create_by_class(self,cls,**kwargs):
        self.count += 1
        return cls(**kwargs)

def dddobject(key):
    def ddddeco(cls):
        cls.classkey=key
        DataObjectFactory.classes[key]=cls
        return cls
    return ddddeco
    
class DataObject(object):
    classkey='dataobject'
    def __init__(self):
        self.hash=None
        self.loaded = False
    
    def dumpDict(self,hashed=False,rec=False):
        if hashed and rec:
            return {'ddd_hash':self.getHash()}
        d = self.getJsonDict(hashed=False)
        #print d
        for key,value in d.items():
            if type(value)==type([]):
                tmplist=[]
                for e in value:
                    if isinstance(e, DataObject):
                        tmplist.append(e.dumpDict(hashed=hashed,rec=True))
                    else:
                        tmplist.append(e)
                d[key]=tmplist
            if isinstance(value, DataObject):
                d[key]=value.dumpDict(hashed=hashed,rec=True)
        return d
    def getJsonDict(self,hashed=False):
        return {'ddd_type':self.__class__.classkey}
    def getHash(self):
        tmpstring=json.dumps(self.dumpDict(hashed=True),sort_keys=True,ensure_ascii=False)
        #print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring.encode('utf-8')).hexdigest()
        return newh

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
        
@dddobject('binary')
class DddConversionBin(DddConversion):
    def __init__(self,fraction=0,offset=0):
        self.factor=fractions.Fraction(1)
        self.fraction=fraction
        self.offset=offset
        
        self.name='BIN'+str(fraction)
        if fraction>0:
            self.factor=fractions.Fraction(1,2**fraction)
        else:
            self.factor=fractions.Fraction(2**(-fraction),1)
            
        if self.offset!=0:
            self.name=self.name+'_OFFS'+str(self.offset)
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'fraction':self.fraction,
                    'offset':self.offset})
        return tmp

@dddobject('decimal')
class DddConversionDec(DddConversion):
    def __init__(self,fraction=0,offset=0):
        self.factor=fractions.Fraction(1)
        self.fraction=fraction
        self.offset=offset
        self.name='DEC'+str(fraction)
        
        if fraction>0:
            self.factor=fractions.Fraction(1,10**fraction)
        else:
            self.factor=fractions.Fraction(10**(-fraction),1)
            
        if self.offset!=0:
            self.name=self.name+'_OFFS'+str(self.offset)
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'fraction':self.fraction,
                    'offset':self.offset})
        return tmp
        
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

@dddobject('datatype')
class DddDatatype(DataObject):
    def __init__(self,basetype='',conversion=None,unit='-',constant=False):
        self.basetype=basetype
        if not conversion:
            self.conversion=DddConversion(type='binary',fraction=1)
        else:
            self.conversion=conversion
        self.unit=unit
        self.constant=constant
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'basetype':self.basetype,
                    'unit':self.unit,
                    'constant':self.constant,
                    'conversion':self.conversion})
        return tmp
    
    def get_name(self):
        return self.basetype.upper()+'_'+self.conversion.get_name()
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.conversion.accept(visitor)
        visitor.post_order(self)

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
    
@dddobject('definition')
class DddVariableDef(DataObject):
    def __init__(self,name='',datatype=None,min=0,max=0,displayformat='',dimensions=None):
        self.name=name
        if not datatype:
            self.datatype=DddDatatype()
        else:
            self.datatype=datatype
        self.min=min
        self.max=max
        self.displayformat=displayformat
        self.dimensions=dimensions
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'name':self.name,
                    'min':self.min,
                    'max':self.max,
                    'displayformat':self.displayformat,
                    'dimensions':self.dimensions,
                    'datatype':self.datatype})
        return tmp
    
    def accept(self,visitor):
        visitor.pre_order(self)
        self.datatype.accept(visitor)
        visitor.post_order(self)

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
            
    