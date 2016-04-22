import json
import jsonschema
import codecs
from dataobjects import DataObject

class DDDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataObject):
            return obj.dumpDict(True)
        else:
            return json.JSONEncoder.default(self, obj)
        
class DDDDecoder:
    def __init__(self,repo,index,factory):
        self.index=index
        self.repo=repo
        self.factory=factory
    def __call__(self, data):
        if data.keys()[0]=='ddd_index':
            return self.index.get(data[data.keys()[0]])
        elif data.keys()[0]=='ddd_hash':
            return self.repo.get(data[data.keys()[0]])
        else:
            return self.factory.create_by_name(data.pop('ddd_type'),**data)

class Handler:
    def __init__(self,repo,index,factory):
        self.validators = {}
        self.decoder = DDDDecoder(repo,index,factory)
                
    def load(self,filename):
        with codecs.open(filename,'r',encoding='utf-8') as fp:
            data = json.load(fp,encoding='utf-8',object_hook=self.decoder)
        return data
    
    def dump(self,data,filename):
        with codecs.open(filename,'w',encoding='utf-8') as fp:
            json.dump(data,fp,indent=4,sort_keys=True,ensure_ascii=False,cls=DDDEncoder)
            