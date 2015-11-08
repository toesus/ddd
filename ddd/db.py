import glob
import json
from ddd.file import Handler
import hashlib
import os
import pystache
from fileinput import filename
from collections import defaultdict

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
        self.cur_component=''
        self.found_variables = defaultdict(lambda :dict({'input':[],'output':[],'local':[]}))
        self.variable_versions = defaultdict(lambda : defaultdict(lambda: []))
    def pre_order(self,obj):
        if isinstance(obj, DddComponent):
            self.cur_component=obj.hash
        elif isinstance(obj, DddVariable):
            self.variable_versions[obj.name][obj.datatype.hash].append(self.cur_component)
            self.found_variables[obj.name][obj.scope].append(self.cur_component)
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        pass
        
        
            
class HashVisitor:
    def __init__(self,hashdict):
        self.d = hashdict
    def pre_order(self,obj):
        pass
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        obj.update_hash()
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

class DataObject:
    def __init__(self):
        self.hash=None
    def getChildren(self):
        return []
    def visit(self,visitor):
        visitor.pre_order(self)
        
        for c in self.getChildren():
            c.visit(visitor)
            visitor.in_order(self)
        
        visitor.post_order(self)
        
    def getJsonDict(self,hashed=False):
        raise NotImplementedError
    def update_hash(self):
        tmpstring=json.dumps(self.getJsonDict(hashed=True),sort_keys=True)
        print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring).hexdigest()
        self.hash=newh

class DddDatatype(DataObject):
    def __init__(self,basetype='',conversion=''):
        self.basetype=basetype
        self.conversion=conversion
        
    def getJsonDict(self,hashed=False):
        return {'basetype':self.basetype,
               'conversion':self.conversion}
        
class DddComponent(DataObject):
    def __init__(self,variablelist=None,subcomponents=None):
        if variablelist is not None:
            self.variablelist=variablelist
        else:
            self.variablelist=[]
        if subcomponents is not None:
            self.subcomponents = subcomponents
        else:
            self.subcomponents = []
    def getJsonDict(self,hashed=False):
        return {'variablelist':sorted([(x.hash if hashed else x.getJsonDict()) for x in self.variablelist]),
                'subcomponents':sorted([(x.hash if hashed else x.getJsonDict()) for x in self.subcomponents])}
    def getChildren(self):
        return self.variablelist + self.subcomponents
    
class DddVariable(DataObject):
    def __init__(self,name='',datatype=None,scope='local'):
        self.name=name
        self.datatype=datatype
        self.scope=scope
        DataObject.__init__(self)
        
    def getJsonDict(self,hashed=False):
        return {'name':self.name,'datatype':(self.datatype.hash if hashed else self.datatype.getJsonDict()),'scope':self.scope}
    def getChildren(self):
        return [self.datatype]
               
class DDDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataObject):
            return obj.getJsonDict()
        else:
            return json.JSONEncoder.default(self, obj)
        
class DDDDecoder(json.JSONDecoder):
    def __init__(self,encoding):
            json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d): 
        if 'variablelist' in d:
            tmpvars=[]
            for var in d['variablelist']:
                tmpvars.append(DddVariable(**var))
            return {'variablelist':tmpvars}
        elif 'basetype' in d:
            return DddDatatype(**d)
        elif 'component' in d:
            return DddComponent(**(d['component']))
        else:
            return d
    
