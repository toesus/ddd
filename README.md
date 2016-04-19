# ddd
Distributed Data-Dictionary for Global Variables in Embedded Software Projects.

For a detialed description check the [specification](documentation/spec.md)
## Dependencies
- jsonschema https://github.com/Julian/jsonschema

## Example
The repository includes test data, you can run:
`make project_check` in the folder `test/inconsistent_project`
Which will produce an output such as:
```
Checking current Project
Inconsistent Versions used for: Variable2
 - Version: ef4465ade36f6e2db1e0492c372a72c62be0a78d in ModuleA
 - Version: c03d91e2f98ca16aa25736a84e54b8e637ebcbb3 in ModuleB
Project is not consistent, 1 errors found
make: *** [project_check] Fehler 1
```
