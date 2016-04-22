'''
Created on 22.11.2015

@author: killian
'''
from collections import defaultdict
from ddd.dataobjects import DddVariableDef,DddVariableDecl,\
    DddDatatype, DddComponent

class DddVisitor(object):
    def pre_order(self,obj):
        pass
    def post_order(self,obj):
        pass
    
class PostVisitor(DddVisitor):
    def __init__(self,f):
        self.f=f
    def post_order(self,obj):
        self.f(obj)  
        
class SourceVisitor:
    def __init__(self):
        self.cur_component=''
        self.cur_var = {}
        self.found_variables = defaultdict(lambda:{'definition':None,'output':None,'input':[]})
        #self.conditions = defaultdict(lambda:{'output':None,'input':[]})
    
    def pre_order(self,obj):
        if isinstance(obj, DddVariableDecl):
            self.found_variables[obj.definition.name]['definition']=obj.definition
            if obj.scope=='output':
                self.found_variables[obj.definition.name]['output']=obj.condition
            else:
                if obj.condition:
                    self.found_variables[obj.definition.name]['input'].append(obj.condition)
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        pass
    
class ConditionVisitor:
    def __init__(self):
        self.conditions = {}
    
    def pre_order(self,obj):
        if isinstance(obj, DddVariableDecl):
            if obj.condition:
                self.conditions[obj.condition]=False
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
            #self.found_variables[self.component_stack[-1]][obj.definition.name][conversion.get(obj.scope,obj.scope)].append(self.component_stack[-1])
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
        if not self.found.get(obj.getHash(),None):
            self.data[obj.getKey()].append(obj)
            self.found.update({obj.getHash():True})
    def in_order(self,obj):
        pass
    def post_order(self,obj):
        pass

