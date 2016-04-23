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
	python $(DDD) init repo

source:
	mkdir $(SOURCE)

$(INDEX)/component/ModuleA: ModuleA/ModuleA.ddd repo
	python $(DDD) add ModuleA/ModuleA.ddd $(REPO)
$(INDEX)/component/ModuleB: ModuleB/ModuleB.ddd repo
	python $(DDD) add ModuleB/ModuleB.ddd $(REPO)
$(INDEX)/project/projectxx: project.ddd $(INDEX)/component/ModuleB $(INDEX)/component/ModuleA repo
	python $(DDD) add project.ddd $(REPO)

$(SOURCE)/ModuleA_decl.h:$(INDEX)/component/ModuleA project_check source
	python $(DDD) export component/ModuleA --template decl.h --output $(SOURCE)/ModuleA_decl.h repo
$(SOURCE)/ModuleB_decl.h:$(INDEX)/component/ModuleB project_check source
	python $(DDD) export component/ModuleB --template decl.h --output $(SOURCE)/ModuleB_decl.h repo
$(SOURCE)/projectxx_def.c:$(INDEX)/project/projectxx project_check source
	python $(DDD) export project/projectxx --template def.c --output $(SOURCE)/projectxx_def.c repo

$(SOURCE)/conditions.dummy: $(INDEX)/projectxx
	python $(DDD) export project/projectxx --template conditions.json --output $(SOURCE)/conditions.dummy repo
$(SOURCE)/conditions.json: $(SOURCE)/conditions.dummy
	dcc $(SOURCE)/conditions.dummy -P -o $(SOURCE)/conditions.json

export_sources:$(SOURCE)/ModuleA_decl.h $(SOURCE)/ModuleB_decl.h $(SOURCE)/projectxx_def.c
	echo hallo

project_check: $(INDEX)/project/projectxx
	python $(DDD) check project/projectxx $(REPO)
	touch project_check

build.txt: $(INDEX)/project/projectxx
	if ! test -f build.txt; then echo 0 > build.txt; fi
	echo $$(($$(cat build.txt) + 1)) > build.txt

commit: project_check build.txt
	python $(DDD) commit project/projectxx --message "autocommit" --tag $$(cat build.txt) $(REPO)

view:
	python $(DDD) view $(REPO)
	$(EXPLORER_CMD) viewer.html
    
view_project: $(INDEX)/project/projectxx
	python $(DDD) view projectxx $(REPO)
	$(EXPLORER_CMD) viewer.html

clean:
	rm -rf $(REPO)
	rm build.txt
