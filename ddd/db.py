
import json
from ddd.file import Handler
from ddd.dataobjects import DddVariableDef,DddVariableDecl,\
    DddDatatype, DddComponent, DataObject, DddCommit
import visitors

import getpass
import os
import datetime
import pystache
from collections import defaultdict
import glob
import sys


               
class DDDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataObject):
            return obj.getJsonDict()
        else:
            return json.JSONEncoder.default(self, obj)
        
class WorkingCopyDecoder:
    def __init__(self,repo,index):
        self.index=index
        self.repo=repo
    def __call__(self, d):
        tmpdecl = []
        for decl in d.get('declarations',[]):
            datatype = DddDatatype(**decl['definition']['datatype'])
            vardef = DddVariableDef(name=decl['definition']['name'],datatype=datatype)
            tmpdecl.append(DddVariableDecl(scope=decl['scope'],definition=vardef))
        
        tmpsubc=[]
        for sub in d.get('subcomponents',[]):
            tmpsubc.append(self.index.get(sub))
        comp=DddComponent(name=d.get('name'),subcomponents=tmpsubc,declarations=tmpdecl)
        self.repo.store(comp)   
        return comp

class DataObjectRepository:
    def __init__(self,path,factory,filehandler):
        self.path=path
        self.objects={}
        self.filehandler = filehandler
        self.factory = factory
    def get(self,hash):
        if hash in self.objects:
            return self.objects[hash]
        else:
            data = self.filehandler.load(os.path.join(self.path,hash))
            objecttype = data.get('objecttype','')
            obj = self.factory.create_by_name(objecttype,**data['data'])
            for c in data.get('children',[]):
                obj.appendChild(self.get(c))
            
            if obj.getHash()!= hash:
                raise Exception('Corrupt File')
            self.objects[hash]=obj
            return obj
    def store(self,object):
        h=object.getHash()
        for c in object.getChildren():
            self.store(c)
        if h not in self.objects:
            self.filehandler.dump(object.getJsonDict(hashed=True),os.path.join(self.path,h))
            self.objects[h]=object

class ComponentIndex:
    def __init__(self,path,repo):
        self.path = path
        self.index = {}
        self.repo=repo
    def get(self,name):
        o = self.index.get(name,None)
        if o is not None:
            return o
        else:
            try:
                with open(os.path.join(self.path,name),'r') as fp:
                    h = fp.readline()
                    return self.repo.get(h)
            except IOError as e:
                print name+ " does not exist in Index"
            return None
    def add(self,object):
        self.index[object.name]=object
        with open(os.path.join(self.path,object.name),'w') as fp:
            fp.write(object.getHash())
            
class VersionTag(object):
    def __init__(self,path,repo):
        self.path = path
        self.repo = repo
    def create(self,tag,commit):
        filename=os.path.join(self.path,tag)
        if os.path.isfile(filename):
            raise Exception('Tag '+tag+' already exists')
        with open(os.path.join(self.path,tag),'w') as fp:
            fp.write(commit.getHash())
    def get(self,tag):
        try:
            with open(os.path.join(self.path,tag),'r') as fp:
                h = fp.readline()
                return self.repo.get(h)
        except IOError as e:
            print tag + " is not existing"
        return None
    def keys(self):
        return map(lambda x:os.path.split(x)[1],glob.glob(os.path.join(self.path,'*')))
    def items(self):
        return map(lambda x: (x,self.get(x)),self.keys())
    
class DataObjectFactory:
    def __init__(self):
        self.classes = {}
        self.count = 0
    def add_class(self,cls):
        self.classes[cls.getKey()]=cls
    def create_by_name(self,classname,**kwargs):
        tmp = self.classes[classname](**kwargs)
        self.count += 1
        return tmp
    def create_by_class(self,cls,**kwargs):
        self.count += 1
        return cls(**kwargs)
