'''
Created on 22.11.2015

@author: killian
'''
from ddd.file import Handler
from ddd.dataobjects import DataObjectFactory, DddCommit
import visitors

import getpass
import os
import datetime
import pystache
import glob
import sys
import codecs
from ddd.visitors import SourceVisitor, ConditionVisitor, PostVisitor


               


class DataObjectRepository:
    def __init__(self,path,filehandler):
        self.path=path
        self.objects={}
        self.filehandler = filehandler
    def get(self,hash):
        if hash in self.objects:
            return self.objects[hash]
        else:
            obj = self.filehandler.load(os.path.join(self.path,hash))
            if obj.getHash()!= hash:
                raise Exception('Corrupt File')
            self.objects[hash]=obj
            return obj
    def store(self,object):
        def storage(object):
            h=object.getHash()
            if h not in self.objects:
                self.filehandler.dump(object,os.path.join(self.path,h),hashed=True)
                self.objects[h]=object
        object.accept(PostVisitor(storage))

class ComponentIndex:
    def __init__(self,path,repo):
        self.path = path
        self.index = {}
        self.repo=repo
        for t in map(lambda x:os.path.split(x)[1],glob.glob(os.path.join(self.path,'*'))):
            self.index[t]={}
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
        if object.classkey not in self.index:
            try:
                os.makedirs(os.path.join(self.path,object.classkey))  
            except OSError as e:
                # if the dict has been created by another instance of ddd
                # we can ignore the error and go on "OSError: [Errno 17] File exists"
                # otherwise re-raise the error
                if e.errno != 17:
                    raise
            self.index[object.classkey]={}
        self.index[object.classkey][object.name]=object
        with open(os.path.join(self.path,object.classkey,object.name),'w') as fp:
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
    

class DB:
    
    def __init__(self,repopath):
       
        self.configpath=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),'cfg')
        
        
        self.repopath = repopath
        
        self.factory = DataObjectFactory()
        
        self.repo=DataObjectRepository(os.path.join(repopath,'objects'),None)
        
        self.index = ComponentIndex(os.path.join(repopath,'index'),self.repo)
        self.tags = VersionTag(os.path.join(repopath,'tags'),self.repo)
       
        self.handler = Handler(self.repo,self.index,self.factory)
        self.repo.filehandler=self.handler
    def add(self,filename):
        tmp=self.handler.load(filename)
        self.repo.store(tmp)
        self.index.add(tmp)
    def open(self,filename):
        tmp=self.handler.load(filename)
        return tmp
    def dump(self,object,filename):
        self.handler.dump(object, filename)
    
    def check(self,project,conditions):
        print "Checking current Project"
        e = 0   
        visitor=visitors.CheckVisitor(conditions=conditions)
        project.accept(visitor)
        
        for vname,usage in visitor.variable_versions.items():
            if len(usage.keys())>1:
                print "Inconsistent Versions used for: "+vname
                for v in usage:
                    print " - Version: "+v+' in '+', '.join(map(lambda x:x.name,usage[v]))
                e+=1
        for comp in visitor.found_components:
            for vname,value in visitor.found_variables[comp].iteritems():
                if len(value.get('output',[]))>1:
                    print "Multiple Outputs for: "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:x.name,value['output']))
                    e+=1
                if len(value.get('input',[]))>0:
                    if len(value.get('output',[]))==0:
                        e+=1
                        print "Input with no Output for "+vname+" in Components:\n - "+"\n - ".join(map(lambda x:x.name,value['input']))
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
            o.accept(visitor)
        viewerdata=visitor.data
        viewerdata.update({'tags':[{'tag':t,'commit':o} for t,o in self.tags.items()]})
        with codecs.open('viewer.html','w',encoding='utf-8') as fp:
            fp.write(r.render_name('viewer.html',visitor.data))
    
    def commit_and_tag(self,object,tag,message):
        print "Creating Commit"
        c=DddCommit(message=message,obj=object,user=getpass.getuser(),timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        print "Commit hash: "+c.getHash()
        self.repo.store(c)
        print c.user
        print "Adding Tag"
        self.tags.create(tag,c)
        
        
    def export_source(self,data=None,config=None,filename=None,template=''):
        
        r = pystache.Renderer(search_dirs=os.path.join(self.configpath,'templates'),escape=lambda x:x)
        
        v = SourceVisitor()
        data.accept(v)
        
        out = {'name':data.filename,
               'hash':data.getHash(),
               'groups':[]}
        sectionindex={}
        idx=0
        for section in config.memorysections:
            out['groups'].append({'groupname':section.name,'definitions':[]})
            sectionindex[section.name]=idx
            idx+=1
        
        for name,var in v.found_variables.items():
            for section in config.memorysections:
                match=True
                for key,value in section.conditions.items():
                    if var['definition'].datatype.__dict__[key]!=value:
                        match=False
                        break
                if match:
                    #print var['definition'].name+' matched into '+section.name
                    out['groups'][sectionindex[section.name]]['definitions'].append(var)
                    break
            if not match:
                raise Exception('Variable '+var['definition'].name+' could not be assigned to any memory-section')
        for group in out['groups']:
            group['definitions'].sort(key=lambda x: x['definition'].name)
            
        with open(filename,'wb') as fp:
            fp.write(r.render_name(template,out))
        
    def export_conditions(self,obj,filename=None):
        
        r = pystache.Renderer(search_dirs=os.path.join(self.configpath,'templates'),escape=lambda x:x)
        
        v = ConditionVisitor()
        obj.accept(v)
        
        data = map(lambda x: {"condition":x,"last":False},v.conditions.keys())
        data[-1]['last']=True
        
        with open(filename,'wb') as fp:
            fp.write(r.render_name('conditions.json',{'conditions':data,'conditionheader':obj.config.conditionheader}))
    
        
    def init(self,path='repo'):
        print "Initializing repoisitory structure in "+path+" ..."
        
    