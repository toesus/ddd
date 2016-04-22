'''
Created on 22.11.2015

@author: killian
'''
import json
import hashlib
import fractions
import math

class DataObject(object):
    classkey='dataobject'
    def __init__(self):
        self.hash=None
        self.loaded = False
    @classmethod
    def getKey(cls):
        return cls.classkey
    
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
        return {'ddd_type':self.__class__.getKey()}
    def getHash(self):
        tmpstring=json.dumps(self.dumpDict(hashed=True),sort_keys=True,ensure_ascii=False)
        #print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring.encode('utf-8')).hexdigest()
        return newh

class DddConversion(DataObject):
    classkey='conversion'
    def __init__(self,type=None,fraction=0,numerator=None,denominator=None,offset=0):
        self.factor=fractions.Fraction(1)
        self.offset=offset
        self.type=type
        self.name='none'
        
        
        if type=='binary':
            if fraction>0:
                self.factor=fractions.Fraction(1,2**fraction)
            else:
                self.factor=fractions.Fraction(2**(-fraction),1)
        elif type=='decimal':
            if fraction>0:
                self.factor=fractions.Fraction(1,10**fraction)
            else:
                self.factor=fractions.Fraction(10**(-fraction),1)
        elif type=='linear' or type is None:
            try:
                self.factor=fractions.Fraction(numerator,denominator)
            except TypeError:
                raise Exception("Only Rational Number factors are supported")
        (m,e)=math.frexp(self.factor)
        if m==0.5:
            self.type='binary'
            self.name='BIN'+str((e-1)*-1)
        else:
            e=math.log10(self.factor)
            if int(e)==e:
                self.type='decimal'
                self.name='DEC'+str(int(e)*-1)
            else:
                self.type='linear'
                self.name='LIN'+str(float(self.factor))
        if self.factor==1:
            self.type='1to1'
            self.name='1TO1'
        if self.offset!=0:
            self.name=self.name+'_OFFS'+str(self.offset)
                
            
    
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, False)
        tmp.update({'numerator':self.factor.numerator,
                    'denominator':self.factor.denominator,
                    'offset':self.offset})
        return tmp
    
    def get_name(self):
        return self.name
    def accept(self,visitor):
        visitor.pre_order(self)
        pass
        visitor.post_order(self)
    
class DddDatatype(DataObject):
    classkey='datatype'
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
            
class DddProject(DataObject):
    classkey='project'
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

class DddComponent(DataObject):
    classkey='component'
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
    
class DddVariableDef(DataObject):
    classkey='definition'
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

class DddVariableDecl(DataObject):
    classkey='declaration'
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

class DddCommit(DataObject):
    classkey='commit'
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
            
    