import glob
import json
from ddd.file import Handler
import hashlib
import os
import pystache

class DataObject:
    def __init__(self,data):
        self.data=data
    def __hash__(self):
        return hash(json.dumps(self.data,sort_keys=True))
    def __eq__(self,other):
        return self.data == other.data


class DB:
    
    def __init__(self):
       
        self.objectnames = {'variable':'/variables/','datatype':None,'project':None,'component':'/*/'}
        
        self.handler = Handler()
        
        self.object_by_hash = {'variable':{},'component':{},'datatype':{},'project':{}}
        self.name_by_hash = {'variable':{},'component':{},'datatype':{},'project':{}}
        self.wc_by_hash = {'variable':{},'component':{},'datatype':{},'project':{}}
    
    def recload(self,data,name,path):
        objname = data.keys()[0]
        print "Recursively Loading "+objname
        new_data = {}
        for key in data[objname]:
            # check if the key is one of the "reserved" ddd types
            # if yes, it has to be treated as a reference
            if self.objectnames.has_key(key):
                #print "Object Found: "+key
                if type(data[objname][key]) == type({}):
                    # It is an inlined Object, we can directly load the referenced object
                    new_data[key] = self.recload(data[objname],'',path)
                elif type( data[objname][key]) == type(''):
                    print 'Reference FK: '+key
                elif type( data[objname][key]) == type([]):
                    #print "Many-To-Many: "+key
                    new_data[key]=[]
                    for ref in data[objname][key]:
                        if type(ref)==type(u""):
                            tmpname = ref
                        else:
                            tmpname=ref.keys()[0]
                        flist = glob.glob(path+self.objectnames[key]+tmpname+'.ddd')
                        if len(flist)!=0:
                            fname = os.path.join(flist[0])
                        tmpname,res=self.handler.load(fname)
                        tmphash = self.recload(res,tmpname,os.path.dirname(fname))
                        if type(ref)==type(u""):
                            new_data[key].append(tmphash)
                        else:
                            new_data[key].append({tmphash:ref[tmpname]})
                        
                        #del new_data[objname][key][ref]
                        #ref[tmphash]=ref.pop(tmpname)
            else:
                print key + ': '+ data[objname][key]
                new_data[key]=data[objname][key]
        
        print "Calculating Hash on:"
        hashstring=json.dumps({name:{objname:new_data}},sort_keys=True)
        print hashstring
        tmphash=hashlib.sha1(hashstring).hexdigest()
        print 'Creating '+objname
        self.name_by_hash[objname][tmphash]=name
        self.object_by_hash[objname][tmphash]=new_data
        self.wc_by_hash[objname][tmphash]=1
        #self.objectnames[objname].create(**data[objname])
        #TODO: Add to DB-Lists
        return tmphash
        
    
            
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
            name,res=self.handler.load(flist[0])
            level = res.keys()[0]
            
            if level=='project' or level == 'component':
                with open(os.path.join('repo','repo.ddd'),'r') as fp:
                    tmp = json.load(fp)
                    self.name_by_hash.update(tmp['names'])
                    self.object_by_hash.update(tmp['objects'])
                self.recload(res,name,path)
                
            elif level == 'variable':
                print "Loading of single variables is not supported"  
    
    def check(self):
        print "Checking current Project"
        e = 0   
        hash_by_name = {}
        for v in self.name_by_hash['variable']:
            if hash_by_name.has_key(self.name_by_hash['variable'][v]):
                print "Inconsistent Versions used for: "+self.name_by_hash['variable'][v]
                e+=1
            hash_by_name[self.name_by_hash['variable'][v]]=v
        
        vartype_by_name = {}
        for c in self.object_by_hash['component']:
            for v in self.object_by_hash['component'][c]['variable']:
                if not vartype_by_name.has_key(self.name_by_hash['variable'][v.keys()[0]]):
                    vartype_by_name[self.name_by_hash['variable'][v.keys()[0]]]={'input':[],'output':[],'local':[]}
                vartype_by_name[self.name_by_hash['variable'][v.keys()[0]]][v[v.keys()[0]]['type']].append(c)
              
        for t in vartype_by_name:
            if len(vartype_by_name[t]['output'])>1:
                print "Multiple Outputs for: "+self.name_by_hash['variable'][t]+" in Components: "+str(vartype_by_name[t]['output'])
                e+=1
            if len(vartype_by_name[t]['input'])>0:
                if len(vartype_by_name[t]['output'])==0:
                    e+=1
                    print "Input with no Output for "+t+" in Components: "+str(map(lambda x: self.name_by_hash['component'][x],vartype_by_name[t]['input']))     
        if e>0:
            print "Project is not consistent, "+str(e)+" errors found"
        else:
            print "Project is consistent"
        return e
    
    def view(self,path='.'):
        print "Viewing Repository..."
        r = pystache.Renderer(search_dirs='./cfg/templates')
        
        viewerdata={}
        for objecttype in self.object_by_hash:
            tmp_list=[]
            for obj in self.object_by_hash[objecttype]:
                tmp_list.append({'hash':obj,'name':self.name_by_hash[objecttype][obj],'wc':self.wc_by_hash[objecttype].get(obj,False)})
            viewerdata.update({objecttype:tmp_list})
        with open('viewer.html','w') as fp:
            fp.write(r.render_name('viewer.html',viewerdata))
    
    def commit(self,path='repo'):
        print "Commiting to local repository..."
        with open(os.path.join(path,'repo.ddd'),'w') as fp:
            json.dump({'names':self.name_by_hash,'objects':self.object_by_hash},fp,indent=4,sort_keys=True)
    
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
            
    def dump(self, object,path=None):
        if path == None:
            path = self.root_folder
        #object.dump(path)
        print object.name
        for d in Variable.select():
            print d.name
    