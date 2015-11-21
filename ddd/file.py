import json
import jsonschema
import os
import glob


class Handler:
    def __init__(self):
        self.validators = {}
                
    def load(self,filename):
        with open(filename,'r') as fp:
            data = json.load(fp)
        return data
    
    def dump(self,data,filename):
        with open(filename,'w') as fp:
            json.dump(data,fp,indent=4,sort_keys=True)