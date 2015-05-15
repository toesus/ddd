import json
import jsonschema
import os
import glob

# Load a *.ddd File
# Validate the schema
class File:
    
    def __init__(self):
        
        self.dict = {}
        self.name = ''
            
        
    def load(self,filename):
        self.name = ''
        try:
            with open(filename, 'r') as fp:
                self.dict = json.load(fp)
                
        except (IOError) as e:
            print "ddd-json: Error when loading "+filename
            print str(e)
            self.dict = {}
            
        else:
            print "ddd-json: Loaded "+filename
            self.name = os.path.splitext(os.path.basename(filename))[0]
            
            
    def dump(self,filename):
        try:
            filename = filename +"/"+self.dict[self.dict.keys()[0]].pop('name')+".ddd"
            with open(filename, 'w') as fp:
                json.dump(self.dict, fp, indent=4, sort_keys=True)
        except IOError as e:
            print "ddd-json: Error when writing "+filename
            print str(e)
        else:
            print "ddd-json: Saved "+filename
            
class Handler:
    def __init__(self):
        self.validators = {}
        
        for f in glob.glob('./cfg/*.schema.json'):
            name = os.path.splitext(f)[0]
            name = os.path.splitext(name)[0]
            name = os.path.split(name)[1]
            print "Loading Schema "+name
            
            try:
                with open(f, 'r') as fp:
                    schema = json.load(fp)
                    jsonschema.Draft4Validator.check_schema(schema)
            except IOError as e:
                print "ddd-json: Error when reading "+f
                print str(e)        
            except jsonschema.SchemaError as e:
                print "ddd-json schema is not valid"
                print e
            else:
                self.validators[name] = jsonschema.Draft4Validator(schema)
                
    def load(self,filename):
        
        dddj = File()
        dddj.load(filename)
        print dddj.name
        dddtype = dddj.dict.keys()[0]
        errormsg = []
        if self.validators.has_key(dddtype):
            
            # use lazy validation to find all errors in one go
            errormsg = sorted(self.validators[dddtype].iter_errors(dddj.dict), key=str)
            
        else:
            raise Exception("ddd-json: Unknown object "+dddtype+" found in file "+filename)     
        
        if len(errormsg)>0:
            print "ddd-json: invalid json file loaded"
            for e in errormsg:
                print e.message 
        
        else:
            return dddj.name,dddj.dict
             