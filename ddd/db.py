import glob
import json
from ddd.file import Handler
import hashlib
import os

class DataObject:
    def __init__(self,data):
        self.data=data
    def __hash__(self):
        return hash(json.dumps(self.data,sort_keys=True))
    def __eq__(self,other):
        return self.data == other.data


class DB:
    
    def __init__(self):
       
        self.objectnames = {'variable':None,'datatype':None}
        
        self.handler = Handler()
        
        self.object_by_hash = {'variable':{},'component':{},'datatype':{}}
        self.name_by_hash = {'variable':{},'component':{},'datatype':{}}
    
    def recload(self,data,name):
        objname = data.keys()[0]
        print "Recursively Loading "+objname
        new_data = {objname:{}}
        for key in data[objname]:
            # check if the key is one of the "reserved" ddd types
            # if yes, it has to be treated as a reference
            if self.objectnames.has_key(key):
                #print "Object Found: "+key
                if type(data[objname][key]) == type({}):
                    # It is an inlined Object, we can directly load the referenced object
                    new_data[objname][key] = self.recload(data[objname],'')
                elif type( data[objname][key]) == type(''):
                    print 'Reference FK: '+key
                elif type( data[objname][key]) == type([]):
                    #print "Many-To-Many: "+key
                    new_data[objname][key]=[]
                    for ref in data[objname][key]:
                        tmpname=ref.keys()[0]
                        fname = os.path.join(self.root_folder,'variables',tmpname+'.ddd')
                        tmpname,res=self.handler.load(fname)
                        tmphash = self.recload(res,tmpname)
                        new_data[objname][key].append({tmphash:ref[tmpname]})
                        #del new_data[objname][key][ref]
                        #ref[tmphash]=ref.pop(tmpname)
            else:
                print key + ': '+ data[objname][key]
                new_data[objname][key]=data[objname][key]
        
        print "Calculating Hash on:"
        hashstring=json.dumps({name:new_data[objname]},sort_keys=True)
        print hashstring
        tmphash=hashlib.sha1(hashstring).hexdigest()
        print 'Creating '+objname
        self.name_by_hash[objname][tmphash]=name
        self.object_by_hash[objname][tmphash]=data
        #self.objectnames[objname].create(**data[objname])
        #TODO: Add to DB-Lists
        return tmphash
        
    
    # return a ddd_object corresponding to the name or hash
    # if both arguments are given, both have to match
    def getComponent(self,name=None,hash=None):
        d = Component.get(name=name)
        
        return d
            
    def load(self,path):
        print "Loading DDD DB"
        self.root_folder = path
        list = glob.glob(path+'/*.ddd')
        if len(list)==0:
            print "No .ddd file found in: "+path
            return
        elif len(list)>1:
            print "Multiple .ddd files found in: "+path
            print "The root-level of a DDD db should contain only one file"
            return
        else:
            print "Found file: "+list[0]
            name,res=self.handler.load(list[0])
            level = res.keys()[0]
            
            print "object name: "+name
            print "it is a type: "+level
            
            if level=='project':
                #self.load_project(self,list[0])
                print "projects not supported yet"
            elif level == 'component':
                #self.load_component(list[0])
                self.recload(res,name)
                
            elif level == 'variable':
                print "Loading of single variables is not supported"  
            
    def dump(self, object,path=None):
        if path == None:
            path = self.root_folder
        #object.dump(path)
        print object.name
        for d in Variable.select():
            print d.name
    