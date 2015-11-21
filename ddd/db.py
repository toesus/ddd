import glob
import json
from ddd.file import Handler
import hashlib
import os
import pystache
from fileinput import filename
from collections import defaultdict
from duplicity.path import Path

class SourceVisitor:
    def __init__(self):
        self.cur_component=''
        self.cur_var = {}
        self.found_variables = defaultdict(lambda :dict({'hash':None,'name':None,'declarations':[],'definitions':[]}))
    
    def pre_order(self,obj):
        if obj.objtype=='component':
            self.cur_component=obj.name
            self.found_variables[self.cur_component]['hash']=obj.hash
            self.found_variables[self.cur_component]['name']=self.cur_component
        elif obj.objtype=='variable-list':
            self.cur_var.update({obj.children[0].hash:obj.data['type']})
            if obj.data['type']=='output' or obj.data['type']=='local':
                self.found_variables[self.cur_component]['definitions'].append(obj.children[0])
            self.found_variables[self.cur_component]['declarations'].append(obj.children[0])
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        pass
    
class CheckVisitor:
    def __init__(self):
        self.component_stack=['rootlevel']
        self.found_components=['rootlevel']
        self.found_variables = {'rootlevel':defaultdict(lambda :dict({'input':[],'output':[],'local':[]}))}
        self.variable_versions = defaultdict(lambda : defaultdict(lambda: []))
    def pre_order(self,obj):
        if isinstance(obj, DddComponent):
            self.component_stack.append(obj.getHash())
            self.found_components.append(obj.getHash())
            self.found_variables[self.component_stack[-1]]=defaultdict(lambda :dict({'input':[],'output':[],'local':[]}))
#             for v in obj.variablelist:
#                 self.found_variables[self.component_stack[-1]][v.name][v.scope].append(self.component_stack[-1])
        elif isinstance(obj, DddVariableDecl):
            #raise Exception
            self.variable_versions[obj.definition.name][obj.definition.getHash()].append(self.component_stack[-1])
            #add variable once at its component (interface variables)
            conversion = {'input':'output','output':'input'}
            self.found_variables[self.component_stack[-1]][obj.definition.name][conversion.get(obj.scope,obj.scope)].append(self.component_stack[-1])
            #add variable also at its "grandparent"
            self.found_variables[self.component_stack[-2]][obj.definition.name][obj.scope].append(self.component_stack[-1])
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        if isinstance(obj, DddComponent):
            c=self.component_stack.pop()
            
#             d = dict([[v.hash]+[v.name] for v in obj.variablelist])
#             
#             for varname,scope in self.found_variables[c].items():
#                 print scope
#                 self.found_variables[self.found_components[-1]][varname].update(scope)
            
class HashVisitor:
    def __init__(self,hashdict):
        self.d = hashdict
    def pre_order(self,obj):
        pass
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        obj.getHash()
        self.d[obj.hash]=obj

class ViewerVisitor:
    def __init__(self):
        self.data = defaultdict(lambda:[])
        self.found={}
    def pre_order(self,obj):
        if not self.found.get(obj.hash,None):
            self.data[obj.objtype].append({'name':obj.name,
                               'hash':obj.hash,
                               'data':obj.data,
                               'children':map(lambda c:{'hash':c.hash,'name':c.name,'objtype':c.objtype},obj.children)})
            self.found.update({obj.hash:True})
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        pass

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
        tmpstring=json.dumps(self.getJsonDict(hashed=True),sort_keys=True)
        #print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring).hexdigest()
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
            datatype = DddDatatype(decl['definition']['datatype'])
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
        
        self.objects = {} # hash:DataObject
        
        self.modulenames = {}
        
        
        self.factory = DataObjectFactory()
        self.factory.add_class(DddVariableDecl)
        self.factory.add_class(DddVariableDef)
        self.factory.add_class(DddDatatype)
        self.factory.add_class(DddComponent)
        self.repo=DataObjectRepository(os.path.join(repopath,'objects'),self.factory,Handler())
        
        self.index = ComponentIndex(os.path.join(repopath,'index'),self.repo)
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
        hv = HashVisitor(self.objects)
        h = tmpc.getHash()
        self.index.add(tmpc)
        #self.index[modulename]=tmpc
        self.modulenames[h]=modulename
        #with open(os.path.join(self.repopath,'index',modulename),'w') as fp:
        #    fp.write(h)
    
    def check(self,hash):
        print "Checking current Project"
        e = 0   
        visitor=CheckVisitor()
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
    
    def view(self,path='.'):
        print "Viewing Repository..."
        r = pystache.Renderer(search_dirs='./cfg/templates')
        
        visitor = ViewerVisitor()
        self.root.visit(visitor)
        viewerdata={'types':[]}
        for k,v in visitor.data.iteritems():
            viewerdata['types'].append({'type':k,'objects':v})
        with open('viewer.html','w') as fp:
            fp.write(r.render_name('viewer.html',viewerdata))
    
    def commit(self,path='repo'):
        print "Commiting to local repository..."
        with open(os.path.join(path,'repo.ddd'),'w') as fp:
            json.dump({'tree':self.tree},fp,indent=4,sort_keys=True,cls=DDDEncoder)
    
    def export_source(self,hash,path='source'):
        visitor = SourceVisitor()
        self.tree[hash].visit(visitor)
        print visitor.found_variables
        r = pystache.Renderer(search_dirs='./cfg/templates')
        for m in visitor.found_variables:
            print r.render_name('decl.h',visitor.found_variables[m])
    
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
        
    