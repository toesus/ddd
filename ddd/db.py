import glob
import json
from ddd.file import Handler
import hashlib
import os
from peewee import *



pwdb = SqliteDatabase(':memory:')
    
class ddd(Model):
    class Meta:
        database = pwdb

class Datatype(ddd):
    hash = CharField(primary_key=True)
    basetype = CharField()
    conversion = CharField()
    
class Variable(ddd):
    hash = CharField(primary_key=True)
    name = CharField()
    datatype = ForeignKeyField(Datatype,related_name='variable_id')
        
class Component(ddd):
    hash = CharField(primary_key=True)
    name = CharField()

class ComponentVariables(ddd):
    type = CharField()
    variable = ForeignKeyField(Variable)  
    component = ForeignKeyField(Component)
    
class DB:
    
    tables = [Datatype,Variable,Component,ComponentVariables]
    
    def __init__(self):
        pwdb.connect()
        pwdb.create_tables(self.tables)
        
        self.objectnames = {}
        for t in self.tables:
            self.objectnames.update({t._meta.name:t})
        self.root_folder = ''
        
        self.handler = Handler()
    
    def recload(self,data,name):
        objname = data.keys()[0]
        print "Recursively Loading "+objname
        manytomany = {}
        hashstring = objname
        for key in data[objname]:
            if self.objectnames.has_key(key):
                #print "Object Found: "+key
                if type(data[objname][key]) == type({}):
                    #print 'Inline FK: '+key
                    data[objname][key] = self.recload(data[objname],'')
                elif type( data[objname][key]) == type(''):
                    print 'Reference FK: '+key
                elif type( data[objname][key]) == type([]):
                    #print "Many-To-Many: "+key
                    tmpref = [x for x in self.objectnames[key]._meta.rel.keys() if x != objname][0]
                    manytomany[key]=[]
                    for ref in data[objname][key]:
                        tmpname=ref.keys()[0]
                        fname = os.path.join(self.root_folder,'variables',tmpname+'.ddd')
                        tmpname,res=self.handler.load(fname)
                        tmphash = self.recload(res,tmpname)
                        tmpdict = {tmpref:tmphash}
                        tmpdict.update(ref[tmpname])
                        manytomany[key].append(tmpdict)
                        hashstring += tmphash
                        ref[tmphash]=ref.pop(tmpname)
            else:
                print key + ': '+ data[objname][key]
                hashstring += key +':'+data[objname][key]
        
        print "Calculating Hash on:"
        hashstring=json.dumps({name:data[objname]},sort_keys=True)
        print hashstring
        data[objname]['hash']=hashlib.sha1(hashstring).hexdigest()
        for key in manytomany:
            for ref in manytomany[key]:
                ref.update({objname:data[objname]['hash']})
                self.objectnames[key].create(**ref)
        data[objname]['name']=name
        print 'Creating '+objname
        self.objectnames[objname].create(**data[objname])
        return data[objname]['hash']
        
    
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
    