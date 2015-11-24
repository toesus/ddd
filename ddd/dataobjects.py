'''
Created on 22.11.2015

@author: killian
'''
import json
import hashlib

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

class DddDatatype(DataObject):
    def __init__(self,basetype='',conversion=''):
        self.basetype=basetype
        self.conversion=conversion
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'basetype':self.basetype,
               'conversion':self.conversion}})
        return tmp
    @classmethod
    def getChildKeys(cls):
        return []
    @classmethod
    def getKey(cls):
        return 'datatype'
        
class DddComponent(DataObject):
    def __init__(self,name='',declarations=None,subcomponents=None):
        self.name=name
        self.variablescope=0
        if declarations is not None:
            self.declarations=declarations
        else:
            self.declarations=[]
        if subcomponents is not None:
            self.subcomponents = subcomponents
        else:
            self.subcomponents = []
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'name':self.name}})
        return tmp
        #return {'variablelist':sorted([(x.hash if hashed else x.getJsonDict()) for x in self.variablelist]),
        #        'subcomponents':sorted([(x.hash if hashed else x.getJsonDict()) for x in self.subcomponents])}
    def getChildren(self):
        return self.declarations + self.subcomponents
    def appendChild(self, obj):
        if isinstance(obj,DddVariableDecl):
            self.declarations.append(obj)
        elif isinstance(obj,DddComponent):
            self.subcomponents.append(obj)
        else:
            raise Exception("Unsupported Child")
    @classmethod
    def getKey(cls):
        return 'component'
    
class DddVariableDef(DataObject):
    def __init__(self,name='',datatype=None):
        self.name=name
        self.datatype=datatype
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'name':self.name}})#,'children':([self.getChildren()[0].hash] if hashed else [self.getChildren()[0].getJsonDict()])}})
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
    def __init__(self,scope='local',definition=None):
        self.definition=definition
        self.scope=scope
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        tmp = DataObject.getJsonDict(self,hashed)
        tmp.update({'data':{'scope':self.scope}})#,'children':([self.getChildren()[0].hash] if hashed else [self.getChildren()[0].getJsonDict()])}})
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
    
    