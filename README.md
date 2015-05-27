# ddd
Distributed Data-Dictionary for Global Variables in Embedded Software Projects
## Dependencies
- jsonschema https://github.com/Julian/jsonschema

## Example
The repository includes test data, you can run:
`python ddd.py check test/inconsistent_project`
Which will produce an output such as:
```
Checking current Project
Inconsistent Versions used for: VariableB
Input with no Output for VariableD in Components: [u'ModuleB']
Project is not consistent, 2 errors found
```
