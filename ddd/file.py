import json
import jsonschema
import os
import glob
import codecs


class Handler:
    def __init__(self):
        self.validators = {}
                
    def load(self,filename,object_hook=None):
        with codecs.open(filename,'r',encoding='utf-8') as fp:
            data = json.load(fp,encoding='utf-8',object_hook=object_hook)
        return data
    
    def dump(self,data,filename):
        with codecs.open(filename,'w',encoding='utf-8') as fp:
            json.dump(data,fp,indent=4,sort_keys=True,ensure_ascii=False)