class DB:
    
    def __init__(self,repopath):
       
        self.objectnames = {'variable-list':None,
                            'variable':'variables/',
                            'datatype':None,
                            'project':None,
                            'component':'*/',
                            'component-list':'*/'}
        
        self.handler = Handler()
        self.repopath = repopath
        
        self.wc_files = defaultdict(list)
        
        #self.objects = {} # hash:DataObject
        
        self.modulenames = {}
        
        
        self.factory = DataObjectFactory()
        self.factory.add_class(DddVariableDecl)
        self.factory.add_class(DddVariableDef)
        self.factory.add_class(DddDatatype)
        self.factory.add_class(DddComponent)
        self.factory.add_class(DddCommit)
        self.repo=DataObjectRepository(os.path.join(repopath,'objects'),self.factory,Handler())
        
        self.index = ComponentIndex(os.path.join(repopath,'index'),self.repo)
        self.tags = VersionTag(os.path.join(repopath,'tags'),self.repo)
        self.decoder = WorkingCopyDecoder(self.repo,self.index)
          
    def add(self,filename):
        modulename = os.path.splitext(os.path.basename(filename))[0]
        with open(filename,'r') as fp:
            tmp=json.load(fp)
        tmpc=self.decoder(tmp['component'])
#         for sc in tmp.subcomponents:
#             if sc in self.index:
#                 tmpc.append(self.index[sc])
#             else:
#                 raise Exception("Subcomponent "+sc+" not found in Index")
#         tmp.subcomponents = tmpc
        h = tmpc.getHash()
        self.index.add(tmpc)
        #self.index[modulename]=tmpc
        self.modulenames[h]=modulename
        #with open(os.path.join(self.repopath,'index',modulename),'w') as fp:
        #    fp.write(h)
    
    def check(self,hash):
        print "Checking current Project"
        e = 0   
        visitor=visitors.CheckVisitor()
        self.repo.get(hash).visit(visitor)
        
        
        for vname,usage in visitor.variable_versions.items():
            if len(usage.keys())>1:
                print "Inconsistent Versions used for: "+vname
                for v in usage:
                    print " - Version: "+v+' in '+', '.join(map(lambda x:self.repo.get(x).name,usage[v]))
                e+=1
        for comp in visitor.found_components:
            for vname,value in visitor.found_variables[comp].iteritems():
                if len(value.get('output',[]))>1:
                    print "Multiple Outputs for: "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:self.repo.get(x).name,value['output']))
                    e+=1
                if len(value.get('input',[]))>0:
                    if len(value.get('output',[]))==0:
                        if not (comp in set( value['input']) and len(self.repo.get(comp).subcomponents)==0):
                            e+=1
                            print "Input with no Output for "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:self.repo.get(x).name,value['input']))
        if e>0:
            print "Project is not consistent, "+str(e)+" errors found"
        else:
            print "Project is consistent"
        return e
    
    def view(self,hash=None, name=None):
        print "Viewing Repository..."
        obj=[]
        if hash is None:
            if name is None:
                print "Viewing all tags..."
                for t,o in self.tags.items():
                    obj.append(o)  
            else:
                obj = [self.index.get(name)]
        else:
            obj=[self.repo.get(hash)]
        r = pystache.Renderer(search_dirs=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),'./cfg/templates'))
        
        visitor = visitors.ViewerVisitor()
        for o in obj:
            o.visit(visitor)
        viewerdata=visitor.data
        viewerdata.update({'tags':[{'tag':t,'commit':o} for t,o in self.tags.items()]})
        with open('viewer.html','w') as fp:
            fp.write(r.render_name('viewer.html',visitor.data))
    
    def commit_and_tag(self,name,tag,message):
        print "Creating Commit"
        c=DddCommit(message=message,obj=self.index.get(name),user=getpass.getuser(),timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        print "Commit hash: "+c.getHash()
        self.repo.store(c)
        print c.user
        print "Adding Tag"
        self.tags.create(tag,c)
    
    def export_source(self,hash,path='source'):
        r = pystache.Renderer(search_dirs='./cfg/templates')
        print r.render_name('decl.h',self.repo.get(hash))
        
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
        
    