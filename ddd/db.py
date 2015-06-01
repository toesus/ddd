import glob
import json
from ddd.file import Handler
import hashlib
import os
import pystache
from fileinput import filename
from collections import defaultdict

class CheckVisitor:
    def __init__(self):
        self.cur_component=''
        self.found_variables = defaultdict(lambda :dict({'input':[],'output':[],'local':[]}))
    
    def __call__(self,tree,obj):
        if tree['type']=='component':
            self.cur_component=tree['name']
        elif tree['type']=='variable-list':
            self.found_variables[obj['variable'][0]][obj['type']].append(self.cur_component)

class DB:
    
    def __init__(self):
       
        self.objectnames = {'variable-list':None,
                            'variable':'variables/',
                            'datatype':None,
                            'project':None,
                            'component':'*/',
                            'component-list':'*/'}
        
        self.handler = Handler()
        
        self.objects = {}
        self.tree = {}
        self.wc_files = defaultdict(list)
        
    def walk(self,visitor,h):
#         if self.tree[h]['type']=='component':
#             comp=self.tree[h]['name']
        o = self.objects.get(self.tree.get(h,{})['object'],{})
        visitor(self.tree.get(h,{}),o)
        
        for key,value in o.iteritems():
            if self.objectnames.has_key(key):
                    if type(value)!=type([]):
                        value = [value]
                    for listvalue in value:
                        self.walk(visitor,listvalue)
        return
    
    def recload(self,objtype,data,name,filename):
        #objtype = data.keys()[0]
        print "Recursively Loading "+objtype
        new_data = {}
        for key,value in data.iteritems():
            # check if the key is one of the "reserved" ddd types
            # if yes, it has to be treated as a reference
            if self.objectnames.has_key(key):
                #print "Object Found: "+key
                if type(value)!=type([]):
                    value = [value]
                new_data[key]=[]
                for listvalue in value:
                    if type(listvalue) == type({}):
                        # It is an inlined Object, we can directly load the referenced object
                        new_data[key].append(self.recload(key,listvalue,'',filename))
                    elif type( listvalue) == type(u''):
                        tmpsearch=os.path.join(os.path.split(filename)[0],self.objectnames[key],listvalue+'.ddd')
                        fname = glob.glob(tmpsearch)
                        if len(fname)==0:
                            raise Exception('The file '+tmpsearch+' does not exist!')
                        tmpname,tmptype,res,tmpfilename=self.handler.load(fname[0],expected_type=key)
                        tmphash = self.recload(tmptype,res,tmpname,fname[0])
                        new_data[key].append(tmphash)
            else:
                print key + ': '+ value
                new_data[key]=value
        
        print "Calculating Hash on:"
        ohashstring=json.dumps(new_data,sort_keys=True)
        print ohashstring
        otmphash=hashlib.sha1(ohashstring).hexdigest()
        print 'Creating '+objtype
        self.objects[otmphash]=new_data
        
        t={'object':otmphash,
           'type':objtype,
           'name':name,
           'parent':None}
        thash=hashlib.sha1(json.dumps(t,sort_keys=True)).hexdigest()
        self.tree[thash]=t
        
        self.wc_files[thash].append(filename)
        
        return thash
        
    
            
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
                        tmp = json.load(fp)
                        self.objects.update(tmp['objects'])
                        self.tree.update(tmp['tree'])
                return self.recload(level,res,name,flist[0])
                
            elif level == 'variable':
                print "Loading of single variables is not supported"
    
    def check(self,hash):
        print "Checking current Project"
        e = 0   
        visitor=CheckVisitor()
        self.walk(visitor,hash)
        
        hash_by_name = {}
        for v in visitor.found_variables:
            if hash_by_name.has_key(self.tree[v]['name']):
                print "Inconsistent Versions used for: "+self.tree[v]['name']
                e+=1
            hash_by_name[self.tree[v]['name']]=v
        for hash,value in visitor.found_variables.iteritems():
            if len(value.get('output',[]))>1:
                print "Multiple Outputs for: "+self.tree[hash]['name']+" in Components: "+str(value['output'])
                e+=1
            if len(value.get('input',[]))>0:
                if len(value.get('output',[]))==0:
                    e+=1
                    print "Input with no Output for "+self.tree[hash]['name']+" in Components: "+str(value['input'])
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
            for h,o in filter(lambda o: o[1]['type']==objecttype, self.tree.iteritems()):
                tmp_list.append({'hash':h,'name':o['name'],'wc':False,'raw':json.dumps(self.objects[o['object']],indent=4)})#self.wc_by_hash[objecttype].get(obj,False)})
            viewerdata['types'].append({'type':objecttype,'objects':tmp_list})
        with open('viewer.html','w') as fp:
            fp.write(r.render_name('viewer.html',viewerdata))
    
    def commit(self,path='repo'):
        print "Commiting to local repository..."
        with open(os.path.join(path,'repo.ddd'),'w') as fp:
            json.dump({'objects':self.objects,'tree':self.tree},fp,indent=4,sort_keys=True)
    
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
        
    