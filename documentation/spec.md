# DDD Specification
## Introduction
The objective of DDD is to handle global variables in the scope of an embedded software development project.
It shall support component-based development methods, where individual components may be developed by different developers working in separate teams/companies.

The interfaces between the software-components consist simply in reading from / writing to global variables. DDD shall provide tools to avoid issues commonly associated with extensive use of global variables.
### Interface specification
DDD allows the software developer to clearly specify the (global variable) interface of a software-component. The scope of each variable can be defined (input/output of the component). The specification also includes physical units, scaling information for fixed-point datatypes, enums etc.
### Consistency check
When assembling several components into a complete project, DDD ensures consistency of the global variable interfaces. It checks that each variable is written by only one component, and that components which consume inputs agree on datatypes/units/scaling etc.
### Source Code generation
In order to enforce the access rules specified for each component, the global variables shall be defined and declared by DDD. The tool generates a global definition c-code file, which contains all used global variables. This file can later be compiled and linked to the project in the build process.
DDD shall also generate a variable declaration c-header for each software component. This header shall only contain declarations for the variables specified in the interface description of the component.

### Calibration Tool support
DDD shall support the A2L file format, to integrate the resulting sw into common calibration tools used in the automotive industry.
## File formats
All files used by DDD contain simple json formatting.
### Project description
Contains a list of components (or other (sub-)projects)
### Software component description
The top level key `"component"` is mandatory, and it contains the follwing elements:
    
*   `"name"` The name of the component
*   `"declarations"` A list of variable declaration objects

Each variable declaration contains:

* `"scope"` One of input/output/local, indicating the scope of the declaration
* `"condition"` A c-preprocessor conditional expression which will wrap the generated variable declarations (optional)
* `"definition"` A variable-definition object

Example file:
- - -

```
    {
    	"component": {
    		"name": "ModuleA",
    		"declarations": [{
    			"definition": {
    				"name": "Variable2",
    				"datatype": {
    					"basetype": "sint16",
    					"conversion": {
    						"type": "linear",
    						"numerator": 4,
    						"denominator": 10,
    						"offset": 10
    					}
    				}
    			},
    			"scope": "output",
    			"condition": "Mydefine_D==1"
    		}]
    
    	}
    }
```
- - -
## Repository Structure
objects,index,tags
## Code Structure
### .ddd file handler
asd
### Repository handler
interface,

### DB Class
Database class
Supported functions:

* add
* check
* commit


## Command Line Interface