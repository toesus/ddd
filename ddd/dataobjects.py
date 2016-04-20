'''
Created on 22.11.2015

@author: killian
'''
import json
import hashlib
import fractions
import math

class DataObject(object):
    def __init__(self):
        self.hash=None
        self.loaded = False
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
        
    def getJsonDict(self,hashed=False):
        return {'objecttype':self.__class__.getKey(),
                'children':[x.getHash() if hashed else x.getJsonDict(hashed) for x in self.getChildren()]}
    def getHash(self):
        tmpstring=json.dumps(self.getJsonDict(hashed=True),sort_keys=True,ensure_ascii=False)
        #print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring.encode('utf-8')).hexdigest()
        return newh

class DddConversion(DataObject):
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
        tmp = DataObject.getJsonDict(self, hashed=hashed)
        tmp.update({'data':{'numerator':self.factor.numerator,
                            'denominator':self.factor.denominator,
                            'offset':self.offset}})
        return tmp
    
    def get_name(self):
        return self.name
    
    @classmethod
    def getChildKeys(cls):
        return []
    @classmethod
    def getKey(cls):
        return 'conversion'
    
    
class DddDatatype(DataObject):
    def __init__(self,basetype='',conversion=None,unit='-',constant=False):
        self.basetype=basetype
        self.conversion=conversion
        self.unit=unit
        self.constant=constant
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'basetype':self.basetype,
                            'unit':self.unit,
                            'constant':self.constant}})
        return tmp
    
    def get_name(self):
        return self.basetype.upper()+'_'+self.conversion.get_name()
    def getChildren(self):
        return [self.conversion]
    def appendChild(self, obj):
        if isinstance(obj,DddConversion):
            self.conversion = obj
    @classmethod
    def getKey(cls):
        return 'datatype'
        
class DddProject(DataObject):
    def __init__(self,name='',components=None):
        self.name=name
        if components is not None:
            self.components = components
        else:
            self.components = []
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'name':self.name}})
        return tmp
    def getChildren(self):
        return self.components
    def appendChild(self, obj):
        if isinstance(obj,DddComponent):
            self.components.append(obj)
        else:
            raise Exception("Unsupported Child")
    @classmethod
    def getKey(cls):
        return 'project'

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
        tmp.update({'data':{'name':self.name}})
        return tmp
    def getChildren(self):
        return self.declarations
    def appendChild(self, obj):
        if isinstance(obj,DddVariableDecl):
            self.declarations.append(obj)
        else:
            raise Exception("Unsupported Child")
    @classmethod
    def getKey(cls):
        return 'component'
    
class DddVariableDef(DataObject):
    def __init__(self,name='',datatype=None,min=0,max=0,displayformat='',dimensions=None):
        self.name=name
        self.datatype=datatype
        self.min=min
        self.max=max
        self.displayformat=displayformat
        self.dimensions=dimensions
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'name':self.name,
                            'min':self.min,
                            'max':self.max,
                            'displayformat':self.displayformat,
                            'dimensions':self.dimensions}})#,'children':([self.getChildren()[0].hash] if hashed else [self.getChildren()[0].getJsonDict()])}})
        return tmp
    def getChildren(self):
        return [self.datatype]
    def appendChild(self, obj):
        if isinstance(obj,DddDatatype):
            self.datatype = obj
    @classmethod
    def getChildKeys(cls):
        return ['datatype']
    @classmethod
    def getKey(cls):
        return 'definition'

class DddVariableDecl(DataObject):
    def __init__(self,scope='local',definitionref=None,condition=None,**kwargs):
        self.definition=definitionref
        self.scope=scope
        self.condition=condition
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'scope':self.scope,'condition':self.condition}})#,'children':([self.getChildren()[0].hash] if hashed else [self.getChildren()[0].getJsonDict()])}})
        return tmp
    def getChildren(self):
        return [self.definition]
    def appendChild(self, obj):
        if isinstance(obj,DddVariableDef):
            self.definition = obj
    @classmethod
    def getChildKeys(cls):
        return ['definition']
    @classmethod
    def getKey(cls):
        return 'declaration'

class DddCommit(DataObject):
    def __init__(self,message='',obj=None, user='',timestamp=None):
        self.message=message
        self.obj=obj
        self.user = user
        self.timestamp=timestamp
        DataObject.__init__(self)
    def getJsonDict(self, hashed=False):
        tmp = DataObject.getJsonDict(self, hashed)
        tmp.update({'data':{'message':self.message,
                            'user':self.user,
                            'timestamp':self.timestamp}})
        return tmp
    def getChildren(self):
        return [self.obj]
    def appendChild(self, obj):
        if isinstance(obj,DataObject):
            self.obj = obj
    @classmethod
    def getKey(cls):
        return 'commit'
    
    