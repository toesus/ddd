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
    
    def __call__(self,h,tree,obj):
        if tree['type']=='component':
            self.cur_component=tree['name']
            self.found_variables[self.cur_component]['hash']=h
            self.found_variables[self.cur_component]['name']=self.cur_component
        elif tree['type']=='variable-list':
            self.cur_var.update({obj['variable']:obj['type']})
        elif tree['type']=='variable':
            if self.cur_var[h]=='output' or self.cur_var[h]=='local':
                self.found_variables[self.cur_component]['definitions'].append(tree['name'])
            self.found_variables[self.cur_component]['declarations'].append(tree['name'])
            
class CheckVisitor:
    def __init__(self):
        self.cur_component=''
        self.found_variables = defaultdict(lambda :dict({'input':[],'output':[],'local':[]}))
    def pre_order(self,obj):
        if obj.objtype=='component':
            self.cur_component=obj.name
        elif obj.objtype=='variable-list':
            self.found_variables[obj.children[0].hash][obj.data['type']].append(self.cur_component)
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
        if not obj.objtype=='repo' and not obj.objtype=='root':
            self.d[obj.hash]=obj


class DataObject:
    def __init__(self,data=None,name='',objtype='',hash=None,children=None):
        # this needs to be done to avoid mutable objects as default arguments
        if data is None: data = {}
        if children is None: children = []
        self.data = data
        self.children = children
        self.name=name
        self.objtype=objtype
        self.hash=hash
    def visit(self,visitor):
        visitor.pre_order(self)
        
        for c in self.children:
            c.visit(visitor)
            visitor.in_order(self)
        
        visitor.post_order(self)
    def getJsonDict(self):
        return {'data':self.data,
               'objtype':self.objtype,
               'name':self.name,
               #'hash':self.hash,
               'children':map(lambda c:c.hash,self.children)}
    def update_hash(self):
        tmpstring=json.dumps(self.getJsonDict(),sort_keys=True)
        print "Calculating Hash on: "+tmpstring
        newh=hashlib.sha1(tmpstring).hexdigest()
        if self.hash and self.hash!=newh:
            raise Exception('Object with a bad hash found')
        self.hash=newh
        
class DDDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataObject):
            return obj.getJsonDict()#json.dumps(obj.getJsonDict(),indent=4,sort_keys=True)
        else:
            return json.JSONEncoder.default(self, obj)
        
class DDDDecoder(json.JSONDecoder):
    def __init__(self,encoding):
            json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d): 
        if 'objtype' not in d:
            return d
        return DataObject(**d)
class DB:
    
    def __init__(self):
       
        self.objectnames = {'variable-list':None,
                            'variable':'variables/',
                            'datatype':None,
                            'project':None,
                            'component':'*/',
                            'component-list':'*/'}
        
        self.handler = Handler()
        
        self.root = DataObject(name='root', objtype='root')
        self.tree = {}
        self.wc_files = defaultdict(list)
        
    
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
                        tmpobj=self.recload(key,listvalue,'',filename)
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
        self.tree[hash].visit(visitor)
        
        hash_by_name = {}
        for v in visitor.found_variables:
            if hash_by_name.has_key(self.tree[v].name):
                print "Inconsistent Versions used for: "+self.tree[v].name
                e+=1
            hash_by_name[self.tree[v].name]=v
        for hash,value in visitor.found_variables.iteritems():
            if len(value.get('output',[]))>1:
                print "Multiple Outputs for: "+self.tree[hash].name+" in Components: "+str(value['output'])
                e+=1
            if len(value.get('input',[]))>0:
                if len(value.get('output',[]))==0:
                    e+=1
                    print "Input with no Output for "+self.tree[hash].name+" in Components: "+str(value['input'])
        if e>0:
            print "Project is not consistent, "+str(e)+" errors found"
        else:
            print "Project is consistent"
        return e
    
    def view(self,path='.'):
        print "Viewing Repository..."
        r = pystache.Renderer(search_dirs='./cfg/templates')
        
        viewerdata={'types':[]}
        for objecttype in self.objectnames:
            tmp_list=[]
            for h,o in filter(lambda o: o[1].objtype==objecttype, self.tree.iteritems()):
                tmp_list.append({'hash':o.hash,'name':o.name,'wc':False,'raw':json.dumps({'data':o.data,'children':map(lambda c:c.hash,o.children)},indent=4)})#self.wc_by_hash[objecttype].get(obj,False)})
            viewerdata['types'].append({'type':objecttype,'objects':tmp_list})
        with open('viewer.html','w') as fp:
            fp.write(r.render_name('viewer.html',viewerdata))
    
    def commit(self,path='repo'):
        print "Commiting to local repository..."
        with open(os.path.join(path,'repo.ddd'),'w') as fp:
            json.dump({'tree':self.tree},fp,indent=4,sort_keys=True,cls=DDDEncoder)
    
    def export_source(self,hash,path='source'):
        visitor = SourceVisitor()
        self.walk(visitor,hash)
        print visitor.found_variables
        r = pystache.Renderer(search_dirs='./cfg/templates')
        for m in visitor.found_variables:
            print r.render_name('decl.h',visitor.found_variables[m])
    
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
        
    