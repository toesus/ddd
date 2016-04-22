'''
Created on 22.11.2015

@author: killian
'''
import json
import hashlib
import fractions
import math

class DataObject(object):
    classkey='ddd_dataobject'
    def __init__(self):
        self.hash=None
        self.loaded = False
    @classmethod
    def getKey(cls):
        return cls.classkey
    def getChildren(self):
        return []
    def appendChild(self,obj):
        raise NotImplementedError
    def visit(self,visitor):
        visitor.pre_order(self)
        
        for c in self.getChildren():
            c.visit(visitor)
            visitor.in_order(self)
        
        visitor.post_order(self)
    def dumpDict(self,hashed=False,rec=False):
        if hashed and rec:
            return {'ddd_hash':self.getHash()}
        d = self.getJsonDict(hashed=False)
        #print d
        for key,value in d.items():
            if type(value)==type([]):
                tmplist=[]
                for e in value:
                    tmplist.append(e.dumpDict(hashed=hashed,rec=True))
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
    def __init__(self,type=None,fraction=0,numerator=None,denominator=None,offset=0):
        DddConversion.classkey='ddd_conversion'
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
    
    @classmethod
    def getChildKeys(cls):
        return []
    
    
class DddDatatype(DataObject):
    def __init__(self,basetype='',conversion=None,unit='-',constant=False):
        DddDatatype.classkey='ddd_datatype'
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
    def getChildren(self):
        return [self.conversion]
    def appendChild(self, obj):
        if isinstance(obj,DddConversion):
            self.conversion = obj
            
class DddProject(DataObject):
    def __init__(self,name='',components=None):
        DddProject.classkey='ddd_project'
        self.name=name
        if components is not None:
            self.components = components
        else:
            self.components = []
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'name':self.name})
        return tmp
    def getChildren(self):
        return self.components
    def appendChild(self, obj):
        if isinstance(obj,DddComponent):
            self.components.append(obj)
        else:
            raise Exception("Unsupported Child")

class DddComponent(DataObject):
    def __init__(self,name='',declarations=None):
        DddComponent.classkey='ddd_component'
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
    def getChildren(self):
        return self.declarations
    def appendChild(self, obj):
        if isinstance(obj,DddVariableDecl):
            self.declarations.append(obj)
        else:
            raise Exception("Unsupported Child")
    
class DddVariableDef(DataObject):
    def __init__(self,name='',datatype=None,min=0,max=0,displayformat='',dimensions=None):
        DddVariableDef.classkey='ddd_definition'
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
    def getChildren(self):
        return [self.datatype]
    def appendChild(self, obj):
        if isinstance(obj,DddDatatype):
            self.datatype = obj
    @classmethod
    def getChildKeys(cls):
        return ['datatype']

class DddVariableDecl(DataObject):
    def __init__(self,scope='local',definitionref=None,condition=None,**kwargs):
        DddVariableDecl.classkey='ddd_declaration'
        if not definitionref:
            self.definition=DddVariableDef()
        else:
            self.definition=definitionref
        self.scope=scope
        self.condition=condition
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,False)
        tmp.update({'scope':self.scope,
                    'condition':self.condition,
                    'definition':self.definition})
        return tmp
    def getChildren(self):
        return [self.definition]
    def appendChild(self, obj):
        if isinstance(obj,DddVariableDef):
            self.definition = obj
    @classmethod
    def getChildKeys(cls):
        return ['definition']

class DddCommit(DataObject):
    def __init__(self,message='',obj=None, user='',timestamp=None):
        DddCommit.classkey='ddd_commit'
        self.message=message
        self.obj=obj
        self.user = user
        self.timestamp=timestamp
        DataObject.__init__(self)
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, hashed)
        tmp.update({'message':self.message,
                    'user':self.user,
                    'timestamp':self.timestamp})
        return tmp
    def getChildren(self):
        return [self.obj]
    def appendChild(self, obj):
        if isinstance(obj,DataObject):
            self.obj = obj
            
    