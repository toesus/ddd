'''
Created on 24.04.2016

@author: killian
'''
import json
import hashlib

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