class DB:
    
    def __init__(self):
       
        self.objectnames = {'variable-list':None,
                            'variable':'variables/',
                            'datatype':None,
                            'project':None,
                            'component':'*/',
                            'component-list':'*/'}
        
        self.handler = Handler()
        
        
        self.wc_files = defaultdict(list)
        
        self.objects = {} # hash:DataObject
        self.index = {} # modulename:hash
        self.modulenames = {}
        
    def add(self,filename):
        modulename = os.path.splitext(os.path.basename(filename))[0]
        with open(filename,'r') as fp:
            tmp=json.load(fp,cls=DDDDecoder)
        tmpc = []
        for sc in tmp.subcomponents:
            if sc in self.index:
                tmpc.append(self.index[sc])
        tmp.subcomponents = tmpc
        hv = HashVisitor(self.objects)
        tmp.visit(hv)
        self.index[modulename]=tmp
        self.modulenames[tmp.hash]=modulename
        
    def recload(self,objtype,data,name,filename):
        #objtype = data.keys()[0]
        #print "Recursively Loading "+objtype
        new_data = {}
        new_children = []
        for key,value in data.iteritems():
            # check if the key is one of the "reserved" ddd types
            # if yes, it has to be treated as a reference
            if self.objectnames.has_key(key):
                #print "Object Found: "+key
                
                for listvalue in value if key.endswith('-list') else [value]:
                    if type(listvalue) == type({}):
                        # It is an inlined Object, we can directly load the referenced object
                        tmpobj=self.recload(key,listvalue,listvalue.get('name',''),filename)
                    elif type( listvalue) == type(u''):
                        tmpsearch=os.path.join(os.path.split(filename)[0],self.objectnames[key],listvalue+'.ddd')
                        fname = glob.glob(tmpsearch)
                        if len(fname)==0:
                            raise Exception('The file '+tmpsearch+' does not exist!')
                        tmpname,tmptype,res,tmpfilename=self.handler.load(fname[0],expected_type=key)
                        tmpobj = self.recload(tmptype,res,tmpname,fname[0])
                    new_children.append(tmpobj)
            else:
                #print key + ': '+ str(value)
                new_data[key]=value
        newobj = DataObject(data=new_data, name=name, objtype=objtype, children=new_children)
        newobj.update_hash()
        tmp=self.tree.get(newobj.hash,None)
        if not tmp:
            print "Object does not exist in repo"
        return newobj
        
    
            
    def load(self,path):
        print "Loading DDD DB"
        self.root_folder = path
        flist = glob.glob(path+'/*.ddd')
        if len(flist)==0:
            print "No .ddd file found in: "+path
            return
        elif len(flist)>1:
            print "Multiple .ddd files found in: "+path
            print "The root-level of a DDD db should contain only one file"
            return
        else:
            print "Found file: "+flist[0]
            name,level,res,filename=self.handler.load(flist[0])
            
            if level=='project' or level == 'component':
                if os.path.isfile(os.path.join('repo','repo.ddd')):
                    with open(os.path.join('repo','repo.ddd'),'r') as fp:
                        tmp = json.load(fp,cls=DDDDecoder)
                        orphans = tmp['tree'].copy()
                        for t,o in tmp['tree'].iteritems():
                            o.hash=t
                            for idx,c in enumerate(o.children):
                                o.children[idx]=tmp['tree'][c]
                                orphans.pop(c,None)
                        r=DataObject(name='LocalRepository', objtype='repo')
                        self.root.children.append(r)
                        for h in orphans:
                            print "orphan in repo: "+orphans[h].objtype+' '+h
                            if orphans[h].objtype=='project':
                                r.children.append(orphans[h])  
                        r.visit(HashVisitor(self.tree))
                tmpobj=self.recload(level,res,name,flist[0])
                
                self.root.children.append(tmpobj)
                self.root.visit(HashVisitor(self.tree))
                return tmpobj.hash
                
            elif level == 'variable':
                print "Loading of single variables is not supported"
    
    def check(self,hash):
        print "Checking current Project"
        e = 0   
        visitor=CheckVisitor()
        self.objects[hash].visit(visitor)
        print visitor.variable_versions
        print visitor.found_variables
        hash_by_name = {}
        for vname,usage in visitor.variable_versions.items():
            if len(usage.keys())>1:
                print "Inconsistent Versions used for: "+vname
                for v in usage:
                    print " - Version: "+v+' in '+''.join(map(lambda x:self.modulenames[x],usage[v]))
                e+=1
            hash_by_name[vname]=usage.keys()[0]
        for vname,value in visitor.found_variables.iteritems():
            if len(value.get('output',[]))>1:
                print "Multiple Outputs for: "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:self.modulenames[x],value['output']))
                e+=1
            if len(value.get('input',[]))>0:
                if len(value.get('output',[]))==0:
                    e+=1
                    print "Input with no Output for "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:self.modulenames[x],value['input']))
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
        
    