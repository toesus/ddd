REPO=repo
INDEX=$(REPO)/index
SOURCE=source

ifeq ($(OS),Windows_NT)
    DDD=c:/git/ddd/ddd.py
    EXPLORER_CMD = explorer
else
    DDD=~/workspace/ddd/ddd.py
    EXPLORER_CMD = xdg-open
endif
repo:
	python $(DDD) init


$(REPO)/project.ddd:ModuleA/ModuleA.ddd ModuleB/ModuleB.ddd config.ddd repo
	python $(DDD) combine ModuleA/ModuleA.ddd ModuleB/ModuleB.ddd --config config.ddd --output $(REPO)/project.ddd

project_check: $(REPO)/project.ddd $(SOURCE)/conditions.json
	python $(DDD) check $(REPO)/project.ddd --config config.ddd --conditions $(SOURCE)/conditions.json
	touch project_check
	
$(SOURCE)/ModuleA_decl.h:ModuleA/ModuleA.ddd config.ddd
	python $(DDD) export ModuleA/ModuleA.ddd --config config.ddd --template decl.h --output $(SOURCE)/ModuleA_decl.h
$(SOURCE)/ModuleB_decl.h:ModuleB/ModuleB.ddd config.ddd
	python $(DDD) export ModuleB/ModuleB.ddd --config config.ddd --template decl.h --output $(SOURCE)/ModuleB_decl.h
$(SOURCE)/project_def.c: $(REPO)/project.ddd project_check
	python $(DDD) export $(REPO)/project.ddd --config config.ddd --template def.c --output $(SOURCE)/project_def.c

$(SOURCE)/conditions.dummy: $(REPO)/project.ddd
	python $(DDD) export $(REPO)/project.ddd --template conditions.json --output $(SOURCE)/conditions.dummy
$(SOURCE)/conditions.json: $(SOURCE)/conditions.dummy
	gcc -x c $(SOURCE)/conditions.dummy -E -P -o $(SOURCE)/conditions.json
	
build.txt: $(REPO)/project.ddd
	if ! test -f build.txt; then echo 0 > build.txt; fi
	echo $$(($$(cat build.txt) + 1)) > build.txt

commit:$(SOURCE)/ModuleA_decl.h $(SOURCE)/ModuleB_decl.h $(SOURCE)/project_def.c build.txt
	python $(DDD) commit $(REPO)/project.ddd --message "autocommit" --tag $$(cat build.txt)

view:
	python $(DDD) view $(REPO)
	$(EXPLORER_CMD) viewer.html

clean:
	rm -rf $(REPO)
	rm build.txt project_check -f
	rm $(SOURCE)/conditions.json $(SOURCE)/conditions.dummy $(SOURCE)/ModuleA_decl.h $(SOURCE)/ModuleB_decl.h $(SOURCE)/project_def.c -f
